import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EPISODE_PATH = BASE_DIR / "episodes" / "episode01.json"
RUBRIC_PATH = BASE_DIR / "rubrics" / "episode01-rubric.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def validate_episode(episode, rubric):

    errors = []

    # 1. 기본 정보 검사
    if "episode_id" not in episode:
        errors.append("episode_id가 없습니다.")

    if "title" not in episode:
        errors.append("title이 없습니다.")

    if "stages" not in episode:
        errors.append("stages가 없습니다.")
        return errors

    stages = episode["stages"]

    # 2. Stage 수 확인
    if len(stages) != episode.get("total_stages"):
        errors.append(
            f"total_stages={episode.get('total_stages')}인데 "
            f"실제 Stage 수는 {len(stages)}개입니다."
        )

    stage_ids = []

    for stage in stages:

        required_fields = [
            "stage_id",
            "stage_number",
            "title",
            "messages",
            "question",
            "evaluation_axis",
            "evaluation_criteria"
        ]

        for field in required_fields:
            if field not in stage:
                errors.append(
                    f"{stage.get('stage_id', 'UNKNOWN')}에 "
                    f"{field}가 없습니다."
                )

        if "stage_id" in stage:
            stage_ids.append(stage["stage_id"])

    # 3. next_stage 연결 검사
    for stage in stages:

        next_stage = stage.get("next_stage")

        if next_stage is not None and next_stage not in stage_ids:
            errors.append(
                f"{stage['stage_id']}의 next_stage "
                f"{next_stage}가 존재하지 않습니다."
            )

    # 4. 마지막 Stage 검사
    if stages:
        last_stage = stages[-1]

        if last_stage.get("next_stage") is not None:
            errors.append(
                "마지막 Stage의 next_stage는 null이어야 합니다."
            )

    # 5. Rubric 검사
    rubric_stages = rubric.get("stages", {})

    for stage in stages:

        stage_id = stage.get("stage_id")

        if stage_id not in rubric_stages:
            errors.append(
                f"{stage_id}에 대한 Rubric이 없습니다."
            )

    return errors


def main():

    episode = load_json(EPISODE_PATH)
    rubric = load_json(RUBRIC_PATH)

    errors = validate_episode(
        episode,
        rubric
    )

    print("\nEP01 시나리오 검사 시작\n")

    if errors:

        print("검사 실패\n")

        for error in errors:
            print(f"- {error}")

    else:

        print("검사 성공")
        print("EP01 시나리오 구조에 문제가 없습니다.")

        print("\nStage 흐름")

        for stage in episode["stages"]:

            print(
                f"{stage['stage_id']} "
                f"→ {stage.get('next_stage')}"
            )


if __name__ == "__main__":
    main()