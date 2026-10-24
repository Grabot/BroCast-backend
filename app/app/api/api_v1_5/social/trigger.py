from typing import Optional
from fastapi import Depends, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.sockets.sockets import sio
from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Broup, Chat
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class TriggerRequest(BaseModel):
    broup_id: int
    trigger_type: str
    trigger_data: dict


@api_router_v1_5.post("/trigger", status_code=200)
async def handle_trigger(
    trigger_request: TriggerRequest,
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
    
    broup_id = trigger_request.broup_id
    trigger_type = trigger_request.trigger_type
    trigger_data = trigger_request.trigger_data
    
    # Verify the bro is part of the broup
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
            "message": "Broup not found or access denied",
        }
    
    # Broadcast the trigger to all members of the broup
    broup_room = f"broup_{broup_id}"
    
    trigger_message = {
        "broup_id": broup_id,
        "bro_id": me.id,
        "trigger_type": trigger_type,
        "trigger_data": trigger_data
    }
    
    await sio.emit("trigger_received", trigger_message, room=broup_room)
    
    return {
        "result": True,
        "message": "Trigger broadcasted successfully"
    }


class TriggerReceivedRequest(BaseModel):
    broup_id: int


@api_router_v1_5.post("/trigger/received", status_code=200)
async def trigger_received(
    trigger_received_request: TriggerReceivedRequest,
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
    
    broup_id = trigger_received_request.broup_id
    
    # Verify the bro is part of the broup
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
            "message": "Broup not found or access denied",
        }
    
    # Clear any pending triggers for this broup
    broup: Broup = result_broup.Broup
    broup.trigger_data = None
    db.add(broup)
    await db.commit()
    
    return {
        "result": True,
    }
