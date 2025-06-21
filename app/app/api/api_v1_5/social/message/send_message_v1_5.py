from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.notification_util import send_notification_broup
from app.util.util import check_token, get_auth_token, save_image_v1_5


@api_router_v1_5.post("/message/send", status_code=200)
async def send_message(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    broup_id: int = Form(...),
    message: str = Form(...),
    text_message: Optional[str] = Form(None),
    message_data: Optional[UploadFile] = File(default=None),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_statement = select(Broup).where(
        Broup.broup_id == broup_id,
    ).options(selectinload(Broup.broup_member))
    results_broup = await db.execute(broup_statement)
    broup_objects = results_broup.all()
    if broup_objects is None:
        return {
            "result": False,
            "error": "Broup does not exist",
        }

    # We retrieve and quickly update the chat object along with the message
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

    tokens = []
    for broup_object in broup_objects:
        broup: Broup = broup_object.Broup
        if broup.bro_id == me.id:
            # We have sent a message, so the chat must be open,
            # which means we've read all the messages currently in the chat.
            broup.last_message_read_id = chat.current_message_id
        else:
            if not broup.is_removed():
                broup.update_unread_messages()
                broup.check_mute()
            if not broup.is_muted() and not broup.open and not broup.removed and not broup.deleted:
                broup_member: Bro = broup.broup_member
                bro_fcm_token = broup_member.fcm_token
                if bro_fcm_token is not None and bro_fcm_token != "":
                    tokens.append(
                        [
                            bro_fcm_token,
                            broup_member.platform
                        ]
                    )
        db.add(broup)
        await db.commit()

    # The broup object and the message will have the same timestamp so we can check if it's equal
    current_timestamp = datetime.now(pytz.utc).replace(tzinfo=None)
    file_name = None
    data_type = None
    if message_data is not None:
        # If the message includes image data we want to take the data and save it as an image
        # The path to that image will be saved on the message db object.
        # This is because we don't want to save the image in the db itself.
        # Create a filename based on the current timestamp
        file_name = f"broup_{broup_id}_image_{current_timestamp.strftime('%Y%m%d%H%M%S%f')}"
        data_type = 0
        # Read the contents of the uploaded file
        image_bytes = await message_data.read()
        save_image_v1_5(image_bytes, file_name)

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
        replied_to=None,
        receive_remaining=chat.bro_ids
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
            "data": image_bytes,
            "type": data_type,
        }
        message_send_data["data"] = image_data
    await sio.emit(
        "message_received",
        message_send_data,
        room=broup_room,
    )
    print(f"image send")

    return {
        "result": True,
    }
