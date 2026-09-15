from typing import Optional
from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    episode_id: str


class SessionCreateResponse(BaseModel):
    session_id: str
    episode_id: str
    current_stage: str


class SessionResultResponse(BaseModel):
    episode_id: str

    scores: dict

    completed_stages: list[str]

    is_complete: bool


class SessionStateResponse(BaseModel):
    session_id: str

    progress: int

    episode_id: str

    current_stage: Optional[str]

    completed_stages: list[str]

    scores: dict

    is_complete: bool