# 사용자 답변을 평가하고 다음 Stage로 진행시키는 API 모듈입니다.
import asyncio

from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from schemas.chat import (
    ChatRequest,
    ChatResponse
)

from core.scenario_engine import (
    get_stage
)

from core.session_store import (
    session_store
)

from services.fallback_service import (
    build_fallback_result
)
from ai.safety import (
    is_fallback_response_meaningful
)

from core.flow_trace import (
    trace_flow,
    trace_db_candidate,
)


router = APIRouter(
    tags=["Chat"]
)

FILE = "backend/src/routes/chat.py"


# =====================================================================
# DB 담당 참고
# ---------------------------------------------------------------------
# POST /api/chat -> chat()
#
# 프론트에서 들어오는 값
#   session_id / episode_id / stage_id / message
#
# AI 평가 후 만들어지는 값
#   npc_response / feedback / scores / next_stage / 완료 여부
#
# 현재는 아래 결과를 DB에 넣지 않고 core/session_store.py 메모리에만 저장합니다.
# [DB-CANDIDATE][SAVE_STAGE_RESULT] 로그가 실제 DB INSERT/UPDATE 연결 후보입니다.
# =====================================================================


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    trace_flow(
        FILE,
        "chat",
        "IN",
        {
            "session_id": request.session_id,
            "episode_id": request.episode_id,
            "stage_id": request.stage_id,
            "message": request.message,
        },
    )

    # 1. Session 존재 확인
    session = session_store.get_session(request.session_id)

    if session is None:
        trace_flow(
            FILE,
            "chat",
            "ERROR",
            {"reason": "Session not found", "session_id": request.session_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # 2. Session의 Episode와 요청 Episode 일치 확인
    if session["episode_id"] != request.episode_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode does not match session"
        )

    # 3. 이미 Episode가 완료됐는지 확인
    if session["is_complete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Episode already completed"
        )

    # 4. 이미 완료한 Stage인지 확인
    if request.stage_id in session["completed_stages"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage already completed"
        )

    expected_prefix = f"{request.episode_id}_STAGE"

    if not request.stage_id.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage does not belong to episode"
        )

    # 5. 현재 진행해야 할 Stage인지 확인
    if session["current_stage"] != request.stage_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stage"
        )

    # 6. Scenario에서 현재 Stage 조회
    stage = get_stage(
        request.episode_id,
        request.stage_id
    )

    if stage is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )

    trace_flow(
        FILE,
        "chat",
        "STAGE_LOADED",
        {
            "stage_id": stage.get("stage_id"),
            "evaluation_axis": stage.get("evaluation_axis"),
            "stage_type": stage.get("type"),
            "next_stage": stage.get("next_stage"),
        },
    )

    # 7. AI 평가
    fallback_mode = False
    analysis_available = True

    try:
        from services.ai_service import evaluate_response

        ai_result = await asyncio.wait_for(
            evaluate_response(
                episode_id=request.episode_id,
                stage_id=request.stage_id,
                user_message=request.message,
                stage_data=stage
            ),
            timeout=20
        )

    except (asyncio.TimeoutError, Exception) as exc:
        trace_flow(
            FILE,
            "chat",
            "AI_FALLBACK",
            {
                "exception_type": type(exc).__name__,
                "stage_id": request.stage_id,
            },
        )

        if not is_fallback_response_meaningful(request.message, stage):
            response = ChatResponse(
                npc_response=(
                    "방금 말만으로는 어떻게 하겠다는 건지 잘 모르겠어. "
                    "조금 더 구체적으로 말해줄래?"
                ),
                feedback=(
                    "현재 상황에서 무엇이 걱정되는지, 무엇을 하지 않을지, "
                    "또는 누구에게 도움을 요청할지 실제로 말하듯 표현해보세요."
                ),
                scores={
                    "risk_awareness": 0,
                    "refusal": 0,
                    "help_request": 0,
                },
                next_stage=request.stage_id,
                is_episode_complete=False,
                fallback_mode=True,
                analysis_available=False,
                retry_required=True,
            )

            trace_flow(
                FILE,
                "chat",
                "OUT_RETRY_FALLBACK",
                response.model_dump(),
            )
            return response

        ai_result = build_fallback_result(stage)
        fallback_mode = True
        analysis_available = False

    trace_flow(
        FILE,
        "chat",
        "AI_RESULT",
        {
            "scores": ai_result.get("scores"),
            "retry_required": ai_result.get("retry_required"),
            "fallback_mode": ai_result.get("fallback_mode", fallback_mode),
            "analysis_available": ai_result.get(
                "analysis_available",
                analysis_available,
            ),
        },
    )

    required_ai_fields = {
        "npc_response",
        "feedback",
        "scores"
    }

    if not required_ai_fields.issubset(ai_result.keys()):
        ai_result = build_fallback_result(stage)
        fallback_mode = True
        analysis_available = False

    required_score_fields = {
        "risk_awareness",
        "refusal",
        "help_request"
    }

    scores = ai_result.get("scores", {})

    if not required_score_fields.issubset(scores.keys()):
        ai_result = build_fallback_result(stage)
        scores = ai_result["scores"]
        fallback_mode = True
        analysis_available = False

    if ai_result.get("fallback_mode") is True:
        fallback_mode = True

    if ai_result.get("analysis_available") is False:
        analysis_available = False

    # 8. 평가 불가 입력은 같은 Stage에서 재입력
    if ai_result.get("retry_required") is True:
        response = ChatResponse(
            npc_response=ai_result["npc_response"],
            feedback=ai_result["feedback"],
            scores={
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0,
            },
            next_stage=request.stage_id,
            is_episode_complete=False,
            fallback_mode=False,
            analysis_available=True,
            retry_required=True,
        )

        trace_flow(
            FILE,
            "chat",
            "OUT_RETRY",
            response.model_dump(),
        )
        return response

    # 9. 다음 Stage는 AI가 아닌 검수된 Scenario가 결정
    next_stage = stage.get("next_stage")

    # 10. 점수 + Stage 결과 + 진행상태 저장
    # -----------------------------------------------------------------
    # DB 담당 핵심 포인트:
    # 아래 데이터가 한 번의 Stage 완료 시 영속 저장해야 할 후보입니다.
    # 사용자 원문까지 저장하려면 현재 Chatting 모델에 본문 컬럼이 없으므로
    # DB 스키마 합의가 먼저 필요합니다.
    # -----------------------------------------------------------------
    trace_db_candidate(
        FILE,
        "chat",
        "SAVE_STAGE_RESULT",
        {
            "session_id": request.session_id,
            "episode_id": request.episode_id,
            "stage_id": request.stage_id,
            "user_message": request.message,
            "npc_response": ai_result["npc_response"],
            "feedback": ai_result["feedback"],
            "scores": scores,
            "next_stage": next_stage,
            "analysis_available": analysis_available,
            "fallback_mode": fallback_mode,
        },
    )

    saved = session_store.apply_stage_result(
        session_id=request.session_id,
        stage_id=request.stage_id,
        feedback=ai_result["feedback"],
        scores=scores,
        next_stage=next_stage,
        analysis_available=analysis_available
    )

    if not saved:
        raise HTTPException(
            status_code=409,
            detail="Failed to save stage result"
        )

    # 11. Episode 종료 여부
    is_episode_complete = next_stage is None

    # 12. Frontend 반환
    response = ChatResponse(
        npc_response=ai_result["npc_response"],
        feedback=ai_result["feedback"],
        scores=scores,
        next_stage=next_stage,
        is_episode_complete=is_episode_complete,
        fallback_mode=fallback_mode,
        analysis_available=analysis_available,
        retry_required=False
    )

    trace_flow(
        FILE,
        "chat",
        "OUT",
        response.model_dump(),
    )

    return response
