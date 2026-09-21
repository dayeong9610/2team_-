"""학생 학습 데이터를 기존 DB 모델에 저장하는 서비스.

DB 담당 요청에 맞춰 별도 ai_evaluation 테이블을 사용하지 않습니다.

- llm_role  : Episode/시츄에이션 JSON
- chat_room : 한 번의 학생 학습 Session
- chatting  : Stage별 USER/AI 대화
- score     : USER 답변에 대한 실제 LLM 평가 점수

DB 장애는 학생 학습 API 응답에 영향을 주지 않도록 모든 저장 함수가 실패를
False로 반환하고 예외를 밖으로 전파하지 않습니다.
"""

import json
import logging

from sqlmodel import Session, select

from database.connection import engine_url
from model.chat_room import ChatRoom
from model.chatting import Chatting, ChatterEnum
from model.llm_role import LlmRole
from model.score import Score


logger = logging.getLogger(__name__)

_SCORE_KEYS = (
    "risk_awareness",
    "refusal",
    "help_request",
)
_VALID_CATEGORIES = {"user_defined", "school", "trip", "club"}


def _normalized_score(scores: dict, key: str) -> int:
    value = int(scores.get(key, 0))
    return max(0, min(3, value))


def _episode_category(episode: dict) -> str:
    category = str(episode.get("category") or "user_defined").strip()
    return category if category in _VALID_CATEGORIES else "user_defined"


def _ensure_llm_role(db_session: Session, episode: dict) -> LlmRole:
    """Episode가 llm_role에 없으면 시스템 기본 Episode로 등록합니다."""
    episode_id = str(episode.get("episode_id") or "").strip().upper()
    if not episode_id:
        raise ValueError("episode_id is required")

    row = db_session.exec(
        select(LlmRole).where(LlmRole.episode_id == episode_id)
    ).first()

    if row is not None:
        # 마이그레이션 과정에서 ai_evaluation만 존재했던 Episode는
        # title=EPxx / stages=[] / draft 형태의 placeholder로 생성될 수 있습니다.
        # 학생이 실제 기본 JSON Episode를 시작하면 해당 placeholder를 실제 Episode
        # 데이터로 보강해서 이후 대시보드가 stage.evaluation_axis를 읽을 수 있게 합니다.
        should_upgrade_placeholder = False
        if row.admin_id is None and row.status == "draft":
            try:
                stored_payload = json.loads(row.content or "{}")
            except (TypeError, json.JSONDecodeError):
                stored_payload = {}

            stored_stages = stored_payload.get("stages")
            should_upgrade_placeholder = (
                str(row.title or "").strip().upper() == episode_id
                and (not isinstance(stored_stages, list) or len(stored_stages) == 0)
            )

        if should_upgrade_placeholder:
            row.title = str(episode.get("title") or episode_id).strip()
            row.category = _episode_category(episode)
            row.content = json.dumps(episode, ensure_ascii=False, indent=2)
            row.status = "published"
            db_session.add(row)
            db_session.flush()
            logger.info(
                "LLM_ROLE PLACEHOLDER UPGRADE episode_id=%s lr_num=%s",
                episode_id,
                row.lr_num,
            )

        return row

    row = LlmRole(
        episode_id=episode_id,
        title=str(episode.get("title") or episode_id).strip(),
        admin_id=None,
        category=_episode_category(episode),
        content=json.dumps(episode, ensure_ascii=False, indent=2),
        status="published",
    )
    db_session.add(row)
    db_session.flush()

    logger.info(
        "LLM_ROLE AUTO INSERT episode_id=%s lr_num=%s",
        episode_id,
        row.lr_num,
    )
    return row


def _ensure_chat_room(
    db_session: Session,
    *,
    session_id: str,
    episode: dict,
    total_stages: int,
) -> ChatRoom:
    room = db_session.exec(
        select(ChatRoom).where(ChatRoom.session_id == session_id)
    ).first()

    if room is not None:
        return room

    role = _ensure_llm_role(db_session, episode)
    room = ChatRoom(
        session_id=session_id,
        lr_num=role.lr_num,
        admin_id=role.admin_id,
        limits=max(0, int(total_stages)),
    )
    db_session.add(room)
    db_session.flush()

    logger.info(
        "CHAT_ROOM INSERT session_id=%s room_id=%s lr_num=%s",
        session_id,
        room.room_id,
        role.lr_num,
    )
    return room


