from fastapi import (
    APIRouter,
    HTTPException
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.core.scenario_engine import get_stage

from app.services.ai_service import evaluate_response

from app.core.session_store import (
    get_session,
    add_scores,
    complete_stage
)

from app.services.ai_service import (
    evaluate_response
)


router = APIRouter(
    tags=["Chat"]
)


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
async def chat(
    request: ChatRequest
):

    # 1. Session 존재 확인
    session = get_session(
        request.session_id
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )


    # 2. 현재 진행해야 할 Stage인지 확인
    if (
        session["current_stage"]
        != request.stage_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid stage"
        )


    # 3. 이미 완료한 Stage인지 확인
    if (
        request.stage_id
        in session["completed_stages"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Stage already completed"
        )


    # 4. Scenario에서 현재 Stage 조회
    stage = get_stage(
        request.episode_id,
        request.stage_id
    )

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found"
        )

    ai_result = await evaluate_response(
        episode_id=request.episode_id,
        stage_id=request.stage_id,
        user_message=request.message,
        stage_data=stage
    )

    update_score(
        request.session_id,
        ai_result["scores"]


    # 5. AI 평가
    ai_result = await evaluate_response(
        episode_id=request.episode_id,
        stage_id=request.stage_id,
        user_message=request.message,
        stage_data=stage
    )


    # 6. AI 점수 누적
    add_scores(
        request.session_id,
        ai_result["scores"]
    )


    # 7. 다음 Stage는 Scenario가 결정
    next_stage = stage.get(
        "next_stage"
    )


    # 8. 현재 Stage 완료 처리
    complete_stage(
        session_id=request.session_id,
        stage_id=request.stage_id,
        next_stage=next_stage
    )


    # 9. Episode 종료 여부
    is_episode_complete = (
        next_stage is None
    )

    return {
        "npc_response":
            ai_result["npc_response"],

    # 10. Frontend 반환
    return ChatResponse(
        npc_response=(
            ai_result["npc_response"]
        ),

        "feedback":
            ai_result["feedback"],
        feedback=(
            ai_result["feedback"]
        ),

        "scores":
            ai_result["scores"],
        scores=(
            ai_result["scores"]
        ),

        "next_stage":
            next_stage,
        next_stage=next_stage,

        "is_episode_complete":
            is_complete
    }


# DB 없는 임시 세션 저장
sessions = {}


def update_score(
    session_id: str,
    scores: dict
):

    if session_id not in sessions:

        sessions[session_id] = {
            "risk_awareness": 0,
            "refusal": 0,
            "help_request": 0
        }

    sessions[session_id][
        "risk_awareness"
    ] += scores.get(
        "risk_awareness",
        0
    )

    sessions[session_id][
        "refusal"
    ] += scores.get(
        "refusal",
        0
    )

    sessions[session_id][
        "help_request"
    ] += scores.get(
        "help_request",
        0
        is_episode_complete=(
            is_episode_complete
        )
    )