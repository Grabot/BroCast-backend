from app import db
from datetime import datetime
from sqlalchemy import types


class BroBros(db.Model):
    """
    A connection between one bro and another bro.
    Here we store which bros are connected
    and also the last time both bros read the chat
    """
    __tablename__ = 'BroBros'
    id = db.Column(db.Integer, primary_key=True)
    bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    bros_bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    chat_name = db.Column(db.String)
    alias = db.Column(db.String)
    chat_description = db.Column(db.String)
    chat_colour = db.Column(db.String)
    room_name = db.Column(db.String)
    last_message_read_time_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_time_activity = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unread_messages = db.Column(db.Integer)
    blocked = db.Column(db.Boolean, default=False)
    mute = db.Column(db.Boolean, default=False)
    removed = db.Column(db.Boolean, default=False)
    mute_timestamp = db.Column(db.DateTime)
    blocked_timestamps = db.Column(types.ARRAY(db.DateTime))

    def update_unread_messages(self):
        self.unread_messages += 1

    def read_messages(self):
        self.unread_messages = 0

    def update_last_activity(self):
        self.last_time_activity = datetime.utcnow()

    def update_description(self, description):
        self.chat_description = description

    def update_alias(self, alias):
        self.alias = alias

    def update_colour(self, colour):
        self.chat_colour = colour

    def block_chat(self, blocked):
        self.blocked = blocked

    def is_blocked(self):
        return self.blocked

    def mute_chat(self, mute):
        self.mute = mute

    def is_muted(self):
        return self.mute

    def check_mute(self):
        if self.mute_timestamp is not None and self.mute_timestamp < datetime.now().utcnow():
            self.set_mute_timestamp(None)
            self.mute_chat(False)
            return True
        return False

    def bro_removed(self):
        self.removed = True

    def is_removed(self):
        return self.removed

    def add_blocked_timestamp(self):
        if self.blocked_timestamps is None:
            self.blocked_timestamps = []
        blocks = []
        for blocked_time in self.blocked_timestamps:
            blocks.append(blocked_time)
        blocks.append(datetime.utcnow())
        self.blocked_timestamps = blocks

    def get_blocked_timestamps(self):
        return self.blocked_timestamps

    def has_been_blocked(self):
        return self.blocked_timestamps is not None and len(self.blocked_timestamps) >= 1

    def get_mute_timestamp(self):
        return self.mute_timestamp

    def set_mute_timestamp(self, mute_timestamp):
        self.mute_timestamp = mute_timestamp

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bro_id': self.bro_id,
            'bros_bro_id': self.bros_bro_id,
            'chat_name': self.chat_name,
            'alias': self.alias,
            'chat_description': self.chat_description,
            'chat_colour': self.chat_colour,
            'unread_messages': self.unread_messages,
            'last_time_activity': self.last_time_activity.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'room_name': self.room_name,
            'blocked': self.blocked,
            'mute': self.mute
        }

