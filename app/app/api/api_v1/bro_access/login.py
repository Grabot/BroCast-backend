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
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens
import hashlib


class LoginRequest(BaseModel):
    email: Optional[str] = None
    bro_name: Optional[str] = None
    bromotion: Optional[str] = None
    password: str
    platform: int


@api_router_v1.post("/login", status_code=200)
async def login_bro(
    login_request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    email = login_request.email
    bro_name = login_request.bro_name
    bromotion = login_request.bromotion
    password = login_request.password
    platform = login_request.platform

    if password is None:
        return get_failed_response("Invalid request", response)
    if bro_name is None and bromotion is None:
        if email is None:
            return get_failed_response("Invalid request", response)
        # login with email
        email_hash = hashlib.sha512(email.lower().encode("utf-8")).hexdigest()
        statement = (
            select(Bro)
            .where(Bro.origin == 0)
            .where(Bro.email_hash == email_hash)
            .options(selectinload(Bro.broups).options(selectinload(Broup.chat)))
        )
        results = await db.execute(statement)
        result_bro = results.first()
    elif email is None:
        if bro_name is None or bromotion is None:
            return get_failed_response("Invalid request", response)
        # login with bro_name and bromotion
        statement = (
            select(Bro)
            .where(Bro.origin == 0)
            .where(func.lower(Bro.bro_name) == bro_name.lower(), Bro.bromotion == bromotion)
            .options(selectinload(Bro.broups).options(selectinload(Broup.chat)))
        )
        results = await db.execute(statement)
        result_bro = results.first()
    else:
        return get_failed_response("Invalid request", response)

    if not result_bro:
        return get_failed_response("bro name or email not found", response)

    bro: Bro = result_bro.Bro

    if not bro.verify_password(password):
        return get_failed_response("password not correct", response)

    # Valid login, we refresh the token for this bro.
    bro_token = get_bro_tokens(bro)
    if bro.platform != platform:
        bro.platform = platform
    db.add(bro_token)
    
    broup_ids = []
    return_broups = []
    for broup in bro.broups:
        if not broup.deleted:
            broup_ids.append(broup.broup_id)
        # We only send the broups if there is something new
        if broup.broup_updated:
            return_broups.append(broup.serialize)
            broup.broup_updated = False
            broup.new_avatar = False
            broup.new_messages = False
            broup.update_bros = []
            broup.update_bros_avatar = []
            db.add(broup)
        elif broup.new_avatar:
            return_broups.append(broup.serialize_new_avatar)
            broup.new_avatar = False
            broup.new_messages = False
            db.add(broup)
        elif broup.new_messages:
            return_broups.append(broup.serialize_minimal)
            broup.new_messages = False
            db.add(broup)
    await db.commit()

    # When logging in via email or bro_name we will also pass all the broup ids
    # If the bro logs in on another device we will know what is missing from the local db.
    bro_details = {
        "id": bro.id,
        "bro_name": bro.bro_name,
        "bromotion": bro.bromotion,
        "origin": bro.origin == 0,
        "broups": return_broups,
    }

    # We don't refresh the bro object because we know all we want to know
    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
        "fcm_token": bro.fcm_token,
        "bro": bro_details,
        "broup_ids": broup_ids
    }

    return login_response
