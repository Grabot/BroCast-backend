from datetime import datetime
import base64
import os
from typing import Optional, List
import pytz
from sqlmodel import Field, SQLModel, Column, ARRAY, Integer
from app.config.config import settings


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
    data_type: Optional[int]
    replied_to: Optional[int]
    # A int list which indicates which bros still need to receive and read this message.
    receive_remaining: List[int] = Field(default=[], sa_column=Column(ARRAY(Integer())))

    def bro_received_message(self, bro_id):
        old_received = self.receive_remaining
        new_received = []
        for old in old_received:
            if old != bro_id:
                new_received.append(old)
        self.receive_remaining = new_received

    def get_message_image_data(self):
        # TODO: at some point only send the ids or something to do a seperate call for only images in bytes?
        if not self.data:
            return None
        file_folder = settings.UPLOAD_FOLDER_IMAGES
        file_path = os.path.join(file_folder, f"{self.data}.png")
        if not os.path.isfile(file_path):
            return None
        else:
            with open(file_path, "rb") as fd:
                image_as_base64 = base64.encodebytes(fd.read()).decode()
            image_data = {
                "data": image_as_base64,
                "type": self.data_type,
            }
            return image_data
        
    @property
    def serialize(self):
        return {
            "sender_id": self.sender_id,
            "broup_id": self.broup_id,
            "message_id": self.message_id,
            "body": self.body,
            "text_message": self.text_message,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "info": self.info,
            "data": self.get_message_image_data(),
        }
        
    # If you send the image we know the data already, so there's no need to retrieve it again.
    @property
    def serialize_no_image(self):
        return {
            "sender_id": self.sender_id,
            "broup_id": self.broup_id,
            "message_id": self.message_id,
            "body": self.body,
            "text_message": self.text_message,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "info": self.info,
        }
