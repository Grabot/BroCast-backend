import asyncio
from contextlib import asynccontextmanager
from typing import Any, Awaitable, Callable

import boto3
import uvicorn
from botocore import client as boto_client
from cryptography.fernet import Fernet
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from sqlalchemy import text

from app.api import api_login, api_v1, api_v1_5
from app.config.config import settings
from app.database import async_session
from app.sockets.sockets import redis, sio_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    cipher = Fernet(settings.S3_ENCRYPTION_KEY.encode())
    app.state.cipher = cipher
    app.state.s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="eu-central-1",
        config=boto_client.Config(signature_version="s3v4"),
    )
    try:
        app.state.s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except Exception:
        app.state.s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)

    yield


app = FastAPI(lifespan=lifespan)

add_pagination(app)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(api_v1.api_router_v1, tags=["api_v1"])
api_router_login = APIRouter()
api_router_login.include_router(api_login.api_router_login, tags=["api_login"])
api_router_v15 = APIRouter()
api_router_v15.include_router(api_v1_5.api_router_v1_5, tags=["api_v1_5"])

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router_login, prefix=settings.API_LOGIN_STR)
app.include_router(api_router_v15, prefix=settings.API_V1_5_STR)

_CHECK_TIMEOUT_SECONDS = 2


async def check_database() -> None:
    """Raise on failure: single round-trip proving the database answers."""
    async with async_session() as db:
        await db.execute(text("SELECT 1"))


async def check_redis() -> None:
    """Raise on failure: PING over the shared socket.io Redis client."""
    await redis.ping()


@app.get("/livez")
async def liveness() -> dict:
    """Liveness probe target: always 200 while the process runs."""
    return {"status": "ok"}


@app.get("/readyz")
async def readiness() -> JSONResponse:
    """Readiness probe target: 200 when dependencies answer, else 503."""
    checks: dict[str, Callable[[], Awaitable[Any]]] = {
        "database": check_database,
        "redis": check_redis,
    }
    failures: dict[str, str] = {}
    for name, check in checks.items():
        try:
            await asyncio.wait_for(check(), timeout=_CHECK_TIMEOUT_SECONDS)
        except Exception as exc:
            failures[name] = type(exc).__name__
    if failures:
        return JSONResponse(
            status_code=503, content={"status": "not-ready", "failures": failures}
        )
    return JSONResponse(status_code=200, content={"status": "ready"})


app.mount("/", sio_app)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, host="0.0.0.0", reload=False)
