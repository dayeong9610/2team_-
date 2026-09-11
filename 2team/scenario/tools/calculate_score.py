def calculate_episode_score(stage_scores):

    stage1 = stage_scores["EP01_STAGE01"]
    stage2 = stage_scores["EP01_STAGE02"]
    stage3 = stage_scores["EP01_STAGE03"]
    stage4 = stage_scores["EP01_STAGE04"]
    stage5 = stage_scores["EP01_STAGE05"]

    risk_awareness = round(
        stage1 / 3 * 100
    )

    refusal = round(
        (stage2 + stage3) / 6 * 100
    )

    help_request = round(
        (stage4 + stage5) / 6 * 100
    )

    return {
        "risk_awareness": risk_awareness,
        "refusal": refusal,
        "help_request": help_request
    }


if __name__ == "__main__":

    test_scores = {
        "EP01_STAGE01": 2,
        "EP01_STAGE02": 3,
        "EP01_STAGE03": 2,
        "EP01_STAGE04": 3,
        "EP01_STAGE05": 2
    }

    result = calculate_episode_score(
        test_scores
    )

    print(result)