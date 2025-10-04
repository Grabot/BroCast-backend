from typing import Optional
from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1_5 import api_router_v1_5
from app.database import get_db
from app.models import Bro, Message
from app.util.util import check_token, get_auth_token


class GetMessageOtherDataRequest(BaseModel):
    broup_id: int
    message_id: int


@api_router_v1_5.post("/message/get/data/other/filename", status_code=200)
async def get_messages_data_other_filename_v1_5(
    get_message_other_data_request: GetMessageOtherDataRequest,
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

    broup_id = get_message_other_data_request.broup_id
    message_id = get_message_other_data_request.message_id

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
    
    message_with_data_and_extension: Message = result_message.Message
    file_path_message = message_with_data_and_extension.data
    if not file_path_message:
        return Response(
            content="Message data could not be retrieved",
            media_type="text/plain",
            status_code=500
        )

    path_split = file_path_message.split("___")
    original_file_path = path_split[-1]
    if isinstance(original_file_path, list):
        original_filename = original_file_path.join("")
    else:
        original_filename = original_file_path

    return Response(
            content=original_filename,
            media_type="text/plain",
            status_code=200
        )
