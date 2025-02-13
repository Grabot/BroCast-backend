from typing import Optional, List

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



def add_broup_object(bro_id: int, broup_id: int, broup_name: str, broup_update: bool, member_update: bool) -> Broup:
    
    broup = Broup(
        bro_id=bro_id,
        broup_id=broup_id,
        broup_name=broup_name,
        alias="",
        unread_messages=0,
        mute=False,
        is_left=False,
        removed=False,
        broup_updated=broup_update,
        new_members=member_update,
    )
    return broup

async def create_broup_chat(db: AsyncSession, me: Bro, broup_name: str, private_broup_ids: list) -> dict:
    admins = [me.id]
    broup_colour = '%02X%02X%02X' % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    chat = Chat(
        private=False,
        bro_ids=private_broup_ids,
        bro_admin_ids=admins,
        broup_description="",
        broup_colour=broup_colour,
        current_message_id=1,
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    broup_id = chat.id
    
    chat_serialize = chat.serialize
    broup_add_me = None
    for bro_id in private_broup_ids:
        print(f"test: {bro_id}")
        broup_add = add_broup_object(bro_id, broup_id, broup_name, True, True)

        db.add(broup_add)
        bro_add_room = f"room_{bro_id}"

        new_broup_dict = broup_add.serialize_no_chat
        new_broup_dict["chat"] = chat_serialize
        # We only send the broup details, the channel indicates that a broup is added
        socket_response = {
            "broup": new_broup_dict
        }

        if bro_id == me.id:
            broup_add_me = new_broup_dict
        else:
            print(f"bro_add_room {bro_add_room}")
            await sio.emit(
                "chat_added",
                socket_response,
                room=bro_add_room,
            )
        
    await db.commit()

    return {
        "result": True,
        "broup": broup_add_me,
    }


class AddBroupRequest(BaseModel):
    bro_ids: List[int]
    broup_name: str


@api_router_v1.post("/broup/add", status_code=200)
async def add_broup(
    add_broup_request: AddBroupRequest,
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

    bro_ids = add_broup_request.bro_ids
    broup_name = add_broup_request.broup_name
    print(f"add_broup_request {bro_ids}")
    
    # The private chat will be a broup object where private is true and the bro ids are the two bros")
    private_broup_ids = [me.id] + bro_ids
    print(f"before sort private_broup_ids {private_broup_ids}")
    private_broup_ids.sort()
    print(f"after sort private_broup_ids {private_broup_ids}")

    return await create_broup_chat(db, me, broup_name, private_broup_ids)
    # We return the broup without the avatar because it is being created




