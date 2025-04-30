from typing import Optional
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload
from app.sockets.sockets import sio


class BroupChangeDescriptionRequest(BaseModel):
    broup_id: int
    new_broup_description: Optional[str]


@api_router_v1.post("/broup/change_description", status_code=200)
async def broup_change_description(
    broup_change_description_request: BroupChangeDescriptionRequest,
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

    broup_id = broup_change_description_request.broup_id
    new_broup_description = broup_change_description_request.new_broup_description

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
        )
        .options(selectinload(Broup.chat))
    )
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if result_broups is None or result_broups == []:
        return {
            "result": False,
        }
    chat: Chat = result_broups[0].Broup.chat
    if chat.broup_description == new_broup_description:
        return {
            "result": False,
            "message": "Description is the same",
        }

    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        broup.broup_updated = True
        broup.new_messages = True
        db.add(broup)

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "new_broup_description": new_broup_description}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    chat.update_broup_description(new_broup_description)

    message_text = f"Bro {me.bro_name} {me.bromotion} changed the chat description! 📝"
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
