from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, BroToken
from app.util.rest_util import get_failed_response, leave_broup_me
from app.util.util import refresh_bro_token
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.util.util import get_auth_token
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

    bro_statement = (
        select(Bro)
        .filter_by(id=bro_token.bro_id)
        .options(selectinload(Bro.broups))
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is None:
        return {
            "result": False,
            "message": "Bro account deletion failed",
        }
    me = result.Bro
    for broup in me.broups:
        _ = await leave_broup_me(me, broup.broup_id, db)
    await db.commit()
    # Retrieve the bro again, this time for the tokens which might have changed.
    bro_statement_2 = (
        select(Bro)
        .filter_by(id=bro_token.bro_id)
        .options(selectinload(Bro.tokens))
    )
    results_2 = await db.execute(bro_statement_2)
    result_2 = results_2.first()
    if result_2 is None:
        return {
            "result": False,
            "message": "Bro account deletion failed",
        }
    me = result_2.Bro
    for token in me.tokens:
        await db.delete(token)
    me.email_hash = ""
    me.bro_name = ""
    me.bromotion = ""
    db.add(me)
    await db.commit()

    return {
        "result": True,
        "message": "Bro account deleted successfully",
    }


class DeleteAccountRequest(BaseModel):
    access_token: str
    refresh_token: str


@api_router_v1.post("/delete/account/all", status_code=200)
async def delete_account_all(
    delete_account_request: DeleteAccountRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    access_token = delete_account_request.access_token
    refresh_token = delete_account_request.refresh_token

    me: Optional[Bro] = await refresh_bro_token(db, access_token, refresh_token, False)
    if not me:
        return get_failed_response("Bro not found", response)
    statement = (
        select(Bro)
        .where(Bro.email_hash == me.email_hash)
        .options(selectinload(Bro.broups))
    )
    results = await db.execute(statement)
    result = results.all()
    if result is None or result == []:
        return get_failed_response("no account found with that email", response)

    for bro_result in result:
        bro_me: Bro = bro_result.Bro
        for broup in bro_me.broups:
            _ = await leave_broup_me(bro_me, broup.broup_id, db)
        await db.commit()
        # Retrieve the bro again, this time for the tokens which might have changed.
        bro_statement_2 = (
            select(Bro)
            .filter_by(id=bro_me.id)
            .options(selectinload(Bro.tokens))
        )
        results_2 = await db.execute(bro_statement_2)
        result_2 = results_2.first()
        if result_2 is None:
            return {
                "result": False,
                "message": "Bro account deletion failed",
            }
        bro_token = result_2.Bro
        for token in bro_token.tokens:
            await db.delete(token)
        bro_token.email_hash = ""
        bro_token.bro_name = ""
        bro_token.bromotion = ""
        db.add(bro_token)
    await db.commit()

    return {
        "result": True,
    }
