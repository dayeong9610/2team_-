from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chat_room import ChatRoom


class LlmRole(SQLModel, table=True):
    __tablename__ = "LLM_ROLE"

    lr_num: int | None = Field(default=None, primary_key=True)
    admin_id: str | None = Field(default=None, foreign_key="ADMIN_TABLE.admin_id", max_length=20)
    category: str | None = Field(default=None, max_length=50)
    content: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    admin: Optional["Admin"] = Relationship(back_populates="llm_roles")
    chat_rooms: list["ChatRoom"] = Relationship(back_populates="llm_role")


class WriteLlmRole(SQLModel):
    category: str | None = Field(default=None, max_length=50)
    content: str | None = None
