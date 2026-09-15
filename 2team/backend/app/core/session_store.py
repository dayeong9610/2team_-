from copy import deepcopy
from typing import Dict, Optional


class SessionStore:

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    def create_session(
        self,
        session_id: str,
        episode_id: str,
        first_stage: str
    ) -> dict:

        session = {
            "episode_id": episode_id,

            "current_stage": first_stage,

            "completed_stages": [],

            "stage_results": [],

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },

            "is_complete": False
        }

        self._sessions[
            session_id
        ] = session

        return deepcopy(session)

    def get_session(
        self,
        session_id: str
    ) -> Optional[dict]:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return None

        return deepcopy(session)

    def get_session_state(
        self,
        session_id: str,
        total_stages: int
    ) -> Optional[dict]:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return None

        completed_count = len(
            session[
                "completed_stages"
            ]
        )

        if total_stages <= 0:
            progress = 0

        else:
            progress = int(
                completed_count
                / total_stages
                * 100
            )

        return {
            "session_id":
                session_id,

            "episode_id":
                session[
                    "episode_id"
                ],

            "current_stage":
                session[
                    "current_stage"
                ],

            "completed_stages":
                list(
                    session[
                        "completed_stages"
                    ]
                ),

            "scores":
                deepcopy(
                    session[
                        "scores"
                    ]
                ),

            "progress":
                progress,

            "is_complete":
                session[
                    "is_complete"
                ]
        }
    

    def add_scores(
        self,
        session_id: str,
        scores: dict
    ) -> bool:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return False

        session["scores"][
            "risk_awareness"
        ] += scores.get(
            "risk_awareness",
            0
        )

        session["scores"][
            "refusal"
        ] += scores.get(
            "refusal",
            0
        )

        session["scores"][
            "help_request"
        ] += scores.get(
            "help_request",
            0
        )

        return True

    def save_stage_result(
        self,
        session_id: str,
        stage_id: str,
        feedback: str,
        scores: dict
    ) -> bool:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return False

        for result in session[
            "stage_results"
        ]:

            if (
                result["stage_id"]
                == stage_id
            ):
                return False

        session[
            "stage_results"
        ].append(
            {
                "stage_id":
                    stage_id,

                "feedback":
                    feedback,

                "scores": {
                    "risk_awareness":
                        scores.get(
                            "risk_awareness",
                            0
                        ),

                    "refusal":
                        scores.get(
                            "refusal",
                            0
                        ),

                    "help_request":
                        scores.get(
                            "help_request",
                            0
                        )
                }
            }
        )

        return True

    def complete_stage(
        self,
        session_id: str,
        stage_id: str,
        next_stage: Optional[str]
    ) -> bool:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return False

        if (
            stage_id
            not in session[
                "completed_stages"
            ]
        ):
            session[
                "completed_stages"
            ].append(
                stage_id
            )

        session[
            "current_stage"
        ] = next_stage

        if next_stage is None:
            session[
                "is_complete"
            ] = True

        return True

    def get_result(
        self,
        session_id: str
    ) -> Optional[dict]:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return None

        return {
            "episode_id":
                session["episode_id"],

            "scores":
                deepcopy(
                    session["scores"]
                ),

            "stage_results":
                deepcopy(
                    session[
                        "stage_results"
                    ]
                ),

            "completed_stages":
                list(
                    session[
                        "completed_stages"
                    ]
                ),

            "is_complete":
                session["is_complete"]
        }

    def delete_session(
        self,
        session_id: str
    ) -> bool:

        if (
            session_id
            not in self._sessions
        ):
            return False

        del self._sessions[
            session_id
        ]

        return True

    def clear(self):

        self._sessions.clear()


session_store = SessionStore()