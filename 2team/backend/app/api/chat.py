import asyncio

from fastapi import (
    APIRouter,
    HTTPException
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.core.scenario_engine import (
    get_stage
)

from app.core.session_store import (
    session_store
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
    request: ChatRequest
):

    # 1. Session 존재 확인
    session = (
        session_store.get_session(
            request.session_id
        )
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )


    # 2. Session의 Episode와 요청 Episode 일치 확인
    if (
        session["episode_id"]
        != request.episode_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Episode does not match session"
        )


    # 3. 이미 Episode가 완료됐는지 확인
    if session["is_complete"]:
        raise HTTPException(
            status_code=400,
            detail="Episode already completed"
        )


    # 4. 이미 완료한 Stage인지 확인
    if (
        request.stage_id
        in session["completed_stages"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Stage already completed"
        )


    # 5. 현재 진행해야 할 Stage인지 확인
    if (
        session["current_stage"]
        != request.stage_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid stage"
        )


    # 6. Scenario에서 현재 Stage 조회
    stage = get_stage(
        request.episode_id,
        request.stage_id
    )

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found"
        )


    # 7. AI 평가
    try:

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
            status_code=504,
            detail="AI response timeout"
        )

    except Exception as exc:

        # 사용자 message 자체는 로그에 남기지 않음
        print(
            "AI evaluation failed:",
            type(exc).__name__
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "AI service temporarily "
                "unavailable"
            )
        )

    # 8. Scenario 기준으로 다음 Stage 결정
    next_stage = stage.get(
        "next_stage"
    )

     # 9. 점수 + Stage 결과 + 진행상태 저장
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