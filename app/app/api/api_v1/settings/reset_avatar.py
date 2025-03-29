import base64
import os
from typing import Optional, List
from sqlmodel import select
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Chat, Broup, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload
from app.sockets.sockets import sio
from datetime import datetime
import pytz


@api_router_v1.post("/reset/avatar/me", status_code=200)
async def reset_avatar_me(
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

    file_folder = settings.UPLOAD_FOLDER_AVATARS
    file_name = me.avatar_filename_default()
    file_path = os.path.join(file_folder, "%s.png" % file_name)

    if not os.path.isfile(file_path):
        return get_failed_response("An error occurred", response)
    else:
        with open(file_path, "rb") as fd:
            image_as_base64 = base64.encodebytes(fd.read()).decode()

        me.set_default_avatar(True)
        db.add(me)
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
                    else:
                        # TODO:
                        print("Updating bro in broup avatar")
                    db.add(chat_broup)

            broup_room = f"broup_{chat.id}"
            socket_response = {
                "bro_id": me.id,
                "broup_id": chat.id,
                "new_avatar": True
            }
            await sio.emit(
                "bro_update",
                socket_response,
                room=broup_room,
            )
        await db.commit()
        
        return {"result": True, "message": image_as_base64}


class ResetAvatarBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/reset/avatar/broup", status_code=200)
async def reset_avatar_broup(
    reset_avatar_broup_request: ResetAvatarBroupRequest,
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

    broup_id = reset_avatar_broup_request.broup_id
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    ).options(selectinload(Chat.chat_broups))
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)

    chat: Chat = chat_object.Chat
    
    chat.set_default_avatar(True)
    file_folder = settings.UPLOAD_FOLDER_AVATARS
    file_name = chat.avatar_filename_default()
    file_path = os.path.join(file_folder, "%s.png" % file_name)
    
    chat_broups: List[Broup] = chat.chat_broups
    for chat_broup in chat_broups:
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
        data_type=None,
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

    if not os.path.isfile(file_path):
        return get_failed_response("An error occurred", response)
    else:
        with open(file_path, "rb") as fd:
            image_as_base64 = base64.encodebytes(fd.read()).decode()

        return {"result": True, "message": image_as_base64}
