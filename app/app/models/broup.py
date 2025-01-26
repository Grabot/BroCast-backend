from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, ForeignKey, Relationship, Column, ARRAY, Integer
import pytz


class Broup(SQLModel, table=True):
    """
    A Bro group
    """
    __tablename__ = 'Broup'
    id: int = Field(default=None, primary_key=True)
    broup_id: int = Field(unique=False)
    bro_id: int = Field(ForeignKey('Bro.id'))
    bro_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    bro_admin_ids: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))
    broup_name: str
    alias: str
    broup_description: str
    broup_colour: str
    last_message_read_time_bro: datetime = Field(index=True, default=datetime.now(pytz.utc).replace(tzinfo=None))
    last_time_activity: datetime = Field(index=True, default=datetime.now(pytz.utc).replace(tzinfo=None))
    unread_messages: int
    mute: bool = Field(default=False)
    mute_timestamp: datetime
    accepted: bool = Field(default=False)
    requested: Optional[bool] = Field(default=None)
    removed: bool = Field(default=False)
    is_left: bool = Field(default=False)

    broup_member: "Bro" = Relationship(
        back_populates="bros",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "Bro.id==Broup.bro_id",
        },
    )

    def update_last_message_read_time_bro(self):
        self.last_message_read_time_bro = datetime.now(pytz.utc).replace(tzinfo=None)

    def get_last_message_read_time_bro(self):
        return self.last_message_read_time_bro

    def update_unread_messages(self):
        self.unread_messages += 1

    def read_messages(self):
        self.unread_messages = 0

    def get_admins(self):
        return self.bro_admin_ids

    def get_alias(self):
        return self.alias

    def set_admins(self, bro_admin_ids):
        self.bro_admin_ids = bro_admin_ids

    def get_bro_id(self):
        return self.bro_id

    def get_broup_name(self):
        return self.broup_name

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def get_broup_colour(self):
        return self.broup_colour

    def add_participant(self, bro_id):
        old_bros = self.bro_ids
        new_bros = []
        for old in old_bros:
            new_bros.append(old)
        new_bros.append(bro_id)
        self.bro_ids = new_bros

    def get_participants(self):
        return self.bro_ids

    def set_participants(self, bro_ids):
        self.bro_ids = bro_ids

    def set_broup_name(self, broup_name):
        self.broup_name = broup_name

    def add_admin(self, bro_id):
        old_admins = self.bro_admin_ids
        new_admins = []
        for old in old_admins:
            new_admins.append(old)
        new_admins.append(bro_id)
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

    def remove_bro(self, bro_id):
        if bro_id in self.bro_admin_ids:
            self.dismiss_admin(bro_id)
        if self.bro_ids is None:
            self.bro_ids = []
        old_bros = self.bro_ids
        new_bros = []
        for old in old_bros:
            if old != bro_id:
                new_bros.append(old)
        self.bro_ids = new_bros

    def update_last_activity(self):
        self.last_time_activity = datetime.now(pytz.utc).replace(tzinfo=None)

    def update_description(self, description):
        self.broup_description = description

    def get_broup_description(self):
        return self.broup_description

    def update_alias(self, alias):
        self.alias = alias

    def update_colour(self, colour):
        self.broup_colour = colour

    def mute_broup(self, mute):
        self.mute = mute

    def is_muted(self):
        return self.mute

    def check_mute(self):
        if self.mute_timestamp is not None and self.mute_timestamp < datetime.now(pytz.utc).replace(tzinfo=None):
            self.set_mute_timestamp(None)
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
            'id': self.broup_id,
            'bro_id': self.bro_id,
            'bro_ids': self.bro_ids,
            'bro_admin_ids': self.bro_admin_ids,
            'broup_name': self.broup_name,
            'alias': self.alias,
            'broup_description': self.broup_description,
            'broup_colour': self.broup_colour,
            'unread_messages': self.unread_messages,
            'last_time_activity': self.last_time_activity.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'left': self.is_left,
            'mute': self.mute
        }