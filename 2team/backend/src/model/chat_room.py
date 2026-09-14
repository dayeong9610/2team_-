from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.admin import Admin
    from model.chatting import Chatting
    from model.deep_analysis import DeepAnalysis
    from model.llm_role import LlmRole


class ChatRoom(SQLModel, table=True):
    __tablename__ = "CHAT_ROOM"

    room_id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    admin_id: str = Field(foreign_key="ADMIN_TABLE.admin_id", max_length=20)
    limits: int
    status: str = Field(max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    room_requester: str = Field(max_length=50)
    lr_num: int = Field(foreign_key="LLM_ROLE.lr_num")

    admin: "Admin" = Relationship(back_populates="chat_rooms")
    llm_role: "LlmRole" = Relationship(back_populates="chat_rooms")
    chatting: list["Chatting"] = Relationship(back_populates="room")
    analyses: list["DeepAnalysis"] = Relationship(back_populates="room")