def persist_chat_room(
    *,
    session_id: str,
    episode: dict,
    total_stages: int,
) -> bool:
    """학생이 Episode를 시작하면 llm_role + chat_room을 준비합니다."""
    try:
        with Session(engine_url) as db_session:
            _ensure_chat_room(
                db_session,
                session_id=session_id,
                episode=episode,
                total_stages=total_stages,
            )
            db_session.commit()
        return True
    except Exception as exc:
        logger.warning(
            "CHAT_ROOM save skipped: %s",
            type(exc).__name__,
        )
        return False


def _upsert_chatting(
    db_session: Session,
    *,
    room_id: int,
    stage_id: str,
    chatter: ChatterEnum,
    content: str | None,
    feedback: str | None = None,
) -> Chatting:
    row = db_session.exec(
        select(Chatting).where(
            Chatting.room_id == room_id,
            Chatting.stage_id == stage_id,
            Chatting.chatter == chatter,
        )
    ).first()

    if row is None:
        row = Chatting(
            room_id=room_id,
            stage_id=stage_id,
            chatter=chatter,
            content=content,
            feedback=feedback,
        )
    else:
        row.content = content
        row.feedback = feedback

    db_session.add(row)
    db_session.flush()
    return row


def persist_stage_evaluation(
    *,
    session_id: str,
    episode_id: str,
    stage_id: str,
    user_message: str,
    npc_response: str,
    feedback: str,
    scores: dict,
) -> bool:
    """실제 GPT 평가 1건을 chatting + score 구조에 저장합니다.

    fallback/재입력 여부는 routes/chat.py에서 걸러진 뒤 이 함수가 호출됩니다.
    Score는 평가 대상인 USER Chatting 행에 연결됩니다.
    """
    normalized_scores = {
        key: _normalized_score(scores, key)
        for key in _SCORE_KEYS
    }

    try:
        with Session(engine_url) as db_session:
            room = db_session.exec(
                select(ChatRoom).where(ChatRoom.session_id == session_id)
            ).first()

            # 세션 시작 시 DB가 잠시 내려가 있어 chat_room 생성이 누락됐더라도
            # 평가 저장 시 한 번 더 복구를 시도합니다.
            if room is None:
                from core.scenario_engine import load_episode

                episode = load_episode(episode_id)
                if episode is None:
                    raise ValueError("Episode not found for DB persistence")
                room = _ensure_chat_room(
                    db_session,
                    session_id=session_id,
                    episode=episode,
                    total_stages=len(episode.get("stages", [])),
                )

            user_chat = _upsert_chatting(
                db_session,
                room_id=int(room.room_id),
                stage_id=stage_id,
                chatter=ChatterEnum.USER,
                content=user_message,
            )

            _upsert_chatting(
                db_session,
                room_id=int(room.room_id),
                stage_id=stage_id,
                chatter=ChatterEnum.AI,
                content=npc_response,
                feedback=feedback,
            )

            for category, value in normalized_scores.items():
                score_row = db_session.exec(
                    select(Score).where(
                        Score.chat_id == user_chat.chat_id,
                        Score.category == category,
                    )
                ).first()

                if score_row is None:
                    score_row = Score(
                        chat_id=int(user_chat.chat_id),
                        category=category,
                        score=value,
                    )
                else:
                    score_row.score = value

                db_session.add(score_row)

            db_session.commit()

        logger.info(
            "STAGE DB SAVE session_id=%s episode_id=%s stage_id=%s",
            session_id,
            episode_id,
            stage_id,
        )
        return True

    except Exception as exc:
        # DB 장애가 학생 학습 흐름을 끊지 않게 예외를 전파하지 않습니다.
        logger.exception(
            "STAGE DB save failed: %s",
            type(exc).__name__,
        )
        return False
