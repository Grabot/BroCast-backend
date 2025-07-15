from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_message_data
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class RemoveBroBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/remove_bro", status_code=200)
async def remove_bro_broup(
    remove_bro_broup_request: RemoveBroBroupRequest,
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

    broup_id = remove_bro_broup_request.broup_id
    bro_id = remove_bro_broup_request.bro_id

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
    remove_bro: Bro = result.Bro

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
        )
        .options(selectinload(Broup.chat))
    )

    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if result_broups is None or result_broups == []:
        return {
            "result": False,
            "message": "Broup not found",
        }
    chat: Chat = result_broups[0].Broup.chat

    broup_room = f"broup_{broup_id}"
    message_text = f"Bro {me.bro_name} {me.bromotion} has removed bro {remove_bro.bro_name} {remove_bro.bromotion}! 😢"
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
    # Send message via socket. No need for notification
    await sio.emit(
        "message_received",
        bro_message.serialize,
        room=broup_room,
    )
    
    if bro_id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }
    chat.remove_participant(bro_id)

    remove_bromotion = remove_bro.bromotion
    # In a broup the broup name is the same for all broup members
    # First find out what the new name should be.
    broup_name_now = chat.broup_name
    # Remove the first occurence from the end of the broup name
    new_broup_name = broup_name_now[::-1].replace(remove_bromotion, "", 1)
    # Reverse the string again
    new_broup_name = new_broup_name[::-1]
    chat.set_broup_name(new_broup_name)
    db.add(chat)
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if broup.bro_id == bro_id:
            broup.removed = True
        broup.broup_updated = True
        db.add(broup)

    # Remove the bro from the `receive` indicator on the messages
    select_messages_statement = (
        select(Message)
        .where(Message.broup_id == broup_id)
    )
    results_messages = await db.execute(select_messages_statement)
    result_messages = results_messages.all()
    if result_messages is None or result_messages == []:
        return {
            "result": False,
            "error": "No messages found",
        }

    for result_message in result_messages:
        message: Message = result_message.Message

        message.bro_received_message(bro_id)
        if message.received_by_all():
            if message.data:
                remove_message_data(message.data, message.data_type)
            await db.delete(message)

    socket_response = {
        "broup_id": broup_id,
        "remove_bro_id": bro_id,
        "new_broup_name": new_broup_name
    }
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    await db.commit()

    return {
        "result": True,
    }
