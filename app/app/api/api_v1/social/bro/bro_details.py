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


class BroDetailsRequest(BaseModel):
    bro_update_ids: List[int]
    bro_avatar_update_ids: List[int]


@api_router_v1.post("/bro/details", status_code=200)
async def bro_details(
    bro_details_request: BroDetailsRequest,
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

    bro_update_ids = bro_details_request.bro_update_ids
    bro_avatar_update_ids = bro_details_request.bro_avatar_update_ids
    bro_ids = list(set(bro_update_ids + bro_avatar_update_ids))

    if not bro_ids:
        return {
            "result": True,
            "bros": [],
        }

    bros_statement = select(Bro).where(Bro.id.in_(bro_ids))
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
        # No avatar since the `new_avatar` flag should have been true
        if bro.id in bro_avatar_update_ids:
            # It's possible that we won't need the broname or bromotion.
            # Maybe a future improvement, but we don't need to worry about it now.
            bro_list.append(bro.serialize_avatar)
        else:
            bro_list.append(bro.serialize_no_detail)

    return {"result": True, "bros": bro_list}
