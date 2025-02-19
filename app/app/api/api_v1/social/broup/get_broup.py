from typing import Optional, List

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


class GetBroupRequest(BaseModel):
    broup_ids: List[int]


@api_router_v1.post("/broup/get", status_code=200)
async def get_broup(
    get_broups_request: GetBroupRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    print("getting broups")
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, False)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_ids = get_broups_request.broup_ids
    broups_statement = (
        select(Broup)
        .where(Broup.bro_id == me.id, Broup.broup_id.in_(broup_ids))
        .options(selectinload(Broup.chat))
    )
    print(f"broups_statement {broups_statement}")
    results_broups = await db.execute(broups_statement)
    print(f"results_broups {results_broups}")
    result_broups = results_broups.all()
    print(f"result_broups {result_broups}")

    if result_broups is None or result_broups == []:
        return {
            "result": True,
            "broups": [],
        }

    broup_list = []
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        # Retrieved full data, so no longer set to updated
        broup.set_updated(False)
        db.add(broup)
        broup_list.append(broup.serialize)
    await db.commit()

    return {"result": True, "broups": broup_list}
