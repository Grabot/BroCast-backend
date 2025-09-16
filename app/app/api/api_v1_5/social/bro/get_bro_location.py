from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1_5 import api_router_v1_5
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
    
    # me: Optional[Bro] = await check_token(db, auth_token)
    # TODO: Add validity checks
    
    bro_id = get_bro_location_request.bro_id
    broup_id = get_bro_location_request.broup_id
    location = await redis.get(f"bro:{bro_id}:broup:{broup_id}:location")
    if not location:
        return get_failed_response("Location not found", response)

    lat, lng = location.decode("utf-8").split(",")
    return {
        "result": True,
        "lat": float(lat),
        "lng": float(lng),
    }
