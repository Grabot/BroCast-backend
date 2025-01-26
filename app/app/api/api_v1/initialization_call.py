from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_activate_celery
import os
import stat
from app.config.config import settings


@api_router_v1.get("/initialization", status_code=200)
async def test_call() -> dict:
    if not os.path.exists(settings.UPLOAD_FOLDER_AVATARS):
        os.makedirs(settings.UPLOAD_FOLDER_AVATARS)
        os.chmod(settings.UPLOAD_FOLDER_AVATARS, stat.S_IRWXO)
    
    _ = task_activate_celery.delay()
    return {
        "result": True,
    }
