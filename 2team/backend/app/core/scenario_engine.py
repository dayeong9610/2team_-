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

    if not SCENARIO_DIR.exists():
        return []

    episodes = []

    for file_path in sorted(
        SCENARIO_DIR.glob(
            "episode*.json"
        )
    ):

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