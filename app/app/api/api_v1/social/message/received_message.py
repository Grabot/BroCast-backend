from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Message, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_message_image_data
from sqlalchemy.orm import selectinload
from datetime import datetime
import pytz


class ReceievedMessageRequest(BaseModel):
    broup_id: int
    message_id: int


@api_router_v1.post("/message/received/single", status_code=200)
async def message_received_single(
    receieved_message_request: ReceievedMessageRequest,
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

    broup_id = receieved_message_request.broup_id
    message_id = receieved_message_request.message_id

    select_message_statement = (
        select(Message)
        .where(
            Message.message_id == message_id,
            Message.broup_id == broup_id,
        )
    )
    results_message = await db.execute(select_message_statement)
    result_message = results_message.first()
    if result_message is None:
        return {
            "result": False,
            "error": "No messages found",
        }

    message: Message = result_message.Message
    
    message.bro_received_message(me.id)
    db.add(message)
    if message.receive_remaining == []:
        if message.data:
            remove_message_image_data(message.data)
        await db.delete(message)

    await db.commit()

    return {
        "result": True,
    }




class ReceievedMessagesRequest(BaseModel):
    broup_id: int
    message_ids: List[int]


@api_router_v1.post("/message/received", status_code=200)
async def message_received(
    receieved_messages_request: ReceievedMessagesRequest,
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

    broup_id = receieved_messages_request.broup_id
    message_ids = receieved_messages_request.message_ids

    select_messages_statement = (
        select(Message)
        .where(Message.message_id.in_(message_ids))
        .where(Message.broup_id == broup_id)
    )
    results_messages = await db.execute(select_messages_statement)
    result_messages = results_messages.all()
    if result_messages is None or result_messages == []:
        return {
            "result": False,
            "error": "No messages found",
        }

    for result_message in result_messages:
        message: Message = result_message.Message

        message.bro_received_message(me.id)
        if message.receive_remaining == []:
            if message.data:
                remove_message_image_data(message.data)
            await db.delete(message)

    await db.commit()

    return {
        "result": True,
    }
