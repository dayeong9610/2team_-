import os

from functools import lru_cache

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI
)

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from app.ai.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt
)

from app.ai.evaluator import (
    AIResponse
)

from app.ai.safety import (
    check_user_message
)


load_dotenv()


@lru_cache
def get_structured_llm():

    model = os.getenv(
        "LLM_MODEL"
    )

    api_key = os.getenv(
        "GOOGLE_API_KEY"
    )

    if not model:
        raise RuntimeError(
            "LLM_MODEL is not configured"
        )

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured"
        )

    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.3
    )

    return llm.with_structured_output(
        AIResponse
    )


async def evaluate_response(
    episode_id: str,
    stage_id: str,
    user_message: str,
    stage_data: dict
) -> dict:

    # 1. Safety 검사
    safety_result = (
        check_user_message(
            user_message
        )
    )

    if safety_result.blocked:

        return {
            "npc_response": (
                "그 내용보다는 지금 상황에서 "
                "어떻게 안전하게 행동할지 "
                "생각해보자."
            ),

            "feedback": (
                safety_result.feedback
                or
                "안전한 대응 방법을 생각해보세요."
            ),

            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            }
        }

    # 2. Prompt 구성
    user_prompt = build_user_prompt(
        episode_id=episode_id,
        stage_id=stage_id,
        user_message=user_message,
        stage_data=stage_data
    )

    # 3. LLM 준비
    structured_llm = (
        get_structured_llm()
    )

    # 4. AI 호출
    result = await structured_llm.ainvoke(
        [
            SystemMessage(
                content=SYSTEM_PROMPT
            ),

            HumanMessage(
                content=user_prompt
            )
        ]
    )

    # 5. 응답 검증
    validated = (
        AIResponse.model_validate(
            result
        )
    )

    return validated.model_dump()