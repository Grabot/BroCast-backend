import asyncio
import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import delete, select

from app.config.config import settings
from app.models import BroToken, Bro

engine_sync = create_engine(settings.SYNC_DB_URL, pool_pre_ping=True, pool_size=32, max_overflow=64)


def check_fcm_token_expiration():
    with Session(engine_sync) as session:
        query = select(Bro).where(Bro.fcm_token_timestamp < int(time.time()))
        expired_bros = session.execute(query).scalars().all()

        for bro in expired_bros:
            # Delete all BroToken objects associated with the Bro
            session.execute(delete(BroToken).where(BroToken.bro_id == bro.id))
            # Clear the fcm token on the bro
            bro.fcm_token = None
            bro.fcm_token_timestamp = None
            session.add(bro)
            session.commit()

        session.commit()

        # TODO: Implement the logic to remove the expired FCM tokens


def remove_expired_tokens():
    with Session(engine_sync) as session:
        delete_expired_tokens = delete(BroToken).where(
            BroToken.refresh_token_expiration < int(time.time())
        )
        session.execute(delete_expired_tokens)
        session.commit()


async def main():
    scheduler = AsyncIOScheduler()
    # every day at midnight
    scheduler.add_job(remove_expired_tokens, trigger="cron", hour="0", minute="0")
    # once every half a year
    # scheduler.add_job(check_fcm_token_expiration, trigger="interval", seconds=15778463)
    scheduler.add_job(check_fcm_token_expiration, trigger="interval", seconds=60)
    scheduler.start()

    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())  # Ensure an event loop is properly started
    except (KeyboardInterrupt, SystemExit):
        pass
