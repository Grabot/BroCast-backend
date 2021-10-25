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
    blocked = db.Column(db.Boolean, default=False)
    removed = db.Column(db.Boolean, default=False)
    blocked_timestamps = db.Column(types.ARRAY(db.DateTime))

    def update_last_activity(self):
        self.last_time_activity = datetime.utcnow()

    def update_description(self, description):
        self.broup_description = description

    def update_alias(self, alias):
        self.alias = alias

    def update_colour(self, colour):
        self.broup_colour = colour

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
            'blocked': self.blocked
        }
