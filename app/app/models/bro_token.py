import time
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class BroToken(SQLModel, table=True):
    """
    BroToken
    """

    __tablename__ = "BroToken"
    id: Optional[int] = Field(default=None, primary_key=True)
    bro_id: int = Field(foreign_key="Bro.id")
    access_token: str = Field(index=True)
    token_expiration: int
    refresh_token: str
    refresh_token_expiration: int

    bro: "Bro" = Relationship(back_populates="tokens")

    def refresh_is_expired(self) -> bool:
        return self.refresh_token_expiration < int(time.time())
