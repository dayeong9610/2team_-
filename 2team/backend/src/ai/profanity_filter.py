"""청소년 서비스용 비속어/모욕 표현 탐지기.

목표는 '단어 하나가 보이면 대화를 막기'가 아니라,
1) 부적절한 표현은 별도로 탐지하고
2) 사용자가 말한 실제 행동 의도는 가능한 한 계속 평가하며
3) 강도에 따라 마냥이의 언어 피드백 수준만 조절하는 것입니다.

리스트는 팀이 제공한 기존 욕설 목록과 게임 채팅 필터 목록에서
오탐 가능성이 낮은 표현 위주로 선별했습니다. 중립적인 교육 문맥에서도
등장할 수 있는 성/신체/약물 용어는 단어만으로 차단하지 않습니다.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


SEVERITY_RANK = {
    "mild": 1,
    "strong": 2,
    "severe": 3,
}

# 가족 모욕, 성적 모욕, 혐오/차별 비하처럼 청소년 서비스에서 가장 강하게
# 경고할 표현. '강간', '성관계'처럼 교육 문맥에서 정상적으로 나올 수 있는
# 중립 용어는 의도적으로 포함하지 않습니다.
SEVERE_TERMS = {
    "느금마", "니애미", "니에미", "니어미", "애미", "애비",
    "창녀", "걸레년", "갈보", "개보지", "개자지",
    "쌍년", "쌍놈", "후레자식", "후레년",
    "짱깨", "쪽바리", "칭챙총", "니그로", "nigger", "nigga",
    "faggot", "kike",
}

# 강한 욕설과 직접적인 인신공격. 흔한 우회 표기도 함께 포함합니다.
STRONG_TERMS = {
    "씨발", "시발", "시빨", "씨빨", "씹발", "쉬발", "슈발",
    "ㅅㅂ", "ㅆㅂ", "시1발", "씨1발", "c발", "c8", "18놈", "18년",
    "병신", "븅신", "빙신", "ㅂㅅ", "병쉰",
    "개새끼", "개새기", "개쉑", "개쉐끼", "개쌔끼", "개세끼",
    "새끼", "새키", "새퀴", "쉑", "쉐끼",
    "좆", "좃", "좇", "졷", "조또", "조옷", "ㅈ같", "좆같",
    "지랄", "지럴", "ㅈㄹ", "쥐랄",
    "썅", "씨팔", "십팔", "씹팔",
    "fuck", "motherfuck", "mother fuck", "asshole", "bitch", "cunt",
    "cocksucker", "bullshit", "prick", "twat",
}

# 비교적 약한 비속어/모욕. 차단보다 '표현을 순화해보자'는 코칭에 사용합니다.
MILD_TERMS = {
    "존나", "졸라", "전나", "존내", "존니",
    "개같", "개같은", "개놈", "개년", "개자식",
    "미친놈", "미친년", "미친", "또라이", "똘추", "돌아이",
    "닥쳐", "꺼져", "엿먹어", "대가리", "눈깔",
    "쉣", "shit", "sh*t", "wtf", "ㅗ", "ㅗㅗ",
}

# 리스트 밖의 흔한 변형을 잡기 위한 고신뢰 정규식. 너무 넓은 패턴은
# 정상 문장을 오탐할 수 있으므로 핵심 욕설 계열에만 제한합니다.
REGEX_PATTERNS: tuple[tuple[str, str, str], ...] = (
    (r"[씨시쉬슈쒸씌]{1,2}[\s._*\-]*[발빨벌팔펄]", "strong", "시발계열"),
    (r"ㅅ[\s._*\-]*ㅂ", "strong", "ㅅㅂ"),
    (r"ㅂ[\s._*\-]*ㅅ", "strong", "ㅂㅅ"),
    (r"ㅈ[\s._*\-]*ㄹ", "strong", "ㅈㄹ"),
    (r"개[\s._*\-]*(새끼|새기|쉑|쉐끼|쌔끼|세끼)", "strong", "개새끼계열"),
    (r"좆+[\s._*\-]*같", "strong", "좆같계열"),
)


@dataclass(frozen=True)
class ProfanityMatch:
    term: str
    severity: str


@dataclass(frozen=True)
class ProfanityResult:
    detected: bool
    severity: str | None
    matches: tuple[ProfanityMatch, ...]
    cleaned_text: str


def normalize_for_filter(text: str) -> str:
    """유니코드/공백/대소문자를 정리해 우회 표기를 조금 더 잘 잡습니다."""
    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = normalized.replace("\u200b", "").replace("\ufeff", "")
    return " ".join(normalized.split())


def _all_terms() -> tuple[tuple[str, str], ...]:
    items: list[tuple[str, str]] = []
    items.extend((term, "severe") for term in SEVERE_TERMS)
    items.extend((term, "strong") for term in STRONG_TERMS)
    items.extend((term, "mild") for term in MILD_TERMS)
    # 긴 표현을 먼저 처리하면 '개새끼'가 '새끼'보다 먼저 제거됩니다.
    items.sort(key=lambda item: len(item[0]), reverse=True)
    return tuple(items)


ALL_TERMS = _all_terms()


def detect_profanity(message: str) -> ProfanityResult:
    text = normalize_for_filter(message)
    compact = re.sub(r"\s+", "", text)
    matches: list[ProfanityMatch] = []

    for term, severity in ALL_TERMS:
        normalized_term = normalize_for_filter(term)
        compact_term = re.sub(r"\s+", "", normalized_term)
        if normalized_term in text or (compact_term and compact_term in compact):
            matches.append(ProfanityMatch(term=term, severity=severity))

    for pattern, severity, label in REGEX_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            matches.append(ProfanityMatch(term=label, severity=severity))

    # 같은 계열이 여러 번 잡혀도 사용자에게 원문/목록을 노출할 필요는 없습니다.
    unique: dict[tuple[str, str], ProfanityMatch] = {
        (match.term, match.severity): match for match in matches
    }
    deduped = tuple(unique.values())

    highest = None
    if deduped:
        highest = max(deduped, key=lambda item: SEVERITY_RANK[item.severity]).severity

    cleaned = redact_profanity(message)
    return ProfanityResult(
        detected=bool(deduped),
        severity=highest,
        matches=deduped,
        cleaned_text=cleaned,
    )


def redact_profanity(message: str) -> str:
    """평가용 문장에서 고신뢰 욕설만 제거하고 행동 의도는 남깁니다."""
    cleaned = unicodedata.normalize("NFKC", message)

    for term, _severity in ALL_TERMS:
        cleaned = re.sub(re.escape(term), " ", cleaned, flags=re.IGNORECASE)

    for pattern, _severity, _label in REGEX_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def language_feedback(severity: str | None) -> str:
    if severity == "severe":
        return "상대를 모욕하거나 혐오하는 표현은 빼고, 네가 하려는 행동을 직접 말해보자."
    if severity == "strong":
        return "강한 욕설은 빼고, 지금 상황에서 네가 어떻게 행동할지 말해보자."
    return "비속어는 조금 순화하고, 네 생각과 행동을 직접 표현해보자."
