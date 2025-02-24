import asyncio
from typing import Optional

from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_generate_avatar
from app.database import get_db
from app.models import Bro
from app.sockets.sockets import sio
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens
import hashlib
import time


class RegisterRequest(BaseModel):
    email: str
    bro_name: str
    bromotion: str
    password: str
    platform: int
    fcm_token: Optional[str]


@api_router_v1.post("/register", status_code=200)
async def register_bro(
    register_request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    email = register_request.email
    bro_name = register_request.bro_name
    bromotion = register_request.bromotion
    password = register_request.password
    fcm_token = register_request.fcm_token
    platform = register_request.platform

    if email is None or password is None or bro_name is None or bromotion is None:
        return get_failed_response("Invalid request", response)

    # Not loading the bros and followers here, just checking if the email is taken.
    email_hash = hashlib.sha512(email.lower().encode("utf-8")).hexdigest()
    statement = select(Bro).where(Bro.origin == 0, Bro.email_hash == email_hash)
    results = await db.execute(statement)
    result = results.first()

    if result is not None:
        return get_failed_response(
            "This email has already been used to create an account, please log in instead", response
        )
    # Also not loading the bros and followers here.
    # Just checking if the broname and bromotion combination is taken.
    # Multiple statements in the where clause defaults to AND.
    statement = select(Bro).where(
        func.lower(Bro.bro_name) == bro_name.lower(),
        Bro.bromotion == bromotion,
    )
    results = await db.execute(statement)
    result = results.first()

    if result is not None:
        return get_failed_response(
            "Broname and bromotion combination is already taken, please choose a different one.",
            response,
        )

    fcm_refresh_expiration_time = 7889232  # about 3 months
    bro = Bro(
        bro_name=bro_name,
        bromotion=bromotion,
        email_hash=email_hash,
        origin=0,
        fcm_token=fcm_token,
        fcm_token_timestamp=time.time() + fcm_refresh_expiration_time,
        platform=platform,
    )
    bro.hash_password(password)
    db.add(bro)
    # Refresh bro so we can get the id.
    await db.commit()
    await db.refresh(bro)
    bro_token = get_bro_tokens(bro)
    db.add(bro_token)
    await db.commit()
    bro_return = bro.serialize_no_detail
    bro_return["origin"] = True

    _ = task_generate_avatar.delay(bro.avatar_filename(), bro.id)

    # Return the bro with no bro information because they have none yet.
    # And no avatar, because it might still be generating.
    return {
        "result": True,
        "message": "Bro created successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
        "bro": bro_return,
    }


class AvatarCreatedRequest(BaseModel):
    bro_id: int


@api_router_v1.post("/avatar/created", status_code=200)
async def avatar_created(
    avatar_created_request: AvatarCreatedRequest,
) -> dict:
    bro_id = avatar_created_request.bro_id
    room = "room_%s" % bro_id

    # A short sleep, just in case the bro has not made the socket connection yet
    await asyncio.sleep(1)

    await sio.emit(
        "message_event",
        "Avatar creation done!",
        room=room,
    )

    return {
        "result": True,
        "message": "Avatar creation done!",
    }
