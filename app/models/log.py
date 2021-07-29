from app import db
from datetime import datetime


class Log(db.Model):
    """
    Logging from the reports of bros.
    When a bro reports another bro the chat messages are stored here in the logs so they can be viewed later.
    If it is determined that the messages are UNACCEPTABLE! Than that bro's account shall be removed!
    If not, than the blocking of the bro will be deemed sufficient.
    """
    __tablename__ = 'Log'
    id = db.Column(db.Integer, primary_key=True)
    report_from = db.Column(db.Text, unique=False)
    report_to = db.Column(db.Text, unique=False)
    messages = db.Column(db.Text, unique=False)
    report_date = db.Column(db.DateTime, default=datetime.utcnow)


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'report_from': self.report_from,
            'report_to': self.report_to,
            'messages': self.messages,
            'report_date': self.report_date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }

