from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from core.scenario_engine import (
    load_episode,
    get_stage,
    list_episodes
)

from schemas.episode import (
    EpisodeSummary,
    EpisodeDetailResponse,
    StageResponse
)

# 첫 번째 API: 사용 가능한 에피소드의 요약 정보를 반환합니다.
router = APIRouter(
    tags=["Episodes"]
)

@router.get(
    "/episodes",
    response_model=list[EpisodeSummary]
)
def get_episodes():
    # 시나리오 폴더의 전체 에피소드를 읽어 목록 형태로 변환합니다.
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

# 두 번째 API: 특정 에피소드의 상세 정보와 Stage 목록을 반환합니다.
@router.get(
    "/episodes/{episode_id}",
    response_model=EpisodeDetailResponse
)
def get_episode(
    episode_id: str
):
    # 요청한 에피소드 ID에 해당하는 JSON 시나리오를 조회합니다.
    episode = load_episode(
        episode_id
    )

    if episode is None:

        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
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


# Stage 조회 API: 특정 에피소드 안의 한 장면을 반환합니다.
@router.get(
    "/episodes/{episode_id}/stages/{stage_id}",
    response_model=StageResponse
)
def get_episode_stage(
    episode_id: str,
    stage_id: str
):
    # 시나리오 엔진에서 Stage를 찾고 없으면 404를 반환합니다.
    stage = get_stage(
        episode_id,
        stage_id
    )

    if stage is None:

        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="Stage not found"
        )

    return stage
