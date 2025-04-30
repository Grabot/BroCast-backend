from fastapi import Response, status
from datetime import datetime
import pytz
from fastapi import Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db
from app.models import Bro, Broup, Chat, Message
from app.util.util import remove_broup_traces
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


def get_failed_response(message, response: Response):
    # It's a failed response, but the response itself is fine
    response.status_code = status.HTTP_200_OK
    actual_response = {
        "result": False,
        "message": message,
    }
    return actual_response


async def leave_broup_me(
        me: Bro,
        broup_id: int,
        db: AsyncSession = Depends(get_db)
    ):

    broup_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.bro_id == me.id,
        )
        .options(selectinload(Broup.chat).options(selectinload(Chat.chat_broups)))
    )

    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()

    if result_broup is None:
        return {
            "result": True,
            "broup": [],
        }
    
    me_broup: Broup = result_broup.Broup
    if me_broup.removed:
        return {
            "result": False,
            "error": "Bro has already left the Broup",
        }

    chat: Chat = me_broup.chat

    if me.id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }
    broup_room = f"broup_{broup_id}"

    message_text = f"Bro {me.bro_name} {me.bromotion} has left the broup! 😭"
    if chat.private:
        message_text = f"Bro {me.bro_name} {me.bromotion} has blocked the chat! 😭"        
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

    # Send message via socket. No need for notification
    # Done before removing the bro from the broup 
    await sio.emit(
        "message_received",
        bro_message.serialize,
        room=broup_room,
    )

    # In a private chat we don't remove the id from the participants.
    # We want to keep the bro details in the chat.
    # In a regular broup we actually leave the broup including our id in the participants.
    if not chat.private:
        remove_bromotion = me.bromotion
        # In a broup the broup name is the same for all broup members
        # First find out what the new name should be.
        broup_name_now = chat.broup_name
        # Remove the first occurence from the end of the broup name
        new_broup_name = broup_name_now[::-1].replace(remove_bromotion, "", 1)
        # Reverse the string again
        new_broup_name = new_broup_name[::-1]
        chat.set_broup_name(new_broup_name)
        chat.remove_participant(me.id)
        if len(chat.bro_ids) == 0:
            await remove_broup_traces(chat, db)
            await db.commit()
            return {
                "result": True,
            }

        socket_response_chat_changed = {
            "broup_id": broup_id,
            "remove_bro_id": me.id,
            "new_broup_name": new_broup_name
        }
        if me.id in chat.bro_admin_ids:
            chat.dismiss_admin(me.id)
            if chat.bro_admin_ids == []:
                new_admin_id = chat.bro_ids[0]
                chat.add_admin(new_admin_id)

                # Find bro and add information message
                bro_statement = select(Bro).where(
                    Bro.id == new_admin_id
                )
                results = await db.execute(bro_statement)
                result = results.first()
                if result is None:
                    return {
                        "result": False,
                        "message": "Bro does not exists",
                    }
                new_admin_bro: Bro = result.Bro

                message_text = f"Bro {new_admin_bro.bro_name} {new_admin_bro.bromotion} is now admin! 👑"
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
                socket_response_chat_changed["new_admin_id"] = new_admin_id
        
        await sio.emit(
            "chat_changed",
            socket_response_chat_changed,
            room=broup_room,
        )
    
    for broup in chat.chat_broups:
        if broup.bro_id == me.id:
            broup.removed = True
            if chat.private:
                # In a private chat we re-use the admin ids to indicate who blocked the chat
                # Only this bro could possibly unblock the chat.
                chat.add_admin(me.id)
                db.add(chat)
        else:
            if chat.private:
                # In a private chat both broup objects will be removed
                # So the other bro sees that the chat is blocked.
                broup.removed = True
        broup.broup_updated = True
        db.add(broup)

    await db.commit()

    if chat.private:
        socket_response_chat_blocked = {
            "broup_id": broup_id,
            "chat_blocked": True,
        }
        await sio.emit(
            "chat_changed",
            socket_response_chat_blocked,
            room=broup_room,
        )
    return me_broup
