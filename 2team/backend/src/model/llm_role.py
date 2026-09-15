from datetime import datetime
from typing import TYPE_CHECKING, Optional, Literal

from sqlalchemy import BigInteger, Column, CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chat_room import ChatRoom


class LlmRole(SQLModel, table=True):
    __tablename__ = "LLM_ROLE"
    __table_args__ = (
        CheckConstraint(
            "category = 'user_defined' OR category = 'school' OR category = 'trip'",
            name="CHK_LLM_ROLE_CATEGORY",
        ),
    )

    lr_num: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        ),
    )
    title: str | None = Field(default=None, max_length=30)
    admin_id: str | None = Field(default=None, foreign_key="ADMIN_TABLE.admin_id", max_length=20)
    category: str | None = Field(default=None, max_length=50)  # 여기는 str로 유지
    content: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    admin: Optional["Admin"] = Relationship(back_populates="llm_roles")
    chat_rooms: list["ChatRoom"] = Relationship(back_populates="llm_role")


class WriteLlmRole(SQLModel):
    # table=True가 아니므로 Literal 사용 가능 → 요청 검증에 활용
    category: Literal["user_defined", "school", "trip"] | None = Field(default=None, max_length=50)
    content: str | None = None