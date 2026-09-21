# 안전 검사를 거친 사용자 답변을 OpenAI GPT에 전달하고 결과를 검증하는 서비스입니다.
import os

from functools import lru_cache

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

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

from core.flow_trace import trace_flow


load_dotenv()

FILE = "backend/src/services/ai_service.py"


@lru_cache
def get_structured_llm():
    # LLM 객체를 한 번만 생성해 이후 요청에서 재사용합니다.
    model = os.getenv(
        "LLM_MODEL"
    )

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not model:
        # 모델명이 없으면 잘못된 외부 API 호출을 막고 설정 오류를 알립니다.
        raise RuntimeError(
            "LLM_MODEL is not configured"
        )

    if not api_key:
        # API 키가 없으면 인증되지 않은 요청을 보내지 않습니다.
        raise RuntimeError(
            "OPENAI_API_KEY is not configured"
        )

    trace_flow(
        FILE,
        "get_structured_llm",
        "CONFIG",
        {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "model": model,
            # OPENAI_API_KEY는 flow_trace에서 출력하지도 않지만,
            # 애초에 추적 데이터에 넣지 않습니다.
        },
    )

    llm = ChatOpenAI(
        model=model,
        api_key=api_key
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
    trace_flow(
        FILE,
        "evaluate_response",
        "IN",
        {
            "episode_id": episode_id,
            "stage_id": stage_id,
            "message_length": len(user_message),
            "evaluation_axis": stage_data.get("evaluation_axis"),
            "stage_type": stage_data.get("type"),
        },
    )

    # 1. Safety 검사
    safety_result = (
        check_user_message(
            user_message
        )
    )

    trace_flow(
        FILE,
        "evaluate_response",
        "SAFETY",
        {
            "blocked": safety_result.blocked,
            "reason": safety_result.reason,
            "language_violation": safety_result.language_violation,
            "language_severity": safety_result.language_severity,
        },
    )

    if safety_result.blocked:
        # 재입력이 필요한 경우에는 NPC가 교사/상담사처럼 안전 코칭하지 않습니다.
        # NPC 말풍선은 비우고, 안내는 전부 마냥이 feedback에서만 제공합니다.
        response = {
            "npc_response": "",
            "feedback": (
                safety_result.feedback
                or "현재 상황에서 실제로 어떻게 행동할지 한 문장으로 표현해보세요."
            ),
            "scores": {
                "risk_awareness": 0,
                "refusal": 0,
                "help_request": 0
            },
            "retry_required": True,
            "retry_reason": safety_result.reason,
        }

        trace_flow(
            FILE,
            "evaluate_response",
            "OUT_RETRY",
            {
                "retry_required": True,
                "retry_reason": safety_result.reason,
                "language_violation": safety_result.language_violation,
            },
        )
        return response

    # 2. Prompt 구성
    # 욕설이 섞였더라도 행동 의도는 보존하고, LLM에는 정제된 문장만 전달합니다.
    evaluation_message = safety_result.cleaned_message or user_message
    user_prompt = build_user_prompt(
        episode_id=episode_id,
        stage_id=stage_id,
        user_message=evaluation_message,
        stage_data=stage_data
    )

    trace_flow(
        FILE,
        "evaluate_response",
        "PROMPT_READY",
        {
            "episode_id": episode_id,
            "stage_id": stage_id,
            "prompt_length": len(user_prompt),
        },
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

    payload = validated.model_dump()

    # 비속어 탐지와 행동 평가는 서로 분리합니다. 행동 평가는 그대로 살리고,
    # 언어 사용에 대한 코칭만 마냥이 feedback 앞에 짧게 덧붙입니다.
    if safety_result.language_violation and safety_result.feedback:
        payload["feedback"] = (
            f"{safety_result.feedback} "
            f"{payload.get('feedback', '').strip()}"
        ).strip()

    trace_flow(
        FILE,
        "evaluate_response",
        "LLM_RESULT",
        {
            "scores": payload.get("scores"),
            "retry_required": payload.get("retry_required"),
            "retry_reason": payload.get("retry_reason"),
            "npc_response_length": len(payload.get("npc_response", "")),
            "feedback_length": len(payload.get("feedback", "")),
        },
    )

    if payload.get("retry_required") is True:
        response = {
            "npc_response": "",
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

        trace_flow(
            FILE,
            "evaluate_response",
            "OUT_RETRY",
            response,
        )
        return response

    payload["retry_required"] = False

    trace_flow(
        FILE,
        "evaluate_response",
        "OUT",
        payload,
    )

    return payload
