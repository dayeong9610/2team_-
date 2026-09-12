from fastapi import APIRouter, HTTPException
from app.core.scenario_engine import load_episode, get_stage

#첫 번째 API: 에피소드 정보 반환
router = APIRouter(
    tags=["Episodes"]
)


@router.get("/episodes/{episode_id}")
def get_episode(episode_id: str):

    episode = load_episode(episode_id)

    if episode is None:
        raise HTTPException(
            status_code=404,
            detail="Episode not found"
        )

    return episode

#Stage 조회 API
@router.get(
    "/episodes/{episode_id}/stages/{stage_id}"
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