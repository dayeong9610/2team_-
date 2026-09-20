import json
from pathlib import Path
from typing import (
    Optional,
    Dict,
    Any,
    List
)

from core.flow_trace import trace_flow
from sqlmodel import Session, select
from database.connection import engine_url
from model.episode_scenario import EpisodeScenario


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

SCENARIO_DIR = (
    PROJECT_ROOT
    / "scenario"
    / "episodes"
)

FILE = "backend/src/core/scenario_engine.py"


def _load_episode_from_db(episode_id: str) -> Optional[Dict[str, Any]]:
    """공개된 관리자 작성 에피소드를 DB에서 조회합니다. DB 장애 시 파일 방식으로 fallback."""
    try:
        with Session(engine_url) as session:
            row = session.exec(
                select(EpisodeScenario).where(
                    EpisodeScenario.episode_id == episode_id.upper(),
                    EpisodeScenario.status == "published",
                )
            ).first()
        if row is None:
            return None
        episode = json.loads(row.scenario_json)
        if episode.get("episode_id") != episode_id.upper():
            return None
        return episode
    except Exception:
        return None


def _list_db_episodes() -> List[dict]:
    try:
        with Session(engine_url) as session:
            rows = session.exec(
                select(EpisodeScenario)
                .where(EpisodeScenario.status == "published")
                .order_by(EpisodeScenario.episode_id)
            ).all()
        result = []
        for row in rows:
            try:
                result.append(json.loads(row.scenario_json))
            except json.JSONDecodeError:
                continue
        return result
    except Exception:
        return []


# DB 담당 참고:
# 현재 에피소드/Stage 원본은 DB가 아니라 scenario/episodes/episodeXX.json 입니다.
# 향후 시나리오까지 DB 관리한다면 이 파일의 load_episode()/get_stage()가
# JSON 조회 -> DB SELECT로 바뀌는 핵심 지점입니다.


def get_episode_path(
    episode_id: str
) -> Optional[Path]:
    trace_flow(
        FILE,
        "get_episode_path",
        "IN",
        {"episode_id": episode_id},
    )

    normalized = (
        episode_id
        .strip()
        .upper()
    )

    if not normalized.startswith("EP"):
        trace_flow(FILE, "get_episode_path", "OUT", None)
        return None

    number = normalized[2:]

    if not (
        len(number) == 2
        and number.isdigit()
    ):
        trace_flow(FILE, "get_episode_path", "OUT", None)
        return None

    result = SCENARIO_DIR / f"episode{number}.json"
    trace_flow(
        FILE,
        "get_episode_path",
        "OUT",
        {"path": str(result)},
    )
    return result


def load_episode(
    episode_id: str
) -> Optional[Dict[str, Any]]:
    trace_flow(
        FILE,
        "load_episode",
        "IN",
        {"episode_id": episode_id},
    )

    db_episode = _load_episode_from_db(episode_id)
    if db_episode is not None:
        trace_flow(
            FILE,
            "load_episode",
            "OUT",
            {
                "episode_id": db_episode.get("episode_id"),
                "stage_count": len(db_episode.get("stages", [])),
                "source": "database",
            },
        )
        return db_episode

    file_path = get_episode_path(episode_id)

    if file_path is None or not file_path.exists():
        trace_flow(FILE, "load_episode", "OUT", None)
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        episode = json.load(file)

    if episode.get("episode_id") != episode_id.upper():
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


def get_stage(
    episode_id: str,
    stage_id: str
) -> Optional[Dict[str, Any]]:
    trace_flow(
        FILE,
        "get_stage",
        "IN",
        {
            "episode_id": episode_id,
            "stage_id": stage_id,
        },
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


def get_total_stages(
    episode_id: str
) -> int:
    episode = load_episode(episode_id)

    if episode is None:
        return 0

    count = len(episode.get("stages", []))
    trace_flow(
        FILE,
        "get_total_stages",
        "OUT",
        {
            "episode_id": episode_id,
            "total_stages": count,
        },
    )
    return count


def list_episodes() -> List[dict]:
    trace_flow(FILE, "list_episodes", "IN", {"scenario_dir": str(SCENARIO_DIR)})

    # DB에서 publish된 에피소드를 우선 사용하고, 같은 episode_id의 파일은 중복 노출하지 않습니다.
    merged: dict[str, dict] = {}
    for episode in _list_db_episodes():
        episode_id = episode.get("episode_id")
        if episode_id:
            merged[episode_id] = episode

    if SCENARIO_DIR.exists():
        for file_path in sorted(SCENARIO_DIR.glob("episode*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    episode = json.load(file)
                episode_id = episode.get("episode_id")
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
