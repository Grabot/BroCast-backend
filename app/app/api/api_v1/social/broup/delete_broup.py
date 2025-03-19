from typing import Optional

from fastapi import Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.api_v1 import api_router_v1
from app.database import get_db
from app.models import Bro, Broup
from app.util.rest_util import get_failed_response
from app.util.util import check_token, get_auth_token
from sqlalchemy.orm import selectinload



class DeleteBroupRequest(BaseModel):
    broup_id: int


@api_router_v1.post("/broup/delete", status_code=200)
async def delete_broup(
    delete_broup_request: DeleteBroupRequest,
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

    broup_id = delete_broup_request.broup_id
    broup_statement = (
        select(Broup)
        .where(
            Broup.bro_id == me.id,
            Broup.broup_id == broup_id
        ).options(selectinload(Broup.chat))
    )
    print(f"broups_statement {broup_statement}")
    results_broup = await db.execute(broup_statement)
    print(f"results_broups {results_broup}")
    result_broup = results_broup.first()
    print(f"result_broups {result_broup}")

    if result_broup is None:
        # Broup is already gone, so we can return True
        return {
            "result": True,
        }

    broup: Broup = result_broup.Broup
    broup.deleted = True
    db.add(broup)
    await db.commit()

    return {"result": True}

