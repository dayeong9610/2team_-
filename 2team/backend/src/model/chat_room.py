from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chatting import Chatting
    from model.llm_role import LlmRole


class ChatRoom(SQLModel, table=True):
    """학생 한 명의 한 번의 Episode 학습 세션."""

    __tablename__ = "chat_room"

    room_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    session_id: str = Field(
        max_length=36,
        unique=True,
        index=True,
    )

    # 어떤 시츄에이션(llm_role)을 플레이한 방인지 연결합니다.
    lr_num: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey(
                "llm_role.lr_num",
                ondelete="SET NULL",
                onupdate="CASCADE",
            ),
            nullable=True,
            index=True,
        ),
    )

    # 시츄에이션 작성 관리자. 시스템 기본 JSON이면 NULL일 수 있습니다.
    admin_id: str | None = Field(
        default=None,
        sa_column=Column(
            String(20),
            ForeignKey(
                "admin_table.admin_id",
                ondelete="RESTRICT",
                onupdate="RESTRICT",
            ),
            nullable=True,
        ),
    )

    # 해당 Episode의 전체 Stage 수.
    limits: int = Field(default=0)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        )
    )

    admin: Optional["Admin"] = Relationship(
        back_populates="chat_rooms"
    )
    llm_role: Optional["LlmRole"] = Relationship(
        back_populates="chat_rooms"
    )
    chatting: list["Chatting"] = Relationship(
        back_populates="room"
    )
