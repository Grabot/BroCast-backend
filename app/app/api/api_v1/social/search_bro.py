from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class SearchBroRequest(BaseModel):
    bro_name: str
    bromotion: Optional[str] = None


@api_router_v1.post("/bro/search", status_code=200)
async def search_bro(
    search_bro_request: SearchBroRequest,
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

    bro_name = search_bro_request.bro_name
    bromotion = search_bro_request.bromotion
    if bromotion == "":
        bro_statement = select(Bro).where(func.lower(Bro.bro_name) == bro_name.lower())
        results = await db.execute(bro_statement)
        bros = results.all()

    else:
        bro_statement = select(Bro).where(
            func.lower(Bro.bro_name) == bro_name.lower(),
            Bro.bromotion == bromotion,
        )
        results = await db.execute(bro_statement)
        bros = results.all()

    if bros is None or bros == []:
        return {
            "result": True,
            "bros": [],
        }

    bro_list = []
    for bro in bros:
        if bro.Bro is not me:
            bro_list.append(bro.Bro.serialize_small)

    return {
        "result": True,
        "bros": bro_list,
    }
