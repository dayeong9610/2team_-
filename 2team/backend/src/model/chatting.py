from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom


class Chatting(SQLModel, table=True):
    __tablename__ = "CHATTING"

    chat_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    room_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey(
                "CHAT_ROOM.room_id",
                ondelete="RESTRICT",
                onupdate="RESTRICT",
            ),
            nullable=False,
        )
    )
    chatter: str = Field(
        sa_column=Column(
            Enum("AI", "USER", name="chatter_enum"),
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False)
    )

    room: "ChatRoom" = Relationship(back_populates="chatting")
