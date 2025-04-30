import base64
import os
import secrets
import time
from hashlib import md5
from typing import List, Optional

from authlib.jose import jwt
from passlib.apps import custom_app_context as pwd_context
from sqlmodel import Field, Relationship, SQLModel

from app.config.config import settings


class Bro(SQLModel, table=True):
    """
    Bro
    """

    __tablename__ = "Bro"
    id: int = Field(default=None, primary_key=True)
    bro_name: str = Field(index=True, unique=False)
    bromotion: str = Field(index=True, unique=False)
    email_hash: str
    password_hash: str
    salt: str
    origin: int
    default_avatar: bool = Field(default=True)
    fcm_token: Optional[str] = Field(default=None)
    fcm_token_timestamp: Optional[int] = Field(default=None)  # timestamp when fcm token was set in unix time
    platform: int = Field(default=0)  # 0: android, 1: ios

    tokens: List["BroToken"] = Relationship(back_populates="bro_token")

    broups: List["Broup"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(Bro.id==Broup.bro_id, Broup.deleted==False)",
        },
    )

    def generate_auth_token(self, expires_in=1800):
        # also used for email password reset token
        payload = {
            "id": self.id,
            "iss": settings.JWT_ISS,
            "aud": settings.JWT_AUD,
            "sub": settings.JWT_SUB,
            "exp": int(time.time()) + expires_in,  # expiration time
            "iat": int(time.time()),  # issued at
        }
        return jwt.encode(settings.header, payload, settings.jwk)

    def generate_refresh_token(self, expires_in=345600):
        payload = {
            "bro_name": self.bro_name,
            "bromotion": self.bromotion,
            "iss": settings.JWT_ISS,
            "aud": settings.JWT_AUD,
            "sub": settings.JWT_SUB,
            "exp": int(time.time()) + expires_in,  # expiration time
            "iat": int(time.time()),  # issued at
        }
        return jwt.encode(settings.header, payload, settings.jwk)

    def hash_password(self, password):
        salt = secrets.token_hex(8)
        self.salt = salt
        self.password_hash = pwd_context.hash(password + salt)

    def verify_password(self, password):
        # If the bro has any other origin than regular it should not get here
        # because the verification is does elsewhere. So if it does, we return False
        if self.origin != 0:
            return False
        else:
            return pwd_context.verify(password + self.salt, self.password_hash)

    def set_new_broname(self, new_broname):
        self.bro_name = new_broname

    def set_new_bromotion(self, new_bromotion):
        self.bromotion = new_bromotion

    def get_bromotion(self):
        return self.bromotion

    def avatar_filename(self):
        return md5(self.email_hash.encode("utf-8")).hexdigest()

    def avatar_filename_default(self):
        return self.avatar_filename() + "_default"

    def set_default_avatar(self, value):
        self.default_avatar = value

    def is_default(self):
        return self.default_avatar

    def get_bro_avatar(self):
        if self.default_avatar:
            file_name = self.avatar_filename_default()
        else:
            file_name = self.avatar_filename()
        file_folder = settings.UPLOAD_FOLDER_AVATARS

        file_path = os.path.join(file_folder, "%s.png" % file_name)
        if not os.path.isfile(file_path):
            return None
        else:
            with open(file_path, "rb") as fd:
                image_as_base64 = base64.encodebytes(fd.read()).decode()
            return image_as_base64

    @property
    def serialize_avatar(self):
        return {
            "id": self.id,
            "bro_name": self.bro_name,
            "bromotion": self.bromotion,
            "avatar": self.get_bro_avatar(),
        }

    @property
    def serialize_no_detail(self):
        # Usually we want to get the bro details without the avatar.
        # If we want the avatar we can get it seperate.
        return {
            "id": self.id,
            "bro_name": self.bro_name,
            "bromotion": self.bromotion,
        }
