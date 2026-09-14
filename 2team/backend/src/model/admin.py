from datetime import datetime
from typing import TYPE_CHECKING, List

from pydantic import BaseModel

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom
    from model.llm_role import LlmRole


class Admin(SQLModel, table=True):
    __tablename__ = "ADMIN_TABLE"

    admin_id: str = Field(primary_key=True, max_length=20)
    admin_pw: str = Field(max_length=255)
    teacher_num: int
    enabled: int = Field(default=1, ge=0, le=1)
    admin_name: str = Field(max_length=100)
    contact: str = Field(max_length=14)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    llm_roles: List["LlmRole"] = Relationship(back_populates="admin")
    chat_rooms: List["ChatRoom"] = Relationship(back_populates="admin")


class AdminSignIn(SQLModel):
    admin_id: str
    admin_pw: str


class AdminSignUp(SQLModel):
    admin_id: str = Field(max_length=20)
    admin_pw: str = Field(max_length=255)
    teacher_num: int
    admin_name: str = Field(max_length=100)
    contact: str = Field(max_length=14)


class TokenResponse(BaseModel):
    access_token : str
    token_type : str

