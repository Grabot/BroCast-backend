from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import time

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class ChangeFCMTokenRequest(BaseModel):
    fcm_token: str


@api_router_v1.post("/change/fcm_token", status_code=200)
async def change_broname(
    change_fcm_token_request: ChangeFCMTokenRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    fcm_token = change_fcm_token_request.fcm_token
    me.fcm_token = fcm_token
    fcm_refresh_expiration_time = 15778463  # about 6 months
    me.fcm_token_timestamp = int(time.time()) + fcm_refresh_expiration_time
    db.add(me)
    await db.commit()

    return {
        "result": True,
    }
