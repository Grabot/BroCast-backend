from typing import Optional

from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, BroToken
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


@api_router_v1.post("/logout", status_code=200)
async def logout_bro(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if auth_token == "":
        return get_failed_response("An error occurred", response)

    bro: Optional[Bro] = await check_token(db, auth_token)
    if not bro:
        return get_failed_response("An error occurred", response)

    token_statement = select(BroToken).filter_by(access_token=auth_token)
    results_token = await db.execute(token_statement)
    result_token = results_token.first()
    if result_token is None:
        return get_failed_response("An error occurred", response)

    bro_token = result_token.BroToken
    await db.delete(bro_token)
    await db.commit()

    return {
        "result": True,
        "message": "Bro logged out successfully.",
    }
