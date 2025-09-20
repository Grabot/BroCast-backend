from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.notification_util import send_notification_broup
from app.util.util import check_token, get_auth_token, save_image_v1_5, save_video_v1_5, save_audio_v1_5
from app.sockets.sockets import redis


class SendLocationRequest(BaseModel):
    broup_id: int
    message: str
    location: str
    text_message: Optional[str]
    data_type: int


@api_router_v1_5.post("/message/send/location", status_code=200)
async def send_message(
    send_location_request: SendLocationRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return Response(
            content="An error occurred",
            media_type="text/plain",
            status_code=500
        )

    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return Response(
            content="An error occurred",
            media_type="text/plain",
            status_code=500
        )

    broup_id = send_location_request.broup_id
    message = send_location_request.message
    location = send_location_request.location
    text_message = send_location_request.text_message
    data_type = send_location_request.data_type

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

    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=chat.current_message_id,
        body=message,
        text_message=text_message,
        timestamp=current_timestamp,
        info=False,
        data=location,
        data_type=data_type,
        replied_to=None,
        receive_remaining=chat.bro_ids
    )
    chat.current_message_id += 1
    db.add(chat)
    bro_message.bro_received_message(me.id)
    db.add(bro_message)
    await db.commit()

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

    if data_type == 4:
        # For live location we set the initial location and the expiration time in the redis db.
        lat_lng, end_time_string = location.split(";")
        lat, lng = lat_lng.split(",")
        end_time = datetime.fromisoformat(end_time_string)
        now = datetime.now(pytz.utc)
        delta = end_time - now
        ttl = int(delta.total_seconds())
        await redis.setex(f"bro:{me.id}:broup:{broup_id}:location", ttl, f"{lat},{lng}")

    broup_room = f"broup_{broup_id}"
    message_send_data = bro_message.serialize_no_image
    image_data = {
        "type": data_type,
        "location_data": location
    }
    message_send_data["location_data"] = image_data
    await sio.emit(
        "message_received",
        message_send_data,
        room=broup_room,
    )

    return {
        "result": True,
        "message_id": bro_message.message_id,
    }
