from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload


class ReceivedBroIdsBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/received/broids", status_code=200)
async def retrieved_broup(
    received_bro_ids_broup_request: ReceivedBroIdsBroupRequest,
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

    broup_id = received_bro_ids_broup_request.broup_id

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
            "result": False,
        }
    me_broup: Broup = result_broup.Broup
    me_broup.update_bros = []
    me_broup.update_bros_avatar = []
    db.add(me_broup)
    await db.commit()

    return {"result": True}


class ReceivedBroIdsBroupsRequest(BaseModel):
    broup_ids: List[int]


@api_router_v1.post("/broups/received/broids", status_code=200)
async def retrieved_broup(
    received_bro_ids_broups_request: ReceivedBroIdsBroupsRequest,
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

    broup_ids = received_bro_ids_broups_request.broup_ids

    broups_statement = (
        select(Broup)
        .where(Broup.bro_id == me.id, Broup.broup_id.in_(broup_ids))
    )
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()

    if result_broups is None or result_broups == []:
        return {
            "result": False,
        }

    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        # Retrieved full data, so no longer set to updated
        broup.update_bros = []
        broup.update_bros_avatar = []
        db.add(broup)
    await db.commit()

    return {"result": True}

