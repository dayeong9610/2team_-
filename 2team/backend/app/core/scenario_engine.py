import json
from pathlib import Path
from typing import Optional, Dict, Any


BASE_DIR = Path(__file__).resolve().parent.parent


def load_episode(
    episode_id: str
) -> Optional[Dict[str, Any]]:

    if episode_id != "EP01":
        return None

    file_path = (
        BASE_DIR
        / "data"
        / "episode01.json"
    )

    if not file_path.exists():
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


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
        if stage.get(
            "stage_id"
        ) == stage_id:
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