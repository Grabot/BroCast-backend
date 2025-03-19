from typing import Optional, List
from datetime import datetime
import pytz
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup, Chat, Message, Log
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_broup_traces
from app.util.rest_util import leave_broup_me
from app.sockets.sockets import sio
from sqlalchemy.orm import selectinload
import json


class ReportBroupRequest(BaseModel):
    broup_id: int
    broup_name: str
    report_messages: List[str]


@api_router_v1.post("/broup/report", status_code=200)
async def report_broup(
    report_broup_request: ReportBroupRequest,
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

    broup_id = report_broup_request.broup_id
    report_messages = report_broup_request.report_messages
    broup_name = report_broup_request.broup_name

    # First log the report
    log = Log(
        report_from=f"bro id: {me.id}  bro name: {me.bro_name} {me.bromotion}",
        report_broup=broup_name,
        report_broup_id=broup_id,
        messages=json.dumps(report_messages),
    )
    db.add(log)

    me_broup = await leave_broup_me(me, broup_id, db)

    # Next delete the broup
    me_broup.deleted = True
    db.add(me_broup)

    await db.commit()

    return {
        "result": True,
    }

