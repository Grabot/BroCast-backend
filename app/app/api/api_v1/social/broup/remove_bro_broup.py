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


class RemoveBroBroupRequest(BaseModel):
    broup_id: int
    bro_id: int


@api_router_v1.post("/broup/remove_bro", status_code=200)
async def remove_bro_broup(
    remove_bro_broup_request: RemoveBroBroupRequest,
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

    broup_id = remove_bro_broup_request.broup_id
    bro_id = remove_bro_broup_request.bro_id
    print(f"remove_bro_broup_request {bro_id}  {broup_id}")

    broup_room = f"broup_{broup_id}"
    socket_response = {"broup_id": broup_id, "remove_bro_id": bro_id}
    await sio.emit(
        "chat_changed",
        socket_response,
        room=broup_room,
    )

    return {
        "result": True,
    }
