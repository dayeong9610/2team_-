# 데이터베이스 대신 메모리에 학습 Session 상태를 보관하는 모듈입니다.
from copy import deepcopy
from typing import Dict, Optional


class MemorySessionStore:
    # 서버 프로세스가 실행되는 동안만 유지되는 Session 저장소입니다.

    def __init__(self):
        # Session ID를 키로 하여 상태 딕셔너리를 저장합니다.
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
        # 새 Session의 초기 상태와 세 가지 누적 점수를 생성합니다.
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

            "is_complete": False,

            # 모든 Stage가 AI 분석으로 평가됐는지 여부.
            # 한 번이라도 fallback이 사용되면 False로 유지합니다.
            "analysis_available": True,

            "fallback_mode": False
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
        # 원본 상태가 외부에서 직접 변경되지 않도록 복사본을 반환합니다.
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
        # 현재 Stage와 완료 Stage 수를 바탕으로 진행률을 계산합니다.
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
                ],

            "fallback_mode":
                session.get(
                    "fallback_mode",
                    False
                ),

            "analysis_available":
                session.get(
                    "analysis_available",
                    True
                )
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
        next_stage: Optional[str],
        analysis_available: bool = True
    ) -> bool:
        # 한 Stage의 피드백과 점수를 저장하고 다음 Stage로 상태를 이동합니다.
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
                },

                "analysis_available":
                    analysis_available
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

        if not analysis_available:
            session["analysis_available"] = False
            session["fallback_mode"] = True

        return True


    # =========================
    # 최종 결과 조회
    # =========================
    def get_result(
        self,
        session_id: str
    ) -> Optional[dict]:
        # Session 전체 결과를 외부 응답용 형태로 정리합니다.
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
                ],

            "fallback_mode":
                session.get(
                    "fallback_mode",
                    False
                ),

            "analysis_available":
                session.get(
                    "analysis_available",
                    True
                )
        }


    # =========================
    # Session 삭제
    # =========================
    def delete_session(
        self,
        session_id: str
    ) -> bool:
        # 지정한 Session을 저장소에서 제거합니다.
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
        # 테스트나 개발 중 전체 Session을 초기화합니다.
        self._sessions.clear()


# Backend 전체에서 공유하는 전역 메모리 Session 저장소입니다.
session_store = MemorySessionStore()
