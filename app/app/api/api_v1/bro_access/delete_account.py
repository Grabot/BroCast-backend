from typing import Optional

from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from sqlalchemy.orm import selectinload
from app.models import Bro, BroToken
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
import time


@api_router_v1.post("/delete/account", status_code=200)
async def delete_account(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if auth_token == "":
        return get_failed_response("An error occurred", response)

    token_statement = select(BroToken).filter_by(access_token=auth_token)
    results_token = await db.execute(token_statement)
    result_token = results_token.first()
    if result_token is None:
        return {
            "result": False,
            "message": "Bro account deletion failed",
        }

    bro_token: BroToken = result_token.BroToken
    if bro_token.token_expiration < int(time.time()):
        return {
            "result": False,
            "message": "Bro account deletion failed",
        }
    
    bro_statement = select(Bro).filter_by(id=bro_token.bro_id).options(selectinload(Bro.tokens))
    results = await db.execute(bro_statement)
    result = results.first()
    if result is None:
        return {
            "result": False,
            "message": "Bro account deletion failed",
        }
    me = result.Bro
    for token in me.tokens:
        await db.delete(token)
    await db.delete(me)
    await db.commit()

    return {
        "result": True,
        "message": "Bro account deleted successfully",
    }
