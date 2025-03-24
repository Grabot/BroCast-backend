from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column, ARRAY, Integer
import pytz
from app.config.config import settings
import base64
import os
from hashlib import md5

# from models import Broup


class Chat(SQLModel, table=True):
    """
    A Chat
    """

    __tablename__ = "Chat"
    id: int = Field(default=None, primary_key=True)
    bro_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    bro_admin_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    private: bool = Field(default=True)  # indicates if it's a private chat between 2 bros
    broup_name: str
    broup_description: str
    broup_colour: str
    default_avatar: bool = Field(default=True)
    current_message_id: int
    last_message_read_time_bro: datetime = Field(
        default=datetime.now(pytz.utc).replace(tzinfo=None)
    )
    last_message_received_time_bro: datetime = Field(
        default=datetime.now(pytz.utc).replace(tzinfo=None)
    )

    chat_broups: List["Broup"] = Relationship(
        back_populates="chat",
        sa_relationship_kwargs={
            "uselist": True,
            "primaryjoin": "Chat.id==Broup.broup_id",
        },
    )

    def update_last_message_received_time_bro(self):
        self.last_message_received_time_bro = datetime.now(pytz.utc).replace(tzinfo=None)

    def get_last_message_received_time_bro(self):
        return self.last_message_received_time_bro

    def get_broup_colour(self):
        return self.broup_colour

    def get_participants(self):
        return self.bro_ids

    def set_participants(self, bro_ids):
        self.bro_ids = bro_ids

    def set_broup_colour(self, new_broup_colour):
        self.broup_colour = new_broup_colour

    def set_admins(self, bro_admin_ids):
        self.bro_admin_ids = bro_admin_ids

    def get_admins(self):
        return self.bro_admin_ids

    def add_participant(self, bro_id):
        old_bros = self.bro_ids
        new_bros = []
        for old in old_bros:
            new_bros.append(old)
        if bro_id not in new_bros:
            new_bros.append(bro_id)
        new_bros.sort()
        self.bro_ids = new_bros
    
    def remove_participant(self, bro_id):
        if self.bro_ids is None:
            self.bro_ids = []
        old_bros = self.bro_ids
        new_bros = []
        for old in old_bros:
            if old != bro_id:
                new_bros.append(old)
        self.bro_ids = new_bros

    def add_admin(self, bro_id):
        old_admins = self.bro_admin_ids
        new_admins = []
        for old in old_admins:
            new_admins.append(old)
        if bro_id not in new_admins:
            new_admins.append(bro_id)
        new_admins.sort()
        self.bro_admin_ids = new_admins

    def dismiss_admin(self, bro_id):
        if self.bro_admin_ids is None:
            self.bro_admin_ids = []
        old_admins = self.bro_admin_ids
        new_admins = []
        for old in old_admins:
            if old != bro_id:
                new_admins.append(old)
        self.bro_admin_ids = new_admins

    def update_broup_description(self, description):
        self.broup_description = description

    def get_broup_description(self):
        return self.broup_description

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def get_broup_name(self):
        return self.broup_name

    def is_default(self):
        return self.default_avatar
    
    def avatar_filename(self):
        # We need something that is unique for each broup but doesn't change
        # So we use the broup_id
        broup_indicator = f"broup_{self.id}"
        return md5(broup_indicator.encode("utf-8")).hexdigest()

    def avatar_filename_default(self):
        return self.avatar_filename() + "_default"
    
    def set_default_avatar(self, value):
        self.default_avatar = value

    def get_broup_avatar(self):
        if self.default_avatar:
            file_name = self.avatar_filename_default()
        else:
            file_name = self.avatar_filename()
        file_folder = settings.UPLOAD_FOLDER_AVATARS

        file_path = os.path.join(file_folder, "%s.png" % file_name)
        if not os.path.isfile(file_path):
            return None
        else:
            with open(file_path, "rb") as fd:
                image_as_base64 = base64.encodebytes(fd.read()).decode()
            return image_as_base64
    
    def delete_broup_avatar(self):
        file_folder = settings.UPLOAD_FOLDER_AVATARS
        file_name = self.avatar_filename_default()
        file_path = os.path.join(file_folder, "%s.png" % file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
        file_name_avatar = self.avatar_filename()
        file_path_avatar = os.path.join(file_folder, "%s.png" % file_name_avatar)
        if os.path.isfile(file_path_avatar):
            os.remove(file_path_avatar)
            

    @property
    def serialize(self):
        # Avatar is not included and is retrieved with a seperate call.
        return {
            "bro_ids": self.bro_ids,
            "admin_ids": self.bro_admin_ids,
            "broup_name": self.broup_name,
            "private": self.private,
            "broup_description": self.broup_description,
            "broup_colour": self.broup_colour,
        }
    