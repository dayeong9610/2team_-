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
    request: ChatRequest
):

    # Session 존재 확인
    session = get_session(
    request.session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session["current_stage"] != request.stage_id:

        raise HTTPException(
            status_code=400,
            detail="Invalid stage"
        )
    

    # 1. 현재 Stage 가져오기
    stage = get_stage(
        request.episode_id,
        request.stage_id
    )

    if stage is None:
        raise HTTPException(
            status_code=404,
            detail="Stage not found"
        )

    # Stage 완료 여부 확인
    if request.stage_id in session[
    "completed_stages"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Stage already completed"
        )
    

    # 2. AI 평가
    ai_result = await evaluate_response(
        episode_id=request.episode_id,
        stage_id=request.stage_id,
        user_message=request.message,
        stage_data=stage
    )

    # 3. 점수 저장
    add_scores(
        request.session_id,
        ai_result["scores"]
    )

    # 4. 다음 Stage는
    # Scenario가 결정
    next_stage = stage.get(
        "next_stage"
    )


    # Scenario에서 next_stage 조회
    complete_stage(
    session_id=request.session_id,
    stage_id=request.stage_id,
    next_stage=next_stage
    )   


    # 5. 종료 여부 판단
    is_episode_complete = (
        next_stage is None
    )

    # 6. Frontend 반환
    return ChatResponse(
        npc_response=(
            ai_result[
                "npc_response"
            ]
        ),
        feedback=(
            ai_result[
                "feedback"
            ]
        ),
        scores=(
            ai_result[
                "scores"
            ]
        ),
        next_stage=next_stage,
        is_episode_complete=(
            is_episode_complete
        )
    )