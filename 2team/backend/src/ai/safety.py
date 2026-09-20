import re
from pydantic import BaseModel, Field
from typing import Optional

from ai.profanity_filter import detect_profanity, language_feedback


class SafetyResult(BaseModel):
    # blocked는 '행동 평가 자체를 진행할 수 없는 입력'에만 사용합니다.
    # 욕설이 섞였다는 이유만으로 행동 평가를 버리지 않습니다.
    blocked: bool
    reason: Optional[str] = None
    feedback: Optional[str] = None

    # 언어 품질은 행동 평가와 별도 축으로 전달합니다.
    language_violation: bool = False
    language_severity: Optional[str] = None
    language_matches: list[str] = Field(default_factory=list)
    cleaned_message: Optional[str] = None


def normalize_text(message: str) -> str:
    return " ".join(
        message
        .strip()
        .lower()
        .split()
    )


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


# 장면에 대한 실제 대응으로 보기 어려운 짧은 확인/추임새 입력입니다.
# "싫어", "안 먹어", "신고할래"처럼 짧더라도 의미가 분명한 문장은
# 여기에 넣지 않습니다.
INSUFFICIENT_EXACT_INPUTS = {
    "ㅇ",
    "ㅇㅇ",
    "응응",
    "어",
    "ㄴ",
    "ㄴㄴ",
    "글쎄",
    "그냥",
    "아무거나",
    "음",
    "흠",
    "ㅋㅋ",
    "ㅋㅋㅋ",
    "ㅎㅎ",
    "ㅎㅎㅎ",
}


def is_insufficient_response(message: str) -> bool:
    """실제 대응 의도를 판단하기 어려운 입력인지 확인합니다."""
    text = normalize_text(message)
    compact = re.sub(r"\s+", "", text)

    if not compact:
        return True

    if compact in INSUFFICIENT_EXACT_INPUTS:
        return True

    # 자음/웃음/울음/구두점만 반복된 입력도 실제 답변으로 보지 않습니다.
    if re.fullmatch(r"[ㅇㅋㅎㅠㅜㄴ.!?~]+", compact):
        return True

    return False


def check_user_message(message: str) -> SafetyResult:
    text = normalize_text(message)

    if not text:
        return SafetyResult(
            blocked=True,
            reason="empty_message",
            feedback="답변을 입력한 뒤 다시 시도해 주세요.",
            cleaned_message="",
        )

    profanity = detect_profanity(message)
    cleaned_message = profanity.cleaned_text or message.strip()

    # 욕설을 걷어낸 뒤 실제 대응 내용이 하나도 남지 않는 경우에만 재입력합니다.
    # 예: "씨발" -> 재입력 / "씨발 난 안 먹을래" -> 거절 행동은 정상 평가.
    if profanity.detected and is_insufficient_response(profanity.cleaned_text):
        return SafetyResult(
            blocked=True,
            reason="abusive_only",
            feedback=language_feedback(profanity.severity),
            language_violation=True,
            language_severity=profanity.severity,
            language_matches=[match.term for match in profanity.matches],
            cleaned_message=profanity.cleaned_text,
        )

    # 욕설이 아닌 단순 추임새/무의미 입력은 기존처럼 재입력합니다.
    if not profanity.detected and is_insufficient_response(message):
        return SafetyResult(
            blocked=True,
            reason="insufficient_response",
            feedback=(
                "지금 답변만으로는 어떤 대응을 하려는지 알기 어려워요. "
                "왜 그렇게 생각했는지 또는 무엇을 하겠는지 "
                "실제로 말하듯 한 문장으로 표현해보세요."
            ),
            cleaned_message=message.strip(),
        )

    # 위험정보 요청은 행동 연습이 아니라 구체적 위험정보 요청이므로 차단합니다.
    for pattern in DANGEROUS_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="dangerous_information",
                feedback=(
                    "위험한 약물의 구매·제조·복용·은폐 방법은 "
                    "안내할 수 없어요. 현재 상황에서 자신을 안전하게 "
                    "지키는 방법을 생각해보세요."
                ),
                language_violation=profanity.detected,
                language_severity=profanity.severity,
                language_matches=[match.term for match in profanity.matches],
                cleaned_message=cleaned_message,
            )

    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in text:
            return SafetyResult(
                blocked=True,
                reason="prompt_injection",
                feedback="현재 에피소드의 안전한 대응 연습 범위 안에서 답변해 주세요.",
                language_violation=profanity.detected,
                language_severity=profanity.severity,
                language_matches=[match.term for match in profanity.matches],
                cleaned_message=cleaned_message,
            )

    # 여기까지 왔다면 욕설이 섞였어도 행동 의도는 평가할 수 있습니다.
    return SafetyResult(
        blocked=False,
        feedback=(language_feedback(profanity.severity) if profanity.detected else None),
        language_violation=profanity.detected,
        language_severity=profanity.severity,
        language_matches=[match.term for match in profanity.matches],
        cleaned_message=cleaned_message,
    )


FALLBACK_MEANINGFUL_MARKERS = (
    # 거절 / 회피 / 안전 행동
    "싫", "안 먹", "먹지", "거절", "안 할", "하지 않", "필요 없",
    "그만", "됐어", "괜찮아", "자리", "떠날", "나갈", "피할", "차단",

    # 수락 / 위험한 선택도 '의미 있는 대응'이므로 평가 가능
    "네", "응", "웅", "예", "넵", "오케이", "okay", "ok", "ㅇㅋ",
    "먹을래", "먹을게", "먹겠다", "먹어볼", "먹어 보", "먹어야",
    "써볼", "사용할", "해볼", "해 볼", "마실래", "마실게",
    "받을래", "받을게", "따라할", "같이 할", "나도 먹", "나만 먹",

    # 위험 인지
    "위험", "수상", "이상", "출처", "정체", "성분", "안전", "모르",
    "확인", "불분명", "의심", "걱정", "약", "알약", "사진", "포장",
    "처방", "약국", "병원", "믿", "문제",

    # 도움 요청 / 신고
    "선생", "교사", "부모", "보호자", "어른", "상담", "신고", "도움",
    "119", "112", "보건", "알리", "말할", "말하", "연락", "구급", "도와",

    # 판단 / 행동 의사 표현
    "몰라", "모름", "모르겠",
    "아닌 것", "하지 말", "해야", "하겠", "할래", "할게",
    "생각", "같아", "보여", "왜", "좋아", "싫어"
)


def is_fallback_response_meaningful(message: str, stage_data: dict | None = None) -> bool:
    """AI 장애 시에도 욕설과 행동 의도를 분리해 판단합니다."""
    profanity = detect_profanity(message)
    candidate = profanity.cleaned_text if profanity.detected else message

    if is_insufficient_response(candidate):
        return False

    text = normalize_text(candidate)

    if any(marker in text for marker in FALLBACK_MEANINGFUL_MARKERS):
        return True

    compact = re.sub(r"[^0-9a-z가-힣]", "", text)
    if len(compact) < 4:
        return False

    return False
