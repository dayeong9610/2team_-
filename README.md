# 마냥이

청소년이 약물·유해 상황에서 **위험을 인지하고, 거절하고, 도움을 요청하는 방법을 실제 대화처럼 연습**하는 AI 기반 체험형 예방교육 서비스입니다.

정답을 고르는 객관식 게임이 아니라, 사용자가 상황 속 인물에게 **직접 문장으로 대응**하면 NPC가 역할에 맞게 반응하고 `마냥이`가 단계별 학습 피드백을 제공합니다.

---

## 1. 최종 구현 범위

### 1-1. 청소년 사용자

- 회원가입 없이 이용하는 무가입 체험
- 홈 / 서비스 소개
- 튜토리얼
- Episode 선택
- Episode / Stage 기반 상황 학습
- 실제 대화처럼 자유 문장 입력
- NPC 역할 기반 AI 후속 반응
- 청소년 대상 언어·욕설 필터링
- 의미가 분명한 답변은 단순 키워드가 아니라 **행동 의도**를 기준으로 평가
- 의미를 판단하기 어려운 입력은 같은 Stage에서 재입력 유도
- LLM 장애 시 검수된 fallback 흐름으로 학습 지속
- 마냥이 코칭 피드백
- 3개 평가축 기록
  - 위험 인지 `risk_awareness`
  - 거절 대응 `refusal`
  - 도움 요청 `help_request`
- Episode별 장면 UI
  - 일반 대화
  - SNS Feed
  - SNS DM
- 결과 화면에서 Stage별 피드백 및 AI 평가 점수 확인
- 수업용 QR / Episode 코드로 바로 접속

### 1-2. 관리자

- 관리자 회원가입 / 로그인
- 관리자 대시보드
- DB 등록 Episode 현황
- 관리자 현황
- 카테고리별 Episode 현황
- 실제 AI 평가 저장 현황
- 평가축별 평균 점수 확인
- Episode / Stage별 개발자 피드백용 통계
- Episode JSON 작성 / 구조 검증
- 초안(`draft`) 저장
- 공개(`published`) / 비공개 전환
- Episode 수정 / 삭제
- 공개된 DB Episode를 학생 서비스에 반영
- **수업코드 · QR 발급**
  - 별도 수업 DB 테이블 없음
  - Episode ID를 수업코드로 사용
  - QR 스캔 시 해당 Episode 자동 입장

---

## 2. 서비스 핵심 흐름

```text
[청소년]

홈
 ↓
튜토리얼
 ↓
Episode 선택
 ↓
장면 확인
 ↓
NPC 대화
 ↓
사용자 자유문장 입력
 ↓
GPT 평가
 ├─ NPC 후속 반응
 ├─ 마냥이 피드백
 └─ 3축 점수
 ↓
다음 Stage
 ↓
Episode 완료
 ↓
Stage별 결과 확인
```

관리자 수업 QR 사용 시:

```text
[관리자]

수업 QR 발급
 ↓
Episode 선택
 ↓
수업코드 = Episode ID
 ↓
QR 생성
 ↓
학생 QR 스캔
 ↓
/class/{episode_id}
 ↓
Episode 존재 확인
 ↓
/play/{episode_id}
```

---

## 3. 기술 스택

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

### 기타

- `qrcode`
- Pillow
- Cloudflare Quick Tunnel

---

## 4. 프로젝트 구조

Repository 루트 기준입니다.

