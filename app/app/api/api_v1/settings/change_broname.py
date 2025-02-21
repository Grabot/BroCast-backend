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
from app.sockets.sockets import sio


class ChangeBronameRequest(BaseModel):
    broname: str


@api_router_v1.post("/change/broname", status_code=200)
async def change_broname(
    change_broname_request: ChangeBronameRequest,
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

    new_broname = change_broname_request.broname
    bro_statement = select(Bro).where(
        func.lower(Bro.bro_name) == new_broname.lower(),
        Bro.bromotion == me.bromotion
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is not None:
        return get_failed_response(
            "Bro name bromotion combination is already taken, please choose a different one.", response
        )

    me.set_new_broname(new_broname)
    db.add(me)
    broups: List[Broup] = me.broups
    for broup in broups:
        print(f"broup {broup.serialize_no_chat}")
        chat: Chat = broup.chat
        chat_broups: List[Broup] = chat.chat_broups
        for chat_broup in chat_broups:
            if chat_broup.bro_id != me.id:
                chat_broup.broup_updated = True
                chat_broup.add_bro_to_update(me.id)
                db.add(chat_broup)
                if chat.private:
                    # We send it specifically to the other bro, who's broup name we changed.
                    bro_room = f"room_{chat_broup.bro_id}"
                    socket_response = {
                        "bro_id": me.id,
                        "broname": new_broname
                    }
                    await sio.emit(
                        "bro_update",
                        socket_response,
                        room=bro_room,
                    )
            
        broup_room = f"broup_{chat.id}"
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

    # TODO: update message?
    return {
        "result": True,
        "message": new_broname,
    }
