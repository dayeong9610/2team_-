# 마냥이 관리자 대시보드 + 실제 AI 평가 DB 저장 패치

기준 파일: `2team_-최신.zip`

## 이번 패치에서 바뀌는 것

1. `/admins/` 로그인 후 화면을 콘텐츠/관리자 현황 대시보드로 변경
   - 전체 시츄에이션 수
   - 내가 작성한 시츄에이션 수
   - 전체 관리자 수
   - 활성 관리자 수
   - 카테고리별 시츄에이션 수
   - 최근 등록 시츄에이션 5건
   - 실제 AI 평가 저장 건수 및 3개 평가축 평균

2. 기존 관리자 기능 유지
   - 새 시츄에이션 작성
   - 전체 시츄에이션 목록
   - 내가 작성한 시츄에이션
   - 시츄에이션 상세/수정/삭제
   - 회원정보 수정/로그아웃/회원탈퇴

3. 실제 GPT 평가 결과 DB 저장
   - 신규 테이블: `ai_evaluation`
   - 저장 항목: `session_id`, `episode_id`, `stage_id`, 3개 점수, `LLM_PROVIDER`, `LLM_MODEL`, 생성 시각
   - 사용자 입력 원문/NPC 답변/피드백 원문은 저장하지 않음
   - `retry_required=True` 결과는 저장하지 않음
   - fallback 결과는 실제 AI 평가가 아니므로 저장하지 않음
   - DB 장애 시 저장을 건너뛰고 학생 서비스는 계속 진행

## 왜 기존 `score` 테이블에 바로 넣지 않았나

현재 `score.chat_id`는 `chatting.chat_id`를 참조하고, `chatting`은 다시 `chat_room`을 필요로 합니다.
하지만 현재 학생용 `/api/sessions` + `/api/chat` 흐름은 `MemorySessionStore`를 사용하며 `chat_room/chatting` 행을 만들지 않습니다.

따라서 기존 `score`에 억지로 넣으려면 `chat_room -> admin_table/llm_role`까지 가짜 또는 추가 연결을 만들어야 합니다.
이번 패치는 기존 DB 테이블/FK를 건드리지 않고 실제 AI 평가만 안전하게 남기도록 `ai_evaluation`을 추가했습니다.

## 적용 파일

- `backend/src/model/ai_evaluation.py` (신규)
- `backend/src/model/__init__.py`
- `backend/src/services/evaluation_log_service.py` (신규)
- `backend/src/database/connection.py`
- `backend/src/routes/chat.py`
- `backend/src/routes/admin_route.py`
- `backend/src/templates/admin/admin_index.html`

`frontend/vite.config.ts`는 수정하지 않습니다. 현재 `/admins` 프록시가 정상 동작하는 상태를 그대로 유지하세요.

## 적용 방법

프로젝트 루트가 `2team`이라고 할 때 이 ZIP의 `backend` 폴더를 같은 위치에 덮어씁니다.
적용 전 현재 로컬 수정사항은 커밋하거나 백업하는 것을 권장합니다.

백엔드를 재시작하면 DB 연결 성공 시 `SQLModel.metadata.create_all()`이 기존 테이블을 유지한 채 `ai_evaluation` 테이블만 새로 생성합니다.

터미널에서 아래 로그를 확인하세요.

```text
[DB] connection ready
```

이후 학생 화면에서 GPT가 정상 평가한 Stage를 1회 진행하면 아래와 같은 로그가 나옵니다.

```text
[AI EVALUATION DB INSERT] session_id=..., episode_id=EP01, stage_id=EP01_STAGE01
```

동일 `session_id + stage_id`가 다시 저장되면 중복 INSERT 대신 UPDATE 처리합니다.

## DB 확인 SQL

```sql
SELECT
    evaluation_id,
    session_id,
    episode_id,
    stage_id,
    risk_awareness,
    refusal,
    help_request,
    llm_provider,
    llm_model,
    created_at
FROM ai_evaluation
ORDER BY evaluation_id DESC;
```

## 관리자 화면 확인

1. 백엔드 재시작
2. 프론트(Vite) 재시작은 `vite.config.ts`를 변경하지 않았다면 필수 아님
3. `http://localhost:5173/admins/` 접속
4. 로그인
5. 대시보드 통계와 기존 시츄에이션 관리 버튼 확인
6. 학생 시나리오를 정상 GPT 평가로 진행
7. `/admins/` 새로고침 후 `실제 AI 평가 저장 현황` 숫자 확인

## 검증

패치 Python 파일은 AST/컴파일 문법 검사를 통과했습니다.
현재 실행 환경에는 프로젝트의 `sqlmodel` 의존성이 설치되어 있지 않아 실제 PostgreSQL 연결 통합 테스트는 수행하지 않았습니다. 로컬 프로젝트 환경에서 백엔드 재시작 후 위 순서로 최종 확인하세요.
