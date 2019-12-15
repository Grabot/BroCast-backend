from datetime import datetime
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from app import db
from app.view.models.bro_bros import BroBros
from app.view.models.message import Message


class Bro(db.Model):
    """
    Bro that is stored in the database.
    The bro has a unique id and bro name
    The bros of the bro are stored and the message he send and received as well.
    The password is hashed and it can be checked.
    """
    __tablename__ = 'Bro'
    id = db.Column(db.Integer, primary_key=True)
    bro_name = db.Column(db.String(64), index=True, unique=True)
    bros = db.relationship('BroBros',
                           foreign_keys=[BroBros.bro_id],
                           backref=db.backref('bro_bros', lazy='joined'),
                           lazy='dynamic',
                           cascade='all, delete-orphan')
    bro_bros = db.relationship('BroBros',
                               foreign_keys=[BroBros.bros_bro_id],
                               backref=db.backref('bros', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    password_hash = db.Column(db.String(128))
    registration_id = db.Column(db.String(255))
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_password(self):
        return self.password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()

    # TODO: figure out how this works when it is his own table
    def add_bro(self, bro):
        if not self.get_bro(bro):
            b = BroBros(bro_id=self.id, bros_bro_id=bro.id)
            db.session.add(b)

    def remove_bro(self, bro):
        # This is to remove a bro connection, not the bro itself.
        if self.get_bro(bro):
            bro_bros_query = BroBros.query.filter_by(bro_id=self.id, bros_bro_id=bro.id).first()
            # Just a safety check to make sure it exists before deleting it.
            if bro_bros_query is not None:
                BroBros.query.filter_by(bro_id=self.id, bros_bro_id=bro.id).delete()

    def get_bro(self, bro):
        # see if the bro that is passed is already in the BroBros list
        if bro.id is None:
            return False
        return self.bros.filter_by(bros_bro_id=bro.id).first() is not None

