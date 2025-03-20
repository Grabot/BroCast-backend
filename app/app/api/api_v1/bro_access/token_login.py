from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_bro_tokens
import time

class LoginTokenRequest(BaseModel):
    access_token: str


@api_router_v1.post("/login/token", status_code=200)
async def login_token_bro(
    login_token_request: LoginTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    bro = await check_token(db, login_token_request.access_token, True)

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
