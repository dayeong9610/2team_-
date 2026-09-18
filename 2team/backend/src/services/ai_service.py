# 안전 검사를 거친 사용자 답변을 Google Gemini에 전달하고 결과를 검증하는 서비스입니다.
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

from ai.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt
)

from ai.evaluator import (
    AIResponse
)

from ai.safety import (
    check_user_message
)


load_dotenv()


@lru_cache
def get_structured_llm():
    # LLM 객체를 한 번만 생성해 이후 요청에서 재사용합니다.
    model = os.getenv(
        "LLM_MODEL"
    )

    api_key = os.getenv(
        "GOOGLE_API_KEY"
    )

    if not model:
        # 모델명이 없으면 잘못된 외부 API 호출을 막고 설정 오류를 알립니다.
        raise RuntimeError(
            "LLM_MODEL is not configured"
        )

    if not api_key:
        # API 키가 없으면 인증되지 않은 요청을 보내지 않습니다.
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
    # 사용자 입력을 안전하게 검사한 뒤 구조화된 AI 평가 결과를 반환합니다.
    # 1. Safety 검사
    safety_result = (
        check_user_message(
            user_message
        )
    )

    if safety_result.blocked:
        # 평가할 수 없는/안전하지 않은 입력은 Stage를 완료 처리하지 않습니다.
        # 특히 "ㅇㅇ", "ㅋㅋ" 같은 짧은 반응을 실제 대응으로 오해해
        # NPC가 부자연스럽게 다음 반응을 만드는 문제를 막습니다.
        if safety_result.reason == "insufficient_response":
            npc_response = (
                "응? 어떻게 하겠다는 건지 잘 모르겠어. "
                "조금 더 구체적으로 말해줄래?"
            )
        else:
            npc_response = (
                "그 내용보다는 지금 상황에서 "
                "어떻게 안전하게 행동할지 생각해보자."
            )

        return {
            "npc_response": npc_response,
            "feedback": (
                safety_result.feedback
                or
                "안전한 대응 방법을 생각해보세요."
            ),
            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },
            # True이면 /chat 라우터가 Stage 결과를 저장하거나
            # 다음 Stage로 이동시키지 않습니다.
            "retry_required": True,
            "retry_reason": safety_result.reason,
        }

    # 2. Prompt 구성
    # 현재 에피소드와 Stage 정보를 포함한 사용자 프롬프트를 생성합니다.
    user_prompt = build_user_prompt(
        episode_id=episode_id,
        stage_id=stage_id,
        user_message=user_message,
        stage_data=stage_data
    )

    # 3. LLM 준비
    # 환경 설정을 확인한 구조화 출력용 LLM을 가져옵니다.
    structured_llm = (
        get_structured_llm()
    )

    # 4. AI 호출
    # 시스템 규칙과 현재 장면 프롬프트를 함께 전달합니다.
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
    # LLM 응답이 지정된 필드와 점수 범위를 지키는지 검증합니다.
    validated = (
        AIResponse.model_validate(
            result
        )
    )

    payload = validated.model_dump()

    # LLM이 현재 질문과 무관하거나 의미를 판단할 수 없는 답변으로 분류했다면
    # Stage 평가/점수 계산을 하지 않고 같은 장면에서 다시 입력받습니다.
    if payload.get("retry_required") is True:
        return {
            "npc_response": (
                "방금 말만으로는 어떻게 하겠다는 건지 잘 모르겠어. "
                "조금 더 구체적으로 말해줄래?"
            ),
            "feedback": (
                "현재 상황에서 무엇이 걱정되는지, 무엇을 하지 않을지, "
                "또는 누구에게 도움을 요청할지 실제로 말하듯 표현해보세요."
            ),
            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },
            "retry_required": True,
            "retry_reason": (
                payload.get("retry_reason")
                or "irrelevant_or_unclear_response"
            ),
        }

    payload["retry_required"] = False
    return payload
