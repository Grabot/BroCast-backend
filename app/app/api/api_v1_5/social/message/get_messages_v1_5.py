from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token


class GetMessagesRequest(BaseModel):
    broup_id: int
    last_message_id: int


@api_router_v1_5.post("/message/get", status_code=200)
async def get_messages_v1_5(
    get_messages_request: GetMessagesRequest,
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

    broup_id = get_messages_request.broup_id
    last_message_id = get_messages_request.last_message_id

    select_statement = (
        select(Message)
        .where(
            Message.broup_id == broup_id,
            Message.message_id > last_message_id,
        )
        .order_by(Message.message_id)
    )
    results_messages = await db.execute(select_statement)
    result_messages = results_messages.all()
    if result_messages is None:
        return {
            "result": False,
            "error": "No messages found",
        }

    message_list = []
    for result_message in result_messages:
        message: Message = result_message.Message
        message_list.append(message.serialize_v1_5)

    return {"result": True, "messages": message_list}
