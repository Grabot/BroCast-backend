from typing import Optional
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token

class EmojiReactionReceivedRequest(BaseModel):
    broup_id: int

@api_router_v1_5.post("/emoji_reaction/received", status_code=200)
async def send_message(
    emoji_reaction_received_request: EmojiReactionReceivedRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    
    if auth_token == "":
        return get_failed_response("An error occurred", response)

    me: Optional[Bro] = await check_token(db, auth_token)
    
    if not me:
        return get_failed_response("An error occurred", response)

    broup_id = emoji_reaction_received_request.broup_id

    broup_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
            Broup.bro_id == me.id
        )
    )

    results_broup = await db.execute(broup_statement)
    result_broup = results_broup.first()
    if result_broup is None:
        return {
            "result": False,
            "message": "Broup not found",
        }

    broup: Broup = result_broup.Broup
    broup.emoji_reactions = None
    db.add(broup)
    await db.commit()
    
    return {
        "result": True,
    }
