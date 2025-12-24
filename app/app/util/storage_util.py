from io import BytesIO
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
