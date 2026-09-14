from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.chat_room import ChatRoom


class DeepAnalysis(SQLModel, table=True):
    __tablename__ = "DEEP_ANALYSIS"

    analysis_id: str = Field(primary_key=True, max_length=36)
    room_id: int = Field(foreign_key="CHAT_ROOM.room_id")
    dl_model: str = Field(max_length=100)
    analysis_result: str
    drug_risk_score: Decimal = Field(sa_column=Column(DECIMAL(18, 3), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    room: "ChatRoom" = Relationship(back_populates="analyses")
