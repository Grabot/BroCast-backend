"""One-shot migration of disk avatars to S3.

Run once after deploying the S3 avatar handling: with the staged
``static/uploads/avatars`` files present on the pod (kubectl cp), POST this
endpoint to upload every bro/broup avatar to S3. Idempotent: keys that
already exist are skipped, so re-running is safe.

Missing custom avatars (no S3 key, no disk file) are reported, not invented:
those users can re-upload through the app.
"""

import os
from io import BytesIO

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.config.config import settings
from app.database import get_db
from app.models import Bro, Chat
from app.util.avatar.generate_avatar import generate_avatar
from app.util.storage_util import (
    avatar_exists,
    avatar_key,
    ensure_bucket,
    upload_avatar,
)


def _ensure_key(
    file_name: str,
    encrypted: bool,
    stats: dict,
    owner: str,
    generate_base: str | None = None,
) -> None:
    key = avatar_key(file_name)
    if avatar_exists(key):
        stats["skipped"] += 1
        return
    disk_path = os.path.join(settings.UPLOAD_FOLDER_AVATARS, f"{file_name}.png")
    if os.path.isfile(disk_path):
        with open(disk_path, "rb") as handle:
            upload_avatar(handle.read(), key, encrypted=encrypted)
        stats["uploaded"] += 1
    elif generate_base is not None:
        buffer = BytesIO()
        generate_avatar(generate_base).save(buffer, format="PNG")
        upload_avatar(buffer.getvalue(), key, encrypted=encrypted)
        stats["generated"] += 1
    else:
        stats["missing"].append(owner)


@api_router_v1.post("/admin/migrate_avatars/{password}", status_code=200)
async def migrate_avatars(
    password: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    if password != settings.LOG_READ_PASSWORD:
        return {"result": False}
    ensure_bucket()
    stats: dict = {
        "bros": 0,
        "chats": 0,
        "uploaded": 0,
        "generated": 0,
        "skipped": 0,
        "missing": [],
    }
    bros = (await db.execute(select(Bro))).scalars().all()
    for bro in bros:
        stats["bros"] += 1
        _ensure_key(
            bro.avatar_filename_default(),
            False,
            stats,
            f"bro:{bro.id}",
            generate_base=bro.avatar_filename(),
        )
        if not bro.default_avatar:
            _ensure_key(bro.avatar_filename(), True, stats, f"bro:{bro.id}")
    chats = (await db.execute(select(Chat))).scalars().all()
    for chat in chats:
        stats["chats"] += 1
        _ensure_key(
            chat.avatar_filename_default(),
            False,
            stats,
            f"chat:{chat.id}",
            generate_base=chat.avatar_filename(),
        )
        if not chat.default_avatar:
            _ensure_key(chat.avatar_filename(), True, stats, f"chat:{chat.id}")
    return {"result": True, **stats}
