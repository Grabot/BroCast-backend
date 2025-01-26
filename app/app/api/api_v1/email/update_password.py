from typing import Optional

from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import refresh_bro_token


class PasswordUpdateRequest(BaseModel):
    access_token: str
    refresh_token: str
    new_password: str


@api_router_v1.post("/password/update", status_code=200)
async def update_password(
    password_update_request: PasswordUpdateRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_token = password_update_request.access_token
    refresh_token = password_update_request.refresh_token

    bro: Optional[Bro] = await refresh_bro_token(db, access_token, refresh_token)
    if not bro:
        return get_failed_response("Bro not found", response)

    new_password = password_update_request.new_password
    bro.hash_password(new_password)
    db.add(bro)
    await db.commit()

    return {
        "result": True,
        "message": "password updated!",
    }
