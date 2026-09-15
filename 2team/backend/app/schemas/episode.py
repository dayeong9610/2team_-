from typing import Optional
from pydantic import BaseModel


class EpisodeSummary(BaseModel):
    episode_id: str
    title: str
    description: str
    total_stages: int


class StageResponse(BaseModel):
    stage_id: str
    type: Optional[str] = None
    title: str

    scene: dict

    npc_messages: list[str]

    question: str

    evaluation: dict

    next_stage: Optional[str] = None


class EpisodeDetailResponse(BaseModel):
    episode_id: str
    title: str
    description: str
    total_stages: int

    stages: list[StageResponse]