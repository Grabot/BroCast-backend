import time
from typing import Optional

from authlib.jose import jwt
from authlib.jose.errors import DecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.config.config import settings
from app.models import Bro, BroToken


async def delete_bro_token_and_return(db: AsyncSession, bro_token, return_value: Optional[Bro]):
    await db.delete(bro_token)
    await db.commit()
    return return_value


async def refresh_bro_token(db: AsyncSession, access_token, refresh_token):
    token_statement = (
        select(BroToken)
        .filter_by(access_token=access_token)
        .filter_by(refresh_token=refresh_token)
    )
    results_token = await db.execute(token_statement)
    result_token = results_token.first()
    if result_token is None:
        return None

    bro_token: BroToken = result_token.BroToken
    if bro_token.refresh_token_expiration < int(time.time()):
        return await delete_bro_token_and_return(db, bro_token, None)

    bro_statement = (
        select(Bro)
        .filter_by(id=bro_token.bro_id)
        .options(selectinload(Bro.bros))
        .options(selectinload(Bro.tokens))
    )
    bro_results = await db.execute(bro_statement)
    bro_result = bro_results.first()
    if bro_result is None:
        return await delete_bro_token_and_return(db, bro_token, None)
    bro = bro_result.Bro

    if bro_token.token_expiration > int(time.time()):
        return await delete_bro_token_and_return(db, bro_token, bro)
    try:
        access = jwt.decode(access_token, settings.jwk)
        refresh = jwt.decode(refresh_token, settings.jwk)
    except DecodeError:
        return await delete_bro_token_and_return(db, bro_token, None)

    if not access or not refresh:
        return await delete_bro_token_and_return(db, bro_token, None)

    # do the refresh time check again, just in case.
    if refresh["exp"] < int(time.time()):
        return await delete_bro_token_and_return(db, bro_token, None)

    # It all needs to match before you accept the login
    if bro.id == access["id"] and bro.broname == refresh["bro_name"]:
        return await delete_bro_token_and_return(db, bro_token, bro)
    else:
        return await delete_bro_token_and_return(db, bro_token, None)


async def check_token(db: AsyncSession, token, retrieve_full=False) -> Optional[Bro]:
    token_statement = select(BroToken).filter_by(access_token=token)
    results_token = await db.execute(token_statement)
    result_token = results_token.first()
    if result_token is None:
        return None

    bro_token: BroToken = result_token.BroToken
    if bro_token.token_expiration < int(time.time()):
        return None
    if retrieve_full:
        bro_statement = (
            select(Bro).filter_by(id=bro_token.bro_id).options(selectinload(Bro.bros))
        )
    else:
        bro_statement = select(Bro).filter_by(id=bro_token.bro_id)
    results = await db.execute(bro_statement)
    result = results.first()
    if result is None:
        return None
    bro = result.Bro
    return bro


def get_bro_tokens(bro: Bro, access_expiration=1800, refresh_expiration=2678400):
    # Create an access_token that the bro can use to do bro authentication
    token_expiration = int(time.time()) + access_expiration
    refresh_token_expiration = int(time.time()) + refresh_expiration
    access_token = bro.generate_auth_token(access_expiration).decode("ascii")
    # Create a refresh token that lasts longer that the bro can use to generate a new access token
    # right now choose 30 minutes and 31 days for access and refresh token.
    refresh_token = bro.generate_refresh_token(refresh_expiration).decode("ascii")
    bro_token = BroToken(
        bro_id=bro.id,
        access_token=access_token,
        refresh_token=refresh_token,
        token_expiration=token_expiration,
        refresh_token_expiration=refresh_token_expiration,
    )
    return bro_token


def get_auth_token(auth_header):
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ""
    return auth_token
