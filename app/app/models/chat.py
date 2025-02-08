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
    __tablename__ = 'Chat'
    id: int = Field(default=None, primary_key=True)
    bro_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    bro_admin_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    private: bool = Field(default=True)  # indicates if it's a private chat between 2 bros
    broup_description: str
    broup_colour: str
    default_avatar: bool = Field(default=True)
    current_message_id: int
    last_message_read_time_bro: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    last_message_received_time_bro: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    # We don't need to send these details all the time. Only when needed.
    broup_updated: bool = Field(default=True)  # TODO: implement this?
    # Don't send the avatar every time. Only send it if changes have been made.
    new_avatar: bool = Field(default=True)  # TODO: implement this?

    chat_broups: "Broup" = Relationship(
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

    # def set_admins(self, bro_admin_ids):
    #     self.bro_admin_ids = bro_admin_ids

    # def get_admins(self):
    #     return self.bro_admin_ids

    # def add_participant(self, bro_id):
    #     old_bros = self.bro_ids
    #     new_bros = []
    #     for old in old_bros:
    #         new_bros.append(old)
    #     new_bros.append(bro_id)
    #     self.bro_ids = new_bros

    # def add_admin(self, bro_id):
    #     old_admins = self.bro_admin_ids
    #     new_admins = []
    #     for old in old_admins:
    #         new_admins.append(old)
    #     new_admins.append(bro_id)
    #     self.bro_admin_ids = new_admins

    # def dismiss_admin(self, bro_id):
    #     if self.bro_admin_ids is None:
    #         self.bro_admin_ids = []
    #     old_admins = self.bro_admin_ids
    #     new_admins = []
    #     for old in old_admins:
    #         if old != bro_id:
    #             new_admins.append(old)
    #     self.bro_admin_ids = new_admins

    # def remove_bro(self, bro_id):
    #     if bro_id in self.bro_admin_ids:
    #         self.dismiss_admin(bro_id)
    #     if self.bro_ids is None:
    #         self.bro_ids = []
    #     old_bros = self.bro_ids
    #     new_bros = []
    #     for old in old_bros:
    #         if old != bro_id:
    #             new_bros.append(old)
    #     self.bro_ids = new_bros

    def update_description(self, description):
        self.broup_description = description

    def get_broup_description(self):
        return self.broup_description

    def update_colour(self, colour):
        self.broup_colour = colour

    def avatar_filename(self):
        # We need something that is unique for each broup but doesn't change
        # So we use the broup_id
        broup_indicator = f"broup_{self.id}"
        return md5(broup_indicator.encode("utf-8")).hexdigest()

    def avatar_filename_small(self):
        return self.avatar_filename() + "_small"

    def avatar_filename_default(self):
        return self.avatar_filename() + "_default"

    def get_bro_avatar(self, full=False):
        if self.default_avatar:
            file_name = self.avatar_filename_default()
        else:
            if full:
                file_name = self.avatar_filename()
            else:
                file_name = self.avatar_filename_small()
        file_folder = settings.UPLOAD_FOLDER_AVATARS

        file_path = os.path.join(file_folder, "%s.png" % file_name)
        if not os.path.isfile(file_path):
            return None
        else:
            with open(file_path, "rb") as fd:
                image_as_base64 = base64.encodebytes(fd.read()).decode()
            return image_as_base64

    @property
    def serialize(self):
        return {
            'broup_id': self.id,
            'bro_ids': self.bro_ids,
            'admin_ids': self.bro_admin_ids,
            'private': self.private,
            'broup_description': self.broup_description,
            'broup_colour': self.broup_colour,
        }
    