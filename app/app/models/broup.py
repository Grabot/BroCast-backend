from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship, Column, ARRAY, Integer
import pytz
from app.config.config import settings
from hashlib import md5


class Broup(SQLModel, table=True):
    """
    A Bro group
    """

    __tablename__ = "Broup"
    id: int = Field(default=None, primary_key=True)
    bro_id: int = Field(foreign_key="Bro.id")
    broup_id: int = Field(foreign_key="Chat.id")
    alias: str
    unread_messages: int
    mute: bool = Field(default=False)
    # Determines if the bro currently has the chat open.
    open: bool = Field(default=False)
    mute_timestamp: Optional[datetime]
    removed: bool = Field(default=False)
    deleted: bool = Field(default=False)
    # This is different from the unread messages.
    # The bro can have received the message, but not read it.
    # In this case this variable will remain False. If the bro later receives more messages without
    # his phone being active this variable will indicate that he has to retrieve the new messages.
    new_messages: bool = Field(default=False)
    # We don't need to send these details all the time. Only when needed.
    broup_updated: bool = Field(default=True)
    # If a bro made a change to themselves we have to update that in the broup.
    update_bros: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    update_bros_avatar: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    # Don't send the avatar every time. Only send it if changes have been made.
    new_avatar: bool = Field(default=True)
    last_message_read_id: int = Field(default=0)

    chat: "Chat" = Relationship(
        back_populates="chat_broups",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "Chat.id==Broup.broup_id",
        },
    )

    broup_member: "Bro" = Relationship(
        back_populates="broups",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "Bro.id==Broup.bro_id",
        },
    )

    def update_unread_messages(self):
        self.unread_messages += 1
        self.new_messages = True

    def get_alias(self):
        return self.alias

    def get_bro_id(self):
        return self.bro_id

    def add_bro_to_update(self, bro_id):
        old_update_bros = self.update_bros
        new_update_bros = []
        for old in old_update_bros:
            new_update_bros.append(old)
        if bro_id not in new_update_bros:
            new_update_bros.append(bro_id)
        self.update_bros = new_update_bros
    
    def dismiss_bro_to_update(self, bro_id):
        if self.update_bros is None:
            self.update_bros = []
        old_bros = self.update_bros
        new_bros = []
        for old in old_bros:
            if old != bro_id:
                new_bros.append(old)
        self.update_bros = new_bros
    
    def add_bro_avatar_to_update(self, bro_id):
        old_update_bros_avatar = self.update_bros_avatar
        new_update_bros_avatar = []
        for old in old_update_bros_avatar:
            new_update_bros_avatar.append(old)
        if bro_id not in new_update_bros_avatar:
            new_update_bros_avatar.append(bro_id)
        self.update_bros_avatar = new_update_bros_avatar
    
    def dismiss_bro_avatar_to_update(self, bro_id):
        if self.update_bros_avatar is None:
            self.update_bros_avatar = []
        old_bros_avatar = self.update_bros_avatar
        new_bros_avatar = []
        for old in old_bros_avatar:
            if old != bro_id:
                new_bros_avatar.append(old)
        self.update_bros_avatar = new_bros_avatar
    

    def bros_retrieved(self):
        self.update_bros = []

    def update_broup_alias(self, new_broup_alias):
        self.alias = new_broup_alias

    def mute_broup(self, mute):
        self.mute = mute

    def is_muted(self):
        return self.mute

    def check_mute(self):
        if self.is_muted() and (self.mute_timestamp is not None and self.mute_timestamp < datetime.now(pytz.utc).replace(tzinfo=None)):
            self.mute_broup(False)
            self.set_mute_timestamp(None)
            return True
        return False

    def is_removed(self):
        return self.removed

    def get_mute_timestamp(self):
        return self.mute_timestamp

    def set_mute_timestamp(self, mute_timestamp):
        self.mute_timestamp = mute_timestamp


    @property
    def serialize(self):
        data = {
            "broup_id": self.broup_id,
            "alias": self.alias,
            "unread_messages": self.unread_messages,
            "last_message_read_id_chat": self.chat.last_message_read_id_chat,
            "removed": self.removed,
            "mute": self.mute,
            "chat": self.chat.serialize,
        }
        if self.update_bros is not None and len(self.update_bros) > 0:
            data["update_bros"] = self.update_bros
            self.update_bros = []
        if self.update_bros_avatar is not None and len(self.update_bros_avatar) > 0:
            data["update_bros_avatar"] = self.update_bros_avatar
            self.update_bros_avatar = []
        if self.broup_updated:
            data["broup_updated"] = self.broup_updated
            self.broup_updated = False
        if self.new_messages:
            data["new_messages"] = self.new_messages
            self.new_messages = False
        if self.new_avatar:
            data["new_avatar"] = self.new_avatar
            self.new_avatar = False
        return data


    @property
    def serialize_avatar(self):
        # Full retrieval call.
        data = {
            "broup_id": self.broup_id,
            "alias": self.alias,
            "unread_messages": self.unread_messages,
            "last_message_read_id_chat": self.chat.last_message_read_id_chat,
            "removed": self.removed,
            "mute": self.mute,
            "chat": self.chat.serialize_avatar,
        }
        if self.update_bros is not None and len(self.update_bros) > 0:
            data["update_bros"] = self.update_bros
        if self.update_bros_avatar is not None and len(self.update_bros_avatar) > 0:
            data["update_bros_avatar"] = self.update_bros_avatar
        if self.broup_updated:
            data["broup_updated"] = self.broup_updated
        if self.new_messages:
            data["new_messages"] = self.new_messages
        if self.new_avatar:
            data["new_avatar"] = self.new_avatar
        return data

    @property
    def serialize_only_avatar(self):
        return {
            "broup_id": self.broup_id,
            "chat": self.chat.serialize_only_avatar
        }

    @property
    def serialize_new_avatar(self):
        data = {
            "broup_id": self.broup_id,
            "unread_messages": self.unread_messages,
            "last_message_read_id_chat": self.chat.last_message_read_id_chat,
        }
        if self.new_messages:
            data["new_messages"] = self.new_messages
        if self.new_avatar:
            data["new_avatar"] = self.new_avatar
        return data
    
    @property
    def serialize_removed(self):
        data = {
            "broup_id": self.broup_id,
            "removed": self.removed,
        }
        if self.broup_updated:
            data["broup_updated"] = self.broup_updated
        return data

    @property
    def serialize_messages(self):
        data = {
            "broup_id": self.broup_id,
            "unread_messages": self.unread_messages,
            "last_message_read_id_chat": self.chat.last_message_read_id_chat
        }
        if self.new_messages:
            data["new_messages"] = self.new_messages
        return data

    @property
    def serialize_no_chat(self):
        # Used for creating a new broup, we might not have the chat yet.
        data = {
            "broup_id": self.broup_id,
            "alias": self.alias,
            "unread_messages": self.unread_messages,
            "removed": self.removed,
            "mute": self.mute,
        }
        if self.new_messages:
            data["new_messages"] = self.new_messages
        if self.broup_updated:
            data["broup_updated"] = self.broup_updated
        # We don't include the `new_avatar` here because it should always be true for a new brou
        # So there is not need to include it.
        return data

