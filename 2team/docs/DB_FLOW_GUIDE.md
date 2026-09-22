# 마냥이 DB 연동 실행 흐름 가이드

현재 학생 서비스는 **실시간 진행상태는 MemorySessionStore에 유지**하면서, DB가 정상일 때 학습 기록을 기존 DB 모델에도 저장합니다. DB 장애가 학생 학습 중단으로 이어지지 않게 두 저장 흐름을 분리합니다.

## 1. 최종 DB 역할

```text
llm_role
  Episode/시츄에이션 JSON(content), episode_id, 공개상태(status)
        ↓
chat_room
  한 번의 학생 학습 session_id, lr_num, limits
        ↓
chatting
  Stage별 USER 답변 / AI NPC 응답 + feedback
        ↓
score
  USER chat_id에 연결된 실제 GPT 평가 점수
```

별도 `ai_evaluation`, `episode_scenario` 모델은 사용하지 않습니다.

## 2. Episode 시작

```text
frontend createSession()
        ↓ POST /api/sessions
routes/sessions.py::start_session()
        ↓
scenario_engine.load_episode()
        ↓
MemorySessionStore.create_session()
        ↓ DB 정상일 때
persist_chat_room()
        ├─ llm_role 확인/INSERT
        └─ chat_room INSERT
```

`llm_role`에 없는 기본 JSON Episode를 학생이 처음 실행하면 시스템 Episode로 자동 등록됩니다.

## 3. 학생 답변 / GPT 평가

```text
frontend sendChat()
        ↓ POST /api/chat
routes/chat.py::chat()
        ↓
ai_service.evaluate_response()
        ↓
MemorySessionStore.apply_stage_result()
        ↓ 실제 GPT 평가 성공 + DB 정상
persist_stage_evaluation()
        ├─ chatting USER INSERT/UPDATE
        ├─ chatting AI INSERT/UPDATE
        └─ score 3개 INSERT/UPDATE
```

`retry_required=True` 또는 fallback 결과는 실제 GPT 평가 데이터가 아니므로 `score` 저장 대상에서 제외합니다.

## 4. 저장 데이터

### llm_role

- `lr_num`: PK
- `episode_id`: `EP01` 형태의 게임 식별자
- `title`
- `admin_id`
- `category`
- `content`: Episode JSON 원문
- `status`: `draft` / `published`

### chat_room

- `room_id`: PK
- `session_id`: 프론트/메모리 세션 UUID
- `lr_num`: 플레이한 `llm_role`
- `admin_id`: 해당 시츄에이션 작성자, 시스템 기본 Episode는 NULL 가능
- `limits`: 전체 Stage 수

### chatting

Stage마다 최대 두 행을 저장합니다.

- USER: `content=학생 답변`, `feedback=NULL`
- AI: `content=NPC 응답`, `feedback=교육 피드백`

공통으로 `room_id`, `stage_id`, `chatter`, `created_at`을 가집니다.

### score

USER `chat_id`에 다음 세 카테고리를 저장합니다.

- `risk_awareness`
- `refusal`
- `help_request`

각 점수 범위는 `0~3`입니다.

## 5. DB 장애 시

DB가 내려가면 `app.state.db_available=False`가 되고 DB INSERT를 건너뜁니다. 학생의 현재 학습은 기존 `MemorySessionStore`로 계속 진행됩니다.

즉:

```text
학생 서비스       계속 사용 가능
GPT 평가          정상 동작 가능
진행상태          메모리에 유지
DB 기록           DB 복구 전까지 건너뜀
```

## 6. 관리자 대시보드

관리자 대시보드는:

- 콘텐츠/관리자 현황 → `llm_role`, `admin_table`
- 실제 AI 평가 통계 → `score -> chatting -> chat_room -> llm_role`

관계로 조회합니다.

## 7. 기존 DB 마이그레이션

이미 PostgreSQL 테이블을 만든 상태라면 `SQLModel.metadata.create_all()`만으로 컬럼이 추가되지 않습니다.

반드시 DB 담당자가 한 번:

```text
docs/db_refactor_migration.sql
```

을 검토·백업 후 적용해야 합니다.
