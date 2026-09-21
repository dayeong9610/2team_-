# 마냥이

청소년이 약물·유해 상황에서 **위험을 인지하고, 거절하고, 도움을 요청하는 방법을 실제 대화처럼 연습**하는 AI 기반 교육 서비스입니다.

정답을 고르는 객관식 게임이 아니라, 사용자가 직접 문장을 입력하면 NPC가 역할에 맞게 반응하고 `마냥이`가 학습 피드백을 제공합니다.

---

## 1. 주요 기능

### 학생용 게임

- Episode / Stage 기반 상황 학습
- 실제 대화처럼 자유 문장 입력
- NPC 역할 기반 AI 반응
- 청소년 대상 언어·욕설 필터링
- 의미가 분명한 답변은 단순 키워드가 아니라 행동 의도를 기준으로 평가
- 평가하기 어려운 짧은 입력은 같은 Stage에서 재입력 유도
- LLM 장애 시 검수된 fallback 시나리오로 학습 지속
- 마냥이 코칭 피드백
- 3개 평가축 기록
  - 위험 인지 `risk_awareness`
  - 거절 대응 `refusal`
  - 도움 요청 `help_request`
- Episode 2·3 장면 시각화 및 장면 → 대화 전환 UX
- 모바일 / 데스크톱 반응형 지원

### 관리자

- 관리자 회원가입 / 로그인
- Episode JSON 작성 및 검증
- 초안(`draft`) 저장
- 공개(`published`) / 비공개 전환
- 관리자 작성 Episode 수정 / 삭제
- 공개된 DB Episode를 학생 게임에 즉시 반영
- 콘텐츠 / 관리자 현황 대시보드
- 실제 AI 평가 저장 현황 확인
- Episode / Stage / 평가축별 개발자 피드백용 점수 확인

---

## 2. 기술 스택

### Frontend

- React 19
- TypeScript
- Vite
- React Router

### Backend

- Python
- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL
- Jinja2 관리자 화면
- JWT 인증

### AI

- OpenAI API
- LangChain OpenAI
- Pydantic 구조화 응답

---

## 3. 프로젝트 구조

README를 Repository 루트에 두는 기준입니다.

```text
.
├─ README.md
└─ 2team/
   ├─ backend/
   │  ├─ .env                  # 로컬 전용, Git에 올리지 않음
   │  ├─ .env.example
   │  ├─ src/
   │  │  ├─ app.py            # FastAPI 시작점
   │  │  ├─ ai/               # Prompt / Safety / 평가 스키마
   │  │  ├─ auth/             # 관리자 인증
   │  │  ├─ core/             # Scenario / Session / Trace
   │  │  ├─ database/         # PostgreSQL 연결
   │  │  ├─ model/            # SQLModel 테이블
   │  │  ├─ routes/           # API / 관리자 라우트
   │  │  ├─ schemas/          # API 계약
   │  │  ├─ services/         # AI / 평가 DB 저장 서비스
   │  │  └─ templates/        # 관리자 Jinja2 HTML
   │  └─ tests/
   │
   ├─ frontend/
   │  ├─ src/
   │  │  ├─ components/
   │  │  ├─ data/
   │  │  ├─ pages/
   │  │  ├─ services/
   │  │  └─ types/
   │  ├─ package.json
   │  └─ vite.config.ts
   │
   ├─ scenario/
   │  ├─ episodes/             # 기본 EP01~EP03 JSON
   │  ├─ contracts/
   │  ├─ fixtures/
   │  ├─ rubrics/
   │  └─ tests/
   │
   └─ docs/
      ├─ DB_FLOW_GUIDE.md
      ├─ DB_REFACTOR_GUIDE.md
      └─ db_refactor_migration.sql
```

---

## 4. 사전 준비

필요한 프로그램:

- Python 3.x
- Node.js + npm
- PostgreSQL
- Git

현재 개발 환경에서는 Python 3.14 계열로 실행하고 있습니다.

---

## 5. Python 가상환경 및 패키지 설치

Repository 루트에서 가상환경을 생성합니다.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

