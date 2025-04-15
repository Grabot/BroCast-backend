from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, BroToken
from app.util.rest_util import get_failed_response
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

    print(f"called the delete account all endpoint with access token {access_token} and refresh token {refresh_token}")

    bro: Optional[Bro] = await refresh_bro_token(db, access_token, refresh_token, False)
    if not bro:
        return get_failed_response("Bro not found", response)
    print(f"removing all accounts of bro {bro.bro_name} {bro.bromotion}")
    statement = (
        select(Bro)
        .where(Bro.email_hash == bro.email_hash)
        .options(selectinload(Bro.tokens))
    )
    results = await db.execute(statement)
    result = results.all()
    if result is None or result == []:
        return get_failed_response("no account found with that email", response)

    print(f"found ${len(result)} accounts to remove")
    for bro_result in result:
        bro_remove = bro_result.Bro

        for token in bro_remove.tokens:
            print("removing bro token")
            await db.delete(token)
        print("removing bro")
        await db.delete(bro_remove)
    print("finally removing bro")
    await db.commit()

    return {
        "result": True,
    }
