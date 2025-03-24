from app.api.api_v1 import api_router_v1
from app.config.config import settings
from fastapi import Depends
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Log
from sqlmodel import select, delete


@api_router_v1.get("/read/logs/{password}", status_code=200)
async def test_call(
    password: str,
    db: AsyncSession = Depends(get_db),) -> dict:
    if password != settings.LOG_READ_PASSWORD:
        return {
            "result": False,
            "log_list": ["no logs"]
        }
    statement = (
        select(Log)
    )
    results = await db.execute(statement)
    result = results.all()
    if result is None or result == []:
        return {
            "result": False,
            "log_list": ["no logs"]
        }
    
    log_lines = []
    for log_line in result:
        log: Log = log_line.Log
        log_lines.append(log.serialize)
    
    return {
        "result": True,
        "log_list": log_lines
    }


@api_router_v1.get("/delete/logs/{password}/{log_id}", status_code=200)
async def test_call(
    password: str,
    log_id: int,
    db: AsyncSession = Depends(get_db),) -> dict:
    if password != settings.LOG_READ_PASSWORD:
        return {
            "result": False,
            "log_list": ["no logs"]
        }
    if log_id is None:
        return {
            "result": False,
            "log_list": ["no logs"]
        }
    statement = (
        select(Log).where(Log.id == log_id)
    )
    results = await db.execute(statement)
    result = results.first()
    if result is None:
        return {
            "result": False,
            "log_list": ["no logs"]
        }
    
    log_line: Log = result.Log
    await db.delete(log_line)
    await db.commit()
    
    return {
        "result": True,
    }
