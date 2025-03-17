from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload
from app.sockets.sockets import sio


class ChangeBromotionRequest(BaseModel):
    bromotion: str


@api_router_v1.post("/change/bromotion", status_code=200)
async def change_bromotion(
    change_bromotion_request: ChangeBromotionRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    new_bromotion = change_bromotion_request.bromotion
    bro_statement = select(Bro).where(
        func.lower(Bro.bro_name) == me.bro_name.lower(), Bro.bromotion == new_bromotion
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is not None:
        return {
            "result": False,
            "message": "Broname bromotion combination is already taken, please choose a different bromotion.",
        }

    old_bromotion = me.bromotion
    me.set_new_bromotion(new_bromotion)
    db.add(me)

    broups: List[Broup] = me.broups
    for broup in broups:
        print(f"broup {broup.serialize_no_chat}")
        chat: Chat = broup.chat
        if not chat.private:
            # For broup chats the bromotion is shown in the broup name, we want to update it
            broup_name_now = chat.broup_name
            print(f"broup_name_now {broup_name_now}")
            # Remove the first occurence from the end of the broup name
            new_broup_name = broup_name_now[::-1].replace(old_bromotion, new_bromotion, 1)
            # Reverse the string again
            new_broup_name = new_broup_name[::-1]
            chat.set_broup_name(new_broup_name)
            db.add(chat)

        chat_broups: List[Broup] = chat.chat_broups
        for chat_broup in chat_broups:
            if chat_broup.bro_id != me.id:
                chat_broup.broup_updated = True
                chat_broup.add_bro_to_update(me.id)
                db.add(chat_broup)
                # We send it specifically to the other bro, who's broup name we changed.
                bro_room = f"room_{chat_broup.bro_id}"
                socket_response = {
                    "bro_id": me.id,
                    "bromotion": new_bromotion
                }
                await sio.emit(
                    "bro_update",
                    socket_response,
                    room=bro_room,
                )
            
        broup_room = f"broup_{chat.id}"
        if not chat.private:
            socket_response = {
                "broup_id": chat.id,
                "new_broup_name": new_broup_name,
                "broup_updated": True
            }
        else:
            socket_response = {
                "broup_id": chat.id,
                "broup_updated": True
            }
        await sio.emit(
            "chat_changed",
            socket_response,
            room=broup_room,
        )

    await db.commit()

    return {
        "result": True,
        "message": new_bromotion,
    }
