from app import db
from sqlalchemy import types
from datetime import datetime


class Broup(db.Model):
    """
    A Bro group
    """
    __tablename__ = 'Broup'
    id = db.Column(db.Integer, primary_key=True)
    broup_id = db.Column(db.Integer, unique=False)
    bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    bro_ids = db.Column(types.ARRAY(db.Integer))
    bro_admin_ids = db.Column(types.ARRAY(db.Integer))
    broup_name = db.Column(db.String)
    alias = db.Column(db.String)
    broup_description = db.Column(db.String)
    broup_colour = db.Column(db.String)
    room_name = db.Column(db.String)
    last_message_read_time_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_time_activity = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unread_messages = db.Column(db.Integer)
    mute = db.Column(db.Boolean, default=False)
    removed = db.Column(db.Boolean, default=False)
    blocked_timestamps = db.Column(types.ARRAY(db.DateTime))

    def update_last_message_read_time_bro(self, read_time):
        self.last_message_read_time_bro = read_time

    def get_last_message_read_time_bro(self):
        return self.last_message_read_time_bro

    def update_unread_messages(self):
        self.unread_messages += 1

    def read_messages(self):
        self.unread_messages = 0

    def get_admins(self):
        return self.bro_admin_ids

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
        if self.bro_ids is None:
            self.bro_ids = []
        old_bros = self.bro_ids
        new_bros = []
        for old in old_bros:
            new_bros.append(old)
        new_bros.append(bro_id)
        self.bro_ids = new_bros

    def get_participants(self):
        return self.bro_ids

    def add_admin(self, bro_id):
        if self.bro_admin_ids is None:
            self.bro_admin_ids = []
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
        self.last_time_activity = datetime.utcnow()

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

    def broup_removed(self):
        self.removed = True

    def is_removed(self):
        return self.removed

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
            'room_name': self.room_name,
            'mute': self.mute
        }
