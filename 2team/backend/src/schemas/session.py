# 학습 Session 생성·상태·결과 API에서 사용하는 스키마 모듈입니다.
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
    # 한 Stage에서 얻을 수 있는 행동 점수는 각 항목 0~3점입니다.
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
    # 여러 Stage의 점수를 누적한 전체 점수입니다.
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
    # 완료된 한 Stage의 피드백과 점수입니다.
    stage_id: str

    feedback: str

    scores: StageScores


# =========================
# Session 생성
# =========================

class SessionCreateRequest(BaseModel):
    # Session 시작에 필요한 에피소드 ID입니다.
    episode_id: str


class SessionCreateResponse(BaseModel):
    # 새로 생성된 Session의 식별자와 첫 Stage입니다.
    session_id: str

    episode_id: str

    current_stage: str


# =========================
# Session 현재 상태
# =========================

class SessionStateResponse(BaseModel):
    # 진행 중인 Session의 현재 상태와 진행률입니다.
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
    # Session 종료 후 누적 점수와 Stage별 결과입니다.
    episode_id: str

    scores: TotalScores

    stage_results: list[
        StageResultResponse
    ]

    completed_stages: list[str]

    is_complete: bool
