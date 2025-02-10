from datetime import datetime
import pytz
from fastapi import Depends, Response
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload
from app.models import Broup, Chat, Bro
from app.util.rest_util import get_failed_response


async def reading_messages(
    db: AsyncSession,
    response: Response,
    me: Bro,
    broup_id: int,
):
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

    last_message_read_time = datetime.now(pytz.utc).replace(tzinfo=None)
    print(f"time indicator: {last_message_read_time}")
    for broup_object in result_broups:
        broup: Broup = broup_object.Broup
        if broup.bro_id == me.id:
            # The bro who read the message
            broup.read_messages(last_message_read_time)
            print(f"bro {me.id} read message. Last read time: {broup.last_message_read_time}")
            db.add(broup)
        else:
            if broup.last_message_read_time < last_message_read_time:
                print(f"last_message_read_time: {last_message_read_time}")
                last_message_read_time = broup.last_message_read_time
            print(f"Last read time (should be lower): {broup.last_message_read_time}")
            print(f"last_message_read_time now: {last_message_read_time}")
    
    print(f"chat last message read time before: {chat.last_message_read_time_bro}")
    if chat.last_message_read_time_bro <= last_message_read_time:
        print("updating chat last message read time")
        # update the chat last message read time
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
                "timestamp": last_message_read_time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            },
            room=broup_room,
        )
    await db.commit()
