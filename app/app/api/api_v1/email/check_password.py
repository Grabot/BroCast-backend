import time

from authlib.jose import jwt
from authlib.jose.errors import DecodeError
from fastapi import Response
from pydantic import BaseModel

from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.util.rest_util import get_failed_response


class PasswordCheckRequest(BaseModel):
    access_token: str
    refresh_token: str


@api_router_v1.post("/password/check", status_code=200)
async def check_password(
    password_check_request: PasswordCheckRequest,
    response: Response,
) -> dict:
    access_token = password_check_request.access_token
    refresh_token = password_check_request.refresh_token

    try:
        _ = jwt.decode(access_token, settings.jwk)
        refresh = jwt.decode(refresh_token, settings.jwk)
    except DecodeError:
        return get_failed_response("invalid token", response)

    if refresh["exp"] < int(time.time()):
        return get_failed_response("the link has expired", response)

    return {
        "result": True,
        "message": "password check was good",
    }