```text
.
├─ README.md
└─ 2team/
   ├─ backend/
   │  ├─ .env
   │  ├─ .env.example
   │  ├─ requirements-qr.txt
   │  ├─ src/
   │  │  ├─ app.py
   │  │  ├─ ai/
   │  │  │  ├─ evaluator.py
   │  │  │  ├─ npc.py
   │  │  │  ├─ prompts.py
   │  │  │  └─ safety.py
   │  │  ├─ auth/
   │  │  ├─ core/
   │  │  ├─ database/
   │  │  ├─ model/
   │  │  │  ├─ admin.py
   │  │  │  ├─ llm_role.py
   │  │  │  ├─ chat_room.py
   │  │  │  ├─ chatting.py
   │  │  │  └─ score.py
   │  │  ├─ routes/
   │  │  │  ├─ admin_route.py
   │  │  │  ├─ chat.py
   │  │  │  ├─ episodes.py
   │  │  │  └─ sessions.py
   │  │  ├─ schemas/
   │  │  ├─ services/
   │  │  └─ templates/
   │  │     └─ admin/
   │  │        ├─ admin_index.html
   │  │        └─ class_qr.html
   │  └─ tests/
   │
   ├─ frontend/
   │  ├─ public/
   │  ├─ src/
   │  │  ├─ assets/
   │  │  ├─ components/
   │  │  │  ├─ common/
   │  │  │  └─ game/
   │  │  ├─ data/
   │  │  ├─ hooks/
   │  │  ├─ pages/
   │  │  │  ├─ HomePage.tsx
   │  │  │  ├─ TutorialPage.tsx
   │  │  │  ├─ EpisodeListPage.tsx
   │  │  │  ├─ PlayPage.tsx
   │  │  │  ├─ ResultPage.tsx
   │  │  │  ├─ ProfilePage.tsx
   │  │  │  ├─ ClassJoinPage.tsx
   │  │  │  └─ ClassJoinPage.css
   │  │  ├─ services/
   │  │  ├─ types/
   │  │  └─ utils/
   │  ├─ package.json
   │  └─ vite.config.ts
   │
   ├─ scenario/
   │  ├─ episodes/
   │  │  ├─ episode01.json
   │  │  ├─ episode02.json
   │  │  └─ episode03.json
   │  ├─ contracts/
   │  ├─ fixtures/
   │  ├─ rubrics/
   │  └─ tests/
   │
   └─ docs/
```

> 현재 프로젝트에 없는 파일은 실제 저장소 구조에 맞게 제외하면 됩니다.

---

## 5. 사전 준비

필요한 프로그램:

- Python 3.x
- Node.js
- npm
- PostgreSQL
- Git

현재 개발 환경에서는 Python 3.14 계열에서도 실행을 확인했습니다.

---

## 6. Python 가상환경 및 패키지 설치

Repository 루트 기준:

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

프로젝트에 `requirements.txt`가 있다면:

```powershell
python -m pip install -r requirements.txt
```

QR 기능에 필요한 패키지:

```powershell
python -m pip install "qrcode[pil]>=8.0"
```

또는:

```powershell
python -m pip install -r 2team\backend\requirements-qr.txt
```

`qrcode` 설치 중 아래와 같은 PATH 경고가 나타날 수 있습니다.

```text
WARNING: The script qr.exe is installed in ... which is not on PATH
```

QR 이미지를 Python 코드에서 생성하는 기능에는 문제가 없으며, `Successfully installed ... qrcode ... pillow ...`가 표시되면 설치가 완료된 것입니다.

---

## 7. Frontend 설치

```powershell
cd 2team\frontend
npm install
```

---

## 8. Backend 환경변수

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

DB_FLOW_TRACE=1
DB_FLOW_TRACE_INCLUDE_MESSAGE=0
```

### 중요

- `.env`는 GitHub에 업로드하지 않습니다.
- 현재 Runtime LLM Provider는 OpenAI입니다.
- `LLM_PROVIDER=google_genai`가 남아 있다면 `openai`로 변경합니다.
- `GOOGLE_API_KEY`는 현재 GPT 실행에 필요하지 않습니다.
- DB 비밀번호에 `@`, `#`, `/` 등이 포함되면 URL 인코딩이 필요할 수 있습니다.
- 사용자 원문 로그는 개인정보를 포함할 수 있으므로 `DB_FLOW_TRACE_INCLUDE_MESSAGE=0` 사용을 권장합니다.

---

## 9. PostgreSQL 현재 구조

예시 DB:

```text
manyang
```

현재 주요 테이블:

```text
admin_table
llm_role
chat_room
chatting
score
```

현재는 별도의:

```text
ai_evaluation
episode_scenario
```

모델을 사용하지 않습니다.

---

## 10. DB 관계

```text
admin_table

llm_role
Episode JSON
episode_id
status
   │
   └──── 1:N
          ↓
      chat_room
      학생 1회 Episode Session
      session_id / lr_num
          │
          └──── 1:N
                 ↓
             chatting
             USER / AI 기록
                 │
                 └─ USER chat_id 1:N
                        ↓
                      score
                risk_awareness
                refusal
                help_request
```

---

## 11. 테이블별 역할

### `admin_table`

관리자 계정 정보를 저장합니다.

주요 정보:

