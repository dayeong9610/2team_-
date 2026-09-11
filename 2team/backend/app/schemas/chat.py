from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str
    episode_id: str
    stage_id: str
    message: str


class Scores(BaseModel):
    risk_awareness: int = 0
    refusal: int = 0
    help_request: int = 0


class ChatResponse(BaseModel):
    npc_response: str
    feedback: str

    scores: Scores

    next_stage: Optional[str]

    is_episode_complete: bool