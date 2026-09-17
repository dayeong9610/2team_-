import json
from pathlib import Path
from typing import (
    Optional,
    Dict,
    Any,
    List
)


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


def get_episode_path(
    episode_id: str
) -> Optional[Path]:
    # EP01 같은 ID를 검증한 뒤 대응하는 JSON 파일 경로를 반환합니다.
    normalized = (
        episode_id
        .strip()
        .upper()
    )

    if not normalized.startswith("EP"):
        return None

    number = normalized[2:]

    if not (
        len(number) == 2
        and number.isdigit()
    ):
        return None

    return (
        SCENARIO_DIR
        / f"episode{number}.json"
    )


def load_episode(
    episode_id: str
) -> Optional[Dict[str, Any]]:
    # 에피소드 JSON을 읽고 내부 episode_id까지 확인합니다.
    file_path = get_episode_path(
        episode_id
    )

    if file_path is None:
        return None

    if not file_path.exists():
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        episode = json.load(
            file
        )

    if (
        episode.get("episode_id")
        != episode_id.upper()
    ):
        return None

    return episode


def get_stage(
    episode_id: str,
    stage_id: str
) -> Optional[Dict[str, Any]]:
    # 에피소드의 Stage 목록에서 요청한 Stage ID를 검색합니다.
    episode = load_episode(
        episode_id
    )

    if episode is None:
        return None

    for stage in episode.get(
        "stages",
        []
    ):

        if (
            stage.get("stage_id")
            == stage_id
        ):
            return stage

    return None


def get_total_stages(
    episode_id: str
) -> int:
    # 에피소드에 포함된 전체 Stage 개수를 반환합니다.
    episode = load_episode(
        episode_id
    )

    if episode is None:
        return 0

    return len(
        episode.get(
            "stages",
            []
        )
    )


def list_episodes() -> List[dict]:
    # 시나리오 디렉터리의 모든 episode*.json을 읽어 목록으로 반환합니다.
    if not SCENARIO_DIR.exists():
        return []

    episodes = []

    for file_path in sorted(
        SCENARIO_DIR.glob(
            "episode*.json"
        )
    ):
        # 파일 하나가 손상되어도 다른 에피소드 조회는 계속 진행합니다.
        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                episode = json.load(
                    file
                )

            episodes.append(
                episode
            )

        except (
            json.JSONDecodeError,
            OSError
        ):
            continue

    return episodes