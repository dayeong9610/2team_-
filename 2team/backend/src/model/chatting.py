from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom


class Chatting(SQLModel, table=True):
    __tablename__ = "CHATTING"

    chat_id: int | None = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="CHAT_ROOM.room_id")
    chatter: str = Field(max_length=50)
    chat_content: str | None = None
    chat_emoticon: str | None = Field(default=None, max_length=255)
    chat_file: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    room: "ChatRoom" = Relationship(back_populates="chatting")
