from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.core.scenario_engine import get_stage

from app.services.ai_service import evaluate_response


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
    )

    next_stage = stage.get(
        "next_stage"
    )

    is_complete = (
        next_stage is None
    )

    return {
        "npc_response":
            ai_result["npc_response"],

        "feedback":
            ai_result["feedback"],

        "scores":
            ai_result["scores"],

        "next_stage":
            next_stage,

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
    )