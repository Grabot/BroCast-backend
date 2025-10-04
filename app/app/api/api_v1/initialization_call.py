from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_activate_celery
import os
from app.config.config import settings


@api_router_v1.get("/initialization", status_code=200)
async def test_call() -> dict:
    if not os.path.exists(settings.UPLOAD_FOLDER_AVATARS):
        os.makedirs(settings.UPLOAD_FOLDER_AVATARS)
        os.chmod(settings.UPLOAD_FOLDER_AVATARS, 0o755)
    if not os.path.exists(settings.UPLOAD_FOLDER_MEDIA):
        os.makedirs(settings.UPLOAD_FOLDER_MEDIA)
        os.chmod(settings.UPLOAD_FOLDER_MEDIA, 0o755)
    if not os.path.exists(settings.UPLOAD_FOLDER_IMAGES):
        os.makedirs(settings.UPLOAD_FOLDER_IMAGES)
        os.chmod(settings.UPLOAD_FOLDER_IMAGES, 0o755)
    if not os.path.exists(settings.UPLOAD_FOLDER_VIDEOS):
        os.makedirs(settings.UPLOAD_FOLDER_VIDEOS)
        os.chmod(settings.UPLOAD_FOLDER_VIDEOS, 0o755)
    if not os.path.exists(settings.UPLOAD_FOLDER_AUDIO):
        os.makedirs(settings.UPLOAD_FOLDER_AUDIO)
        os.chmod(settings.UPLOAD_FOLDER_AUDIO, 0o755)
    if not os.path.exists(settings.UPLOAD_FOLDER_OTHER):
        os.makedirs(settings.UPLOAD_FOLDER_OTHER)
        os.chmod(settings.UPLOAD_FOLDER_OTHER, 0o755)

    _ = task_activate_celery.delay()
    return {
        "result": True,
    }
