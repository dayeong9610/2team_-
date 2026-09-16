from fastapi import (
    APIRouter,
    HTTPException
)

from app.core.scenario_engine import (
    load_episode,
    get_stage,
    list_episodes
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

    episodes = list_episodes()

    result = []

    for episode in episodes:

        background = episode.get(
            "background",
            {}
        )

        result.append(
            {
                "episode_id":
                    episode[
                        "episode_id"
                    ],

                "title":
                    episode[
                        "title"
                    ],

                "description":
                    background.get(
                        "situation",
                        ""
                    ),

                "total_stages":
                    len(
                        episode.get(
                            "stages",
                            []
                        )
                    )
            }
        )

    return result

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

    background = episode.get(
        "background",
        {}
    )

    return {
        "episode_id":
            episode["episode_id"],

        "title":
            episode["title"],

        "description":
            background.get(
                "situation",
                ""
            ),

        "total_stages":
            len(
                episode.get(
                    "stages",
                    []
                )
            ),

        "stages":
            episode.get(
                "stages",
                []
            )
    }


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