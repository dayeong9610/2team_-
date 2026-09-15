from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException
)

from app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionResultResponse,
    SessionStateResponse
)

from app.core.session_store import (
    create_session,
    get_result,
    get_session_state,
    delete_session
)


router = APIRouter(
    tags=["Sessions"]
)


@router.post(
    "/sessions",
    response_model=SessionCreateResponse
)
def start_session(
    request: SessionCreateRequest
):

    session_id = str(
        uuid4()
    )

    # 현재 EP01은 항상 Stage01에서 시작
    first_stage = "EP01_STAGE01"

    session = create_session(
        session_id=session_id,
        episode_id=request.episode_id,
        first_stage=first_stage
    )

    return {
        "session_id":
            session_id,

        "episode_id":
            request.episode_id,

        "current_stage":
            session["current_stage"]
    }


@router.get(
    "/sessions/{session_id}/result",
    response_model=SessionResultResponse
)
def session_result(
    session_id: str
):

    result = get_result(
        session_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return result


@router.get(
    "/sessions/{session_id}",
    response_model=SessionStateResponse
)
def session_state(
    session_id: str
):

    session = get_session_state(
        session_id
    )

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session

@router.delete(
    "/sessions/{session_id}"
)
def end_session(
    session_id: str
):

    deleted = delete_session(
        session_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "message":
            "Session deleted"
    }