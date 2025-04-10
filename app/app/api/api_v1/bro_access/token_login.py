from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, get_bro_tokens

@api_router_v1.post("/login/token", status_code=200)
async def login_token_bro(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:

    auth_token = get_auth_token(request.headers.get("Authorization"))
    
    if auth_token == "":
        return get_failed_response("An error occurred", response)
    bro = await check_token(db, auth_token, True)

    if not bro:
        return get_failed_response("Bro not found", response)

    bro_token = get_bro_tokens(bro)
    db.add(bro_token)

    return_broups = []
    for broup in bro.broups:
        # We only send the broups if there is something new
        if broup.removed:
            return_broups.append(broup.serialize_removed)
            broup.broup_updated = False
        else:
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

    bro_details = {
        "id": bro.id,
        "bro_name": bro.bro_name,
        "bromotion": bro.bromotion,
        "origin": bro.origin == 0,
        "broups": return_broups,
    }

    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
        "bro": bro_details,
    }

    return login_response
