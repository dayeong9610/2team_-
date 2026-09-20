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
- 위험한 답변도 의미가 분명하면 재입력시키지 않고 행동 자체를 평가
- 마냥이 코칭 피드백
- 3개 평가축 기록
  - 위험 인지 `risk_awareness`
  - 거절 대응 `refusal`
  - 도움 요청 `help_request`
- Episode 2·3의 장면 시각화 및 장면 → 대화 전환 UX
- 모바일 / 데스크톱 반응형 지원

### 관리자

- 관리자 회원가입 / 로그인
- Episode JSON 작성 및 검증
- 초안(`draft`) 저장
- 공개(`published`) / 비공개 전환
- 관리자 작성 Episode 수정 / 삭제
- 공개된 DB Episode를 학생 게임에 즉시 반영
- AI 평가 데이터 대시보드
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

Repository 루트 기준입니다.

```text
.
├─ README.md
├─ requirements.txt
├─ .gitignore
│
└─ 2team/
   ├─ backend/
   │  ├─ .env                  # 로컬 전용, Git에 올리지 않음
   │  ├─ src/
   │  │  ├─ app.py            # FastAPI 시작점
   │  │  ├─ ai/               # Prompt / Safety / 평가 스키마
   │  │  ├─ auth/             # 관리자 인증
   │  │  ├─ core/             # Scenario / Session / Trace
   │  │  ├─ database/         # PostgreSQL 연결
   │  │  ├─ model/            # SQLModel 테이블
   │  │  ├─ routes/           # API / 관리자 라우트
   │  │  ├─ schemas/          # API 계약
   │  │  ├─ services/         # AI / 평가 저장 서비스
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

Repository 루트에서 실행합니다.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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
```

### 중요

- `.env`에는 API Key와 DB 비밀번호가 있으므로 Git에 커밋하지 않습니다.
- 현재 AI 실행 코드는 OpenAI provider를 사용합니다.
- `GOOGLE_API_KEY`는 현재 Runtime 코드에서 필수 값이 아닙니다.
- DB 비밀번호에 `@`, `#`, `/` 같은 특수문자가 있으면 URL 인코딩이 필요할 수 있습니다.

---

## 8. PostgreSQL 준비

예시 DB 이름:

```text
manyang
```

pgAdmin 또는 PostgreSQL CLI에서 빈 Database를 하나 생성한 뒤 `.env`의 `DATABASE_URL`을 맞춥니다.

Backend가 DB 연결에 성공하면 `SQLModel.metadata.create_all()`을 통해 없는 테이블을 자동 생성합니다.

주요 테이블:

```text
admin_table
ai_evaluation
episode_scenario
chat_room
chatting
llm_role
score
```

### 현재 저장 구조

- 게임 진행 Session: 메모리 `MemorySessionStore`
- Stage AI 평가: `ai_evaluation` DB 저장
- 관리자 작성 Episode: `episode_scenario` DB 저장
- 사용자 입력 원문과 AI 대사는 `ai_evaluation`에 저장하지 않음

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

또는 개발 중 자동 재시작이 필요하면:

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

Vite 개발 서버가 다음 경로를 Backend `127.0.0.1:8000`으로 프록시합니다.

```text
/api
/admins
```

---

## 10. 단일 서버 실행 (발표/데모 권장)

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

이 경우 FastAPI가 `frontend/dist`를 같이 서비스하므로 다음 주소 하나로 접근할 수 있습니다.

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

관리자가 만든 DB Episode는 `published` 상태가 되면 `/api/episodes`에 포함되고 학생용 `/episodes` 화면에도 표시됩니다.

---

## 12. 관리자 기능

관리자 진입:

```text
/admins
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
/api/episodes 노출
  ↓
학생 /episodes에서 선택
  ↓
/play/{episode_id} 실행
```

관리자 DB Episode는 다음 정보와 함께 저장됩니다.

```text
episode_id
title
category
scenario_json
status (draft / published)
admin_id
created_at
updated_at
```

