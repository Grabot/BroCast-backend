from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token, remove_message_data


class GetMessageDataRequest(BaseModel):
    broup_id: int
    message_id: int


@api_router_v1_5.post("/message/get/data", status_code=200)
async def get_messages_v1_5(
    get_message_data_request: GetMessageDataRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Response:
    auth_token = get_auth_token(request.headers.get("Authorization"))

    if auth_token == "":
        return Response(
            content="An error occurred",
            media_type="text/plain",
            status_code=500
        )

    me: Optional[Bro] = await check_token(db, auth_token)
    if not me:
        return Response(
            content="An error occurred",
            media_type="text/plain",
            status_code=500
        )

    broup_id = get_message_data_request.broup_id
    message_id = get_message_data_request.message_id

    print("going to query the message")
    select_statement = (
        select(Message)
        .where(
            Message.broup_id == broup_id,
            Message.message_id == message_id,
        )
        .order_by(Message.message_id)
    )
    results_message = await db.execute(select_statement)
    result_message = results_message.first()
    if result_message is None:
        return Response(
            content="Message can not be found",
            media_type="text/plain",
            status_code=500
        )
    print("message queried and retrieving data.")
    
    message_with_data: Message = result_message.Message
    data_bytes = message_with_data.get_message_image_data_v1_5_data()
    if data_bytes is None:
        return Response(
            content="Message data could not be retrieved",
            media_type="text/plain",
            status_code=500
        )

    message_with_data.bro_received_message(me.id)
    if message_with_data.received_by_all():
        if message_with_data.data:
            remove_message_data(message_with_data.data, message_with_data.data_type)
        await db.delete(message_with_data)

    await db.commit()
        
    print("sending the bytes")
    # TODO: test het.
    return Response(
        content=data_bytes,
        media_type="application/octet-stream"
    )
