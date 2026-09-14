from typing import Dict

#초기 MVP에서는 DB 없이 메모리로 먼저 테스트합니다.
sessions: Dict[str, dict] = {}


def create_session(
    session_id: str
):

    if session_id not in sessions:

        sessions[session_id] = {
            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            }
        }


def add_scores(
    session_id: str,
    scores: dict
):

    create_session(
        session_id
    )

    current = sessions[
        session_id
    ]["scores"]

    current["risk_awareness"] += (
        scores.get(
            "risk_awareness",
            0
        )
    )

    current["refusal"] += (
        scores.get(
            "refusal",
            0
        )
    )

    current["help_request"] += (
        scores.get(
            "help_request",
            0
        )
    )


def get_scores(
    session_id: str
):

    create_session(
        session_id
    )

    return sessions[
        session_id
    ]["scores"]