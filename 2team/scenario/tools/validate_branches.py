import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EPISODE_PATH = BASE_DIR / "episodes" / "episode01.json"

BRANCH_PATH = (
    BASE_DIR
    / "branches"
    / "episode01-branches.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():

    episode = load_json(EPISODE_PATH)
    branch_data = load_json(BRANCH_PATH)

    errors = []

    stage_ids = [
        stage["stage_id"]
        for stage in episode["stages"]
    ]

    branch_stages = branch_data.get(
        "stages",
        {}
    )

    # 모든 Stage에 분기가 있는지 확인
    for stage_id in stage_ids:

        if stage_id not in branch_stages:
            errors.append(
                f"{stage_id} 분기가 없습니다."
            )

            continue

        branches = branch_stages[
            stage_id
        ].get("branches", {})

        # high / medium / low 확인
        for level in [
            "high",
            "medium",
            "low"
        ]:

            if level not in branches:
                errors.append(
                    f"{stage_id}에 "
                    f"{level} 분기가 없습니다."
                )

    # next_stage 검사
    for stage_id, stage_data in (
        branch_stages.items()
    ):

        for branch_name, branch in (
            stage_data
            .get("branches", {})
            .items()
        ):

            next_stage = branch.get(
                "next_stage"
            )

            if (
                next_stage is not None
                and next_stage not in stage_ids
            ):
                errors.append(
                    f"{stage_id} / "
                    f"{branch_name}: "
                    f"{next_stage}가 "
                    "존재하지 않습니다."
                )

    if errors:

        print("\n분기 검사 실패\n")

        for error in errors:
            print("-", error)

    else:

        print(
            "\nEP01 분기 검사 성공"
        )

        print(
            "모든 Stage에 "
            "high / medium / low "
            "분기가 존재합니다."
        )


if __name__ == "__main__":
    main()