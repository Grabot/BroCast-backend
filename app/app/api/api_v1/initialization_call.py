from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_activate_celery
from app.util.storage_util import ensure_bucket


@api_router_v1.get("/initialization", status_code=200)
async def test_call() -> dict:
    ensure_bucket()
    _ = task_activate_celery.delay()
    return {
        "result": True,
    }
