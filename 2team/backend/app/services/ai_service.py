#Backend ↔ AI 접점파일
from typing import Dict, Any

# ai 함수도 동일해야함
async def evaluate_response(
    episode_id: str,
    stage_id: str,
    user_message: str,
    stage_data: Dict[str, Any],
) -> Dict[str, Any]:

    # TODO:
    # feature/ai 완성 후 실제 AI 함수로 교체

    return {
        "npc_response": "왜? 다른 애들도 다 하는데 한 번만 해봐.",
        "feedback": "자신의 생각을 표현했어요.",
        "scores": {
            "risk_awareness": 1,
            "refusal": 2,
            "help_request": 0
        }
    }