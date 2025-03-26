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
from app.util.notification_util import send_notification_broup
from app.util.util import check_token, get_auth_token, save_image


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
    ).options(selectinload(Broup.broup_member))
    results_broup = await db.execute(broup_statement)
    broup_objects = results_broup.all()
    # The broup object and the message will have the same timestamp so we can check if it's equal
    current_timestamp = datetime.now(pytz.utc).replace(tzinfo=None)
    if broup_objects is None:
        return {
            "result": False,
            "error": "Broup does not exist",
        }

    tokens = []
    for broup_object in broup_objects:
        broup: Broup = broup_object.Broup
        if broup.bro_id == me.id:
            broup.received_message(current_timestamp)
            broup.read_messages(current_timestamp)
        else:
            if not broup.is_removed():
                broup.update_unread_messages()
                broup.check_mute()
            if not broup.is_muted() and not broup.removed and not broup.deleted:
                broup_member: Bro = broup.broup_member
                bro_fcm_token = broup_member.fcm_token
                if bro_fcm_token is not None:
                    tokens.append(
                        [
                            bro_fcm_token,
                            broup_member.platform
                        ]
                    )
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
    file_name = None
    data_type = None
    if message_data is not None:
        # If the message includes image data we want to take the data and save it as an image
        # The path to that image will be saved on the message db object.
        # This is because we don't want to save the image in the db itself.
        # Create a filename based on the current timestamp
        file_name = f"broup_{broup_id}_image_{current_timestamp.strftime('%Y%m%d%H%M%S%f')}"
        data_type = 0
        save_image(message_data, file_name)
    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=chat.current_message_id,
        body=message,
        text_message=text_message,
        timestamp=current_timestamp,
        info=False,
        data=file_name,
        data_type=data_type,
    )
    chat.current_message_id += 1
    db.add(chat)
    db.add(bro_message)
    await db.commit()
    # No need to refresh message because we don't send the message id

    broup_name = chat.broup_name
    if chat.private:
        for broup_object in broup_objects:
            broup: Broup = broup_object.Broup
            if broup.bro_id != me.id:
                bro: Bro = broup.broup_member
                broup_name = bro.bro_name + " " + bro.bromotion
                break

    sender_name = me.bro_name + " " + me.bromotion
    await send_notification_broup(tokens, chat.id, chat.private, broup_name, sender_name, message)

    broup_room = f"broup_{broup_id}"
    message_send_data = bro_message.serialize_no_image
    if message_data is not None:
        image_data = {
            "data": message_data,
            "type": data_type,
        }
        message_send_data["data"] = image_data
    await sio.emit(
        "message_received",
        message_send_data,
        room=broup_room,
    )

    return {
        "result": True,
    }
