# DB 통합 구조 가이드

이번 수정은 별도 `ai_evaluation`, `episode_scenario` 모델을 제거하고 DB 담당자가 기존에 설계한 네 모델을 실제 학생 서비스에 연결합니다.

## 최종 역할

```text
llm_role
  └─ Episode/시츄에이션 JSON(content), episode_id, 공개상태(status)
       ↓ 1:N
chat_room
  └─ 학생의 한 번의 학습 session_id, 전체 Stage 수(limits)
       ↓ 1:N
chatting
  ├─ USER: 실제 학생 답변
  └─ AI: NPC 응답 + 교육 피드백
       ↓ USER chat_id 1:N
score
  ├─ risk_awareness
  ├─ refusal
  └─ help_request
```

## 학생 실행 흐름

### Episode 시작

`POST /api/sessions`

1. JSON/DB에서 Episode 조회
2. 기존 `MemorySessionStore` 세션 생성 (실시간 서비스 안정성 유지)
3. DB가 정상일 때 `llm_role`에 Episode가 없으면 등록
4. `chat_room`에 `session_id`, `lr_num`, `limits` INSERT

### 학생 답변

`POST /api/chat`

1. GPT 평가
2. 메모리 진행상태 갱신
3. 실제 GPT 평가 성공이고 fallback이 아닐 때만 DB 저장
4. `chatting` USER 행에 학생 답변 저장
5. `chatting` AI 행에 NPC 응답과 feedback 저장
6. USER `chat_id`에 `score` 3개 INSERT/UPDATE

`retry_required=True` 또는 fallback 결과는 점수 DB 저장 대상에서 제외됩니다.

## DB 장애 시

DB가 내려가도 `MemorySessionStore` 기반 학생 학습은 그대로 진행됩니다. DB 저장 함수는 예외를 학생 API 응답으로 전파하지 않습니다.

## 기존 DB 마이그레이션

기존 PostgreSQL DB를 사용 중이면 `docs/db_refactor_migration.sql`을 1회 적용해야 합니다.

이 스크립트는:

- `episode_scenario` 데이터를 `llm_role`로 이관
- `ai_evaluation` 데이터를 `chat_room/chatting/score`로 가능한 범위에서 이관
- 필요한 컬럼/제약조건 추가
- 이관 후 `ai_evaluation`, `episode_scenario` 테이블 삭제

운영/공용 DB에서는 반드시 백업 후 적용하세요.
