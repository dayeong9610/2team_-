from pydantic import (
    BaseModel,
    Field
)


class Scores(BaseModel):

    risk_awareness: int = Field(
        default=0,
        ge=0,
        le=3
    )

    refusal: int = Field(
        default=0,
        ge=0,
        le=3
    )

    help_request: int = Field(
        default=0,
        ge=0,
        le=3
    )


class AIResponse(BaseModel):

    npc_response: str = Field(
        min_length=1,
        max_length=300
    )

    feedback: str = Field(
        min_length=1,
        max_length=500
    )

    scores: Scores