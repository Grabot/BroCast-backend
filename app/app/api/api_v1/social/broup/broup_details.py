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


class BroupDetailsRequest(BaseModel):
    broup_update_ids: List[int]
    broup_avatar_update_ids: List[int]


@api_router_v1.post("/broup/details", status_code=200)
async def broup_details(
    broup_details_request: BroupDetailsRequest,
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

    broup_update_ids = broup_details_request.broup_update_ids
    broup_avatar_update_ids = broup_details_request.broup_avatar_update_ids
    broup_ids = list(set(broup_update_ids + broup_avatar_update_ids))
    print(f"broup_ids {broup_ids}")

    if not broup_ids:
        return {
            "result": True,
            "bros": [],
        }

    broups_statement = select(Broup).where(
        Broup.broup_id.in_(broup_ids),
        Broup.bro_id == me.id,
    )
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()

    if result_broups is None or result_broups == []:
        return {
            "result": True,
            "broups": [],
        }

    broup_list = []
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        # No avatar since the `new_avatar` flag should have been true
        if broup.broup_id in broup_avatar_update_ids and broup.broup_id in broup_update_ids:
            print("doing both")
            broup_list.append(broup.serialize_avatar)
        elif broup.broup_id in broup_avatar_update_ids:
            print("only avatar")
            # It's possible that we won't need the broname or bromotion.
            # Maybe a future improvement, but we don't need to worry about it now.
            broup_list.append(broup.serialize_only_avatar)
        else:
            print("the rest")
            broup_list.append(broup.serialize)

    return {"result": True, "broups": broup_list}
