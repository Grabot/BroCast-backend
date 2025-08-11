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
        for old_id in old_received:
            if old_id != bro_id:
                new_received.append(old_id)
        self.receive_remaining = new_received

    def received_by_all(self):
        return len(self.receive_remaining) == 0

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
        
    def get_message_image_data_v1_5(self):
        if not self.data:
            return None
        media_data = {
            "type": self.data_type,
        }
        return media_data

    def get_message_data_v1_5_data(self) -> bytes:
        if not self.data:
            return None
        if self.data_type == 0:
            # images
            file_folder = settings.UPLOAD_FOLDER_IMAGES
            file_path = os.path.join(file_folder, f"{self.data}.png")
            if not os.path.isfile(file_path):
                return None
            else:
                with open(file_path, "rb") as fd:
                    image_bytes = fd.read()
                return image_bytes
        elif self.data_type == 1:
            # videos
            file_folder = settings.UPLOAD_FOLDER_VIDEOS
            file_path = os.path.join(file_folder, f"{self.data}.mp4")
            if not os.path.isfile(file_path):
                return None
            else:
                with open(file_path, "rb") as fd:
                    video_bytes = fd.read()
                return video_bytes
        elif self.data_type == 2:
            # audio
            file_folder = settings.UPLOAD_FOLDER_AUDIO
            file_path = os.path.join(file_folder, f"{self.data}.mp3")
            if not os.path.isfile(file_path):
                return None
            else:
                with open(file_path, "rb") as fd:
                    video_bytes = fd.read()
                return video_bytes


    @property
    def serialize(self):
        data = {
            "sender_id": self.sender_id,
            "broup_id": self.broup_id,
            "message_id": self.message_id,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "info": self.info,
            "data": self.get_message_image_data(),
        }

        if self.text_message is not None:
            data["text_message"] = self.text_message

        if self.replied_to is not None:
            data["replied_to"] = self.replied_to

        return data
        
    # If you send the image we know the data already, so there's no need to retrieve it again.
    @property
    def serialize_no_image(self):
        data = {
            "sender_id": self.sender_id,
            "broup_id": self.broup_id,
            "message_id": self.message_id,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "info": self.info,
            "data": self.get_message_image_data_v1_5(),  # This is only the data type
        }
        if self.text_message is not None:
            data["text_message"] = self.text_message

        if self.replied_to is not None:
            data["replied_to"] = self.replied_to
        return data

    @property
    def serialize_v1_5(self):
        data = {
            "sender_id": self.sender_id,
            "broup_id": self.broup_id,
            "message_id": self.message_id,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "info": self.info,
            "data": self.get_message_image_data_v1_5(),
        }

        if self.text_message is not None:
            data["text_message"] = self.text_message

        if self.replied_to is not None:
            data["replied_to"] = self.replied_to

        return data
