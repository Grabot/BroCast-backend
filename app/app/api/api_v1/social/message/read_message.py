from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Message, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.sockets.sockets import sio
import pytz


class ReadMessageRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/message/read", status_code=200)
async def message_read(
    read_message_request: ReadMessageRequest,
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

    broup_id = read_message_request.broup_id

    broups_statement = select(Broup).where(
        Broup.broup_id == broup_id
    ).options(selectinload(Broup.chat))
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if not result_broups:
        return get_failed_response("Broup not found", response)

    if result_broups is None:
        return {
            "result": False,
            "error": "Broup does not exist",
        }
    
    chat: Chat = result_broups[0].Broup.chat
    print(f"chat: {chat}")
    print(f"chat: {chat.id}")
    print(f"current message id: {chat.current_message_id}")

    last_message_read_time = datetime.now(pytz.utc).replace(tzinfo=None)
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        print(f"found broup {broup.broup_id}")
        if broup.bro_id == me.id:
            # The bro who read the message
            broup.read_messages()
            db.add(broup)
        else:
            if broup.last_message_read_time < last_message_read_time:
                print(f"last_message_read_time: {last_message_read_time}")
                last_message_read_time = broup.last_message_read_time
    
    if chat.last_message_read_time_bro < last_message_read_time:
        print("updating chat last message read time")
        # update the chat last message read time
        chat.last_message_read_time_bro = last_message_read_time
        db.add(chat)
        # emit to the broup the latests read time of the chat
        broup_room = f"broup_{broup_id}"
        await sio.emit(
            "message_read",
            {
                "broup_id": broup_id,
                "timestamp": last_message_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            },
            room=broup_room,
        )
    await db.commit()

    return {
        "result": True,
    }
