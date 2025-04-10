from urllib.parse import urlencode

import requests
from app.api.api_login.logins.login_bro_origin import login_bro_origin
from app.celery_worker.tasks import task_generate_avatar
from app.config.config import settings
from app.database import get_db
from app.api.api_login import api_router_login
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens
from fastapi import Depends, Request, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from time import time
from pydantic import BaseModel
from typing import Annotated
from fastapi import Form


def decode_apple_token(token):
    return jwt.decode(token, audience=settings.APPLE_CLIENT_ID, options={"verify_signature": False})


async def log_bro_in(
    broinfo_response,
    db: AsyncSession = Depends(get_db),
):
    id_token = broinfo_response.json()["id_token"]
    apple_token = decode_apple_token(id_token)
    bro_email = apple_token["email"]
    bro_name = apple_token["email"].split("@")[0]

    [bro, bro_created] = await login_bro_origin(bro_name, bro_email, 4, db)

    if bro:
        bro_token = get_bro_tokens(bro, 30, 60)
        db.add(bro_token)
        await db.commit()
        access_token = bro_token.access_token
        refresh_token = bro_token.refresh_token

        if bro_created:
            await db.refresh(bro)
            _ = task_generate_avatar.delay(bro.avatar_filename(), bro.id, False)
        else:
            await db.commit()

        return [True, [access_token, refresh_token, bro, bro_created]]
    else:
        return [False, [None, None, None, None]]


def generate_token():
    private_key = settings.APPLE_AUTH_KEY
    team_id = settings.APPLE_TEAM_ID
    client_id = settings.APPLE_CLIENT_ID
    key_id = settings.APPLE_KEY_ID
    validity_minutes = 15
    timestamp_now = int(time())
    timestamp_exp = timestamp_now + (60 * validity_minutes)
    data = {
        "iss": team_id,
        "iat": timestamp_now,
        "exp": timestamp_exp,
        "aud": settings.APPLE_AUD_URL,
        "sub": client_id,
    }
    token = jwt.encode(
        payload=data, key=private_key.encode("utf-8"), algorithm="ES256", headers={"kid": key_id}
    )
    return token


@api_router_login.get("/apple/redirect")
async def apple_get_redirect(access_token: str, refresh_token: str, request: Request):
    # Send bro to the world
    params = dict()
    params["access_token"] = access_token
    params["refresh_token"] = refresh_token
    url_params = urlencode(params)

    world_url = f"{settings.BASE_URL}/broaccess"
    world_url_params = world_url + "?" + url_params
    return RedirectResponse(world_url_params)


@api_router_login.post("/apple/callback")
async def apple_callback(
    code: Annotated[str, Form()],
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    apple_key_url = settings.APPLE_AUTHORIZE
    broinfo_response = requests.post(
        apple_key_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": settings.APPLE_CLIENT_ID,
            "client_secret": generate_token(),
            "code": code,
            "grant_type": settings.APPLE_GRANT_TYPE,
            "redirect_uri": settings.APPLE_REDIRECT_URL,
        },
    )

    if (
        not broinfo_response.json().get("access_token")
        or not broinfo_response.json().get("refresh_token")
        or not broinfo_response.json().get("id_token")
    ):
        return get_failed_response("Bro email not available or not verified by Apple.", response)

    [success, [_, _, bro, bro_created]] = await log_bro_in(broinfo_response, db)
    if success:
        # Valid login, we refresh the token for this bro.
        bro_token = get_bro_tokens(bro)
        db.add(bro_token)
        await db.commit()

        params = dict()
        params["access_token"] = bro_token.access_token
        params["refresh_token"] = bro_token.refresh_token
        params["code"] = code

        url_params = urlencode(params)

        base_url = settings.BASE_URL
        full_url = f"{base_url}/login/apple/redirect?" + url_params
        return RedirectResponse(full_url, status_code=status.HTTP_302_FOUND)
    else:
        return get_failed_response("An error occurred", response)


@api_router_login.get("/apple/verify")
async def apple_verify(
    code: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    apple_key_url = settings.APPLE_AUTHORIZE

    broinfo_response = requests.post(
        apple_key_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_id": settings.APPLE_CLIENT_ID,
            "client_secret": generate_token(),
            "code": code,
            "grant_type": settings.APPLE_GRANT_TYPE,
            "redirect_uri": settings.APPLE_REDIRECT_URL,
        },
    )

    if (
        not broinfo_response.json().get("access_token")
        or not broinfo_response.json().get("refresh_token")
        or not broinfo_response.json().get("id_token")
    ):
        return get_failed_response("Bro email not available or not verified by Apple.", response)

    [success, [_, _, bro, bro_created]] = await log_bro_in(broinfo_response, db)

    if success:
        # Valid login, we refresh the token for this bro.
        bro_token = get_bro_tokens(bro)
        db.add(bro_token)
        await db.commit()

        login_response ={}
        if bro_created:
            # Register Google login
            bro_return = bro.serialize_no_detail
            bro_return["origin"] = False

            # Return the bro with no bro information because they have none yet.
            # And no avatar, because it might still be generating.
            login_response = {
                "result": True,
                "message": "Bro created successfully.",
                "access_token": bro_token.access_token,
                "refresh_token": bro_token.refresh_token,
                "bro": bro_return,
            }
        else:
            # Login Apple login
            broup_ids = []
            return_broups = []
            for broup in bro.broups:
                if not broup.deleted:
                    broup_ids.append(broup.broup_id)
                
                if broup.removed:
                    return_broups.append(broup.serialize_removed)
                    broup.broup_updated = False
                    db.add(broup)
                else:
                    # We only send the broup details if there is something new
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
    else:
        return get_failed_response("An error occurred", response)