```text
admin_id
admin_pw
admin_name
teacher_num
contact
enabled
created_at
```

### `llm_role`

Episode 원본과 상태를 저장합니다.

```text
lr_num
episode_id
title
admin_id
category
content
status
created_at
updated_at
```

`content`에는 Episode 전체 JSON 문자열이 저장됩니다.

`status`:

```text
draft
published
```

### `chat_room`

학생의 한 번의 Episode 학습 Session을 나타냅니다.

```text
room_id
session_id
lr_num
admin_id
limits
created_at
```

### `chatting`

Stage별 USER / AI 대화 기록을 저장합니다.

```text
chat_id
room_id
stage_id
chatter
content
feedback
created_at
```

`chatter`:

```text
USER
AI
```

### `score`

USER 답변 한 건의 실제 GPT 평가 점수를 저장합니다.

```text
score_id
chat_id
category
score
```

평가축:

```text
risk_awareness
refusal
help_request
```

점수:

```text
0 ~ 3
```

---

## 12. 현재 저장 구조

```text
실시간 게임 진행
→ MemorySessionStore

Episode 원본 / 공개 상태
→ llm_role

학생 1회 학습 Session
→ chat_room

학생 답변
→ chatting / USER

NPC 응답 + 마냥이 피드백
→ chatting / AI

실제 GPT 평가
→ score
```

DB 장애가 발생해도 학생 학습 자체는 `MemorySessionStore`를 이용해 계속 진행할 수 있도록 분리되어 있습니다.

---

## 13. QR 수업 기능과 DB

현재 수업 QR 기능은 **DB 테이블을 추가하지 않습니다.**

```text
class_session 테이블 없음
QR 저장 없음
수업코드 저장 없음
```

발표 안정성을 위해 Episode ID를 수업코드로 사용합니다.

예:

```text
EP01
EP02
EP03
```

관리자가 EP02를 선택하면:

```text
수업코드
EP02

학생 URL
/class/EP02
```

형태로 사용합니다.

즉 QR 기능을 추가해도 기존 DB:

```text
admin_table
llm_role
chat_room
chatting
score
```

에는 구조 변경이 발생하지 않습니다.

---

## 14. 개발 모드 실행

터미널을 2개 사용합니다.

### Backend

```powershell
cd 2team\backend\src
python app.py
```

Backend:

```text
http://127.0.0.1:8000
```

자동 Reload:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

API 상태:

```text
http://127.0.0.1:8000/api/health
```

### Frontend

새 터미널:

```powershell
cd 2team\frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Vite는 다음 경로를 Backend로 Proxy합니다.

```text
/api
/admins
```

---

## 15. 단일 서버 실행

발표 환경에서 Frontend / Backend를 하나의 주소로 운영하려면 Frontend를 먼저 Build합니다.

```powershell
cd 2team\frontend
npm run build
```

Backend:

```powershell
cd ..\backend\src
python app.py
```

이 경우 구성에 따라 FastAPI가 `frontend/dist`를 서비스할 수 있습니다.

```text
http://127.0.0.1:8000
```

---

## 16. 학생용 주요 경로

```text
/                  홈
/tutorial          튜토리얼
/episodes          Episode 선택
/play/EP01         Episode 플레이
/result            결과 화면
/profile           학습 결과

/class             수업코드 직접 입력
/class/EP02        QR / 수업코드 자동 입장
```

기본 Episode:

```text
EP01  시험기간 스터디 그룹
EP02  SNS에서 시작된 유혹
EP03  학원가에서 받은 음료
```

---

## 17. QR 수업 입장 흐름

관리자:

```text
/admins/class-qr
```

Episode 선택:

```text
EP02 · SNS에서 시작된 유혹
```

자동 생성:

```text
수업코드
EP02

접속 링크
http://localhost:5173/class/EP02
```

학생 QR 스캔:

```text
/class/EP02
 ↓
ClassJoinPage
 ↓
GET /api/episodes/EP02
 ↓
Episode 확인
 ↓
