from typing import Optional

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


class BroupChangeColourRequest(BaseModel):
    broup_id: int
    new_broup_colour: str


@api_router_v1.post("/broup/change_colour", status_code=200)
async def broup_change_colour(
    broup_change_colour_request: BroupChangeColourRequest,
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

    broup_id = broup_change_colour_request.broup_id
    new_broup_colour = broup_change_colour_request.new_broup_colour

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
        )
        .options(selectinload(Broup.chat))
    )
    print(f"broups_statement {broups_statement}")
    results_broups = await db.execute(broups_statement)
    print(f"results_broups {results_broups}")
    result_broups = results_broups.all()
    print(f"result_broups {result_broups}")
    if result_broups is None or result_broups == []:
        return {
            "result": False,
        }

    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        broup.set_updated()
        db.add(broup)
        print(f"adding borup {broup.serialize}")

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "new_broup_colour": new_broup_colour}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    chat: Chat = result_broups[0].Broup.chat
    chat.set_broup_colour(new_broup_colour)
    db.add(chat)

    # TODO: Add information message to chat

    await db.commit()
    return {
        "result": True,
    }
