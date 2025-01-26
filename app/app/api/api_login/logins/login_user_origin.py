import re
from typing import Optional

from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db
from app.models import User
from sqlalchemy.orm import selectinload
import hashlib


async def login_user_origin(
    users_name: str,
    users_email: str,
    origin: int,
    db: AsyncSession = Depends(get_db),
) -> [Optional[User], bool]:
    # Some very simple pre-check to make sure the username will not be email formatted.
    if re.match(
        r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+",
        users_name,
    ):
        users_name = users_name.replace("@", "")

    # Check if the user has logged in before using this origin.
    # If that's the case it has a Row in the User database, and we log in
    hashed_email = hashlib.sha512(users_email.lower().encode("utf-8")).hexdigest()
    statement_origin = (
        select(User)
        .where(User.origin == origin)
        .where(User.email_hash == hashed_email)
        .options(selectinload(User.bros))
    )
    results_origin = await db.execute(statement_origin)
    result_user_origin = results_origin.first()

    if not result_user_origin:
        # If not than we create a new entry in the User table and then log in.
        # The last verification is to check if username is not taken
        statement_name = select(User).where(func.lower(User.username) == users_name.lower())
        results_name = await db.execute(statement_name)
        result_user_name = results_name.first()

        if not result_user_name:
            user = User(
                username=users_name, email_hash=hashed_email, password_hash="", salt="", origin=origin
            )
            db.add(user)
            await db.commit()
            return [user, True]
        else:
            # If the username is taken than we change it because we have to create the user here.
            # The user can change it later if that person really hates it.
            # We just assume that it eventually always manages to create a user.
            index = 2
            while index < 1000:
                new_user_name = users_name + "_%s" % index
                statement_name_new = select(User).where(
                    func.lower(User.username) == new_user_name.lower()
                )
                results_name_new = await db.execute(statement_name_new)
                result_user_name_name = results_name_new.first()

                if not result_user_name_name:
                    user = User(
                        username=new_user_name,
                        email_hash=hashed_email,
                        password_hash="",
                        salt="",
                        origin=origin,
                    )
                    db.add(user)
                    await db.commit()
                    return [user, True]
                else:
                    index += 1
            return [None, False]
    else:
        origin_user: User = result_user_origin.User
        return [origin_user, False]
