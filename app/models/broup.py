from app import db
from sqlalchemy import types
from datetime import datetime


class Broup(db.Model):
    """
    A Bro group
    """
    __tablename__ = 'Broup'
    id = db.Column(db.Integer, primary_key=True)
    broup_id = db.Column(db.Integer, unique=True)
    bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    bro_ids = db.Column(types.ARRAY(db.Integer))
    broup_name = db.Column(db.String)
    broup_description = db.Column(db.String)
    broup_colour = db.Column(db.String)
    room_name = db.Column(db.String)
    last_message_read_time_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_time_activity = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unread_messages = db.Column(db.Integer)
    blocked = db.Column(db.Boolean, default=False)
    removed = db.Column(db.Boolean, default=False)
    blocked_timestamps = db.Column(types.ARRAY(db.DateTime))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bro_id': self.bro_id,
            'bro_ids': self.bro_ids,
            'broup_name': self.broup_name,
            'broup_description': self.broup_description,
            'broup_colour': self.broup_colour,
            'unread_messages': self.unread_messages,
            'last_time_activity': self.last_time_activity.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'room_name': self.room_name,
            'blocked': self.blocked
        }