/play/EP02
```

### 직접 코드 입력

학생은 다음 주소에서:

```text
/class
```

수업코드를 직접 입력할 수도 있습니다.

예:

```text
EP02
```

---

## 18. 휴대폰 QR 사용 시 주의사항

다음 QR은 휴대폰에서 사용할 수 없습니다.

```text
http://localhost:5173/class/EP02
```

휴대폰의 `localhost`는 개발 PC가 아니라 휴대폰 자신을 의미하기 때문입니다.

외부 테스트는 Cloudflare Quick Tunnel을 사용합니다.

```powershell
cloudflared tunnel --url http://localhost:5173
```

예:

```text
https://example-random.trycloudflare.com
```

관리자도 이 주소로 접속합니다.

```text
https://example-random.trycloudflare.com/admins/class-qr
```

그러면 QR URL도 자동으로:

```text
https://example-random.trycloudflare.com/class/EP02
```

형태가 되어 휴대폰에서 사용할 수 있습니다.

---

## 19. 관리자 주요 경로

```text
/admins/                  관리자 대시보드
/admins/signup            관리자 회원가입
/admins/signin            관리자 로그인
/admins/episodes          전체 Episode 관리
/admins/episodes?mine=1   내가 작성한 Episode
/admins/writeform         새 Episode 작성
/admins/update            관리자 정보 수정

/admins/class-qr          수업코드 · QR 발급
/admins/class-qr/image    QR PNG 즉석 생성
```

QR 이미지는 DB에 저장하지 않고 요청 시 즉석에서 생성합니다.

---

## 20. 관리자 대시보드

### 콘텐츠 / 관리자 현황

- DB 등록 Episode 수
- 내가 작성한 Episode 수
- 전체 관리자 수
- 활성 관리자 수
- 카테고리별 Episode 수
  - 교내
  - 해외여행
  - 클럽마약
  - 사용자 정의
- 최근 등록 Episode

### 실제 AI 평가 저장 현황

집계 관계:

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
- Episode / Stage별 평가
- 평가축별 유효 표본 수

평균 계산 시 현재 Stage의 `evaluation_axis`에 해당하는 점수만 통계에 사용합니다.

---

## 21. Episode 관리 흐름

```text
JSON 작성
 ↓
구조 검증
 ↓
draft 저장
 ↓
published 공개
 ↓
llm_role
 ↓
/api/episodes
 ↓
학생 Episode 목록
 ↓
/play/{episode_id}
```

`published` 상태의 DB Episode가 있으면 학생 서비스에서 사용할 수 있습니다.

---

## 22. Episode JSON 기본 규격

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
      "question": "사용자가 어떻게 대응할지 묻는 질문",
      "evaluation_axis": "risk_awareness",
      "evaluation_criteria": [
        "평가기준 1",
        "평가기준 2"
      ],
      "next_stage": "EP04_STAGE02",
      "npc_speaker": "NPC 이름",
      "npc_identity": "NPC 정체",
      "npc_stance": "NPC 태도",
      "npc_boundaries": "NPC 역할 제한"
    }
  ]
}
```

마지막 Stage:

```json
"next_stage": null
```

---

## 23. 장면 UI 확장 필드

현재 EP02처럼 장면에 따라 다른 UI를 사용할 경우 아래 필드를 사용할 수 있습니다.

```json
{
  "scene_type": "feed",
  "scene_title": "SNS 게시물",
  "scene_subtitle": "출처 불명의 홍보성 게시물",
  "scene_images": [
    "/assets/episodes/ep02/example.png"
  ]
}
```

주요 `scene_type`:

```text
feed
dm
dialog
```

용도:

```text
feed
→ SNS Feed / 후기 게시물

dm
→ SNS 개인 메시지

dialog
→ 일반 대화
```

---

## 24. EP02 SNS 시나리오 UI

EP02는 동일한 말풍선 화면만 반복하지 않고 장면에 따라 UI를 분리합니다.

### Stage 1

```text
SNS Feed
```

- 홍보 게시물
- 제품 이미지
- 후기 이미지
- 댓글 / 후기 형태
- 위험 요소 인지

### Stage 2

```text
SNS DM
```

- 출처 불명의 홍보 계정
- 제품 이미지
- 개인 메시지 형태
- 약물 제안
- 거절 연습

### Stage 3

```text
SNS DM
```

- 후기 / 다수 사용을 근거로 반복 설득
- 후기 이미지 활용
- 반복 권유 거절

### Stage 4

```text
일반 대화
```

- 학교에서 친구와 대화
- 친구가 약물에 호기심을 보이는 상황
- 도움 요청 행동 학습

### Stage 5

```text
SNS DM
```

