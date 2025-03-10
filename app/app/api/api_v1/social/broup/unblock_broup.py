from typing import Optional, List
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class BroUnblockRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/bro/unblock", status_code=200)
async def unblock_bro(
    bro_unblock_request: BroUnblockRequest,
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

    broup_id = bro_unblock_request.broup_id
    bro_id = bro_unblock_request.bro_id

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
    unblock_bro: Bro = result.Bro
    print(f"remove_bro_broup_request {bro_id}  {broup_id}")
    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
        )
        .options(selectinload(Broup.chat))
    )

    results_broups = await db.execute(broups_statement)
    print(f"results_bromotions {results_broups}")
    result_broups = results_broups.all()
    print(f"result_bromotion {result_broups}")
    if result_broups is None or result_broups == []:
        return {
            "result": False,
            "message": "Broup not found",
        }
    chat: Chat = result_broups[0].Broup.chat

    if not chat.private:
        return {
            "result": False,
            "error": "This is not a private broup",
        }

    if bro_id not in chat.bro_ids or me.id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }

    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        broup.removed = False
        if broup.bro_id == me.id:
            # This should reset the admin ids back to nothing for private chats.
            chat.dismiss_admin(me.id)
        broup.broup_updated = True
        # We will send a new message, so we need to set this to true
        broup.new_messages = True
        db.add(broup)

    broup_room = f"broup_{broup_id}"
    message_text = f"Bro {me.bro_name} {me.bromotion} has unblocked the Chat! 🥰"
    socket_response_chat_unblocked = {
        "broup_id": broup_id,
        "chat_unblocked": me.id,
    }
    await sio.emit(
        "chat_changed",
        socket_response_chat_unblocked,
        room=broup_room,
    )

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
    }
