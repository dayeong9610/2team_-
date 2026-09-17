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



router = APIRouter(
    # 채팅 관련 엔드포인트를 Chat 태그로 묶습니다.
    tags=["Chat"]
)


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):
    # 요청된 Session과 Stage가 현재 진행 상태와 일치하는지 검증합니다.
    # 1. Session 존재 확인
    session = (
        session_store.get_session(
            request.session_id
        )
    )

    if session is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


    # 2. Session의 Episode와 요청 Episode 일치 확인
    if (
        session["episode_id"]
        != request.episode_id
    ):
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
    if (
        request.stage_id
        in session["completed_stages"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage already completed"
        )


    expected_prefix = (
        f"{request.episode_id}_STAGE"
    )

    if not request.stage_id.startswith(
        expected_prefix
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stage does not belong to episode"
        )


    # 5. 현재 진행해야 할 Stage인지 확인
    if (
        session["current_stage"]
        != request.stage_id
    ):
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


    # 7. AI 평가
    # 외부 AI 호출이 오래 걸리거나 실패해도 API가 무한 대기하지 않게 합니다.
    try:
        # Keep the main application importable for admin/student pages even
        # when the optional AI dependencies have not been installed yet.
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

    except asyncio.TimeoutError:

        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI response timeout"
        )

    except Exception as exc:

        # 사용자 message 자체는 로그에 남기지 않음
        print(
            "AI evaluation failed:",
            type(exc).__name__
        )

        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "AI service temporarily "
                "unavailable"
            )
        )

    # 8. Scenario 기준으로 다음 Stage 결정
    # 다음 Stage의 결정은 AI가 아니라 시나리오 데이터가 담당합니다.
    next_stage = stage.get(
        "next_stage"
    )

     # 9. 점수 + Stage 결과 + 진행상태 저장
    # 평가 결과를 메모리 Session에 반영한 뒤 프론트엔드에 반환합니다.
    saved = (
        session_store.apply_stage_result(
            session_id=
                request.session_id,

            stage_id=
                request.stage_id,

            feedback=
                ai_result["feedback"],

            scores=
                ai_result["scores"],

            next_stage=next_stage
        )
    )

    if not saved:

        raise HTTPException(
            status_code=409,
            detail=(
                "Failed to save "
                "stage result"
            )
        )

    # 10. Episode 종료 여부
    is_episode_complete = (
        next_stage is None
    )


    # 11. Frontend 반환
    return ChatResponse(
        npc_response=(
            ai_result["npc_response"]
        ),

        feedback=(
            ai_result["feedback"]
        ),

        scores=(
            ai_result["scores"]
        ),

        next_stage=next_stage,

        is_episode_complete=(
            is_episode_complete
        )
    )

    required_ai_fields = {
        "npc_response",
        "feedback",
        "scores"
    }

    if not required_ai_fields.issubset(
        ai_result.keys()
    ):
        raise HTTPException(
            status_code=502,
            detail="Invalid AI response"
        )


    required_score_fields = {
        "risk_awareness",
        "refusal",
        "help_request"
    }

    scores = ai_result.get(
        "scores",
        {}
    )

    if not required_score_fields.issubset(
        scores.keys()
    ):
        raise HTTPException(
            status_code=502,
            detail="Invalid AI score response"
        )
