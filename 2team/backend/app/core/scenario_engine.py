import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"


def load_episode(episode_id: str):

    if episode_id == "EP01":
        file_path = DATA_DIR / "episode01.json"
    else:
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)
def get_stage(
    episode_id: str,
    stage_id: str
):

    episode = load_episode(
        episode_id
    )

    if episode is None:
        return None

    for stage in episode["stages"]:

        if stage["stage_id"] == stage_id:
            return stage

    return None