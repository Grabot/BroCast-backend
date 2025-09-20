from typing import List, Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1_5 import api_router_v1_5
from app.models.chat import Chat
from app.database import get_db
from app.models.bro import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from app.sockets.sockets import redis


class GetBroLocationRequest(BaseModel):
    bro_id: int
    broup_id: int


@api_router_v1_5.post("/bro/location", status_code=200)
async def get_bro_location(
    get_bro_location_request: GetBroLocationRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if not auth_token:
        return get_failed_response("Invalid token", response, 401)
    
    bro_id = get_bro_location_request.bro_id
    broup_id = get_bro_location_request.broup_id
    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return get_failed_response("An error occurred", response)
    
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)
    
    location = await redis.get(f"bro:{bro_id}:broup:{broup_id}:location")
    if not location:
        return get_failed_response("Location not found", response)

    lat, lng = location.decode("utf-8").split(",")
    return {
        "result": True,
        "lat": float(lat),
        "lng": float(lng),
    }



class GetBrosLocationRequest(BaseModel):
    bro_ids: List[int]
    broup_id: int


@api_router_v1_5.post("/bros/location", status_code=200)
async def get_bros_location(
    get_bros_location_request: GetBrosLocationRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if not auth_token:
        return get_failed_response("Invalid token", response, 401)
    
    bro_ids = get_bros_location_request.bro_ids
    broup_id = get_bros_location_request.broup_id
    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return get_failed_response("An error occurred", response)
    
    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)
    
    bro_locations = []
    for bro_id in bro_ids:
        location_bro = await redis.get(f"bro:{bro_id}:broup:{broup_id}:location")
        if location_bro:
            lat, lng = location_bro.decode("utf-8").split(",")
            bro_location_entry = {
                "bro_id": bro_id,
                "lat": float(lat),
                "lng": float(lng),
            }
            bro_locations.append(bro_location_entry)

    return {
        "result": True,
        "bro_locations": bro_locations
    }
