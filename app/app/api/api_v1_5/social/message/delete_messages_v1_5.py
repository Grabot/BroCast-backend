from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import attributes


class DeleteMessagesRequest(BaseModel):
    broup_id: int
    delete_message_id: int


@api_router_v1_5.post("/message/delete", status_code=200)
async def delete_messages_v1_5(
    delete_messages_request: DeleteMessagesRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return get_failed_response("An error occurred", response)

    broup_id = delete_messages_request.broup_id
    delete_message_id = delete_messages_request.delete_message_id

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
        )
    )

    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if result_broups is None or result_broups == []:
        return {
            "result": False,
            "message": "Broup not found",
        }
    
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if broup.bro_id != me.id:
            broup.new_messages = True
            if broup.message_updates is None:
                broup.message_updates = {}

            message_id_key = str(delete_message_id)
            if message_id_key not in broup.message_updates:
                broup.message_updates[message_id_key] = me.id
            attributes.flag_modified(broup, "message_updates")
            db.add(broup)

    select_statement = (
        select(Message)
        .where(
            Message.broup_id == broup_id,
            Message.message_id == delete_message_id,
        )
    )
    results_message = await db.execute(select_statement)
    result_message = results_message.first()

    broup_room = f"broup_{broup_id}"
    message_send_data = {
        "message_id": delete_message_id,
        "broup_id": broup_id,
        "deleted_by": me.id
    }
    if result_message is None:
        # It's possible that the message has already been removed.
        # We still do a socket call and later update the broup messages updates
        await db.commit()
        await sio.emit(
            "message_deleted",
            message_send_data,
            room=broup_room,
        )
        return {
            "result": False,
        }
    delete_message: Message = result_message.Message
    delete_message.delete_message_data()
    db.add(delete_message)
    await db.commit()

    await sio.emit(
        "message_deleted",
        message_send_data,
        room=broup_room,
    )

    return {"result": True}
