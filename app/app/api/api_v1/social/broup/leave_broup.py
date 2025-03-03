from typing import Optional, List
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class LeaveBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/leave", status_code=200)
async def remove_bro_broup(
    leave_broup_request: LeaveBroupRequest,
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

    broup_id = leave_broup_request.broup_id

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
        )
        .options(selectinload(Broup.chat))
    )

    results_broups = await db.execute(broups_statement)
    print(f"results_bromotions {results_broups}")
    result_broups = results_broups.all()
    print(f"result_bromotion {result_broups}")
    if result_broups is None or result_broups == []:
        return {
            "result": False,
            "message": "Broup not found",
        }
    chat: Chat = result_broups[0].Broup.chat

    if me.id not in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro was not in the Broup",
        }
    broup_room = f"broup_{broup_id}"

    # In a private chat we don't remove the id from the participants.
    # We want to keep the bro details in the chat.
    # In a regular broup we actually leave the broup including our id in the participants.
    if not chat.private:
        remove_bromotion = me.bromotion
        # In a broup the broup name is the same for all broup members
        # First find out what the new name should be.
        broup_name_now = chat.broup_name
        print(f"broup_name_now {broup_name_now}")
        # Remove the first occurence from the end of the broup name
        new_broup_name = broup_name_now[::-1].replace(remove_bromotion, "", 1)
        # Reverse the string again
        new_broup_name = new_broup_name[::-1]
        print(f"broup_name_new {new_broup_name}")
        chat.set_broup_name(new_broup_name)
        chat.remove_participant(me.id)

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
    
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        if broup.bro_id == me.id:
            broup.removed = True
            if chat.private:
                # In a private chat we re-use the admin ids to indicate who blocked the chat
                # Only this bro could possibly unblock the chat.
                chat.add_admin(me.id)
        else:
            if chat.private:
                # In a private chat both broup objects will be removed
                # So the other bro sees that the chat is blocked.
                broup.removed = True
        broup.broup_updated = True
        db.add(broup)

    message_text = f"Bro {me.bro_name} {me.bromotion} has left the broup! 😭"
    bro_message = Message(
        sender_id=me.id,
        broup_id=broup_id,
        message_id=chat.current_message_id,
        body=message_text,
        text_message="",
        timestamp=datetime.now(pytz.utc).replace(tzinfo=None),
        info=True,
        data=None,
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

    if chat.private:
        message_text = f"Bro {me.bro_name} {me.bromotion} has blocked the chat! 😭"
        socket_response_chat_blocked = {
            "broup_id": broup_id,
            "chat_blocked": me.id,
        }
        await sio.emit(
            "chat_changed",
            socket_response_chat_blocked,
            room=broup_room,
        )


    return {
        "result": True,
    }
