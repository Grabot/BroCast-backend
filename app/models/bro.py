from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from app.config import Config

from app import db
from app.models.bro_bros import BroBros


class Bro(db.Model):
    """
    Bro that is stored in the database.
    The bro has a unique id and bro name
    The bros of the bro are stored and the message he send and received as well.
    The password is hashed and it can be checked.
    """
    __tablename__ = 'Bro'
    id = db.Column(db.Integer, primary_key=True)
    # The bro name and the bromotion don't have to be unique. But the combination has to be! Do that in the code.
    bro_name = db.Column(db.Text, index=True, unique=False)
    bromotion = db.Column(db.Text, index=True, unique=False)
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
    password_hash = db.Column(db.Text)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = Bro.query.get(data['id'])
        return user

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

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'bro_name': self.bro_name,
            'bromotion': self.bromotion
        }

