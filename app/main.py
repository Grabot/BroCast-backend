from contextlib import asynccontextmanager
import uvicorn
import boto3
from botocore import client as boto_client
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from cryptography.fernet import Fernet

from app.api import api_login, api_v1, api_v1_5
from app.config.config import settings
from app.sockets.sockets import sio_app


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

app.mount("/", sio_app)


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, host="0.0.0.0", reload=True)
