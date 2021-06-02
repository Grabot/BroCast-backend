from app import db
from datetime import datetime


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
    chat_colour = db.Column(db.String)
    room_name = db.Column(db.String)
    last_message_read_time_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_time_activity = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unread_messages = db.Column(db.Integer)

    def update_unread_messages(self):
        self.unread_messages += 1

    def read_messages(self):
        self.unread_messages = 0

    def update_last_activity(self):
        self.last_time_activity = datetime.utcnow()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bro_id': self.bro_id,
            'bros_bro_id': self.bros_bro_id,
            'chat_name': self.chat_name,
            'chat_colour': self.chat_colour,
            'unread_messages': self.unread_messages,
            'last_time_activity': self.last_time_activity.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'room_name': self.room_name
        }

