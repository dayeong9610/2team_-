# Scenario 데이터 규칙

## Episode

현재 구현 Episode

EP01
시험기간 스터디 그룹

---

## Stage 구조

EP01_STAGE01
위험 인지

↓

EP01_STAGE02
거절

↓

EP01_STAGE03
또래 압박

↓

EP01_STAGE04
도움 요청

↓

EP01_STAGE05
최종 판단

↓

RESULT

---

## 평가 점수

각 Stage는 0~3점으로 평가한다.

0 = 적절한 대응 없음
1 = 대응이 매우 약함
2 = 적절하지만 보완 필요
3 = 명확하고 적절한 대응

---

## 결과 계산

risk_awareness

Stage01 / 3 * 100


refusal

(Stage02 + Stage03) / 6 * 100


help_request

(Stage04 + Stage05) / 6 * 100

---

## AI 역할

AI는 다음만 담당한다.

- 사용자 자유문장 평가
- NPC 후속 반응
- 마냥이 피드백
- Stage 점수 생성

AI는 다음 Stage를 결정하지 않는다.

next_stage는 episode JSON에서 결정한다.

---

## 개인정보

사용자의 대화 원문은
분석 DB에 영구 저장하지 않는다.

저장 가능:

- session_id
- episode_id
- stage_id
- score
- axis
- completed

영구 저장하지 않음:

- 사용자 자유문장 원문
## Branch 규칙

각 Stage의 사용자 응답은 0~3점으로 평가한다.

- 3점: high
- 2점: medium
- 0~1점: low

Branch는 NPC 반응 및 마냥이 코칭을
선택하기 위한 용도로 사용한다.

Branch가 핵심 Scenario 흐름을 변경하지 않는다.

EP01 흐름은 항상 다음과 같다.

EP01_STAGE01
→ EP01_STAGE02
→ EP01_STAGE03
→ EP01_STAGE04
→ EP01_STAGE05
→ RESULT

next_stage는 AI가 결정하지 않는다.
Scenario 데이터에서 결정한다.