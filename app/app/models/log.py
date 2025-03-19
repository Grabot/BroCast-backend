from datetime import datetime
import pytz
from sqlmodel import Field, SQLModel
import json


class Log(SQLModel, table=True):
    """
    Logging from the reports of bros.
    When a bro reports another bro the chat messages are stored here in the logs so they can be viewed later.
    If it is determined that the messages are UNACCEPTABLE! Than that bro's account shall be removed!
    If not, than the blocking of the bro will be deemed sufficient.
    """
    __tablename__ = "Log"
    id: int = Field(default=None, primary_key=True)
    report_from: str
    report_broup: str
    report_broup_id: int
    messages: str
    report_date: datetime = Field(
        default=datetime.now(pytz.utc).replace(tzinfo=None)
    )


    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'report_from': self.report_from,
            'report_broup': self.report_broup,
            'messages': json.loads(self.messages),
            'report_date': self.report_date.strftime('%Y-%m-%dT%H:%M:%S.%f'),
        }