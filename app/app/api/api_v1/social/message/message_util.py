from datetime import datetime, timedelta
import pytz
from fastapi import Depends, Response
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload
from app.models import Broup, Chat, Bro, Message
from app.util.rest_util import get_failed_response
from copy import deepcopy


async def reading_messages(
    db: AsyncSession,
    response: Response,
    me: Bro,
    broup_id: int,
):
    broups_statement = select(Broup).where(Broup.broup_id == broup_id)
    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if not result_broups:
        return get_failed_response("Broup not found", response)

    current_read_time = datetime.now(pytz.utc).replace(tzinfo=None)
    last_message_read_time = deepcopy(current_read_time)
    last_message_received_time = deepcopy(current_read_time)
    print(f"time indicator: {last_message_read_time}")
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        if broup.bro_id == me.id:
            # The bro who read the message
            broup.read_messages(current_read_time)
            print(f"bro {me.id} read message. Last read time: {broup.last_message_read_time}")
            db.add(broup)
        else:
            if broup.last_message_read_time < last_message_read_time:
                print(f"last_message_read_time: {last_message_read_time}")
                last_message_read_time = broup.last_message_read_time
            if broup.last_message_received_time < last_message_received_time:
                last_message_received_time = broup.last_message_received_time

    await db.commit()
    # We retrieve and quickly update the chat object
    # This is to avoid concurrency issues
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_objects = results_chat.first()
    if chat_objects is None:
        return {
            "result": False,
            "error": "Chat does not exist",
        }
    chat: Chat = chat_objects.Chat
    print(f"chat last message read time before: {chat.last_message_read_time_bro}")
    if chat.last_message_read_time_bro <= last_message_read_time:
        print("updating chat last message read time")
        # update the chat last message read time
        # We add 1 miliseconds in case that 2 bros read it at the same time. It will update
        # The chat object but maybe some issue arrises that the message is not marked as read
        # Because it only emits the wrong timestamp. Some small delta added to it should fix it.
        last_message_read_time = last_message_read_time + timedelta(milliseconds=2)
        chat.last_message_read_time_bro = last_message_read_time
        print(f"chat last message read time after: {chat.last_message_read_time_bro}")
        db.add(chat)
        # emit to the broup the latests read time of the chat
        broup_room = f"broup_{broup_id}"
        print(f"emitting timestamp {last_message_read_time}")
        await sio.emit(
            "message_read",
            {
                "broup_id": broup_id,
                "timestamp": last_message_read_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            },
            room=broup_room,
        )
    if chat.last_message_received_time_bro < last_message_received_time:
        # update the chat last message read time
        chat.last_message_received_time_bro = last_message_received_time
        db.add(chat)
        print(f"current last read time after receiving {chat.last_message_read_time_bro}")
        # Now check if there are messages that can be removed based on the timestamp
        messages_statement = select(Message).where(
            Message.broup_id == broup_id, Message.timestamp <= last_message_received_time
        )
        results_messages = await db.execute(messages_statement)
        result_messages = results_messages.all()
        if result_messages:
            for result_message in result_messages:
                message: Message = result_message.Message
                print(f"remove message: {message.body}")
                await db.delete(message)
    await db.commit()
