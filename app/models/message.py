from app import db
from datetime import datetime


class Message(db.Model):
    """
    The Message object. Here we have the Bro who send the message and the Bro who received it.
    We also include the BroBros associate table. This allows use to find all the messages they send to each other.
    Finally we include the body of the message.
    """
    __tablename__ = 'Message'
    id = db.Column(db.Integer, primary_key=True)
    bro_bros_id = db.Column(db.Integer, db.ForeignKey('BroBros.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
