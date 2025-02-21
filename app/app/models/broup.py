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
    last_message_read_time: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    last_message_received_time: datetime = Field(
        default=datetime.now(pytz.utc).replace(tzinfo=None)
    )
    unread_messages: int
    mute: bool = Field(default=False)
    mute_timestamp: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    removed: bool = Field(default=False)
    deleted: bool = Field(default=False)
    # This is different from the unread messages.
    # The bro can have received the message, but not read it.
    # In this case this variable will remain False. If the bro later receives more messages without
    # his phone being active this variable will indicate that he has to retrieve the new messages.
    new_messages: bool = Field(default=False)
    new_members: bool = Field(default=True)
    # We don't need to send these details all the time. Only when needed.
    broup_updated: bool = Field(default=True)
    update_bros: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))

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
        # If you've read the message you've received it as well.
        self.last_message_received_time = last_message_read_time

    def received_message(self, last_message_received_time):
        # The bro has received a new message
        self.last_message_received_time = last_message_received_time
        self.new_messages = False

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
    
    def bros_retrieved(self):
        self.update_bros = []

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

    def is_removed(self):
        return self.removed

    def get_mute_timestamp(self):
        return self.mute_timestamp

    def set_mute_timestamp(self, mute_timestamp):
        self.mute_timestamp = mute_timestamp

    @property
    def serialize(self):
        return {
            "broup_id": self.broup_id,
            "bro_id": self.bro_id,
            "alias": self.alias,
            "unread_messages": self.unread_messages,
            "removed": self.removed,
            "mute": self.mute,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
            "update_bros": self.update_bros,
            "chat": self.chat.serialize,
        }

    @property
    def serialize_minimal(self):
        return {
            "broup_id": self.broup_id,
            "bro_id": self.bro_id,
            "unread_messages": self.unread_messages,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
        }

    @property
    def serialize_no_chat(self):
        return {
            "broup_id": self.broup_id,
            "bro_id": self.bro_id,
            "alias": self.alias,
            "unread_messages": self.unread_messages,
            "removed": self.removed,
            "mute": self.mute,
            "broup_updated": self.broup_updated,
            "new_messages": self.new_messages,
        }
