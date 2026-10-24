from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_broup_traces
from app.util.rest_util import leave_broup_me


class LeaveBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/leave", status_code=200)
async def remove_bro_broup(
    leave_broup_request: LeaveBroupRequest,
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

    s3_client = request.app.state.s3
    cipher = request.app.state.cipher

    broup_id = leave_broup_request.broup_id
    _ = await leave_broup_me(me, broup_id, s3_client, cipher, db)

    return {
        "result": True,
    }