`requirements.txt`가 있는 저장소에서는 다음 명령을 사용합니다.

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt`가 없는 경우 Backend 실행에 필요한 주요 패키지는 다음과 같습니다.

```powershell
python -m pip install fastapi uvicorn sqlmodel sqlalchemy psycopg2-binary python-dotenv python-jose passlib bcrypt langchain-openai openai pydantic
```

가상환경이 활성화되면 PowerShell 앞에 보통 `(.venv)`가 표시됩니다.

---

## 6. Frontend 설치

```powershell
cd 2team\frontend
npm install
```

---

## 7. Backend 환경변수

다음 파일을 생성합니다.

```text
2team/backend/.env
```

예시:

```env
OPENAI_API_KEY=your_openai_api_key
LLM_PROVIDER=openai
LLM_MODEL=your_openai_model_name

DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/manyang
SECRET_KEY=change_this_to_a_long_random_secret

# DB 함수/입출력 흐름 로그
DB_FLOW_TRACE=1

# 사용자 입력 원문 로그 여부. 기본 0 권장
DB_FLOW_TRACE_INCLUDE_MESSAGE=0
```

### 중요

- `.env`에는 API Key와 DB 비밀번호가 있으므로 Git에 커밋하지 않습니다.
- 현재 AI 실행 코드는 OpenAI provider를 사용합니다.
- `GOOGLE_API_KEY`는 현재 Runtime 코드에서 필수 값이 아닙니다.
- DB 비밀번호에 `@`, `#`, `/` 같은 특수문자가 있으면 URL 인코딩이 필요할 수 있습니다.
- 개인정보·민감정보 보호를 위해 `DB_FLOW_TRACE_INCLUDE_MESSAGE=0` 사용을 권장합니다.

---

## 8. PostgreSQL 준비 및 현재 DB 구조

예시 DB 이름:

```text
manyang
```

pgAdmin 또는 PostgreSQL CLI에서 Database를 만든 뒤 `.env`의 `DATABASE_URL`을 맞춥니다.

Backend가 DB 연결에 성공하면 `SQLModel.metadata.create_all()`을 실행해 **없는 테이블**을 생성합니다.

> `create_all()`은 이미 존재하는 테이블의 컬럼 변경이나 제약조건 변경까지 수행하지 않습니다. 기존 DB를 새 구조로 변경할 때는 아래 마이그레이션 절차가 필요합니다.

### 현재 주요 테이블

```text
admin_table
llm_role
chat_room
chatting
score
```

현재는 별도 `ai_evaluation`, `episode_scenario` 모델을 사용하지 않습니다.

### DB 관계

```text
admin_table
     │
     └─────────────┐
                   │
llm_role           │
Episode JSON       │
status             │
episode_id         │
     │             │
     └─ 1:N ───────┘
          ↓
      chat_room
      학생 1회 학습 Session
      session_id / lr_num / limits
          │
          └─ 1:N
             ↓
          chatting
          USER 답변 / AI 응답·피드백
             │
             └─ USER chat_id 1:N
                    ↓
                  score
                  risk_awareness
                  refusal
                  help_request
```

### 테이블별 역할

#### `llm_role`

Episode / 시츄에이션 원본을 저장합니다.

주요 컬럼:

```text
lr_num          PK
episode_id      EP01 형태 식별자
title
admin_id
category        user_defined / school / trip / club
content         Episode 전체 JSON 문자열
status          draft / published
created_at
updated_at
```

관리자가 만든 Episode뿐 아니라 기본 JSON Episode도 학생이 실제 실행할 때 DB에 등록될 수 있습니다.

#### `chat_room`

학생의 **한 번의 Episode 학습 Session**을 나타냅니다.

```text
room_id
session_id      MemorySessionStore의 UUID와 연결
lr_num          플레이한 llm_role
admin_id
limits          Episode 전체 Stage 수
created_at
```

#### `chatting`

Stage별 USER / AI 대화 기록을 저장합니다.

```text
chat_id
room_id
stage_id
chatter         USER / AI
content         USER 답변 또는 NPC 응답
feedback        AI 행의 교육 피드백
created_at
```

한 `room_id + stage_id`에서 USER와 AI가 각각 최대 한 행씩 저장됩니다.

#### `score`

USER 답변 한 건의 실제 LLM 평가 점수를 저장합니다.

```text
score_id
chat_id
category
score           0 ~ 3
```

`category`는 다음 세 값만 사용합니다.

```text
risk_awareness
refusal
help_request
```

### 현재 저장 구조

- 실시간 게임 진행 상태: `MemorySessionStore`
- Episode 원본 / 공개 상태: `llm_role`
- 학생 1회 학습 Session: `chat_room`
- 학생 답변 / NPC 응답 / 피드백: `chatting`
- 실제 GPT 평가 점수: `score`

