from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token



class BroupOpenRequest(BaseModel):
    broup_id: int
    open_chat: bool


@api_router_v1.post("/broup/open", status_code=200)
async def broup_open(
    broup_open_request: BroupOpenRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, False)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_id = broup_open_request.broup_id
    open_chat = broup_open_request.open_chat

    broup_statement = (
        select(Broup)
        .where(
            Broup.bro_id == me.id,
            Broup.broup_id == broup_id
        )
    )
    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()

    if result_broup is None:
        return {
            "result": True,
            "broup": [],
        }
    broup: Broup = result_broup.Broup
    broup.open = open_chat
    db.add(broup)
    await db.commit()

    return {"result": True}

