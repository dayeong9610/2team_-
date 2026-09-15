from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    episode_id: str
    stage_id: str
    message: str


class Scores(BaseModel):
    risk_awareness: int = Field(default=0, ge=0, le=3)
    refusal: int = Field(default=0, ge=0, le=3)
    help_request: int = Field(default=0, ge=0, le=3)


class ChatResponse(BaseModel):
    npc_response: str
    feedback: str
    scores: Scores

    next_stage: Optional[str] = None

    is_episode_complete: bool = False