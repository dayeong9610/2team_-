from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chatting import Chatting
    from model.llm_role import LlmRole


class ChatRoom(SQLModel, table=True):
    __tablename__ = "chat_room"

    room_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    title: str = Field(max_length=255)
    admin_id: str = Field(
        sa_column=Column(
            String(20),
            ForeignKey(
                "admin_table.admin_id",
                ondelete="RESTRICT",
                onupdate="RESTRICT",
            ),
            nullable=False,
        )
    )
    limits: int
    status: str = Field(max_length=10)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )
    room_requester: str = Field(max_length=50)
    lr_num: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey(
                "llm_role.lr_num",
                ondelete="RESTRICT",
                onupdate="RESTRICT",
            ),
            nullable=False,
        )
    )

    admin: "Admin" = Relationship(
        back_populates="chat_rooms"
    )

    llm_role: "LlmRole" = Relationship(
        back_populates="chat_rooms"
    )
    chatting: list["Chatting"] = Relationship(back_populates="room")
