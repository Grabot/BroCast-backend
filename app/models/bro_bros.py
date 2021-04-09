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
    room_name = db.Column(db.String)
    last_message_read_time_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_message_read_time_bros_bro = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def get_bros_bro(bros_bro_id):
        bros_bro = BroBros.query.get(bros_bro_id)
        return bros_bro

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'bro_id': self.bro_id,
            'bros_bro_id': self.bros_bro_id,
            'room_name': self.room_name
        }

