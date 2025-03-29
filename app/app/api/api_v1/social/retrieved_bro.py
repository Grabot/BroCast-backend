from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class RetrievedBroRequest(BaseModel):
    bro_id: int


@api_router_v1.post("/bro/retrieved", status_code=200)
async def retrieved_bro(
    retrieved_bro_request: RetrievedBroRequest,
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

    bro_id = retrieved_bro_request.bro_id
    
    # Go over the broups, if the bro is marked to update we know that that is no longer needed
    for broup in me.broups:
        if bro_id in broup.update_bros:
            broup.dismiss_bro_to_update(bro_id)
            db.add(broup)
    await db.commit()

    return {"result": True}



class RetrievedBrosRequest(BaseModel):
    bro_ids: List[int]


@api_router_v1.post("/bros/retrieved", status_code=200)
async def retrieved_bros(
    retrieved_bros_request: RetrievedBrosRequest,
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

    bro_ids = retrieved_bros_request.bro_ids

    # Go over the broups, if the bro is marked to update we know that that is no longer needed
    for broup in me.broups:
        for bro_id in bro_ids:
            if bro_id in broup.update_bros:
                broup.dismiss_bro_to_update(bro_id)
                db.add(broup)
    await db.commit()

    return {"result": True}
