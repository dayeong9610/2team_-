from app.core.session_store import (
    SessionStore
)


def test_session_store():

    store = SessionStore()

    store.create_session(
        session_id="TEST001",
        episode_id="EP01",
        first_stage="EP01_STAGE01"
    )

    session = store.get_session(
        "TEST001"
    )

    assert session is not None

    assert (
        session["episode_id"]
        == "EP01"
    )

    assert (
        session["current_stage"]
        == "EP01_STAGE01"
    )

# 점수 테스트
def test_add_scores():

    store = SessionStore()

    store.create_session(
        "TEST001",
        "EP01",
        "EP01_STAGE01"
    )

    store.add_scores(
        "TEST001",
        {
            "risk_awareness": 3,
            "refusal": 1,
            "help_request": 0
        }
    )

    result = store.get_result(
        "TEST001"
    )

    assert (
        result["scores"][
            "risk_awareness"
        ]
        == 3
    )

    assert (
        result["scores"][
            "refusal"
        ]
        == 1
    )


def test_session_copy():

    store = SessionStore()

    store.create_session(
        "TEST001",
        "EP01",
        "EP01_STAGE01"
    )

    session = store.get_session(
        "TEST001"
    )

    session[
        "scores"
    ][
        "refusal"
    ] = 999

    original = store.get_session(
        "TEST001"
    )

    assert (
        original["scores"][
            "refusal"
        ]
        == 0
    )