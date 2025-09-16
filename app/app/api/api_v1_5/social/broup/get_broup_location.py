from typing import Optional
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
    broup_id: int


@api_router_v1_5.post("/broup/location", status_code=200)
async def get_broup_location(
    get_broup_location_request: GetBroLocationRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    auth_token = get_auth_token(request.headers.get("Authorization"))
    if not auth_token:
        return get_failed_response("Invalid token", response, 401)
    
    # me: Optional[Bro] = await check_token(db, auth_token)
    # TODO: Add checks for validity

    broup_id = get_broup_location_request.broup_id

    chat_statement = select(Chat).where(
        Chat.id == broup_id,
    )
    results_chat = await db.execute(chat_statement)
    chat_object = results_chat.first()
    if not chat_object:
        return get_failed_response("Broup not found", response)
    chat: Chat = chat_object.Chat
    bro_locations = []
    print("going to get bro locations")
    for bro_id in chat.bro_ids:
        print(f"bro_id: {bro_id}")
        location_bro = await redis.get(f"bro:{bro_id}:broup:{broup_id}:location")
        print(f"location_bro: {location_bro}")
        if location_bro:
            lat, lng = location_bro.decode("utf-8").split(",")
            print(f"lat: {lat}, lng: {lng}")
            bro_location_entry = {
                "bro_id": bro_id,
                "lat": float(lat),
                "lng": float(lng),
            }
            bro_locations.append(bro_location_entry)
    print(f"bro_locations: {bro_locations}")
    return {
        "result": True,
        "bro_locations": bro_locations
    }
