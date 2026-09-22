from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import BigInteger, CheckConstraint, Column, DateTime, String, Text, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chat_room import ChatRoom


class LlmRole(SQLModel, table=True):
    """게임 Episode/시츄에이션 원본을 저장하는 모델.

    기존 ``episode_scenario``의 역할을 ``llm_role``로 통합했습니다.
    ``content``에는 Episode JSON 문자열이 저장되며, 기존 게시판형 LLM Role 데이터도
    ``episode_id``가 NULL인 상태로 계속 유지할 수 있습니다.
    """

    __tablename__ = "llm_role"
    __table_args__ = (
        CheckConstraint(
            "category IN ('user_defined', 'school', 'trip', 'club')",
            name="CHK_LLM_ROLE_CATEGORY",
        ),
        CheckConstraint(
            "status IN ('draft', 'published')",
            name="CHK_LLM_ROLE_STATUS",
        ),
        UniqueConstraint("episode_id", name="UK_LLM_ROLE_EPISODE_ID"),
    )

    lr_num: int | None = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            primary_key=True,
            autoincrement=True,
        ),
    )

    # Episode API/게임 엔진에서 사용하는 식별자. 예: EP01
    # 기존 게시판형 데이터는 NULL이어도 됩니다.
    episode_id: str | None = Field(
        default=None,
        sa_column=Column(String(20), nullable=True, index=True),
    )

    title: str | None = Field(default=None, max_length=120)
    admin_id: str | None = Field(
        default=None,
        foreign_key="admin_table.admin_id",
        max_length=20,
    )
    category: str | None = Field(default="user_defined", max_length=50)

    # Episode JSON 원본 또는 기존 LLM Role 텍스트.
    content: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )

    # 학생용 /api/episodes에 노출할지 결정합니다.
    status: str = Field(default="draft", max_length=20, index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )

    admin: Optional["Admin"] = Relationship(
        back_populates="llm_roles"
    )
    chat_rooms: list["ChatRoom"] = Relationship(
        back_populates="llm_role"
    )


class WriteLlmRole(SQLModel):
    category: Literal["user_defined", "school", "trip", "club"] | None = Field(
        default=None, max_length=50
    )
    content: str | None = Field(default=None)
