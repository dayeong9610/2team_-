from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException
)

from schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionResultResponse,
    SessionStateResponse
)

from core.session_store import (
    session_store
)

from core.scenario_engine import (
    load_episode,
    get_total_stages
)

from core.flow_trace import (
    trace_flow,
    trace_db_candidate,
)


router = APIRouter(
    tags=["Sessions"]
)

FILE = "backend/src/routes/sessions.py"


# =====================================================================
# DB 담당 참고
# ---------------------------------------------------------------------
# 이 파일은 웹 프론트가 호출하는 Session API 진입점입니다.
#
# POST   /api/sessions                     -> start_session()
# GET    /api/sessions/{session_id}        -> session_state()
# GET    /api/sessions/{session_id}/result -> session_result()
# DELETE /api/sessions/{session_id}        -> end_session()
#
# 현재 실제 저장은 DB가 아니라 core/session_store.py의 메모리 딕셔너리입니다.
# [DB-CANDIDATE] 로그가 찍히는 부분이 DB 저장/조회로 교체하기 좋은 지점입니다.
# =====================================================================


# =========================
# Session 생성
# =========================

@router.post(
    "/sessions",
    response_model=SessionCreateResponse
)
def start_session(
    request: SessionCreateRequest
):
    trace_flow(
        FILE,
        "start_session",
        "IN",
        {"episode_id": request.episode_id},
    )

    # 1. Episode 조회
    episode = load_episode(
        request.episode_id
    )

    if episode is None:
        trace_flow(
            FILE,
            "start_session",
            "ERROR",
            {"reason": "Episode not found", "episode_id": request.episode_id},
        )
        raise HTTPException(
            status_code=404,
            detail="Episode not found"
        )

    # 2. Episode Stage 확인
    stages = episode.get(
        "stages",
        []
    )

    if not stages:
        raise HTTPException(
            status_code=500,
            detail="Episode has no stages"
        )

    # 3. 첫 Stage 결정
    first_stage = stages[0][
        "stage_id"
    ]

    # 4. Session ID 생성
    session_id = str(
        uuid4()
    )

    # 5. Session 생성
    # 현재는 MemorySessionStore에 저장됨.
    # DB 연동 시 여기에서 학습 세션 INSERT가 필요할 가능성이 큼.
    session = (
        session_store.create_session(
            session_id=session_id,
            episode_id=request.episode_id,
            first_stage=first_stage
        )
    )

    trace_db_candidate(
        FILE,
        "start_session",
        "CREATE_SESSION",
        {
            "session_id": session_id,
            "episode_id": request.episode_id,
            "current_stage": session["current_stage"],
            "scores": session["scores"],
            "is_complete": session["is_complete"],
        },
    )

    response = {
        "session_id": session_id,
        "episode_id": request.episode_id,
        "current_stage": session["current_stage"]
    }

    trace_flow(
        FILE,
        "start_session",
        "OUT",
        response,
    )

    return response


# =========================
# Session 결과 조회
# =========================

@router.get(
    "/sessions/{session_id}/result",
    response_model=SessionResultResponse
)
def session_result(
    session_id: str
):
    trace_flow(
        FILE,
        "session_result",
        "IN",
        {"session_id": session_id},
    )

    result = (
        session_store.get_result(
            session_id
        )
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    trace_db_candidate(
        FILE,
        "session_result",
        "READ_FINAL_RESULT",
        {
            "session_id": session_id,
            "episode_id": result.get("episode_id"),
            "scores": result.get("scores"),
            "completed_stages": result.get("completed_stages"),
            "is_complete": result.get("is_complete"),
        },
    )

    trace_flow(
        FILE,
        "session_result",
        "OUT",
        result,
    )

    return result


# =========================
# Session 현재 상태 조회
# =========================

@router.get(
    "/sessions/{session_id}",
    response_model=SessionStateResponse
)
def session_state(
    session_id: str
):
    trace_flow(
        FILE,
        "session_state",
        "IN",
        {"session_id": session_id},
    )

    session = (
        session_store.get_session(
            session_id
        )
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    total_stages = (
        get_total_stages(
            session["episode_id"]
        )
    )

    if total_stages <= 0:
        raise HTTPException(
            status_code=500,
            detail="Episode has no stages"
        )

    state = (
        session_store.get_session_state(
            session_id,
            total_stages
        )
    )

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    trace_db_candidate(
        FILE,
        "session_state",
        "READ_SESSION_STATE",
        {
            "session_id": session_id,
            "episode_id": state.get("episode_id"),
            "current_stage": state.get("current_stage"),
            "scores": state.get("scores"),
            "progress": state.get("progress"),
            "is_complete": state.get("is_complete"),
        },
    )

    trace_flow(
        FILE,
        "session_state",
        "OUT",
        state,
    )

    return state


# =========================
# Session 종료
# =========================

@router.delete(
    "/sessions/{session_id}"
)
def end_session(
    session_id: str
):
    trace_flow(
        FILE,
        "end_session",
        "IN",
        {"session_id": session_id},
    )

    deleted = (
        session_store.delete_session(
            session_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    trace_db_candidate(
        FILE,
        "end_session",
        "DELETE_OR_CLOSE_SESSION",
        {"session_id": session_id},
    )

    response = {
        "message": "Session deleted"
    }

    trace_flow(
        FILE,
        "end_session",
        "OUT",
        response,
    )

    return response
