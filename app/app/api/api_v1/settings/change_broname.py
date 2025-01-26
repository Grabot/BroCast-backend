from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class ChangeBronameRequest(BaseModel):
    broname: str


@api_router_v1.post("/change/broname", status_code=200)
async def change_broname(
    change_broname_request: ChangeBronameRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    bro: Optional[Bro] = await check_token(db, auth_token)
    if not bro:
        return get_failed_response("An error occurred", response)

    new_broname = change_broname_request.broname
    bro_statement = select(Bro).where(func.lower(Bro.broname) == new_broname.lower())
    results = await db.execute(bro_statement)
    result = results.first()
    if result is not None:
        return get_failed_response(
            "Bro name is already taken, please choose a different one.", response
        )

    bro.set_new_broname(new_broname)
    # TODO: update message?

    db.add(bro)
    await db.commit()

    return {
        "result": True,
        "message": new_broname,
    }
