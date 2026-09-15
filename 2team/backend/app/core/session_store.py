from typing import Dict, Optional

#초기 MVP에서는 DB 없이 메모리로 먼저 테스트합니다.
sessions: Dict[str, dict] = {}


def create_session(
    session_id: str,
    episode_id: str,
    first_stage: str
):

    if session_id not in sessions:

        sessions[session_id] = {
            "episode_id": episode_id,

            "current_stage": first_stage,

            "completed_stages": [],

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },

            "is_complete": False
        }

    return sessions[session_id]


def get_session(
    session_id: str
) -> Optional[dict]:

    return sessions.get(
        session_id
    )


def get_session_state(
    session_id: str
):

    completed_count = len(
    session["completed_stages"]
    )

#    total_stages = get_total_stages(
#        session["episode_id"] ) 수정필요함
    total_stages = 5

    progress = int(
        completed_count
        / total_stages
        * 100
    )

    session = sessions.get(
        session_id
    )

    if session is None:
        return None

    return {
        "session_id":
            session_id,

        "episode_id":
            session["episode_id"],

        "current_stage":
            session["current_stage"],

        "completed_stages":
            session["completed_stages"],

        "scores":
            session["scores"],

        "progress":
            progress,

        "is_complete":
            session["is_complete"]
    }


def add_scores(
    session_id: str,
    scores: dict
):

    session = sessions.get(
        session_id
    )

    if session is None:
        return

    current = session["scores"]

    current["risk_awareness"] += scores.get(
        "risk_awareness",
        0
    )

    current["refusal"] += scores.get(
        "refusal",
        0
    )

    current["help_request"] += scores.get(
        "help_request",
        0
    )


def complete_stage(
    session_id: str,
    stage_id: str,
    next_stage: Optional[str]
):

    session = sessions.get(
        session_id
    )

    if session is None:
        return

    if stage_id not in session["completed_stages"]:
        session["completed_stages"].append(
            stage_id
        )

    session["current_stage"] = next_stage

    if next_stage is None:
        session["is_complete"] = True


def get_result(
    session_id: str
) -> Optional[dict]:

    session = sessions.get(
        session_id
    )

    if session is None:
        return None

    return {
        "episode_id":
            session["episode_id"],

        "scores":
            session["scores"],

        "completed_stages":
            session["completed_stages"],

        "is_complete":
            session["is_complete"]
    }


#Session 종료 기능
def delete_session(
    session_id: str
) -> bool:

    if session_id not in sessions:
        return False

    del sessions[
        session_id
    ]

    return True