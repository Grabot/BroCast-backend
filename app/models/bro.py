from passlib.apps import custom_app_context as pwd_context
from app import db


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
    password_hash = db.Column(db.Text)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'bro_name': self.bro_name,
            'bromotion': self.bromotion,
            'password': self.password_hash
        }

