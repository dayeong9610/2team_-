from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


class DialogueMessage(BaseModel):

    speaker: str

    text: str


class StageResponse(BaseModel):

    stage_id: str

    stage_number: int

    title: str

    type: str

    location: str

    description: str

    messages: list[
        DialogueMessage
    ]

    question: str

    evaluation_axis: str

    evaluation_criteria: list[str]

    next_stage: Optional[str] = None


class EpisodeSummary(BaseModel):

    episode_id: str

    title: str

    description: str

    total_stages: int


class EpisodeDetailResponse(BaseModel):

    episode_id: str

    title: str

    description: str

    total_stages: int

    stages: list[
        StageResponse
    ]