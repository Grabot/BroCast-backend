import time
from typing import Optional
from fastapi import Request, Depends
from pydantic import BaseModel
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_send_email
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Broup, BroToken
from app.util.email.delete_account_email import delete_account_email
from app.util.rest_util import get_failed_response
from app.util.util import refresh_bro_token
from sqlalchemy.orm import selectinload
from app.util.util import check_token, get_auth_token
import hashlib


async def send_delete_email(bro: Bro, email: str, origin: int):
    access_expiration_time = 1800  # 30 minutes
    refresh_expiration_time = 18000  # 5 hours
    token_expiration = int(time.time()) + access_expiration_time
    refresh_token_expiration = int(time.time()) + refresh_expiration_time
    delete_token = bro.generate_auth_token(access_expiration_time).decode("ascii")
    refresh_delete_token = bro.generate_refresh_token(refresh_expiration_time).decode("ascii")

    subject = "BroCast - Delete your account"
    body = delete_account_email.format(
        base_url=settings.BASE_URL,
        token=delete_token,
        refresh_token=refresh_delete_token,
        origin=origin,
    )
    # TODO: add bromotion?
    _ = task_send_email.delay(bro.bro_name, email, subject, body)

    bro_token = BroToken(
        bro_id=bro.id,
        access_token=delete_token,
        refresh_token=refresh_delete_token,
        token_expiration=token_expiration,
        refresh_token_expiration=refresh_token_expiration,
    )
    return bro_token


class RemoveAccountRequest(BaseModel):
    email: str


@api_router_v1.post("/remove/account", status_code=200)
async def remove_account(
    remove_account_request: RemoveAccountRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:

    email = remove_account_request.email
    email = email.strip()
    email_hash = hashlib.sha512(email.lower().encode("utf-8")).hexdigest()
    statement = (
        select(Bro)
        .where(Bro.email_hash == email_hash)
        .options(selectinload(Bro.broups))
        .options(selectinload(Bro.tokens))
    )
    results = await db.execute(statement)
    result = results.all()
    if result is None or result == []:
        return get_failed_response("no account found with that email", response)

    bro = result[0].Bro
    # origin 9 means all the accounts with the email will be deleted
    bro_token = await send_delete_email(bro, email, 9)
    db.add(bro_token)
    await db.commit()

    return {
        "result": True,
        "message": "Account deletion email has been sent",
    }


@api_router_v1.post("/remove/account/token", status_code=200)
async def remove_account_token(
    remove_account_request: RemoveAccountRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:

    email = remove_account_request.email
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    bro: Optional[Bro] = await check_token(db, auth_token, False)
    if not bro:
        return get_failed_response("An error occurred", response)

    email_hash = hashlib.sha512(email.lower().encode("utf-8")).hexdigest()
    if email_hash == bro.email_hash:
        bro_token = await send_delete_email(bro, email, bro.origin)
        db.add(bro_token)
        await db.commit()
        return {
            "result": True,
            "message": "Account deletion email has been sent",
        }
    else:
        return {
            "result": False,
            "message": "Email is not the same as the account email",
        }


class RemoveAccountVerifyRequest(BaseModel):
    access_token: str
    refresh_token: str
    origin: int


@api_router_v1.post("/remove/account/verify", status_code=200)
async def remove_account_verify(
    remove_account_verify_request: RemoveAccountVerifyRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:

    access_token = remove_account_verify_request.access_token
    refresh_token = remove_account_verify_request.refresh_token
    origin = remove_account_verify_request.origin
    bro: Optional[Bro] = await refresh_bro_token(db, access_token, refresh_token)

    if not bro:
        return get_failed_response("Bro not found", response)

    if origin != 9:
        bro_tokens = bro.tokens
        for bro_token in bro_tokens:
            await db.delete(bro_token)
        await db.commit()

        await db.delete(bro)
        await db.commit()
        return {
            "result": True,
            "message": "Account deletion has been cancelled",
        }
    else:
        hashed_email = bro.email_hash
        # Get all the accounts with the same email by checking the hash in the db
        statement = (
            select(Bro).where(Bro.email_hash == hashed_email).options(selectinload(Bro.tokens))
        )
        results = await db.execute(statement)
        bros = results.all()
        if bros is None or bros == []:
            return get_failed_response("no account found with that email", response)

        # First delete tokens, otherwise we can't delete the bro
        for bro in bros:
            log_bro = bro.Bro
            bro_tokens = log_bro.tokens
            for bro_token in bro_tokens:
                await db.delete(bro_token)
        await db.commit()

        # Then delete the bro, which might be multiple because of oauth2
        for bro in bros:
            await db.delete(bro.Bro)
        await db.commit()

        return {
            "result": True,
            "message": "Account has been removed",
        }
