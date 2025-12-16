import time

from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.celery_worker.tasks import task_send_email_forgot_password
from app.database import get_db
from app.models import Bro, BroToken
from app.util.rest_util import get_failed_response
import hashlib


class PasswordResetRequest(BaseModel):
    email: str


@api_router_v1.post("/password/reset", status_code=200)
async def reset_password(
    password_reset_request: PasswordResetRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    email_to_send = password_reset_request.email

    hashed_email = hashlib.sha512(email_to_send.lower().encode("utf-8")).hexdigest()
    statement = select(Bro).where(Bro.origin == 0).where(Bro.email_hash == hashed_email)
    results = await db.execute(statement)
    result_bro = results.first()
    if not result_bro:
        return get_failed_response("no account found using this email", response)

    bro: Bro = result_bro.Bro
    access_expiration_time = 1800  # 30 minutes
    refresh_expiration_time = 18000  # 5 hours
    token_expiration = int(time.time()) + access_expiration_time
    refresh_token_expiration = int(time.time()) + refresh_expiration_time
    reset_token = bro.generate_auth_token(access_expiration_time).decode("ascii")
    refresh_reset_token = bro.generate_refresh_token(refresh_expiration_time).decode("ascii")

    subject = "Brocast - Change your password"
    _ = task_send_email_forgot_password.delay(email_to_send, subject, reset_token, refresh_reset_token)

    bro_token = BroToken(
        bro_id=bro.id,
        access_token=reset_token,
        refresh_token=refresh_reset_token,
        token_expiration=token_expiration,
        refresh_token_expiration=refresh_token_expiration,
    )
    db.add(bro_token)
    await db.commit()

    return {
        "result": True,
    }
