import requests
from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.api.api_login.logins.login_bro_origin import login_bro_origin
from app.celery_worker.tasks import task_generate_avatar
from app.config.config import settings
from app.database import get_db
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens


async def log_bro_in(
    broinfo_response,
    db: AsyncSession = Depends(get_db),
):
    bro_email = broinfo_response.json()["email"]
    bro_name = broinfo_response.json()["given_name"]

    [bro, bro_created] = await login_bro_origin(bro_name, bro_email, 1, True, db)

    if bro:
        bro_token = get_bro_tokens(bro, 30, 60)
        db.add(bro_token)
        await db.commit()
        access_token = bro_token.access_token
        refresh_token = bro_token.refresh_token

        if bro_created:
            await db.refresh(bro)
            _ = task_generate_avatar.delay(bro.avatar_filename(), bro.id, False)

        return [True, [access_token, refresh_token, bro, bro_created]]
    else:
        return [False, [None, None, None, None]]



class GoogleTokenRequest(BaseModel):
    access_token: str


# Bro the v1 router, so it will have `api/v1.4/` before the path
@api_router_v1.post("/login/google/token", status_code=200)
async def login_google_token(
    google_token_request: GoogleTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:

    google_access_token = google_token_request.access_token
    broinfo_response = requests.get(
        f"{settings.GOOGLE_ACCESS_TOKEN_URL}?access_token={google_access_token}",
    )

    if broinfo_response.json().get("error", None):
        return get_failed_response("An error occurred", response)

    # You want to make sure their email is verified.
    # The bro authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if not broinfo_response.json().get("email_verified"):
        return get_failed_response("Bro email not available or not verified by Google.", response)

    # We don't use the tokens send with this,
    # because they are only valid for a short period, and we will refresh them later on
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
            # Login Google login
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
                "platform": bro.platform,
                "bro": bro_details,
                "broup_ids": broup_ids
            }

        return login_response
    else:
        return get_failed_response("An error occurred", response)
