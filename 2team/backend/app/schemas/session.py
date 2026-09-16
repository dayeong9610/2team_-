from typing import Optional

from pydantic import (
    BaseModel,
    Field
)


# =========================
# 점수 Schema
# =========================

# 각 Stage의 AI 평가 점수
# 각 항목은 0~3점
class StageScores(BaseModel):

    risk_awareness: int = Field(
        ge=0,
        le=3
    )

    refusal: int = Field(
        ge=0,
        le=3
    )

    help_request: int = Field(
        ge=0,
        le=3
    )


# 전체 Session 누적 점수
# 여러 Stage의 점수가 합쳐지므로
# 3점을 초과할 수 있음
class TotalScores(BaseModel):

    risk_awareness: int = Field(
        ge=0
    )

    refusal: int = Field(
        ge=0
    )

    help_request: int = Field(
        ge=0
    )


# =========================
# Stage 결과
# =========================

class StageResultResponse(BaseModel):

    stage_id: str

    feedback: str

    scores: StageScores


# =========================
# Session 생성
# =========================

class SessionCreateRequest(BaseModel):

    episode_id: str


class SessionCreateResponse(BaseModel):

    session_id: str

    episode_id: str

    current_stage: str


# =========================
# Session 현재 상태
# =========================

class SessionStateResponse(BaseModel):

    session_id: str

    episode_id: str

    current_stage: Optional[str]

    completed_stages: list[str]

    scores: TotalScores

    progress: int = Field(
        ge=0,
        le=100
    )

    is_complete: bool


# =========================
# Session 최종 결과
# =========================

class SessionResultResponse(BaseModel):

    episode_id: str

    scores: TotalScores

    stage_results: list[
        StageResultResponse
    ]

    completed_stages: list[str]

    is_complete: bool