DB 장애가 발생해도 학생 학습 자체는 `MemorySessionStore`를 이용해 계속 진행할 수 있습니다.

### 기존 DB 마이그레이션

기존에 `ai_evaluation`, `episode_scenario` 구조를 사용하던 DB는 **백업 후 한 번만** 다음 SQL을 적용합니다.

```text
2team/docs/db_refactor_migration.sql
```

마이그레이션의 목적:

```text
episode_scenario → llm_role
ai_evaluation    → chat_room + chatting + score
```

그리고 통합이 끝나면 기존 `ai_evaluation`, `episode_scenario` 테이블은 사용하지 않습니다.

이미 마이그레이션을 정상 완료한 DB에는 같은 SQL을 반복 실행할 필요가 없습니다.

확인용 SQL:

```sql
SELECT * FROM llm_role ORDER BY lr_num DESC;
SELECT * FROM chat_room ORDER BY room_id DESC;
SELECT * FROM chatting ORDER BY chat_id DESC;
SELECT * FROM score ORDER BY score_id DESC;
```

구버전 테이블 제거 여부:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('ai_evaluation', 'episode_scenario');
```

정상 통합 후에는 0행이어야 합니다.

---

## 9. 개발 모드 실행

터미널을 2개 사용하면 편합니다.

### 터미널 1 — Backend

Repository 루트 기준:

```powershell
cd 2team\backend\src
python app.py
```

Backend:

```text
http://127.0.0.1:8000
```

API 상태 확인:

```text
http://127.0.0.1:8000/api/health
```

응답 예시:

```json
{
  "api": "ok",
  "database": "ok",
  "student_service": "available"
}
```

DB가 내려가 있으면 `database`만 `unavailable`이 되고 학생용 API 프로세스는 계속 실행될 수 있습니다.

개발 중 자동 재시작이 필요하면:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 터미널 2 — Frontend

```powershell
cd 2team\frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Vite 개발 서버는 다음 경로를 Backend `127.0.0.1:8000`으로 프록시합니다.

```text
/api
/admins
```

---

## 10. 단일 서버 실행 (발표 / 데모 권장)

Frontend를 먼저 Build합니다.

```powershell
cd 2team\frontend
npm run build
```

그 다음 Backend를 실행합니다.

```powershell
cd ..\backend\src
python app.py
```

FastAPI가 `frontend/dist`를 함께 서비스하므로 다음 주소 하나로 접근할 수 있습니다.

```text
http://127.0.0.1:8000
```

---

## 11. 학생용 주요 화면

```text
/                 홈
/tutorial         게임 설명
/episodes         공개 Episode 선택
/play/EP01        Episode 플레이
/result           결과 화면
/profile          학습 결과 화면
```

기본 Episode:

```text
EP01 시험기간 스터디 그룹
EP02 SNS에서 시작된 유혹
EP03 학원가에서 받은 음료
```

`llm_role.status = published`인 DB Episode는 `/api/episodes`에 포함되고 학생용 `/episodes` 화면에도 표시됩니다.

### 결과 화면 표시 원칙

결과 화면 상단은 평가 점수가 아니라 **학습 완료 정보**만 표시합니다.

```text
Episode 완료
5개 단계 완료
```

`위험 인지 / 거절 대응 / 도움 요청` 실제 AI 평가 점수는 아래 **단계별 마냥이 피드백**에서 Stage별 `0~3점`으로만 표시합니다.

이를 통해 학습 진행률과 AI 평가 점수를 같은 지표로 오해하지 않도록 분리합니다.

---

## 12. 관리자 기능 및 대시보드

관리자 진입:

```text
/admins/
```

개발 모드에서는 Vite proxy를 통해 다음 주소로 접근할 수 있습니다.

```text
http://localhost:5173/admins/
```

주요 경로:

```text
/admins/                 관리자 대시보드
/admins/signup           관리자 가입
/admins/signin           로그인
/admins/episodes         전체 Episode 관리
/admins/episodes?mine=1  내가 작성한 Episode
/admins/writeform        새 Episode 작성
```

### 관리자 대시보드

현재 대시보드는 다음 정보를 제공합니다.

#### 콘텐츠 / 관리자 현황

