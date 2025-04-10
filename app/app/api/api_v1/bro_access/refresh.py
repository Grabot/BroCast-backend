from typing import Optional
from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, refresh_bro_token, get_bro_tokens


class RefreshRequest(BaseModel):
    access_token: str
    refresh_token: str


@api_router_v1.post("/refresh", status_code=200)
async def refresh_bro(
    refresh_request: RefreshRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_token = refresh_request.access_token
    refresh_token = refresh_request.refresh_token

    bro = await refresh_bro_token(db, access_token, refresh_token)
    if not bro:
        return get_failed_response("An error occurred", response)

    bro_token = get_bro_tokens(bro)
    db.add(bro_token)
    await db.commit()

    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
    }

    return login_response


class RefreshOAuthRequest(BaseModel):
    access_token: str
    refresh_token: str


@api_router_v1.post("/refresh/oauth", status_code=200)
async def refresh_bro_oauth(
    refresh_request: RefreshOAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_token = refresh_request.access_token
    refresh_token = refresh_request.refresh_token

    refresh_bro = await refresh_bro_token(db, access_token, refresh_token)
    if not refresh_bro:
        return get_failed_response("An error occurred", response)

    new_bro_token = get_bro_tokens(refresh_bro)
    new_access_token = new_bro_token.access_token
    new_refresh_token = new_bro_token.refresh_token
    db.add(new_bro_token)
    await db.commit()
    
    me: Optional[Bro] = await check_token(db, new_access_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_ids = []
    return_broups = []
    for broup in me.broups:
        if not broup.deleted:
            broup_ids.append(broup.broup_id)
        
        if broup.removed:
            return_broups.append(broup.serialize_removed)
            broup.broup_updated = False
            db.add(broup)
        else:
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
        "id": me.id,
        "bro_name": me.bro_name,
        "bromotion": me.bromotion,
        "origin": me.origin == 0,
        "broups": return_broups,
    }

    # We don't refresh the bro object because we know all we want to know
    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "fcm_token": me.fcm_token,
        "platform": me.platform,
        "bro": bro_details,
        "broup_ids": broup_ids
    }

    return login_response
