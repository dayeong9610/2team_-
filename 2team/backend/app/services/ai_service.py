from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt


async def evaluate_response(
    episode_id: str,
    stage_id: str,
    user_message: str,
    stage_data: dict
) -> dict:

    user_prompt = build_user_prompt(
        episode_id=episode_id,
        stage_id=stage_id,
        user_message=user_message,
        stage_data=stage_data
    )

    # 여기서 실제 LLM API 호출