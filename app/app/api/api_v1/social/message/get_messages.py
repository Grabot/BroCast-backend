from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
from app.api.api_v1.social.message.message_util import reading_messages
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Message, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class GetMessagesRequest(BaseModel):
    broup_id: int
    last_message_id: int


@api_router_v1.post("/message/get", status_code=200)
async def get_messages(
    get_messages_request: GetMessagesRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return get_failed_response("An error occurred", response)

    print(f"message getting by bro {me.id}: {me.bro_name} {me.bromotion}")
    broup_id = get_messages_request.broup_id
    last_message_id = get_messages_request.last_message_id

    select_statement = (
        select(Message)
        .where(
            Message.broup_id == broup_id,
            Message.message_id > last_message_id,
        )
        .order_by(Message.message_id)
    )
    results_messages = await db.execute(select_statement)
    result_messages = results_messages.all()
    if result_messages is None:
        return {
            "result": False,
            "error": "No messages found",
        }

    await reading_messages(db, response, me, broup_id)

    message_list = []
    for result_message in result_messages:
        message: Message = result_message.Message
        message_list.append(message.serialize)

    return {"result": True, "messages": message_list}
