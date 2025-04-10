from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Chat, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio


class DismissAdminBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/dismiss_admin", status_code=200)
async def dismiss_admin_broup(
    dimsiss_admin_broup_request: DismissAdminBroupRequest,
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

    broup_id = dimsiss_admin_broup_request.broup_id
    bro_id = dimsiss_admin_broup_request.bro_id
    
    bro_statement = select(Bro).where(
        Bro.id == bro_id
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is None:
        return {
            "result": False,
            "message": "Bro does not exists",
        }
    dismiss_bro: Bro = result.Bro

    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)

    chat: Chat = chat_object.Chat
    if bro_id not in chat.bro_admin_ids and bro_id in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro is not an admin",
        }
    chat.dismiss_admin(bro_id)
    db.add(chat)

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "dismissed_admin_id": bro_id}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    message_text = f"Bro {me.bro_name} {me.bromotion} dismissed bro {dismiss_bro.bro_name} {dismiss_bro.bromotion} as admin 😅"
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
        replied_to=None,
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
    }
