from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class GetBroRequest(BaseModel):
    bro_ids: List[int]


@api_router_v1.post("/bro/get", status_code=200)
async def get_bro(
    get_bros_request: GetBroRequest,
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

    bro_ids = get_bros_request.bro_ids
    bros_statement = select(Bro).where(
        Bro.id.in_(bro_ids)
    )
    results_bros = await db.execute(bros_statement)
    result_bros = results_bros.all()

    if result_bros is None or result_bros == []:
        return {
            "result": True,
            "bros": [],
        }

    bro_list = []
    for bro_object in result_bros:
        bro: Bro = bro_object.Bro
        bro_list.append(bro.serialize_big)
    await db.commit()

    return {
        "result": True,
        "bros": bro_list
    }
