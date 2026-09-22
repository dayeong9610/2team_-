import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.flow_trace import trace_flow
from sqlmodel import Session, select
from database.connection import engine_url
from model.llm_role import LlmRole


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCENARIO_DIR = PROJECT_ROOT / "scenario" / "episodes"
FILE = "backend/src/core/scenario_engine.py"


def _role_to_episode(row: LlmRole) -> Optional[Dict[str, Any]]:
    """llm_role.content(JSON)를 게임 Episode dict로 변환합니다."""
    if not row.content or not row.episode_id:
        return None
    try:
        episode = json.loads(row.content)
    except (TypeError, json.JSONDecodeError):
        return None

    if str(episode.get("episode_id") or "").strip().upper() != row.episode_id.upper():
        return None
    return episode


def _load_episode_from_db(episode_id: str) -> Optional[Dict[str, Any]]:
    """published llm_role을 DB에서 조회합니다. DB 장애 시 파일 방식으로 fallback."""
    try:
        with Session(engine_url) as session:
            row = session.exec(
                select(LlmRole).where(
                    LlmRole.episode_id == episode_id.upper(),
                    LlmRole.status == "published",
                )
            ).first()
        return _role_to_episode(row) if row is not None else None
    except Exception:
        return None


def _list_db_episodes() -> List[dict]:
    try:
        with Session(engine_url) as session:
            rows = session.exec(
                select(LlmRole)
                .where(
                    LlmRole.episode_id.is_not(None),
                    LlmRole.status == "published",
                )
                .order_by(LlmRole.episode_id)
            ).all()

        result: list[dict] = []
        for row in rows:
            episode = _role_to_episode(row)
            if episode is not None:
                result.append(episode)
        return result
    except Exception:
        return []


# DB 담당 참고:
# 관리자 작성 시나리오는 llm_role.content(JSON)에서 먼저 읽고,
# DB 장애 또는 DB에 없는 기본 Episode는 scenario/episodes/*.json으로 fallback 합니다.


def get_episode_path(episode_id: str) -> Optional[Path]:
    trace_flow(FILE, "get_episode_path", "IN", {"episode_id": episode_id})

    normalized = episode_id.strip().upper()
    if not normalized.startswith("EP"):
        trace_flow(FILE, "get_episode_path", "OUT", None)
        return None

    number = normalized[2:]
    if not (len(number) == 2 and number.isdigit()):
        trace_flow(FILE, "get_episode_path", "OUT", None)
        return None

    result = SCENARIO_DIR / f"episode{number}.json"
    trace_flow(FILE, "get_episode_path", "OUT", {"path": str(result)})
    return result


def load_episode(episode_id: str) -> Optional[Dict[str, Any]]:
    trace_flow(FILE, "load_episode", "IN", {"episode_id": episode_id})

    normalized = episode_id.strip().upper()

    db_episode = _load_episode_from_db(normalized)
    if db_episode is not None:
        trace_flow(
            FILE,
            "load_episode",
            "OUT",
            {
                "episode_id": db_episode.get("episode_id"),
                "stage_count": len(db_episode.get("stages", [])),
                "source": "llm_role",
            },
        )
        return db_episode

    file_path = get_episode_path(normalized)
    if file_path is None or not file_path.exists():
        trace_flow(FILE, "load_episode", "OUT", None)
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        episode = json.load(file)

    if str(episode.get("episode_id") or "").upper() != normalized:
        trace_flow(FILE, "load_episode", "OUT", None)
        return None

    trace_flow(
        FILE,
        "load_episode",
        "OUT",
        {
            "episode_id": episode.get("episode_id"),
            "stage_count": len(episode.get("stages", [])),
            "source": str(file_path),
        },
    )
    return episode


def get_stage(episode_id: str, stage_id: str) -> Optional[Dict[str, Any]]:
    trace_flow(
        FILE,
        "get_stage",
        "IN",
        {"episode_id": episode_id, "stage_id": stage_id},
    )

    episode = load_episode(episode_id)
    if episode is None:
        trace_flow(FILE, "get_stage", "OUT", None)
        return None

    for stage in episode.get("stages", []):
        if stage.get("stage_id") == stage_id:
            trace_flow(
                FILE,
                "get_stage",
                "OUT",
                {
                    "stage_id": stage.get("stage_id"),
                    "evaluation_axis": stage.get("evaluation_axis"),
                    "type": stage.get("type"),
                    "next_stage": stage.get("next_stage"),
                },
            )
            return stage

    trace_flow(FILE, "get_stage", "OUT", None)
    return None


def get_total_stages(episode_id: str) -> int:
    episode = load_episode(episode_id)
    if episode is None:
        return 0

    count = len(episode.get("stages", []))
    trace_flow(
        FILE,
        "get_total_stages",
        "OUT",
        {"episode_id": episode_id, "total_stages": count},
    )
    return count


def list_episodes() -> List[dict]:
    trace_flow(FILE, "list_episodes", "IN", {"scenario_dir": str(SCENARIO_DIR)})

    # published llm_role을 우선 사용하고, 같은 episode_id의 기본 JSON은 중복 노출하지 않습니다.
    merged: dict[str, dict] = {}
    for episode in _list_db_episodes():
        episode_id = str(episode.get("episode_id") or "").upper()
        if episode_id:
            merged[episode_id] = episode

    if SCENARIO_DIR.exists():
        for file_path in sorted(SCENARIO_DIR.glob("episode*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    episode = json.load(file)
                episode_id = str(episode.get("episode_id") or "").upper()
                if episode_id and episode_id not in merged:
                    merged[episode_id] = episode
            except (json.JSONDecodeError, OSError):
                continue

    episodes = [merged[key] for key in sorted(merged)]
    trace_flow(
        FILE,
        "list_episodes",
        "OUT",
        {"count": len(episodes), "episode_ids": [ep.get("episode_id") for ep in episodes]},
    )
    return episodes
