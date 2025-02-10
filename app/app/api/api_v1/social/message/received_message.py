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
import pytz


class ReceievedMessageRequest(BaseModel):
    broup_id: int
    message_id: int


@api_router_v1.post("/message/received", status_code=200)
async def message_received(
    receieved_message_request: ReceievedMessageRequest,
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

    print(f"receiving indication of bro {me.id}: {me.bro_name} {me.bromotion}")
    broup_id = receieved_message_request.broup_id
    message_id = receieved_message_request.message_id

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
    if chat.current_message_id != message_id+1:
         # The `message_received` function only happens right after a message is send
         # and immediatly received by another bro. This should not happen but check anyway.
         # If these id's do not match up we just ignore it.
        return {
            "result": False,
        }
    last_message_received_time = datetime.now(pytz.utc).replace(tzinfo=None)
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        if broup.bro_id == me.id:
            # The bro who received the message
            # If the bro has new messages we can't update the received time yet
            # The bro first needs to retrieve all messages 
            # before the last received time can be updated
            if broup.new_messages == 0:
                broup.update_last_message_received()
                print(f"bro {me.id} received message. Last read time: {broup.last_message_read_time}")
                db.add(broup)
        else:
            if broup.last_message_received_time < last_message_received_time:
                print(f"last_message_received_time: {last_message_received_time}")
                last_message_received_time = broup.last_message_received_time
            print(f"Last read time other bro: {broup.last_message_read_time}")
    
    if chat.last_message_received_time_bro < last_message_received_time:
        # update the chat last message read time
        chat.last_message_received_time_bro = last_message_received_time
        db.add(chat)
        print(f"current last read time after receiving {chat.last_message_read_time_bro}")
        # Now check if there are messages that can be removed based on the timestamp
        messages_statement = select(Message).where(
            Message.broup_id == broup_id,
            Message.timestamp <= last_message_received_time
        )
        results_messages = await db.execute(messages_statement)
        result_messages = results_messages.all()
        if result_messages:
            for result_message in result_messages:
                print(f"message id: {message_id} ")
                message: Message = result_message.Message
                print(f"remove message: {message.body}")
                await db.delete(message)
    await db.commit()

    return {
        "result": True,
    }