- 비밀 유지 요구
- 접촉 차단 / 신고
- 신뢰할 수 있는 어른에게 알리기

---

## 25. EP02 NPC 말투 원칙

SNS 홍보 계정은 처음 보는 학생에게 지나치게 친구처럼 반말하지 않도록 구성합니다.

예:

```text
"게시물 보시고 관심 있으신 분들께 안내드리고 있어요."

"원하시면 보내드릴 수도 있어요."

"후기 보시면 반응 괜찮은 편이에요."
```

NPC는 홍보 / 판매 / 회유 역할을 유지하며 교육자처럼:

```text
"그건 위험해요."
"먹으면 안 돼요."
```

라고 안전 판단을 대신하지 않습니다.

안전 판단과 교육적 교정은 `마냥이 feedback`에서 제공합니다.

---

## 26. 이미지 파일 관리

Windows + Git + ZIP 환경에서는 한글 이미지 파일명이 깨질 수 있으므로 코드에서 사용하는 Asset 이름은 영문 사용을 권장합니다.

권장:

```text
frontend/src/assets/ep02/diet-supplement.png
frontend/src/assets/ep02/diet-reviews.png
```

예:

```tsx
import dietSupplementImg from "../../assets/ep02/diet-supplement.png";
```

비권장:

```tsx
import img from "../../assets/다이어트 보조제.png";
```

---

## 27. 결과 화면 표시 원칙

결과 화면 상단의 학습 진행 정보와 실제 AI 점수를 분리합니다.

상단:

```text
오늘의 학습 결과
Episode 완료
5개 단계 완료
```

상단에는:

```text
위험 인지 100%
거절 대응 100%
도움 요청 0%
```

처럼 평가 결과로 오해할 수 있는 진행률 표시를 사용하지 않습니다.

실제 점수는 Stage별 피드백에서만:

```text
위험 인지 2점
거절 대응 0점
도움 요청 0점
```

형태로 표시합니다.

---

## 28. AI 평가 흐름

```text
사용자 자유 입력
 ↓
Safety / 언어 필터
 ↓
현재 질문에 대한 실제 대응인지 판단
 ↓
현재 Episode / Stage / NPC 역할 전달
 ↓
GPT 구조화 평가
 ├─ NPC 응답
 ├─ feedback
 ├─ risk_awareness
 ├─ refusal
 └─ help_request
 ↓
MemorySessionStore 갱신
 ↓
실제 GPT 평가 + DB 정상
 ↓
chatting / score 저장
```

---

## 29. 재입력 판단

다음과 같이 현재 질문에 대한 행동 의도를 파악할 수 없는 경우:

```text
ㅇㅇ
ㅋㅋ
아무말
```

`retry_required=true`로 처리할 수 있습니다.

반대로 안전하지 않은 선택이라도 행동 의도가 분명하면 평가합니다.

예:

```text
보내줘
한번 먹어볼게
아무한테도 말 안 할래
그냥 넘어갈래
```

이 경우 잘못된 선택이라는 이유로 재입력시키지 않고 낮은 점수와 교육 피드백을 제공합니다.

---

## 30. NPC / 마냥이 역할 분리

### NPC

장면 속 인물 역할만 수행합니다.

예:

- 친구
- 홍보 계정
- 학원 관계자
- 상황 속 상대방

NPC는:

- 사용자의 행동을 평가하지 않음
- 안전 교육자가 되지 않음
- 마냥이 역할을 대신하지 않음

### 마냥이 feedback

교육 코치 역할입니다.

- 안전성 판단
- 잘한 점
- 개선할 점
- 더 안전한 행동 제안

을 짧게 제공합니다.

---

## 31. Stage 답변 DB 저장

정상 GPT 평가:

```text
POST /api/chat
 ↓
chatting USER
 ↓
chatting AI
 ↓
score 3건
  risk_awareness
  refusal
  help_request
```

다음은 실제 평가 통계에서 제외합니다.

- `retry_required=True`
- LLM 장애 fallback
- 분석 불가 응답

---

## 32. DB 장애 시 동작

DB 저장 실패로 학생 서비스 전체가 중단되지 않도록 분리합니다.

```text
DB 정상
→ MemorySessionStore + PostgreSQL

DB 장애
→ MemorySessionStore만 사용
→ 학생 Episode 계속 진행
→ DB 기록만 건너뜀
```

