# AI가 반환해야 하는 평가 결과의 형식을 정의하는 모듈입니다.
from pydantic import (
    BaseModel,
    Field
)


class Scores(BaseModel):
    # 사용자의 안전 대응 행동을 세 가지 기준으로 0~3점 평가합니다.

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
    # NPC 대사, 교육 피드백, 점수를 묶어 반환하는 응답 형식입니다.

    npc_response: str = Field(
        min_length=1,
        max_length=300
    )

    feedback: str = Field(
        min_length=1,
        max_length=500
    )

    scores: Scores
