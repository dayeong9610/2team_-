from datetime import datetime

from sqlalchemy import Column, DateTime, Text, UniqueConstraint, func
from sqlmodel import Field, SQLModel


class EpisodeScenario(SQLModel, table=True):
    """관리자에서 작성한 실제 게임용 Episode JSON 저장 테이블."""

    __tablename__ = "episode_scenario"
    __table_args__ = (
        UniqueConstraint("episode_id", name="UK_EPISODE_SCENARIO_EPISODE_ID"),
    )

    scenario_id: int | None = Field(default=None, primary_key=True)
    episode_id: str = Field(max_length=20, index=True)
    title: str = Field(max_length=120)
    category: str = Field(default="user_defined", max_length=40, index=True)
    scenario_json: str = Field(sa_column=Column(Text, nullable=False))
    status: str = Field(default="draft", max_length=20, index=True)
    admin_id: str | None = Field(default=None, max_length=50, index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
