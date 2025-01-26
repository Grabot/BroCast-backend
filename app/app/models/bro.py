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

    tokens: List["BroToken"] = Relationship(back_populates="user")

    bros: Optional["Broup"] = Relationship(
        back_populates="bro_member",
        sa_relationship_kwargs={
            "uselist": False,
            "primaryjoin": "and_(Bro.id==Broup.bro_id, Broup.accepted==True)",
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
        # TODO: add bromotion?
        payload = {
            "bro_name": self.bro_name,
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
        # If the user has any other origin than regular it should not get here
        # because the verification is does elsewhere. So if it does, we return False
        if self.origin != 0:
            return False
        else:
            return pwd_context.verify(password + self.salt, self.password_hash)

    def set_new_broname(self, new_broname):
        self.bro_name = new_broname

    def avatar_filename(self):
        return md5(self.email_hash.encode("utf-8")).hexdigest()

    def avatar_filename_small(self):
        return self.avatar_filename() + "_small"

    def avatar_filename_default(self):
        return self.avatar_filename() + "_default"
    
    def set_default_avatar(self, value):
        self.default_avatar = value

    def is_default(self):
        return self.default_avatar

    def get_user_avatar(self, full=False):
        if self.default_avatar:
            file_name = self.avatar_filename_default()
        else:
            if full:
                file_name = self.avatar_filename()
            else:
                file_name = self.avatar_filename_small()
        file_folder = settings.UPLOAD_FOLDER_AVATARS

        file_path = os.path.join(file_folder, "%s.png" % file_name)
        if not os.path.isfile(file_path):
            return None
        else:
            with open(file_path, "rb") as fd:
                image_as_base64 = base64.encodebytes(fd.read()).decode()
            return image_as_base64


    @property
    def serialize(self):
        # get user details without personal information
        return {
            "id": self.id,
            "bro_name": self.bro_name,
            "bromotion": self.bromotion,
            "origin": self.origin == 0,
            "avatar": self.get_user_avatar(True),
        }

    @property
    def serialize_no_detail(self):
        return {
            "id": self.id,
            "bro_name": self.bro_name,
            "bromotion": self.bromotion,
            "origin": self.origin == 0,
        }
