from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from datetime import datetime
import pytz



def add_broup(bro_id: int, broup_id: int, broup_name: str) -> Broup:
    
    broup = Broup(
        bro_id=bro_id,
        broup_id=broup_id,
        broup_name=broup_name,
        alias="",
        unread_messages=0,
        mute=False,
        is_left=False,
        removed=False
    )
    return broup

async def create_broup_chat(db: AsyncSession, me: Bro, bro_add: Bro,  private_broup_ids: list) -> dict: 
    # The broup objectc does not exist. Create it.
    admins = private_broup_ids
    broup_colour = '%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    chat = Chat(
        private=True,
        bro_ids=private_broup_ids,
        bro_admin_ids=admins,
        broup_description="",
        broup_colour=broup_colour,
        current_message_id=1,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    print(f"created chat: {chat.serialize}")

    broup_id = chat.id

    broup_name_me = bro_add.bro_name + " " + bro_add.bromotion
    broup_name_bro = me.bro_name + " " + me.bromotion

    # Create the broups. make sure the ids are in order for the array column
    new_broup_me = add_broup(me.id, broup_id, broup_name_me)
    new_broup_bro = add_broup(bro_add.id, broup_id, broup_name_bro)

    db.add(new_broup_me)
    db.add(new_broup_bro)
    await db.commit()
    # Send message to personal bro room that the bro has been added to a chat
    bro_add_room = "room_%s" % bro_add.id
    # We only send the broup details, the channel indicates that a broup is added
    socket_response = {
        "broup": new_broup_bro.serialize
    }

    await sio.emit(
        "chat_added",
        socket_response,
        room=bro_add_room,
    )

    new_broup_dict = new_broup_me.serialize_no_chat
    new_broup_dict["chat"] = chat.serialize
    return {
        "result": True,
        "broup": new_broup_dict,
    }


class AddBroRequest(BaseModel):
    bro_id: int


@api_router_v1.post("/bro/add", status_code=200)
async def add_bro(
    add_bro_request: AddBroRequest,
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

    bro_id = add_bro_request.bro_id
    bro_statement = select(Bro).where(Bro.id == bro_id)
    results_bro = await db.execute(bro_statement)
    result_bro = results_bro.first()

    if not result_bro:
        return get_failed_response("bro name or email not found", response)

    bro_add: Bro = result_bro.Bro

    if bro_add is me:
        return get_failed_response("You can't add yourself as a bro", response)

    # The private chat will be a broup object where private is true and the bro ids are the two bros
    private_broup_ids = [me.id, bro_add.id] if me.id < bro_add.id else [bro_add.id, me.id]
    broup_statement = select(Broup).where(
        Broup.bro_id == bro_id,
    ).join(Chat, Chat.id == Broup.broup_id).filter(
        Chat.private == True,
        Chat.bro_ids == private_broup_ids,
    )
    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()

    if result_broup:
        # The broup object already exists. 
        # This is possible if they are bros, or if the were bros before, 
        # but one of them unbroed the other.
        # TODO: add functionality for re-broing?
        # Already exists, indictated with `False`
        return {
            "result": False,
        }
    else:
        return await create_broup_chat(db, me, bro_add, private_broup_ids)
        # We return the broup without the avatar because it is being created




