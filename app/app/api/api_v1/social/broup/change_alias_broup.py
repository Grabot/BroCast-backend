from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload


class BroupChangeAliasRequest(BaseModel):
    broup_id: int
    new_broup_alias: str


@api_router_v1.post("/broup/change_alias", status_code=200)
async def broup_change_alias(
    broup_change_alias_request: BroupChangeAliasRequest,
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

    broup_id = broup_change_alias_request.broup_id
    new_broup_alias = broup_change_alias_request.new_broup_alias

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
        }

    # The alias is only visible to the user who set the alias.
    broup: Broup = result_broup.Broup
    broup.update_broup_alias(new_broup_alias)
    db.add(broup)
    await db.commit()

    return {
        "result": True,
    }
