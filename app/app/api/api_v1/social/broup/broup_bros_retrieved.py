from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class BroupBrosRetrievedRequest(BaseModel):
    broup_id: int
    bro_ids: List[int]


@api_router_v1.post("/broup/bros_retrieved", status_code=200)
async def remove_bro_broup(
    broup_bros_retrieved_request: BroupBrosRetrievedRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_id = broup_bros_retrieved_request.broup_id

    broup_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.bro_id == me.id,
        )
    )

    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()
    if result_broup is None:
        return {
            "result": False,
            "message": "Broup not found",
        }
    
    bro_ids = broup_bros_retrieved_request.bro_ids

    broup: Broup = result_broup.Broup
    broup.bros_retrieved()
    broup.broup_updated = False
    db.add(broup)

    # Go over the broups, if the bro is marked to update we know that that is no longer needed
    for bro_id in bro_ids:
        for broup in me.broups:
            if bro_id in broup.update_bros:
                broup.dismiss_bro_to_update(bro_id)
                db.add(broup)
    await db.commit()

    return {
        "result": True,
    }
