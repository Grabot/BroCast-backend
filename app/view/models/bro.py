from app import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


bro_bros = db.Table(
    'bro_bros',
    db.Column('bro_id', db.Integer, db.ForeignKey('bro.id')),
    db.Column('bros_bro_id', db.Integer, db.ForeignKey('bro.id'))
)


class Bro(db.Model):
    """
    Bro that is stored in the database.
    The bro has a unique id and bro name
    The password is hashed and it can be checked.
    """
    id = db.Column(db.Integer, primary_key=True)
    bro_name = db.Column(db.String(64), index=True, unique=True)
    bros = db.relationship(
        'Bro',
        secondary=bro_bros,
        primaryjoin=(bro_bros.c.bro_id == id),
        secondaryjoin=(bro_bros.c.bros_bro_id == id),
        backref=db.backref('bro_bros', lazy='dynamic'), lazy='dynamic')
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

    def add_bro(self, bro):
        if not self.get_bro(bro):
            self.bros.append(bro)

    def remove_bro(self, bro):
        if self.get_bro(bro):
            self.bros.remove(bro)

    def get_bro(self, bro):
        # TODO @Sander: check if this is correct.
        return self.bros.filter(
            bro_bros.c.bros_bro_id == bro.id).count() > 0
