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
from sqlalchemy.orm import selectinload
import pytz
from datetime import datetime, timedelta



class MuteBroupRequest(BaseModel):
    broup_id: int
    mute_time: int


@api_router_v1.post("/broup/mute", status_code=200)
async def mute_broup(
    mute_broup_request: MuteBroupRequest,
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

    broup_id = mute_broup_request.broup_id
    mute_time = mute_broup_request.mute_time

    broup_statement = (
        select(Broup)
        .where(
            Broup.bro_id == me.id,
            Broup.broup_id == broup_id
        ).options(selectinload(Broup.chat))
    )
    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()

    if result_broup is None:
        return {
            "result": True,
            "broup": [],
        }
    broup: Broup = result_broup.Broup
    
    mute = True
    unmute_date = None
    if mute_time == -1:
        mute = False
    elif mute_time == 0:
        unmute_date = datetime.now(pytz.utc).replace(tzinfo=None) + timedelta(hours=1)
    elif mute_time == 1:
        unmute_date = datetime.now(pytz.utc).replace(tzinfo=None) + timedelta(hours=8)
    elif mute_time == 2:
        unmute_date = datetime.now(pytz.utc).replace(tzinfo=None) + timedelta(days=7)

    broup.mute_broup(mute)
    if not mute:
        broup.set_mute_timestamp(None)
    if unmute_date:
        broup.set_mute_timestamp(unmute_date)
    
    db.add(broup)
    await db.commit()

    return {"result": True}

