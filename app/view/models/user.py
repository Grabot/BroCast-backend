from app import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


user_bros = db.Table(
    'user_bros',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('bro_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
    """
    The User that is stored in the database.
    The user has a unique id and username
    The password is hashed and it can be checked.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    bros = db.relationship(
        'User',
        secondary=user_bros,
        primaryjoin=(user_bros.c.user_id == id),
        secondaryjoin=(user_bros.c.bro_id == id),
        backref=db.backref('user_bros', lazy='dynamic'), lazy='dynamic')
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # TODO @Sander: possibly the password should be hashed in the app and not here.
    def set_password_dangerous(self, password):
        self.password_hash = password

    def get_password(self):
        return self.password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_bro(self, user):
        if not self.get_bro(user):
            self.bros.append(user)

    def remove_bro(self, user):
        if self.get_bro(user):
            self.bros.remove(user)

    def get_bro(self, user):
        # TODO @Sander: check if this is correct.
        return self.bros.filter(
            user_bros.c.bro_id == user.id).count() > 0

