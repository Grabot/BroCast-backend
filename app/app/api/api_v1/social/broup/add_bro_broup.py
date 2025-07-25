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



class AddBroBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/add_bro", status_code=200)
async def add_bro_broup(
    add_bro_broup_request: AddBroBroupRequest,
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

    broup_id = add_bro_broup_request.broup_id
    bro_id = add_bro_broup_request.bro_id

    new_bro_broup_statement = select(Broup).where(
        Broup.broup_id == broup_id, Broup.bro_id == bro_id
    )
    results_bro_broup = await db.execute(new_bro_broup_statement)
    result_bro_broup = results_bro_broup.first()
    broup_room = f"broup_{broup_id}"
    if result_bro_broup:
        # The broup object already exits which means the bro has been here before
        # Set the values back to be part of the broup
        new_broup: Broup = result_bro_broup.Broup
        new_broup.removed = False
        new_broup.deleted = False
        new_broup.broup_updated = True
        new_broup.new_messages = True
        new_broup.unread_messages = 1
        db.add(new_broup)
    else:
        new_broup = Broup(
            bro_id=bro_id,
            broup_id=broup_id,
            alias="",
            unread_messages=0,
            mute=False,
            deleted=False,
            removed=False,
            broup_updated=True,
        )

    new_bro_statement = select(Bro).where(Bro.id == bro_id)
    results_bro = await db.execute(new_bro_statement)
    result_bro = results_bro.first()
    if not result_bro:
        return {
            "result": False,
            "message": "Bro does not exists",
        }
    new_bro_for_broup: Bro = result_bro.Bro

    broups_statement = (
        select(Broup).where(Broup.broup_id == broup_id).options(selectinload(Broup.chat))
    )
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if not result_broups:
        return {
            "result": False,
            "message": "Broup does not exists",
        }
    bro_broup: Broup = result_broups[0].Broup
    bro_chat: Chat = bro_broup.chat

    broup_name = bro_chat.get_broup_name()
    new_broup_name = broup_name + new_bro_for_broup.get_bromotion()
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if not broup.removed:
            if me.id != broup.bro_id:
                broup.broup_updated = True
                broup.add_bro_to_update(bro_id)
                broup.add_bro_avatar_to_update(bro_id)
                db.add(broup)

    bro_chat.add_participant(bro_id)
    bro_chat.set_broup_name(new_broup_name)
    new_broup.last_message_read_id = bro_chat.current_message_id - 1
    new_broup.new_messages = True
    db.add(bro_chat)

    db.add(new_broup)

    chat_serialize = bro_chat.serialize
    new_broup_dict_bro = new_broup.serialize_no_chat
    new_broup_dict_bro["chat"] = chat_serialize
    new_broup_dict_bro["chat"]["current_message_id"] = bro_chat.current_message_id - 1

    socket_response = {
        "broup_id": broup_id,
        "new_broup_name": new_broup_name,
        "new_member_id": bro_id,
    }
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    # if broup_newly_added:
    # Send the new bro the details of the broup
    bro_add_room = f"room_{bro_id}"
    socket_response = {"broup": new_broup_dict_bro}
    await sio.emit(
        "chat_added",
        socket_response,
        room=bro_add_room,
    )

    message_text = f"Bro {new_bro_for_broup.bro_name} {new_bro_for_broup.bromotion} added to the broup! Welcome! 🥰"
    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=bro_chat.current_message_id,
        body=message_text,
        text_message="",
        timestamp=datetime.now(pytz.utc).replace(tzinfo=None),
        info=True,
        data=None,
        data_type=None,
        replied_to=None,
        receive_remaining=bro_chat.bro_ids
    )
    bro_chat.current_message_id += 1
    db.add(bro_chat)
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
