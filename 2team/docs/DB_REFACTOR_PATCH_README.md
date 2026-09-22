# score / llm_role / chatting / chat_room 통합 패치

## 변경 목표

삭제:
- `backend/src/model/ai_evaluation.py`
- `backend/src/model/episode_scenario.py`

실사용:
- `llm_role`: Episode JSON 및 관리자 시츄에이션
- `chat_room`: 학생 학습 Session
- `chatting`: USER/AI 대화 및 AI feedback
- `score`: 실제 GPT 평가 점수

## 적용 순서

1. 현재 브랜치 백업 커밋
2. 패치 ZIP의 파일을 프로젝트 루트 기준으로 덮어쓰기
3. 기존 PostgreSQL DB를 이미 쓰고 있으면 `docs/db_refactor_migration.sql`을 DB 담당자가 1회 실행
4. 백엔드 재시작
5. EP01 등 학생 시나리오 1회 실행
6. 아래 쿼리로 확인

```sql
SELECT * FROM llm_role ORDER BY lr_num DESC;
SELECT * FROM chat_room ORDER BY room_id DESC;
SELECT * FROM chatting ORDER BY chat_id DESC;
SELECT * FROM score ORDER BY score_id DESC;
```

## 정상 저장 예시

한 Stage에서 학생이 답변하고 GPT 평가가 성공하면:

```text
llm_role  : Episode 1행 (없을 때만)
chat_room : Session 1행
chatting  : USER 1행 + AI 1행
score     : USER chat_id 기준 3행
```

fallback / 재입력은 `score`에 저장하지 않습니다.

## 주의

`SQLModel.metadata.create_all()`은 기존 테이블에 새 컬럼을 추가하지 않습니다. 이미 DB가 만들어져 있다면 Python 파일만 덮어쓰지 말고 `docs/db_refactor_migration.sql`도 적용해야 합니다.