- DB 등록 Episode 수
- 내가 작성한 Episode 수
- 전체 관리자 수
- 활성 관리자 수
- 카테고리별 Episode 수
  - 교내 `school`
  - 해외여행 `trip`
  - 클럽마약 `club`
  - 사용자 정의 `user_defined`
- 최근 등록 Episode

#### 실제 AI 평가 저장 현황

실제 GPT 평가가 DB에 저장된 데이터만 대상으로 집계합니다.

```text
score
  ↓
chatting (USER)
  ↓
chat_room
  ↓
llm_role
```

표시 항목:

- 저장된 AI 평가 건수
- 위험 인지 평균
- 거절 평균
- 도움 요청 평균
- Episode / Stage별 평균 점수 및 평가 건수
- 평가축별 유효 표본 수

평균 계산 시 각 Stage의 `evaluation_axis`에 해당하는 점수만 사용합니다.
예를 들어 `risk_awareness` Stage에서 함께 반환된 다른 축의 0점은 거절·도움요청 평균에 포함하지 않습니다.

### Episode 관리 흐름

```text
JSON 작성
  ↓
구조 검증
  ↓
draft 저장
  ↓
published 공개
  ↓
llm_role 저장
  ↓
/api/episodes 노출
  ↓
학생 /episodes에서 선택
  ↓
/play/{episode_id} 실행
```

관리자 DB Episode는 `llm_role`에 다음 정보와 함께 저장됩니다.

```text
episode_id
title
category
content          # Episode 전체 JSON
status           # draft / published
admin_id
created_at
updated_at
```

EP01~EP03은 기본 JSON 파일이 존재하며, 같은 `episode_id`의 공개 DB 데이터가 있으면 DB Episode를 우선 사용합니다.

---

## 13. Episode JSON 기본 규격

관리자 Episode는 기본적으로 다음 구조를 사용합니다.

```json
{
  "episode_id": "EP04",
  "title": "새 에피소드",
  "background": {
    "character": "고등학생",
    "situation": "상황 설명"
  },
  "total_stages": 5,
  "stages": [
    {
      "stage_id": "EP04_STAGE01",
      "stage_number": 1,
      "title": "위험 인지",
      "type": "risk_awareness",
      "location": "장소",
      "description": "장면 설명",
      "messages": [
        {
          "speaker": "NPC",
          "text": "대사"
        }
      ],
      "question": "사용자에게 묻는 질문",
      "evaluation_axis": "risk_awareness",
      "evaluation_criteria": [
        "평가기준 1",
        "평가기준 2"
      ],
      "next_stage": "EP04_STAGE02",
      "npc_speaker": "NPC 이름",
      "npc_identity": "NPC 정체",
      "npc_stance": "NPC 태도",
      "npc_boundaries": "NPC가 하면 안 되는 역할"
    }
  ]
}
```

마지막 Stage의 `next_stage`는 `null`입니다.

사용 가능한 기본 평가축:

```text
risk_awareness
refusal
help_request
```

---

## 14. 주요 API

```text
GET    /api/health
GET    /api/episodes
GET    /api/episodes/{episode_id}
POST   /api/sessions
GET    /api/sessions/{session_id}
GET    /api/sessions/{session_id}/result
DELETE /api/sessions/{session_id}
POST   /api/chat
```

예시:

```text
GET http://127.0.0.1:8000/api/episodes
```

DB의 `published` Episode까지 정상적으로 조회되면 학생 화면에서도 사용할 수 있습니다.

---

## 15. AI 평가 및 DB 저장 흐름

### 전체 흐름

```text
사용자 자유 입력
    ↓
청소년용 Safety / 언어 필터
    ↓
행동 의도와 부적절 표현 분리
    ↓
현재 Episode / Stage / NPC 역할과 함께 GPT 평가
    ↓
NPC 역할 반응
    ↓
마냥이 피드백
    ↓
3축 점수 생성
    ↓
MemorySessionStore 진행 상태 갱신
    ↓
실제 GPT 평가 성공 + DB 정상일 때
    ↓
chatting + score DB 저장
```

점수 범위:

```text
0 ~ 3
```

### Episode 시작 시 DB 저장

`POST /api/sessions`

```text
Episode 조회
    ↓
MemorySessionStore 세션 생성
    ↓
DB 정상
    ↓
llm_role 확인 / 필요 시 등록
    ↓
chat_room INSERT
```

### Stage 답변 시 DB 저장

`POST /api/chat`

