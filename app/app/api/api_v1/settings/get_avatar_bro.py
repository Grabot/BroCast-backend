import base64
import os
from typing import Optional, List
from sqlmodel import select
from pydantic import BaseModel
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import sio


@api_router_v1.post("/get/avatar/me", status_code=200)
async def get_avatar_me(
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

    file_folder = settings.UPLOAD_FOLDER_AVATARS
    if me.is_default():
        file_name = me.avatar_filename_default()
    else:
        file_name = me.avatar_filename()

    file_path = os.path.join(file_folder, "%s.png" % file_name)

    if not os.path.isfile(file_path):
        return get_failed_response("An error occurred", response)
    else:
        with open(file_path, "rb") as fd:
            image_as_base64 = base64.encodebytes(fd.read()).decode()

        return {
            "result": True,
            "avatar": image_as_base64,
            "is_default": me.is_default()
        }


class GetAvatarBroRequest(BaseModel):
    bro_id: int


@api_router_v1.post("/get/avatar/bro", status_code=200)
async def get_avatar_bro(
    get_avatar_bro_request: GetAvatarBroRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token, True)
    if not me:
        return get_failed_response("An error occurred", response)

    bro_id = get_avatar_bro_request.bro_id
    bro_statement = select(Bro).where(Bro.id == bro_id)
    results_bro = await db.execute(bro_statement)
    result_bro = results_bro.first()

    if not result_bro:
        return get_failed_response("bro name or email not found", response)

    bro_avatar: Bro = result_bro.Bro

    file_folder = settings.UPLOAD_FOLDER_AVATARS
    if bro_avatar.is_default():
        file_name = bro_avatar.avatar_filename_default()
    else:
        file_name = bro_avatar.avatar_filename()

    file_path = os.path.join(file_folder, f"{file_name}.png")

    if not os.path.isfile(file_path):
        return get_failed_response("An error occurred", response)
    else:
        with open(file_path, "rb") as fd:
            image_as_base64 = base64.encodebytes(fd.read()).decode()

        # We are going to retrieve the avatar, 
        # so we can remove the bro id from the list of bros to update.
        broups: List[Broup] = me.broups
        for broup in broups:
            chat: Chat = broup.chat
            if chat.private:
                if bro_id in chat.bro_ids and me.id in chat.bro_ids:
                    # This is a private chat, the broup avatar is the same as the bro avatar
                    # So mark the broup as avatar retrieved.
                    broup.new_avatar = False
                    db.add(broup)

            if bro_id in broup.update_bros_avatar:
                broup.dismiss_bro_avatar_to_update(bro_id)
                db.add(broup)

        await db.commit()

        return {
            "result": True,
            "avatar": image_as_base64,
        }
