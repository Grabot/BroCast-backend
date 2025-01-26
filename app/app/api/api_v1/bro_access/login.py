from copy import copy
from typing import Optional

from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens
import hashlib


class LoginRequest(BaseModel):
    email: Optional[str] = None
    # TODO: add bromotion?
    bro_name: Optional[str] = None
    password: str
    is_web: bool


@api_router_v1.post("/login", status_code=200)
async def login_bro(
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    email = login_request.email
    bro_name = login_request.bro_name
    password = login_request.password
    is_web = login_request.is_web
    if password is None or (email is None and bro_name is None):
        return get_failed_response("Invalid request", response)
    if bro_name is None:
        # login with email
        email_hash = hashlib.sha512(email.lower().encode("utf-8")).hexdigest()
        statement = (
            select(Bro)
            .where(Bro.origin == 0)
            .where(Bro.email_hash == email_hash)
            .options(selectinload(Bro.bros))
        )
        results = await db.execute(statement)
        result_bro = results.first()
    elif email is None:
        statement = (
            select(Bro)
            .where(Bro.origin == 0)
            .where(func.lower(Bro.broname) == bro_name.lower())
            .options(selectinload(Bro.bros))
        )
        results = await db.execute(statement)
        result_bro = results.first()
    else:
        return get_failed_response("Invalid request", response)

    if not result_bro:
        return get_failed_response("bro name or email not found", response)

    bro: Bro = result_bro.Bro
    return_bro = copy(bro.serialize)

    if not bro.verify_password(password):
        return get_failed_response("password not correct", response)

    # If the platform is 3 we don't need to check anything anymore.
    platform_achievement = False

    if bro.platform != 3:
        if is_web:
            platform_value = bro.logged_in_web()
            if platform_value > 0:
                db.add(bro)
            if platform_value == 2:
                platform_achievement = True
        elif not is_web:
            platform_value = bro.logged_in_mobile()
            if platform_value > 0:
                db.add(bro)
            if platform_value == 2:
                platform_achievement = True
    # Valid login, we refresh the token for this bro.
    bro_token = get_bro_tokens(bro)
    db.add(bro_token)
    await db.commit()

    # We don't refresh the bro object because we know all we want to know
    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
        "bro": return_bro,
        "platform_achievement": platform_achievement
    }

    return login_response
