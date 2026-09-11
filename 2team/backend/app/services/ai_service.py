async def evaluate_user_response(
    episode_id: str,
    stage_id: str,
    scene_context: str,
    evaluation_criteria: str,
    user_message: str
):
    # LLM 호출

    return {
        "npc_response": "...",
        "feedback": "...",
        "scores": {
            "risk_awareness": 0,
            "refusal": 0,
            "help_request": 0
        }
    }