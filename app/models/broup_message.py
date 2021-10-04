from app import db
from datetime import datetime


class BroupMessage(db.Model):
    """
    The Broup Message object. Here we have the Bro who send the message and the Broup who received it.
    """
    __tablename__ = 'BroupMessage'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    broup_id = db.Column(db.Integer)  # Foreign key to Broup
    body = db.Column(db.Text)
    text_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_timestamp(self):
        return self.timestamp

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'broup_id': self.broup_id,
            'body': self.body,
            'text_message': self.text_message,
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
        }
