from fastapi import (
    APIRouter,
    HTTPException
)

from app.core.scenario_engine import (
    load_episode,
    get_stage
)

from app.schemas.episode import (
    EpisodeSummary,
    EpisodeDetailResponse,
    StageResponse
)

#첫 번째 API: 에피소드 정보 반환
router = APIRouter(
    tags=["Episodes"]
)


@router.get(
    "/episodes",
    response_model=list[EpisodeSummary]
)
def get_episodes():

    episode = load_episode("EP01")

    if episode is None:
        return []

    return [
        {
            "episode_id":
                episode["episode_id"],

            "title":
                episode["title"],

            "description":
                episode["description"],

            "total_stages":
                episode["total_stages"]
        }
    ]

#두 번째 API: 에피소드 상세 정보 반환
@router.get(
    "/episodes/{episode_id}",
    response_model=EpisodeDetailResponse
)
def get_episode(
    episode_id: str
):

    episode = load_episode(
        episode_id
    )

    if episode is None:

        raise HTTPException(
            status_code=404,
            detail="Episode not found"
        )

    return episode

#Stage 조회 API
@router.get(
    "/episodes/{episode_id}/stages/{stage_id}",
    response_model=StageResponse
)
def get_episode_stage(
    episode_id: str,
    stage_id: str
):

    stage = get_stage(
        episode_id,
        stage_id
    )

    if stage is None:

        raise HTTPException(
            status_code=404,
            detail="Stage not found"
        )

    return stage