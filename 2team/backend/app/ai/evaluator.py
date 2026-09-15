from pydantic import BaseModel, Field
#backend/app/ai/evaluator.py → LLM 출력 검증
#backend/app/schemas/chat.py → Backend ↔ Frontend API 검증

class Scores(BaseModel):
    risk_awareness: int = Field(default=0, ge=0, le=3)
    refusal: int = Field(default=0, ge=0, le=3)
    help_request: int = Field(default=0, ge=0, le=3)


class AIResponse(BaseModel):
    npc_response: str
    feedback: str
    scores: Scores