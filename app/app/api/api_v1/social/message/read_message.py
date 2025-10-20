from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Chat, Broup, Message
from sqlalchemy.orm import selectinload
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_message_data

class ReadMessageRequest(BaseModel):
    broup_id: int
    last_message_read_id: int

@api_router_v1.post("/message/read", status_code=200)
async def message_read(
    read_message_request: ReadMessageRequest,
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

    broup_id = read_message_request.broup_id
    last_message_read_id = read_message_request.last_message_read_id

    broup_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.bro_id == me.id,
        )
        .with_for_update(of=Broup)
    )

    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()
    if result_broup is None:
        return {
            "result": False,
            "message": "Broup not found",
        }
    
    broup_me: Broup = result_broup.Broup
    broup_me.last_message_read_id = last_message_read_id
    broup_me.unread_messages = 0
    broup_me.new_messages = False
    db.add(broup_me)
    await db.commit()
    
    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
        )
        .options(selectinload(Broup.chat))
    )
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if result_broups is None or result_broups == []:
        return {
            "result": False,
        }
    
    lowest_last_message_read_id = last_message_read_id
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if broup.last_message_read_id < lowest_last_message_read_id:
            lowest_last_message_read_id = broup.last_message_read_id

    chat: Chat = result_broups[0].Broup.chat
    if chat.last_message_read_id_chat < lowest_last_message_read_id:
        chat.last_message_read_id_chat = lowest_last_message_read_id
        db.add(chat)

        room = f"broup_{broup_id}"
        socket_response = {
            "last_message_read_id": lowest_last_message_read_id,
            "broup_id": broup_id,
        }
        await sio.emit(
            "message_read",
            socket_response,
            room=room,
        )

    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        broup.new_messages = True
        db.add(broup)

    return {
        "result": True,
    }
