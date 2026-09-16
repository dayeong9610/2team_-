from copy import deepcopy
from typing import Dict, Optional


class MemorySessionStore:

    def __init__(self):
        self._sessions: Dict[str, dict] = {}


    # =========================
    # Session 생성
    # =========================
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


    # =========================
    # Session 조회
    # =========================
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


    # =========================
    # Session 진행 상태 조회
    # =========================
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


    # =========================
    # Stage 결과 한번에 저장
    # =========================
    def apply_stage_result(
        self,
        session_id: str,
        stage_id: str,
        feedback: str,
        scores: dict,
        next_stage: Optional[str]
    ) -> bool:

        session = self._sessions.get(
            session_id
        )

        if session is None:
            return False

        # 같은 Stage 중복 처리 방지
        if (
            stage_id
            in session[
                "completed_stages"
            ]
        ):
            return False


        # -------------------------
        # 1. 점수 누적
        # -------------------------
        current_scores = session[
            "scores"
        ]

        current_scores[
            "risk_awareness"
        ] += scores.get(
            "risk_awareness",
            0
        )

        current_scores[
            "refusal"
        ] += scores.get(
            "refusal",
            0
        )

        current_scores[
            "help_request"
        ] += scores.get(
            "help_request",
            0
        )


        # -------------------------
        # 2. Stage 결과 저장
        # -------------------------
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


        # -------------------------
        # 3. 완료 Stage 추가
        # -------------------------
        session[
            "completed_stages"
        ].append(
            stage_id
        )


        # -------------------------
        # 4. 다음 Stage 설정
        # -------------------------
        session[
            "current_stage"
        ] = next_stage


        # -------------------------
        # 5. Episode 종료 확인
        # -------------------------
        session[
            "is_complete"
        ] = (
            next_stage is None
        )

        return True


    # =========================
    # 최종 결과 조회
    # =========================
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
                session[
                    "episode_id"
                ],

            "scores":
                deepcopy(
                    session[
                        "scores"
                    ]
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
                session[
                    "is_complete"
                ]
        }


    # =========================
    # Session 삭제
    # =========================
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


    # =========================
    # 테스트용 전체 초기화
    # =========================
    def clear(self):

        self._sessions.clear()


# Backend 전체에서 사용하는
# 공용 Memory Session Store
session_store = MemorySessionStore()