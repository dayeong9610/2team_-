# EP01 Scenario API Contract

## Episode

episode_id

EP01

title

시험기간 스터디 그룹

---

# 1. 에피소드 목록

GET /api/episodes

응답

[
  {
    "episode_id": "EP01",
    "title": "시험기간 스터디 그룹",
    "description": "시험기간 스터디 그룹에서 발생하는 상황에 대응해봅니다.",
    "total_stages": 5
  }
]

---

# 2. 에피소드 상세

GET /api/episodes/EP01

응답에 포함할 값

- episode_id
- title
- background
- total_stages

---

# 3. Stage 조회

GET /api/episodes/EP01/stages/EP01_STAGE01

응답에 포함할 값

- episode_id
- stage_id
- stage_number
- title
- location
- description
- messages
- question
- evaluation_axis
- total_stages

주의:

evaluation_criteria와 rubric은
Frontend에 직접 전달하지 않아도 된다.

평가 기준은 Backend/AI 내부에서 사용한다.

---

# 4. 사용자 답변

POST /api/chat

Request

{
  "session_id": "temporary-session-id",
  "episode_id": "EP01",
  "stage_id": "EP01_STAGE01",
  "message": "무슨 약인지 모르니까 위험한 것 같아."
}

---

# 5. Chat 응답

Response

{
  "episode_id": "EP01",
  "stage_id": "EP01_STAGE01",
  "npc_response": "그렇게까지 걱정할 필요 있나?",
  "feedback": "출처와 안전성을 의심한 점이 좋아요.",
  "axis": "risk_awareness",
  "score": 3,
  "next_stage": "EP01_STAGE02",
  "episode_completed": false
}

---

# 6. 마지막 Stage

EP01_STAGE05 완료 시

{
  "episode_id": "EP01",
  "stage_id": "EP01_STAGE05",
  "npc_response": "...",
  "feedback": "...",
  "axis": "help_request",
  "score": 3,
  "next_stage": null,
  "episode_completed": true
}

---

# 7. Result

GET /api/sessions/{session_id}/episodes/EP01/result

Response

{
  "episode_id": "EP01",
  "title": "시험기간 스터디 그룹",

  "scores": {
    "risk_awareness": 67,
    "refusal": 83,
    "help_request": 83
  },

  "completed": true
}