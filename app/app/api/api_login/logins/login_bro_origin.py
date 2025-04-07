import re
from typing import Optional
import random
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db
from app.models import Bro, Broup
from sqlalchemy.orm import selectinload
import hashlib


possible_bro_emojis = [
    "😂", "❤️", "😍", "😊", "😄", "🎉", "💕", "🌟", "✨", "🌈",
    "🌞", "🤤", "🥳", "😛", "😗", "🍀", "🌹", "🌷", "🤣", "🥰",
    "😚", "🥵", "🌠", "❣️", "🔥", "😘", "👀", "🙏", "🫶", "🥹", 
    "😌", "😜", "😝", "😬", "🤯", "🤩", "🤪", "🤗", "🤫", "🤭",
    "🤠", "😇", "😈", "👽", "👾", "😉", "🥸", "😎", "🐱", "🌝",
    "🤖", "🎃", "😺", "😸", "😹", "😻", "😼", "😽", "🎊", "🏆",
    "☀️", "🌙", "🥇", "🩷", "💓", "❤️‍🔥", "🩵", "💙", "💚", "💛",
    "🧡", "💞", "💗", "💖", 
]


async def login_bro_origin(
    bro_name: str,
    bro_email: str,
    origin: int,
    db: AsyncSession = Depends(get_db),
) -> [Optional[Bro], bool]:
    # Some very simple pre-check to make sure the broname will not be email formatted.
    if re.match(
        r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+",
        bro_name,
    ):
        bro_name = bro_name.replace("@", "")

    # Check if the bro has logged in before using this origin.
    # If that's the case it has a Row in the Bro database, and we log in
    hashed_email = hashlib.sha512(bro_email.lower().encode("utf-8")).hexdigest()
    statement_origin = (
        select(Bro)
        .where(Bro.origin == origin)
        .where(Bro.email_hash == hashed_email)
        .options(selectinload(Bro.broups).options(selectinload(Broup.chat)))
    )
    results_origin = await db.execute(statement_origin)
    result_bro_origin = results_origin.first()

    if not result_bro_origin:
        # If not than we create a new entry in the Bro table and then log in.
        # The last verification is to check if broname is not taken
        random.shuffle(possible_bro_emojis)
        chosen_bro_bromotion = possible_bro_emojis[0]
        statement_name = select(Bro).where(
            func.lower(Bro.bro_name) == bro_name.lower(),
            Bro.bromotion == chosen_bro_bromotion
        )
        results_name = await db.execute(statement_name)
        result_bro_name = results_name.first()

        if not result_bro_name:
            bro = Bro(
                bro_name=bro_name, bromotion=chosen_bro_bromotion, email_hash=hashed_email, password_hash="", salt="", origin=origin
            )
            db.add(bro)
            await db.commit()
            return [bro, True]
        else:
            # If the broname and random bromotion is taken than we change it 
            # because we have to create the bro here.
            # The bro can change it later if that person really hates it.
            # We just assume that it eventually always manages to create a bro.
            new_bro_name = bro_name
            index = 2
            while index < 1000:
                for chosen_bro_bromotion in possible_bro_emojis:
                    statement_name_new = select(Bro).where(
                        func.lower(Bro.bro_name) == new_bro_name.lower(),
                        Bro.bromotion == chosen_bro_bromotion
                    )
                    results_name_new = await db.execute(statement_name_new)
                    result_bro_name_name = results_name_new.first()

                    if not result_bro_name_name:
                        bro = Bro(
                            bro_name=new_bro_name,
                            bromotion=chosen_bro_bromotion,
                            email_hash=hashed_email,
                            password_hash="",
                            salt="",
                            origin=origin,
                        )
                        db.add(bro)
                        await db.commit()
                        return [bro, True]
                    else:
                        continue
                # If we get here, it means that the random bromotions are all taken.
                # Now we will try to change the broname.
                new_bro_name = f"{bro_name}_{index}"
                index += 1
            return [None, False]
    else:
        origin_bro: Bro = result_bro_origin.Bro
        return [origin_bro, False]
