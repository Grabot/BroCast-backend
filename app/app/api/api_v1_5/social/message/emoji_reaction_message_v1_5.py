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

class EmojiReactionRequest(BaseModel):
    broup_id: int
    message_id: int
    emoji: str
    is_add: bool = True

@api_router_v1_5.post("/message/emoji_reaction", status_code=200)
async def send_message(
    emoji_reaction_request: EmojiReactionRequest,
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

    broup_id = emoji_reaction_request.broup_id
    message_id = emoji_reaction_request.message_id
    emoji = emoji_reaction_request.emoji
    is_add = emoji_reaction_request.is_add

    broups_statement = (
        select(Broup)
        .where(
            Broup.broup_id == broup_id,
            Broup.removed == False,
        )
    )

    results_broups = await db.execute(broups_statement)
    result_broups = results_broups.all()
    if result_broups is None or result_broups == []:
        return {
            "result": False,
            "message": "Broup not found",
        }
    
    for result_broup in result_broups:
        broup: Broup = result_broup.Broup
        broup.new_messages = True

        print(f"broup emoji reaction before: {broup.emoji_reactions}")
        if broup.emoji_reactions is None:
            broup.emoji_reactions = {}
        
        if is_add:
            if str(message_id) not in broup.emoji_reactions:
                broup.emoji_reactions[str(message_id)] = {}
            broup.emoji_reactions[str(message_id)][str(me.id)] = emoji

        # else:
        #     if message_id in broup.emoji_reactions and me.id in broup.emoji_reactions[message_id]:
        #         del broup.emoji_reactions[message_id][me.id]
        #         if not broup.emoji_reactions[message_id]:
        #             del broup.emoji_reactions[message_id]
        print(f"broup emoji reaction now: {broup.emoji_reactions}")
        db.add(broup)
    
    await db.commit()
    
    broup_room = f"broup_{broup_id}"
    emoji_reaction_data = {
            "broup_id": broup_id,
            "message_id": message_id,
            "emoji": emoji,
            "bro_id": me.id,
        }
    await sio.emit(
        "emoji_reaction",
        emoji_reaction_data,
        room=broup_room,
    )

    return {
        "result": True,
    }
