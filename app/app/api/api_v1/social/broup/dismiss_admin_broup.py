from typing import Optional, List

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, update
import random

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload


class DismissAdminBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/dismiss_admin", status_code=200)
async def dismiss_admin_broup(
    dimsiss_admin_broup_request: DismissAdminBroupRequest,
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

    broup_id = dimsiss_admin_broup_request.broup_id
    bro_id = dimsiss_admin_broup_request.bro_id
    print(f"dimsiss_admin_broup_request {bro_id}  {broup_id}")

    # new_bro_statement = select(Bro).where(
    #     Bro.id == bro_id
    # )
    # results_bro = await db.execute(new_bro_statement)
    # result_bro = results_bro.first()
    # print("query all new bro")
    # if not result_bro:
    #     return get_failed_response("Bro not found", response)

    print("getting chat")
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)

    print("chat gotten")
    chat: Chat = chat_object.Chat
    print(f"bro Id {bro_id} admins {chat.bro_admin_ids}")
    if bro_id not in chat.bro_admin_ids and bro_id in chat.bro_ids:
        return {
            "result": False,
            "error": "Bro is not an admin",
        }
    print(f"admins then {chat.bro_admin_ids}")
    chat.dismiss_admin(bro_id)
    
    await db.commit()
    print(f"admins now {chat.bro_admin_ids}")

    broup_room = f"broup_{broup_id}"
    socket_response = {
        "broup_id": broup_id,
        "dismissed_admin_id": bro_id
    }
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    return {
        "result": True,
    }
