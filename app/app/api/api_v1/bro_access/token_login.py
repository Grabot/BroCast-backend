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
    await db.commit()

    login_response = {
        "result": True,
        "message": "Bro logged in successfully.",
        "access_token": bro_token.access_token,
        "refresh_token": bro_token.refresh_token,
        "bro": bro.serialize_token,
    }

    return login_response
