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
    __tablename__ = 'Broup'
    id: int = Field(default=None, primary_key=True)
    bro_id: int = Field(foreign_key="Bro.id")
    broup_id: int = Field(foreign_key="Chat.id")
    broup_name: str
    alias: str
    last_message_read_time: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    last_message_received_time: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    unread_messages: int
    mute: bool = Field(default=False)
    mute_timestamp: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    removed: bool = Field(default=False)
    is_left: bool = Field(default=False)
    # This is different from the unread messages. 
    # The bro can have received the message, but not read it.
    # In this case this variable will remain False. If the bro later receives more messages without
    # his phone being active this variable will indicate that he has to retrieve the new messages.
    new_messages: bool = Field(default=False)  # TODO: implement this?
    # We don't need to send these details all the time. Only when needed.
    broup_updated: bool = Field(default=False)  # TODO: implement this?

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

    def read_messages(self, last_message_read_time):
        self.unread_messages = 0
        self.new_messages = False
        self.last_message_read_time = last_message_read_time
    
    def received_message(self):
        # The bro has received a new message
        self.new_messages = False

    def set_updated(self, update_value=True):
        self.broup_updated = update_value

    def get_alias(self):
        return self.alias

    def get_bro_id(self):
        return self.bro_id

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def get_broup_name(self):
        return self.broup_name

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def update_last_message_received(self):
        self.last_message_received_time = datetime.now(pytz.utc).replace(tzinfo=None)

    def update_broup_alias(self, new_broup_alias):
        self.alias = new_broup_alias

    def mute_broup(self, mute):
        self.mute = mute

    def is_muted(self):
        return self.mute

    def check_mute(self):
        if self.is_muted() and self.mute_timestamp < datetime.now(pytz.utc).replace(tzinfo=None):
            self.mute_broup(False)
            return True
        return False

    def broup_removed(self):
        self.removed = True

    def is_removed(self):
        return self.removed

    def leave_broup(self):
        self.is_left = True
        self.unread_messages = 0

    def has_left(self):
        return self.is_left

    def rejoin(self):
        self.is_left = False
        self.removed = False

    def get_mute_timestamp(self):
        return self.mute_timestamp

    def set_mute_timestamp(self, mute_timestamp):
        self.mute_timestamp = mute_timestamp


    @property
    def serialize(self):
        return {
            'broup_id': self.broup_id,
            'bro_id': self.bro_id,
            'alias': self.alias,
            'broup_name': self.broup_name,
            'unread_messages': self.unread_messages,
            'left': self.is_left,
            'mute': self.mute,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
            "chat": self.chat.serialize,
        }
    
    @property
    def serialize_minimal(self):
        return {
            'broup_id': self.broup_id,
            'bro_id': self.bro_id,
            'unread_messages': self.unread_messages,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
        }
    
    @property
    def serialize_no_chat(self):
        return {
            'broup_id': self.broup_id,
            'bro_id': self.bro_id,
            'alias': self.alias,
            'broup_name': self.broup_name,
            'unread_messages': self.unread_messages,
            'left': self.is_left,
            'mute': self.mute,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
        }
