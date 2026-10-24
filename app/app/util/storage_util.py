from io import BytesIO
from typing import Any, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet

from app.config.config import settings


def download_media(s3_client, cipher, bucket, s3_key, encrypted: bool = True) -> bytes:
    """Download media from S3."""
    buffer = BytesIO()
    s3_client.download_fileobj(bucket, s3_key, buffer)
    buffer.seek(0)

    if encrypted:
        return cipher.decrypt(buffer.getvalue())
    else:
        # Default avatars are not encrypted
        return buffer.read()


def upload_media(s3_client, cipher, avatar_bytes, bucket, s3_key):
    """Upload media to S3."""
    buffer = BytesIO()
    encrypted_data = cipher.encrypt(avatar_bytes)
    buffer.write(encrypted_data)
    content_type = "application/octet-stream"

    buffer.seek(0)
    s3_client.upload_fileobj(
        buffer, bucket, s3_key, ExtraArgs={"ContentType": content_type}
    )


def avatar_s3_key(data_type: int, file_name: str) -> str:
    """Generate the full S3 key for the avatar."""
    mediaFolder = ""
    if data_type == 0:
        mediaFolder = "images"
    elif data_type == 1:
        mediaFolder = "videos"
    elif data_type == 2:
        mediaFolder = "audio"
    if data_type == 6:
        mediaFolder = "gifs"
    if data_type == 7:
        mediaFolder = "other"
    if mediaFolder == "":
        return f"{settings.PROJECT_NAME}/{file_name}"
    return f"{settings.PROJECT_NAME}/{mediaFolder}/{file_name}"


_s3_client: Optional[Any] = None
_cipher: Optional[Fernet] = None


def get_s3_client() -> Any:
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name="eu-central-1",
            config=Config(signature_version="s3v4"),
        )
    return _s3_client


def get_cipher() -> Fernet:
    global _cipher
    if _cipher is None:
        _cipher = Fernet(settings.S3_ENCRYPTION_KEY.encode())
    return _cipher


def ensure_bucket() -> None:
    s3_client = get_s3_client()
    try:
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError:
        s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)


def avatar_key(file_name: str) -> str:
    """S3 key for bro/broup avatars (custom uploads encrypted, defaults plain)."""
    return f"{settings.PROJECT_NAME}/avatars/{file_name}.png"


def upload_avatar(avatar_bytes: bytes, s3_key: str, encrypted: bool = True) -> None:
    s3_client = get_s3_client()
    cipher = get_cipher()
    buffer = BytesIO()
    data = cipher.encrypt(avatar_bytes) if encrypted else avatar_bytes
    buffer.write(data)
    buffer.seek(0)
    content_type = "application/octet-stream" if encrypted else "image/png"
    s3_client.upload_fileobj(
        buffer,
        settings.S3_BUCKET_NAME,
        s3_key,
        ExtraArgs={"ContentType": content_type},
    )


def download_avatar(s3_key: str, encrypted: bool = True) -> Optional[bytes]:
    s3_client = get_s3_client()
    cipher = get_cipher()
    try:
        buffer = BytesIO()
        s3_client.download_fileobj(settings.S3_BUCKET_NAME, s3_key, buffer)
        buffer.seek(0)
        data = buffer.getvalue()
        if encrypted:
            return cipher.decrypt(data)
        return data
    except ClientError:
        return None


def delete_avatar(s3_key: str) -> None:
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
    except ClientError:
        pass


def avatar_exists(s3_key: str) -> bool:
    s3_client = get_s3_client()
    try:
        s3_client.head_object(Bucket=settings.S3_BUCKET_NAME, Key=s3_key)
        return True
    except ClientError:
        return False
