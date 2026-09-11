from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.core.scenario_engine import (
    get_stage
)


router = APIRouter(
    tags=["Chat"]
)

#임시로 처리
def mock_ai_response(
    stage_id: str,
    message: str
):

    return {
        "npc_response":
        "왜? 다들 하는데 한 번 정도는 괜찮지 않아?",

        "feedback":
        "답변을 잘 표현했어요.",

        "scores": {
            "risk_awareness": 1,
            "refusal": 2,
            "help_request": 0
        }
    }


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
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
#Mock에서 실제 AI로 변경할 때 나중교체해야됨 아래껀 삭제
# ai_result = await evaluate_response(
#     episode_id=request.episode_id,
#     stage_id=request.stage_id,
#     user_message=request.message,
#     stage_data=stage
# )
    ai_result = mock_ai_response(
        request.stage_id,
        request.message
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

#DB없는 형태로 임시 저장, 나중에 Redis/DB로 바꾸기
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