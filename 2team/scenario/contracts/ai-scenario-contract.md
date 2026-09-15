# AI ↔ Scenario Contract

## AI 역할

AI는 사용자의 자유문장을 평가한다.

AI는 다음 Stage를 결정하지 않는다.

AI는 Scenario의 핵심 사건, Stage,
분기 또는 엔딩을 변경하지 않는다.


## AI Response

AI 평가 결과는 다음 구조를 따른다.

{
  "stage_id": "EP01_STAGE02",
  "axis": "refusal",
  "score": 2,
  "reason": "거절 의사는 표현했지만 표현이 다소 소극적임"
}


## stage_id

허용되는 Stage ID

EP01_STAGE01
EP01_STAGE02
EP01_STAGE03
EP01_STAGE04
EP01_STAGE05


## axis

허용되는 평가축

risk_awareness
refusal
help_request


## Score

점수 범위

0 ~ 3


## Branch Mapping

3점
→ high

2점
→ medium

0~1점
→ low


## Stage별 Axis

EP01_STAGE01
→ risk_awareness

EP01_STAGE02
→ refusal

EP01_STAGE03
→ refusal

EP01_STAGE04
→ help_request

EP01_STAGE05
→ help_request


## 중요 규칙

AI는 next_stage를 생성하지 않는다.

next_stage는
episode01-branches.json의
Scenario 데이터에서 결정한다.