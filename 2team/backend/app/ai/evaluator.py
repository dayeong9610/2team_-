from pydantic import BaseModel, Field


class Scores(BaseModel):
    risk_awareness: int = Field(ge=0, le=3)
    refusal: int = Field(ge=0, le=3)
    help_request: int = Field(ge=0, le=3)


class AIResponse(BaseModel):
    npc_response: str
    feedback: str
    scores: Scores