```text
GPT 평가 성공
    ↓
chatting USER
  - 학생 입력
    ↓
chatting AI
  - NPC 응답
  - 교육 피드백
    ↓
USER chat_id 기준 score 3개 INSERT / UPDATE
  - risk_awareness
  - refusal
  - help_request
```

### 저장에서 제외되는 경우

다음 결과는 실제 AI 평가 데이터가 아니므로 `score` 통계에 저장하지 않습니다.

- `retry_required=True`인 재입력 요청
- LLM 장애로 생성된 fallback 결과
- AI 분석을 사용할 수 없는 경우

따라서 관리자 대시보드는 실제 GPT 평가 성공 데이터만 확인할 수 있습니다.

### DB 장애 시

DB 저장 실패는 학생 API 오류로 전파하지 않습니다.

```text
DB 정상
→ MemorySessionStore + PostgreSQL 저장

DB 장애
→ MemorySessionStore로 학습 계속
→ PostgreSQL 기록만 일시적으로 건너뜀
```

NPC는 교사·상담사 역할을 대신하지 않고 해당 장면의 인물 역할을 유지하도록 Prompt에서 제한합니다.

---

## 16. 모바일 / 외부 테스트 (Cloudflare Quick Tunnel)

개발 모드에서는 Vite가 외부 접속을 받을 수 있도록 설정되어 있습니다.

Backend와 Frontend를 모두 실행한 뒤:

```powershell
cloudflared tunnel --url http://localhost:5173
```

출력된:

```text
https://xxxxx.trycloudflare.com
```

주소를 PC, 스마트폰, 다른 네트워크에서 테스트할 수 있습니다.

`vite.config.ts`는 `.trycloudflare.com` 호스트를 허용하도록 설정되어 있습니다.

### 발표용 단일 서버 방식

Frontend를 `npm run build`한 경우에는 Backend 하나만 외부로 열 수 있습니다.

```powershell
cloudflared tunnel --url http://localhost:8000
```

Quick Tunnel 주소는 실행할 때 바뀔 수 있으며 개발·테스트 용도로 사용하는 것을 권장합니다.

---

## 17. 테스트

### Backend

테스트 코드와 환경이 준비되어 있다면 Backend 폴더에서 실행합니다.

```powershell
cd 2team\backend
python -m pytest
```

특정 Safety 테스트 예시:

```powershell
python -m pytest tests\ai\test_safety.py -v
```

### Scenario 검증

```powershell
cd 2team\scenario
python validate_scenario.py
```

### Frontend TypeScript Build

```powershell
cd 2team\frontend
npm run build
```

### Frontend Lint

```powershell
npm run lint
```

---

## 18. 문제 해결

### `ModuleNotFoundError`

가상환경 활성화와 Backend 의존성 설치 여부를 확인합니다.

```powershell
.venv\Scripts\activate
```

### `SECRET_KEY / DATABASE_URL field required`

`2team/backend/.env`가 존재하는지 확인합니다.

### `No module named psycopg2`

```powershell
python -m pip install psycopg2-binary
```

### `Frontend build not found`

FastAPI 단일 서버 모드를 사용할 경우:

```powershell
cd 2team\frontend
npm run build
```

후 Backend를 다시 실행합니다.

### DB 연결은 안 되지만 학생 화면은 뜨는 경우

정상적인 장애 격리 동작일 수 있습니다.

Backend는 DB 상태를 background에서 주기적으로 확인하며 PostgreSQL 연결 실패 때문에 학생용 FastAPI 전체가 종료되지 않도록 구성되어 있습니다.

관리자 DB 기능과 평가 기록 저장이 필요하면:

1. PostgreSQL 실행 상태 확인
2. `.env`의 `DATABASE_URL` 확인
3. `/api/health`의 `database` 값 확인
4. Backend 로그의 `DB connection ready` 확인

### 관리자 대시보드 AI 평가가 0건으로 보일 때

먼저 DB에 실제 점수가 있는지 확인합니다.

```sql
SELECT COUNT(*) FROM score;
SELECT COUNT(*) FROM chatting;
SELECT COUNT(*) FROM chat_room;
```

관계 확인:

```sql
SELECT
    lr.episode_id,
    cr.session_id,
    c.stage_id,
    c.chatter,
    s.category,
    s.score
FROM score s
JOIN chatting c ON c.chat_id = s.chat_id
JOIN chat_room cr ON cr.room_id = c.room_id
LEFT JOIN llm_role lr ON lr.lr_num = cr.lr_num
ORDER BY s.score_id DESC
LIMIT 50;
```

