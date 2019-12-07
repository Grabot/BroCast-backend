from app import db
from datetime import datetime


class Message(db.Model):
    __tablename__ = 'Message'
    id = db.Column(db.Integer, primary_key=True)
    bro_bros_id = db.Column(db.Integer, db.ForeignKey('BroBros.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

