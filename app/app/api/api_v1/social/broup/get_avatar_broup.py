import base64
import os
from typing import Optional
from sqlmodel import select
from pydantic import BaseModel
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class GetAvatarBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/get/avatar/broup", status_code=200)
async def get_avatar_broup(
    get_avatar_broup_request: GetAvatarBroupRequest,
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

    broup_id = get_avatar_broup_request.broup_id

    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)

    print("chat gotten")
    chat: Chat = chat_object.Chat

    file_folder = settings.UPLOAD_FOLDER_AVATARS
    if chat.is_default():
        file_name = chat.avatar_filename_default()
    else:
        file_name = chat.avatar_filename()

    file_path = os.path.join(file_folder, "%s.png" % file_name)

    if not os.path.isfile(file_path):
        return get_failed_response("An error occurred", response)
    else:
        with open(file_path, "rb") as fd:
            image_as_base64 = base64.encodebytes(fd.read()).decode()

        return {
            "result": True,
            "avatar": image_as_base64,
            "is_default": chat.is_default()
        }
