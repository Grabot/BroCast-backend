import base64
from typing import Optional
from sqlmodel import select
from pydantic import BaseModel
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Chat, Broup
from sqlalchemy.orm import selectinload
from app.util.rest_util import get_failed_response
from app.util.storage_util import avatar_key, download_avatar
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

    broup_statement = (
        select(Broup)
        .where(
            Broup.bro_id == me.id,
            Broup.broup_id == broup_id
        ).options(selectinload(Broup.chat))
    )
    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()

    if result_broup is None:
        get_failed_response("Broup not found", response)

    me_broup: Broup = result_broup.Broup
    chat: Chat = me_broup.chat

    if chat.is_default():
        file_name = chat.avatar_filename_default()
        encrypted = False
    else:
        file_name = chat.avatar_filename()
        encrypted = True

    image_bytes = download_avatar(avatar_key(file_name), encrypted=encrypted)
    if image_bytes is None:
        return get_failed_response("An error occurred", response)
    else:
        image_as_base64 = base64.encodebytes(image_bytes).decode()

        me_broup.new_avatar = False
        db.add(me_broup)
        await db.commit()

        return {
            "result": True,
            "avatar": image_as_base64,
            "is_default": chat.is_default()
        }
