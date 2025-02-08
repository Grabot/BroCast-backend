from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Message, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class SendMessageRequest(BaseModel):
    broup_id: int
    message: str
    text_message: Optional[str]
    message_data: Optional[str]


@api_router_v1.post("/message/send", status_code=200)
async def send_message(
    send_message_request: SendMessageRequest,
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

    broup_id = send_message_request.broup_id
    message = send_message_request.message
    text_message = send_message_request.text_message
    message_data = send_message_request.message_data

    broup_statement = select(Broup).where(
        Broup.broup_id == broup_id,
    )
    results_broup = await db.execute(broup_statement)
    broup_objects = results_broup.all()
    # The broup object and the message will have the same timestamp so we can check if it's equal
    current_timestamp = datetime.now(pytz.utc).replace(tzinfo=None)
    if broup_objects is None:
        return {
            "result": False,
            "error": "Broup does not exist",
        }
    else:
        for broup_object in broup_objects:
            broup: Broup = broup_object.Broup
            print(f"found broup {broup.broup_id}")
            if broup.bro_id == me.id:
                # The bro that send the message obviously also read and received it.
                broup.last_message_received_time = current_timestamp
                broup.last_message_read_time = current_timestamp
            else:
                # The other bro's now gets an extra unread message and their chat is moved to the top of their list.
                if not broup.has_left() and not broup.is_removed():
                    broup.update_unread_messages()
                    broup.check_mute()
            db.add(broup)
            await db.commit()

    # We retrieve and quickly update the chat object allong with the message
    # This is to avoid concurrency issues on the message id
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_objects = results_chat.first()
    if chat_objects is None:
        return {
            "result": False,
            "error": "Chat does not exist",
        }
    chat: Chat = chat_objects.Chat
    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=chat.current_message_id,
        body=message,
        text_message=text_message,
        timestamp=current_timestamp,
        info=False,
        data=message_data
    )
    chat.current_message_id += 1
    db.add(chat)
    db.add(bro_message)
    await db.commit()
    # No need to refresh message because we don't send the message id

    # send_notification_broup(bro_ids, message, broup_id, broup_objects, bro_id)
    broup_room = f"broup_{broup_id}"
    await sio.emit(
        "message_received",
        bro_message.serialize,
        room=broup_room,
    )

    return {
        "result": True,
    }
