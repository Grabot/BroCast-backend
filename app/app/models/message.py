from datetime import datetime
import time
from typing import Optional
import pytz
from sqlmodel import Field, Relationship, SQLModel


class Message(SQLModel, table=True):
    """
    Message
    """

    __tablename__ = "Message"
    id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="Bro.id")
    broup_id: int = Field(foreign_key="Chat.id")
    message_id: int
    body: str
    text_message: Optional[str]
    timestamp: datetime = Field(default=datetime.now(pytz.utc).replace(tzinfo=None))
    info: bool = Field(default=False)
    data: Optional[str]

    @property
    def serialize(self):
        return {
            'sender_id': self.sender_id,
            'broup_id': self.broup_id,
            'message_id': self.message_id,
            'body': self.body,
            'text_message': self.text_message,
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'info': self.info,
            'data': self.data,
        }