관리자 DB 기능은 PostgreSQL 연결이 필요합니다.

---

## 33. 주요 API

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

QR 학생 입장은 별도 수업 API나 수업 DB를 사용하지 않고 기존 Episode API를 이용합니다.

---

## 34. 테스트

### Backend

```powershell
cd 2team\backend
python -m pytest
```

### Safety

```powershell
python -m pytest tests\ai\test_safety.py -v
```

### Scenario

```powershell
cd 2team\scenario
python validate_scenario.py
```

### Frontend Build

```powershell
cd 2team\frontend
npm run build
```

### Frontend Lint

```powershell
npm run lint
```

---

## 35. 문제 해결

### 관리자 `/admins/class-qr`이 흰 화면일 때

Backend를 먼저 재시작합니다.

```powershell
cd 2team\backend\src
python app.py
```

또는:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Backend 직접 확인:

```text
http://localhost:8000/admins/class-qr
```

- `8000`에서 정상 → Vite Proxy 확인
- `8000`에서도 문제 → `admin_route.py`, `class_qr.html` 확인

QR용 관리자 Route가 있는지 확인합니다.

```python
@router.get("/class-qr")
```

QR PNG Route:

```python
@router.get("/class-qr/image")
```

---

### `ClassJoinPage.tsx`에서 `setState synchronously within an effect`

수정된 `ClassJoinPage.tsx`는 `useEffect` 시작 부분에서 `setMessage`, `setError`를 동기적으로 반복 호출하지 않습니다.

API 요청 결과의 `.then()` / `.catch()`에서만 조회 상태를 갱신하고, 단순 안내 문구는 현재 URL과 조회 상태를 이용해 계산합니다.

수정 후:

```powershell
npm run lint
npm run dev
```

---

### QR이 PC에서는 되는데 휴대폰에서 안 될 때

QR URL에:

```text
localhost
127.0.0.1
```

이 포함되어 있지 않은지 확인합니다.

Cloudflare URL을 사용해야 합니다.

---

### QR 이미지가 안 보일 때

설치 확인:

```powershell
python -m pip install "qrcode[pil]>=8.0"
```

설치 후 Backend를 재시작합니다.

---

### 이미지 Import 오류

예:

```text
Failed to resolve import "../../assets/다이어트 보조제.png"
```

영문 Asset 경로로 변경합니다.

```text
assets/ep02/diet-supplement.png
assets/ep02/diet-reviews.png
```

그리고 import도 영문 경로를 사용합니다.

---

### 관리자 대시보드 AI 평가가 0건으로 보일 때

먼저 확인:

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
JOIN chatting c
  ON c.chat_id = s.chat_id
JOIN chat_room cr
  ON cr.room_id = c.room_id
LEFT JOIN llm_role lr
  ON lr.lr_num = cr.lr_num
