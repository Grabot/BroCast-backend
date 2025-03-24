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
    
    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.bro_id == bro_id,
        )
        .options(selectinload(Broup.chat).options(selectinload(Chat.chat_broups)))
    )

    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.first()
    if result_broups is None:
        return {
            "result": False,
            "message": "Broup not found",
        }
    result_broup: Broup = result_broups.Broup
    chat: Chat = result_broup.chat

    if not chat.private:
        return {
            "result": False,
            "error": "This is not a private broup",
        }

    # Check if the chat was a correct private chat with both ids
    if bro_id not in chat.bro_ids or me.id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }

    for chat_broup in chat.chat_broups:
        chat_broup.removed = False
        if chat_broup.bro_id == me.id:
            # This should reset the admin ids back to nothing for private chats.
            chat.dismiss_admin(me.id)
        chat_broup.broup_updated = True
        db.add(chat_broup)

    # The client will create a new message but we need to increment the message id here as well
    chat.current_message_id += 1
    # Send a socket message to the other bro, 
    # the bro that did the unblocking will be notified via the REST call
    bro_room = f"room_{bro_id}"
    socket_response_chat_unblocked = {
        "broup_id": broup_id,
        "chat_blocked": False,
    }
    await sio.emit(
        "chat_changed",
        socket_response_chat_unblocked,
        room=bro_room,
    )

    await db.commit()

    return {
        "result": True,
    }
