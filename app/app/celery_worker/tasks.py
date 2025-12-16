import requests
from celery import Celery

from app.util.mail_util import send_delete_account, send_reset_email
from app.config.config import settings
from app.util.avatar.generate_avatar import generate_avatar

celery_app = Celery("tasks", broker=settings.REDIS_URI, backend=f"db+{settings.SYNC_DB_URL}")


@celery_app.task
def task_generate_avatar(avatar_filename: str, bro_id: int, broup: bool):
    generate_avatar(avatar_filename, settings.UPLOAD_FOLDER_AVATARS)

    base_url = settings.BASE_URL
    api_prefix = settings.API_V1_STR
    endpoint = "/avatar/created"
    total_url = base_url + api_prefix + endpoint
    if broup:
        requests.post(total_url, json={"identifier": bro_id, "for_bro": False})
    else:
        requests.post(total_url, json={"identifier": bro_id, "for_bro": True})

    return {"success": True}


@celery_app.task
def task_send_email_forgot_password(
    to_email: str, subject: str, access_token: str, refresh_token: str
) -> dict[str, bool]:
    """Send email to reset password."""
    send_reset_email(to_email, subject, access_token, refresh_token)
    return {"success": True}


@celery_app.task
def task_send_email_delete_account(
    to_email: str, subject: str, access_token: str, refresh_token: str, origin: str
) -> dict[str, bool]:
    """Send email to reset password."""
    send_delete_account(to_email, subject, access_token, refresh_token, origin)
    return {"success": True}


@celery_app.task
def task_activate_celery():
    return {"success": True}