점수가 존재하는데 대시보드가 0건이면 다음을 확인합니다.

- `chatting.chatter = USER`인지
- `chat_room.lr_num`이 `llm_role.lr_num`과 연결되어 있는지
- `llm_role.content`의 해당 Stage에 `evaluation_axis`가 존재하는지
- 기본 EP01~EP03의 경우 `scenario/episodes/*.json`이 존재하는지

대시보드는 DB `llm_role.content`의 Stage 정보를 우선 사용하고, 마이그레이션 placeholder처럼 Stage 정보가 없는 경우 기본 Scenario JSON에서 평가축을 복구합니다.

### 새 DB Episode가 학생 목록에 안 보일 때

1. 관리자에서 Episode 상태가 `published`인지 확인
2. `llm_role.episode_id`가 올바른지 확인
3. `/api/episodes`에서 해당 ID 확인
4. Frontend 새로고침
5. 필요하면 Backend / Frontend 재시작

### 기존 DB 컬럼이 코드와 맞지 않을 때

`SQLModel.metadata.create_all()`은 기존 테이블 구조를 변경하지 않습니다.

기존 DB라면 백업 후:

```text
2team/docs/db_refactor_migration.sql
```

을 검토하여 한 번 적용합니다.

이미 통합 마이그레이션을 완료한 DB에서는 다시 실행하지 않습니다.

---

## 19. 보안 / 저장소 주의사항

다음 파일은 GitHub 또는 제출 ZIP에 포함하지 않는 것을 권장합니다.

```text
.env
.venv/
node_modules/
__pycache__/
*.pyc
```

API Key, DB 비밀번호, `SECRET_KEY`를 코드나 README에 직접 작성하지 마세요.

또한 학생 자유 입력에는 개인정보나 민감정보가 포함될 수 있으므로 운영 환경의 로그 정책을 별도로 점검해야 합니다.

---

## 20. 현재 구조상 참고사항

- EP01~EP03 기본 콘텐츠는 `scenario/episodes/*.json`에 있습니다.
- 관리자 작성 Episode와 DB에 등록된 기본 Episode는 PostgreSQL `llm_role`에 저장됩니다.
- `published` 상태의 `llm_role` Episode가 있으면 기본 JSON보다 우선 로딩합니다.
- 학생 진행 중 Session 상태는 `MemorySessionStore`에 유지되므로 Backend 프로세스를 재시작하면 진행 중 Session은 초기화될 수 있습니다.
- 학생이 Episode를 시작하면 DB 정상 상태에서 `chat_room`이 생성됩니다.
- 실제 GPT 평가가 성공하면 `chatting`에 USER / AI 기록을 저장하고 USER `chat_id` 기준으로 `score` 3개를 저장합니다.
- fallback 및 재입력 결과는 실제 AI 평가 통계에서 제외됩니다.
- 별도 `ai_evaluation`, `episode_scenario` 모델은 현재 사용하지 않습니다.
- 관리자 대시보드의 AI 평가 통계는 `score → chatting → chat_room → llm_role` 관계로 계산합니다.
- 결과 화면 상단은 학습 완료 정보이며, 실제 `0~3`점 평가는 Stage별 피드백 영역에서만 표시합니다.

---

## 21. 빠른 실행 요약

### Backend

```powershell
cd 2team\backend\src
python app.py
```

### Frontend

새 터미널에서:

```powershell
cd 2team\frontend
npm install
npm run dev
```

브라우저:

```text
학생:   http://localhost:5173
관리자: http://localhost:5173/admins/
```

DB 상태 확인:

```text
http://127.0.0.1:8000/api/health
```

---

## 22. DB 흐름 요약

```text
[관리자 Episode]
JSON 작성
   ↓
llm_role
   ↓ published
학생 Episode 목록

[학생 학습]
POST /api/sessions
   ↓
MemorySessionStore
   └─ DB 정상 → chat_room

POST /api/chat
   ↓
GPT 평가
   ↓
MemorySessionStore 진행 상태 갱신
   └─ 실제 AI 평가 + DB 정상
        ↓
      chatting USER
        ↓
      chatting AI
        ↓
      score 3축
        ↓
      관리자 대시보드 집계
```
