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


class RetrievedBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/retrieved", status_code=200)
async def retrieved_broup(
    retrieved_broup_request: RetrievedBroupRequest,
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

    broup_id = retrieved_broup_request.broup_id
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
    me_broup.broup_updated = False
    db.add(me_broup)
    await db.commit()

    return {"result": True}



# class RetrievedBrosRequest(BaseModel):
#     bro_ids: List[int]


# @api_router_v1.post("/bros/retrieved", status_code=200)
# async def retrieved_bros(
#     retrieved_bros_request: RetrievedBrosRequest,
#     request: Request,
#     response: Response,
#     db: AsyncSession = Depends(get_db),
# ) -> dict:
#     auth_token = get_auth_token(request.headers.get("Authorization"))

#     if auth_token == "":
#         return get_failed_response("An error occurred", response)

#     me: Optional[Bro] = await check_token(db, auth_token, True)
#     if not me:
#         return get_failed_response("An error occurred", response)

#     bro_ids = retrieved_bros_request.bro_ids

#     # Go over the broups, if the bro is marked to update we know that that is no longer needed
#     for broup in me.broups:
#         for bro_id in bro_ids:
#             if bro_id in broup.update_bros:
#                 broup.dismiss_bro_to_update(bro_id)
#                 db.add(broup)
#     await db.commit()

#     return {"result": True}
