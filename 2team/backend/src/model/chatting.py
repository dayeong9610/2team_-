from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom


class ChatterEnum(str, PyEnum):
    AI = "AI"
    USER = "USER"


class Chatting(SQLModel, table=True):
    """Stage에서 발생한 USER/AI 대화 기록.

    USER 행에 Score가 연결되고, 같은 Stage의 AI 행에는 NPC 응답과 피드백을 저장합니다.
    """

    __tablename__ = "chatting"
    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "stage_id",
            "chatter",
            name="UK_CHATTING_ROOM_STAGE_CHATTER",
        ),
    )

    chat_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    room_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey(
                "chat_room.room_id",
                ondelete="CASCADE",
                onupdate="CASCADE",
            ),
            nullable=False,
            index=True,
        )
    )
    stage_id: str = Field(
        sa_column=Column(String(50), nullable=False, index=True)
    )
    chatter: ChatterEnum = Field(
        sa_column=Column(
            Enum(ChatterEnum, name="chatter_type", native_enum=True),
            nullable=False,
        )
    )

    # USER이면 사용자 답변, AI이면 NPC 응답을 저장합니다.
    content: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    # AI 행에만 교육 피드백을 저장합니다.
    feedback: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    room: "ChatRoom" = Relationship(back_populates="chatting")
