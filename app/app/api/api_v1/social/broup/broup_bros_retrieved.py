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

    me: Optional[Bro] = await check_token(db, auth_token, False)
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
    print(f"results_bromotions {results_broup}")
    result_broup = results_broup.first()
    print(f"result_bromotion {result_broup}")
    if result_broup is None:
        return {
            "result": False,
            "message": "Broup not found",
        }
    broup: Broup = result_broup.Broup
    broup.bros_retrieved()
    db.add(broup)
    await db.commit()

    return {
        "result": True,
    }
