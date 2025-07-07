from typing import Optional
from sqlmodel import select
from pydantic import BaseModel
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class GetReadTimeBro(BaseModel):
    broup_id: int


@api_router_v1_5.post("/get/broup/read_time", status_code=200)
async def get_avatar_broup(
    get_read_time_bro: GetReadTimeBro,
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

    broup_id = get_read_time_bro.broup_id

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
        get_failed_response("Broup not found", response)

    me_broup: Broup = result_broup.Broup

    return {
        "result": True,
        "last_read_time": me_broup.last_message_read_id
    }
