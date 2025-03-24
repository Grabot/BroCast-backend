import base64
import io
import os
import stat
from typing import Optional, List
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from PIL import Image
import numpy as np
import cv2
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Chat, Broup, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class ChangeAvatarRequest(BaseModel):
    avatar: str
    avatar_small: str


@api_router_v1.post("/change/avatar", status_code=200)
async def change_avatar(
    change_avatar_request: ChangeAvatarRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    new_avatar = change_avatar_request.avatar
    new_avatar_small = change_avatar_request.avatar_small

    image_bytes = base64.b64decode(new_avatar)
    image_bytes_small = base64.b64decode(new_avatar_small)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image_array_small = np.frombuffer(image_bytes_small, dtype=np.uint8)
    new_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    new_image_small = cv2.imdecode(image_array_small, cv2.IMREAD_COLOR)

    # Get the file name and path
    file_folder = settings.UPLOAD_FOLDER_AVATARS
    file_name = me.avatar_filename()
    file_name_small = me.avatar_filename() + "_small"
    # Store the image under the same hash but without the "default".
    file_path = os.path.join(file_folder, "%s.png" % file_name)
    file_path_small = os.path.join(file_folder, "%s.png" % file_name_small)
    
    # Save the image using OpenCV
    cv2.imwrite(file_path, new_image)
    cv2.imwrite(file_path_small, new_image_small)
    os.chmod(file_path, stat.S_IRWXO)
    os.chmod(file_path_small, stat.S_IRWXO)

    me.set_default_avatar(False)
    db.add(me)
    await db.commit()

    # Update all private chats of the bro. 
    # This is because they have the avatar of the bro.
    # and they have to update it now.
    # For broups we will list the bro id in the bros to update column.
    broups: List[Broup] = me.broups
    for broup in broups:
        chat: Chat = broup.chat
        chat_broups: List[Broup] = chat.chat_broups
        for chat_broup in chat_broups:
            if chat_broup.bro_id != me.id:
                chat_broup.broup_updated = True
                if chat.private:
                    # In a private chat the bro avatar is the broup avatar
                    chat_broup.new_avatar = True
                db.add(chat_broup)

                bro_room = f"room_{chat_broup.bro_id}"
                socket_response = {
                    "bro_id": me.id,
                    "new_avatar": True
                }
                # This will update the avatar of the bro, not the broup.
                await sio.emit(
                    "bro_update",
                    socket_response,
                    room=bro_room,
                )
        db.add(chat)

    return {
        "result": True,
        "message": "success",
    }


class ChangeAvatarBroupRequest(BaseModel):
    avatar: str
    avatar_small: str
    broup_id: int


@api_router_v1.post("/change/avatar/broup", status_code=200)
async def change_avatar_broup(
    change_avatar_broup_request: ChangeAvatarBroupRequest,
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

    new_avatar = change_avatar_broup_request.avatar
    new_avatar_small = change_avatar_broup_request.avatar_small
    broup_id = change_avatar_broup_request.broup_id

    new_avatar_pil = Image.open(io.BytesIO(base64.b64decode(new_avatar)))
    new_avatar_small_pil = Image.open(io.BytesIO(base64.b64decode(new_avatar_small)))

    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    ).options(selectinload(Chat.chat_broups))
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)

    chat: Chat = chat_object.Chat

    # Get the file name and path
    file_folder = settings.UPLOAD_FOLDER_AVATARS
    file_name = chat.avatar_filename()
    file_name_small = chat.avatar_filename() + "_small"
    # Store the image under the same hash but without the "default".
    file_path = os.path.join(file_folder, "%s.png" % file_name)
    file_path_small = os.path.join(file_folder, "%s.png" % file_name_small)

    new_avatar_pil.save(file_path)
    new_avatar_small_pil.save(file_path_small)
    os.chmod(file_path, stat.S_IRWXO)
    os.chmod(file_path_small, stat.S_IRWXO)

    chat.set_default_avatar(False)
    chat_broups: List[Broup] = chat.chat_broups
    for chat_broup in chat_broups:
        if chat_broup.bro_id != me.id:
            chat_broup.broup_updated = True
            chat_broup.update_unread_messages()
            chat_broup.new_avatar = True
        db.add(chat_broup)

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "new_avatar": True}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    message_text = f"Bro {me.bro_name} {me.bromotion} changed the chat picture! 🖼️"
    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=chat.current_message_id,
        body=message_text,
        text_message="",
        timestamp=datetime.now(pytz.utc).replace(tzinfo=None),
        info=True,
        data=None,
    )
    chat.current_message_id += 1
    db.add(chat)
    db.add(bro_message)
    await db.commit()

    # Send message via socket. No need for notification
    await sio.emit(
        "message_received",
        bro_message.serialize,
        room=broup_room,
    )

    return {
        "result": True,
        "message": "success",
    }
