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

    me: Optional[Bro] = await check_token(db, auth_token, False)
    if not me:
        return get_failed_response("An error occurred", response)

    new_bromotion = change_bromotion_request.bromotion
    bro_statement = select(Bro).where(
        func.lower(Bro.bro_name) == me.bro_name.lower(),
        Bro.bromotion == new_bromotion
    )
    results = await db.execute(bro_statement)
    result = results.first()
    if result is not None:
        return {
            "result": False,
            "message": "Broname bromotion combination is already taken, please choose a different bromotion."
        }

    me.set_new_bromotion(new_bromotion)

    broups_statement = select(Broup).where(
        Broup.bro_id == me.id,
    ).options(selectinload(Broup.chat).options(selectinload(Chat.chat_broups)))
    print(f"bromotion_statement {broups_statement}")
    results_broups = await db.execute(broups_statement)
    print(f"results_bromotions {results_broups}")
    result_broups = results_broups.all()
    print(f"result_bromotion {result_broups}")

    if result_broups is None or result_broups == []:
        return {
            "result": False,
        }

    for result_broup in result_broups:
        me_broup: Broup = result_broup.Broup
        chat: Chat = me_broup.chat
        broups: List[Broup] = chat.chat_broups
        if chat.private:
            # the broup name is my name with my new bromotion
            new_broup_name = me.bro_name + " " + new_bromotion
            # In private chats the broup name is the name of the other bro.
            # Change the broup name to include the new bromotion.
            for broup in broups:
                if broup.bro_id != me.id:
                    broup.set_broup_name(new_broup_name)
                    db.add(broup)
                    # We send it specifically to the other bro, who's broup name we changed.
                    bro_room = f"room_{broup.bro_id}"
                    socket_response = {
                        "broup_id": broup.broup_id,
                        "new_broup_name": new_broup_name
                    }
                    await sio.emit(
                        "chat_changed",
                        socket_response,
                        room=bro_room,
                    )
        else:
            print("test2")
            # TODO: for a broup the name has all the bromotions appended to it. Change it for everybody

    await db.commit()

    return {
        "result": True,
        "message": new_bromotion,
    }
