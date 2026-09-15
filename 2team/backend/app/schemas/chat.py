from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1
    )

    episode_id: str = Field(
        min_length=1
    )

    stage_id: str = Field(
        min_length=1
    )

    message: str = Field(
        min_length=1,
        max_length=500
    )

    @field_validator("message")
    @classmethod
    def validate_message(
        cls,
        value: str
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Message cannot be empty"
            )

        return value


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