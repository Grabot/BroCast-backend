from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@api_router_v1.post("/change/password", status_code=200)
async def change_password(
    change_password_request: ChangePasswordRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    bro: Optional[Bro] = await check_token(db, auth_token, False)
    if not bro:
        return get_failed_response("An error occurred", response)

    old_password = change_password_request.old_password
    new_password = change_password_request.new_password

    if not bro.verify_password(old_password):
        return {
            "result": False,
            "message": "password not correct",
        }

    bro.hash_password(new_password)
    db.add(bro)
    await db.commit()

    return {
        "result": True,
        "message": new_password,
    }
