import asyncio
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import delete

from app.config.config import settings
from app.models import UserToken

engine_sync = create_engine(settings.SYNC_DB_URL, pool_pre_ping=True, pool_size=32, max_overflow=64)


def remove_expired_tokens():
    with Session(engine_sync) as session:
        delete_expired_tokens = delete(UserToken).where(
            UserToken.refresh_token_expiration < int(time.time())
        )
        session.execute(delete_expired_tokens)
        session.commit()


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(remove_expired_tokens, trigger="cron", hour="0", minute="0")
    scheduler.start()

    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())  # Ensure an event loop is properly started
    except (KeyboardInterrupt, SystemExit):
        pass
