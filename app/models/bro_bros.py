from app import db


class BroBros(db.Model):
    """
    Bro that is stored in the database.
    The bro has a unique id and bro name
    The bros of the bro are stored and the message he send and received as well.
    The password is hashed and it can be checked.
    """
    __tablename__ = 'BroBros'
    id = db.Column(db.Integer, primary_key=True)
    bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))
    bros_bro_id = db.Column(db.Integer, db.ForeignKey('Bro.id'))

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'bro_id': self.bro_id,
            'bros_bro_id': self.bros_bro_id
        }