EP01~EP03은 기본 JSON 파일 기반 콘텐츠이고, 관리자 화면에서는 DB Episode와 구분하여 표시합니다.

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

DB에 공개된 Episode까지 정상적으로 조회되면 학생 화면에서도 사용할 수 있습니다.

---

## 15. AI 평가 흐름

```text
사용자 자유 입력
    ↓
청소년용 Safety / 언어 필터
    ↓
행동 의도와 부적절 표현을 분리
    ↓
현재 Episode / Stage / NPC 역할과 함께 LLM 평가
    ↓
NPC 역할 반응
    ↓
마냥이 피드백
    ↓
3축 점수 생성
    ↓
ai_evaluation DB 저장
```

점수 범위:

```text
0 ~ 3
```

NPC는 교사·상담사 역할을 대신하지 않고 해당 장면의 인물 역할을 유지하도록 Prompt에서 제한합니다.

---

## 16. 모바일 / 외부 테스트 (Cloudflare Quick Tunnel)

개발 모드에서는 Vite가 외부 접속을 받을 수 있도록 설정되어 있습니다.

$env:__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS="marsh-once-mall-mature.trycloudflare.com"

Backend와 Frontend를 모두 실행한 뒤:

```powershell
cloudflared tunnel --url http://localhost:5173
```

출력된:

```text
https://xxxxx.trycloudflare.com
```

주소를 PC, 스마트폰, 다른 네트워크에서 테스트할 수 있습니다.

### 발표용 단일 서버 방식

Frontend를 `npm run build`한 경우에는 Backend 하나만 외부로 열 수 있습니다.

```powershell
cloudflared tunnel --url http://localhost:8000
```

Quick Tunnel 주소는 실행할 때 바뀔 수 있으며 개발·테스트 용도로 사용하는 것을 권장합니다.

---

## 17. 테스트

### Backend

Repository 루트에서 가상환경 활성화 후:

```powershell
cd 2team\backend
python -m pytest
```

특정 Safety 테스트:

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

가상환경이 활성화되어 있는지 확인한 뒤:

```powershell
python -m pip install -r requirements.txt
```

### `SECRET_KEY / DATABASE_URL field required`

`2team/backend/.env`가 존재하는지 확인합니다.

### `No module named psycopg2`

정리된 `requirements.txt`를 설치하거나:

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

Backend는 DB 상태를 background에서 확인하도록 되어 있어 API 프로세스 자체는 시작될 수 있습니다. 관리자 DB 기능과 AI 평가 저장을 사용하려면 PostgreSQL과 `DATABASE_URL`을 확인하세요.

### 새 DB Episode가 학생 목록에 안 보일 때

1. 관리자에서 Episode 상태가 `published`인지 확인
2. `/api/episodes`에서 해당 ID 확인
3. Frontend 새로고침
4. 필요하면 Backend / Frontend 재시작

---

## 19. 보안 / 저장소 주의사항

다음 파일은 GitHub 또는 제출 ZIP에 포함하지 않습니다.

```text
.env
.venv/
node_modules/
__pycache__/
*.pyc
```

API Key, DB 비밀번호, `SECRET_KEY`를 코드나 README에 직접 작성하지 마세요.

---

## 20. 현재 구조상 참고사항

- EP01~EP03은 `scenario/episodes/*.json`의 기본 콘텐츠입니다.
- 관리자 추가 Episode는 PostgreSQL `episode_scenario`에 저장됩니다.
- 공개된 DB Episode는 기본 Episode와 함께 게임 API에서 조회됩니다.
- 학생 진행 중 Session은 현재 메모리 기반이므로 Backend 프로세스를 재시작하면 진행 중 Session은 초기화될 수 있습니다.
- Stage별 AI 평가 결과는 `ai_evaluation`에 저장됩니다.

---

## 21. 빠른 실행 요약

이미 `.venv`를 만들고 활성화했다면 Repository 루트에서:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Backend:

```powershell
cd 2team\backend\src
python app.py
```

새 터미널에서 Frontend:

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