ORDER BY s.score_id DESC
LIMIT 50;
```

점수가 있는데 0건이면:

- `chatting.chatter = USER`
- `chat_room.lr_num`
- `llm_role.lr_num`
- Stage `evaluation_axis`
- 기본 Scenario JSON

을 확인합니다.

---

### DB 연결은 실패하지만 학생 화면은 뜰 때

의도된 장애 격리 동작일 수 있습니다.

확인:

```text
/api/health
```

그리고:

```text
database
student_service
```

상태를 확인합니다.

---

## 36. 기존 DB 마이그레이션

이미 `ai_evaluation`, `episode_scenario`에서 현재 구조로 통합을 완료한 DB라면 마이그레이션 SQL을 다시 실행하지 않습니다.

현재 구조:

```text
llm_role
chat_room
chatting
score
```

QR 기능을 위해 추가 DB 마이그레이션은 **필요하지 않습니다.**

---

## 37. 보안 / 저장소 주의사항

GitHub / 제출 ZIP에서 제외 권장:

```text
.env
.venv/
node_modules/
__pycache__/
*.pyc
```

코드나 README에 다음 값을 직접 넣지 않습니다.

- OpenAI API Key
- DB 비밀번호
- JWT `SECRET_KEY`

학생 자유 입력에는 개인정보나 민감정보가 포함될 수 있으므로 운영 환경 로그 정책을 별도로 검토해야 합니다.

---

## 38. 현재 구조상 참고사항

- 학생 서비스는 무가입 방식입니다.
- EP01~EP03 기본 Scenario는 JSON 파일 기반입니다.
- 관리자가 작성한 Episode는 `llm_role`에 저장됩니다.
- `published` DB Episode는 학생 목록에 노출할 수 있습니다.
- 실시간 Session 진행은 `MemorySessionStore`를 사용합니다.
- Backend 재시작 시 진행 중 메모리 Session은 초기화될 수 있습니다.
- Episode 시작 시 DB 정상 상태라면 `chat_room`을 생성합니다.
- 실제 GPT 평가가 성공하면 `chatting`, `score`에 기록합니다.
- fallback / 재입력 요청은 실제 AI 평가 통계에서 제외합니다.
- 관리자 대시보드는 `score → chatting → chat_room → llm_role` 관계로 집계합니다.
- 결과 화면 상단은 학습 완료 정보입니다.
- 실제 `0~3`점은 Stage별 피드백에서 확인합니다.
- 수업 QR은 별도 DB 테이블 없이 Episode ID를 수업코드로 사용합니다.
- QR은 URL을 즉석에서 이미지로 생성하며 저장하지 않습니다.

---

## 39. 발표용 권장 실행 순서

### 1. PostgreSQL 확인

```text
manyang DB 실행
```

### 2. Backend

```powershell
cd 2team\backend\src
python app.py
```

### 3. Frontend

```powershell
cd 2team\frontend
npm run dev
```

### 4. 브라우저 확인

학생:

```text
http://localhost:5173
```

관리자:

```text
http://localhost:5173/admins/
```

수업 QR:

```text
http://localhost:5173/admins/class-qr
```

학생 코드 입력:

```text
http://localhost:5173/class
```

### 5. 휴대폰 시연이 필요하면

```powershell
cloudflared tunnel --url http://localhost:5173
```

생성된 `https://xxxxx.trycloudflare.com` 주소로 관리자 QR 화면까지 접속한 뒤 QR을 생성합니다.

---

## 40. 발표 시 설명할 핵심 포인트

### 청소년 사용자

```text
무가입
→ 상황 체험
→ 자유문장 대응
→ AI NPC 반응
→ 마냥이 피드백
→ 위험 인지 / 거절 / 도움 요청 연습
```

### 관리자

```text
관리자 로그인
→ Episode 콘텐츠 관리
→ 실제 AI 평가 결과 확인
→ 수업 Episode 선택
→ QR 발급
```

### 수업 QR

```text
별도 학생 계정 없음
별도 수업 DB 없음
추가 DB 마이그레이션 없음

Episode ID
→ QR
→ 학생 스캔
→ Episode 자동 입장
```

### AI 역할

```text
Scenario 시스템
→ Stage 진행 결정

GPT
→ 사용자 대응 평가
→ NPC 반응
→ 마냥이 피드백

DB
→ 실제 평가 결과 기록
```

---

## 41. 전체 시스템 요약

```text
                    ┌───────────────────┐
                    │      관리자       │
                    └─────────┬─────────┘
                              │
                  ┌───────────┼────────────┐
                  │           │            │
               대시보드    Episode 관리   QR 발급
                  │           │            │
                  │        llm_role        │
                  │                        │
                  │                 /class/EP02
                  │                        │
                  │                        ↓
┌──────────────┐  │                ┌──────────────┐
│   청소년     │◀─┴────────────────│ QR / 코드   │
└──────┬───────┘                   └──────────────┘
       │
       ↓
Episode / Stage
       │
       ↓
자유문장 입력
       │
       ↓
GPT
├─ NPC 응답
├─ 마냥이 feedback
└─ 3축 평가
       │
       ├──────────────→ MemorySessionStore
       │
       └─ DB 정상
             ↓
         chat_room
             ↓
         chatting
             ↓
           score
             ↓
      관리자 대시보드
```

---

## 42. 빠른 실행 요약

Backend:

```powershell
cd 2team\backend\src
python app.py
```

Frontend:

```powershell
cd 2team\frontend
npm install
npm run dev
```

QR 패키지가 없다면:

```powershell
python -m pip install "qrcode[pil]>=8.0"
```

브라우저:

```text
학생
http://localhost:5173

관리자
http://localhost:5173/admins/

수업 QR
http://localhost:5173/admins/class-qr

학생 수업코드
http://localhost:5173/class
```

DB 상태:

```text
http://127.0.0.1:8000/api/health
```