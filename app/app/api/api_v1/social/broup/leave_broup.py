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
from sqlalchemy.orm import selectinload


class LeaveBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/leave", status_code=200)
async def remove_bro_broup(
    leave_broup_request: LeaveBroupRequest,
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

    broup_id = leave_broup_request.broup_id

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
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

    if me.id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }
    print("chat gotten")
    chat.remove_participant(me.id)

    if me.id in chat.bro_admin_ids:
        chat.dismiss_admin(me.id)
        if chat.bro_admin_ids == []:
            new_admin_id = chat.bro_ids[0]
            chat.add_admin(new_admin_id)
            broup_room = f"broup_{broup_id}"
            socket_response = {"broup_id": broup_id, "new_admin_id": new_admin_id}
            await sio.emit(
                "chat_changed",
                socket_response,
                room=broup_room,
            )

    remove_bromotion = me.bromotion
    # In a broup the broup name is the same for all broup members
    # First find out what the new name should be.
    broup_name_now = chat.broup_name
    print(f"broup_name_now {broup_name_now}")
    # Remove the first occurence from the end of the broup name
    new_broup_name = broup_name_now[::-1].replace(remove_bromotion, "", 1)
    # Reverse the string again
    new_broup_name = new_broup_name[::-1]
    print(f"broup_name_new {new_broup_name}")
    chat.set_broup_name(new_broup_name)
    db.add(chat)
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if broup.bro_id == me.id:
            broup.removed = True
        broup.broup_updated = True
        db.add(broup)

    await db.commit()

    broup_room = f"broup_{broup_id}"
    socket_response = {
        "broup_id": broup_id,
        "remove_bro_id": me.id,
        "new_broup_name": new_broup_name
    }
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    # TODO: Add information message?

    return {
        "result": True,
    }
