from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from app.celery_worker.tasks import task_generate_avatar
from copy import deepcopy


def add_broup_object(bro_id: int, broup_id: int, broup_update: bool, member_update: bool) -> Broup:

    broup = Broup(
        bro_id=bro_id,
        broup_id=broup_id,
        alias="",
        unread_messages=0,
        mute=False,
        deleted=False,
        removed=False,
        broup_updated=broup_update,
        new_members=member_update,
        new_avatar=True
    )
    return broup


async def create_broup_chat(
    db: AsyncSession, me: Bro, broup_name: str, bros: list, private_broup_ids: list
) -> dict:
    admins = [me.id]
    broup_colour = "%02X%02X%02X" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

    broup_name = f"{broup_name} "
    for bro in bros:
        bromotion = bro.bromotion
        broup_name = f"{broup_name}{bromotion}"

    chat = Chat(
        private=False,
        broup_name=broup_name,
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

    broup_add_me = None
    chat_serialize = chat.serialize
    for bro in bros:
        bro_id = bro.id
        print(f"test: {bro_id}")
        broup_add: Broup = add_broup_object(bro_id, broup_id, True, True)

        db.add(broup_add)
        bro_add_room = f"room_{bro_id}"

        new_broup_dict = broup_add.serialize_no_chat
        new_broup_dict["chat"] = chat_serialize
        # We only send the broup details, the channel indicates that a broup is added
        socket_response = {"broup": new_broup_dict}

        if bro_id == me.id:
            broup_add_me = deepcopy(new_broup_dict)
        else:
            print(f"bro_add_room {bro_add_room}")
            await sio.emit(
                "chat_added",
                socket_response,
                room=bro_add_room,
            )

    await db.commit()

    _ = task_generate_avatar.delay(chat.avatar_filename(), broup_id, True)

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

    bros_statement = select(Bro).where(Bro.id.in_(private_broup_ids))
    results_bros = await db.execute(bros_statement)
    result_bro = results_bros.all()

    bros = []
    for bro in result_bro:
        bros.append(bro.Bro)

    if len(bros) != len(private_broup_ids):
        return get_failed_response("An error occurred", response)

    return await create_broup_chat(db, me, broup_name, bros, private_broup_ids)
    # We return the broup without the avatar because it is being created
