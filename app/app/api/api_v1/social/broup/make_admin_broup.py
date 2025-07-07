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


class MakeAdminBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/make_admin", status_code=200)
async def make_admin_broup(
    make_admin_broup_request: MakeAdminBroupRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    print(f"Auth Token: {auth_token}")

    if auth_token == "":
        print("No auth token provided")
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, False)
    if not me:
        print("Invalid auth token")
        return get_failed_response("An error occurred", response)

    broup_id = make_admin_broup_request.broup_id
    bro_id = make_admin_broup_request.bro_id
    print(f"Broup ID: {broup_id}, Bro ID: {bro_id}")

    bro_statement = select(Bro).where(
        Bro.id == bro_id
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is None:
        print("Bro does not exist")
        return {
            "result": False,
            "message": "Bro does not exists",
        }
    new_admin_bro: Bro = result.Bro
    print(f"New Admin Bro: {new_admin_bro}")

    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        print("Broup not found")
        return get_failed_response("Broup not found", response)

    chat: Chat = chat_object.Chat
    print(f"Chat Object: {chat}")

    if bro_id in chat.bro_admin_ids and bro_id in chat.bro_ids:
        print("Bro is already an admin")
        return {
            "result": False,
            "error": "Bro is already an admin",
        }
    chat.add_admin(bro_id)
    db.add(chat)

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "new_admin_id": bro_id}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )
    print(f"Socket response sent: {socket_response}")

    message_text = f"Bro {me.bro_name} {me.bromotion} made bro {new_admin_bro.bro_name} {new_admin_bro.bromotion} a new admin! 👑"
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
        receive_remaining=chat.bro_ids
    )
    chat.current_message_id += 1
    db.add(chat)
    db.add(bro_message)
    await db.commit()
    print(f"Message committed: {bro_message}")

    # Send message via socket. No need for notification
    await sio.emit(
        "message_received",
        bro_message.serialize,
        room=broup_room,
    )
    print(f"Message sent via socket: {bro_message.serialize}")

    return {
        "result": True,
    }
