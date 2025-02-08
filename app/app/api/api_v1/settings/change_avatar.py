import base64
import io
import os
import stat
from typing import Optional

from fastapi import Depends, Request, Response
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class ChangeAvatarRequest(BaseModel):
    avatar: str
    avatar_small: str


@api_router_v1.post("/change/avatar", status_code=200)
async def change_avatar(
    change_avatar_request: ChangeAvatarRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return get_failed_response("An error occurred", response)

    bro: Optional[Bro] = await check_token(db, auth_token, False)
    if not bro:
        return get_failed_response("An error occurred", response)

    new_avatar = change_avatar_request.avatar
    new_avatar_small = change_avatar_request.avatar_small

    new_avatar_pil = Image.open(io.BytesIO(base64.b64decode(new_avatar)))
    new_avatar_small_pil = Image.open(io.BytesIO(base64.b64decode(new_avatar_small)))

    # Get the file name and path
    file_folder = settings.UPLOAD_FOLDER_AVATARS
    file_name = bro.avatar_filename()
    file_name_small = bro.avatar_filename() + "_small"
    # Store the image under the same hash but without the "default".
    file_path = os.path.join(file_folder, "%s.png" % file_name)
    file_path_small = os.path.join(file_folder, "%s.png" % file_name_small)

    new_avatar_pil.save(file_path)
    new_avatar_small_pil.save(file_path_small)
    os.chmod(file_path, stat.S_IRWXO)
    os.chmod(file_path_small, stat.S_IRWXO)

    bro.set_default_avatar(False)
    db.add(bro)
    await db.commit()

    return {
        "result": True,
        "message": "success",
    }
