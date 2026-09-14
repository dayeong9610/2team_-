from pydantic import BaseModel
from typing import Optional


class SafetyResult(BaseModel):
    blocked: bool
    reason: Optional[str] = None
    feedback: Optional[str] = None


DANGEROUS_PATTERNS = [
    "어디서 구해",
    "어디서 사",
    "구매 방법",
    "사는 방법",
    "제조 방법",
    "만드는 방법",
    "복용량",
    "얼마나 먹어",
    "숨기는 방법",
    "안 걸리는 방법",
]

PROMPT_INJECTION_PATTERNS = [
    "이전 지시 무시",
    "위 지시 무시",
    "규칙 무시",
    "프롬프트 무시",
    "시스템 프롬프트",
    "너의 지시를 무시",
]


def check_user_message(message: str) -> SafetyResult:

    text = message.strip().lower()

    # 빈 입력
    if not text:
        return SafetyResult(
            blocked=True,
            reason="empty_message",
            feedback="답변을 입력한 뒤 다시 시도해 주세요."
        )

    # 위험정보 요청
    for pattern in DANGEROUS_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="dangerous_information",
                feedback=(
                    "위험한 약물의 구매·제조·복용·은폐 방법은 "
                    "안내할 수 없어요. 현재 상황에서 자신을 안전하게 "
                    "지키는 방법을 생각해보세요."
                )
            )

    # Prompt Injection
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="prompt_injection",
                feedback=(
                    "현재 에피소드의 안전한 대응 연습 범위 안에서 "
                    "답변해 주세요."
                )
            )

    return SafetyResult(blocked=False)