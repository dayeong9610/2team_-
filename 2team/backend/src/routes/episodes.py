"""Episode read API.

학생용 프론트가 /api/episodes 를 통해 정적 JSON과 관리자 DB에 공개된
에피소드를 동일한 계약으로 조회하도록 합니다.
"""

import logging
from fastapi import APIRouter, HTTPException

from core.scenario_engine import list_episodes, load_episode
from schemas.episode import EpisodeDetailResponse, EpisodeSummary, StageResponse


router = APIRouter(tags=["Episodes"])
logger = logging.getLogger(__name__)


def _description(episode: dict) -> str:
    background = episode.get("background")
    if isinstance(background, dict):
        return str(background.get("situation") or "")
    return ""


@router.get("/episodes", response_model=list[EpisodeSummary])
def get_episodes() -> list[EpisodeSummary]:
    """게임에서 선택 가능한 전체 공개 Episode 목록을 반환합니다."""
    result: list[EpisodeSummary] = []

    for episode in list_episodes():
        episode_id = str(episode.get("episode_id") or "").strip().upper()
        if not episode_id:
            continue
        stages = episode.get("stages") if isinstance(episode.get("stages"), list) else []
        result.append(
            EpisodeSummary(
                episode_id=episode_id,
                title=str(episode.get("title") or episode_id),
                description=_description(episode),
                total_stages=len(stages),
            )
        )

    logger.info("EPISODE LIST API count=%s", len(result))
    return result


@router.get("/episodes/{episode_id}", response_model=EpisodeDetailResponse)
def get_episode(episode_id: str) -> EpisodeDetailResponse:
    """하나의 공개 Episode와 Stage 전체를 반환합니다."""
    episode = load_episode(episode_id)
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    stages_raw = episode.get("stages") if isinstance(episode.get("stages"), list) else []
    try:
        stages = [StageResponse(**stage) for stage in stages_raw]
    except Exception as exc:
        logger.exception("EPISODE DETAIL schema invalid episode_id=%s", episode_id)
        raise HTTPException(status_code=500, detail="Episode schema is invalid") from exc

    return EpisodeDetailResponse(
        episode_id=str(episode.get("episode_id") or episode_id).upper(),
        title=str(episode.get("title") or episode_id),
        description=_description(episode),
        total_stages=len(stages),
        stages=stages,
    )
