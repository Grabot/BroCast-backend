from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.util.rest_util import get_failed_response
from app.util.util import get_bro_tokens, refresh_bro_token


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
