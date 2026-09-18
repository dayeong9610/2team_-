마냥이 학생 서비스 장애 대응 패치
=================================

기준
----
- 기존 UX 패치 + fetch 수정 패치가 적용된 프로젝트 기준입니다.
- 사용자가 그 이후 별도 수정한 파일이 없다는 전제로 제작했습니다.

적용 방법
---------
1. 현재 작업 브랜치에서 먼저 커밋하거나 백업합니다.
2. 이 ZIP의 frontend/, backend/ 폴더를 프로젝트 루트에 그대로 덮어씁니다.
3. frontend에서 `npm run build` 또는 `npm run dev`로 확인합니다.
4. backend는 기존 실행 방식으로 실행합니다.

핵심 동작
---------
1) PostgreSQL 장애
- FastAPI 시작을 DB 연결 성공에 의존하지 않습니다.
- DB 상태 확인은 background task에서 수행합니다.
- 학생용 session/chat API는 메모리 Session으로 계속 동작합니다.
- `/api/health`에서 api/database/student_service 상태를 확인할 수 있습니다.

2) AI 장애/타임아웃
- Backend의 /api/chat이 503/504로 학습을 중단하지 않습니다.
- 검수된 시나리오 축(위험 인지/거절/도움 요청)에 맞는 fallback 코칭으로 계속 진행합니다.
- fallback 단계는 숫자 AI 점수를 만들지 않습니다.

3) FastAPI 자체 장애
- Frontend가 local session을 sessionStorage에 만들고 학습을 계속합니다.
- 사용자 답변 원문은 sessionStorage/localStorage에 저장하지 않습니다.
- 장면 진행, 기본 NPC 반응, 마냥이 코칭, 결과 화면까지 사용 가능합니다.

4) 서버가 중간에 끊긴 경우
- 정상 세션도 Frontend에 최소 상태를 미러링합니다.
- 서버 세션이 사라지거나 AI/Backend가 실패하면 그 시점부터 local fallback으로 이어집니다.
- 한 번 fallback으로 전환된 세션은 서버/로컬 진행상태 충돌을 막기 위해 해당 에피소드 종료까지 fallback을 유지합니다.

5) 결과 화면
- 정상 AI 평가가 끝까지 가능했을 때만 3축 숫자 점수를 표시합니다.
- fallback이 한 번이라도 사용되면 "기본 학습 모드 완료" 안내와 단계별 코칭만 표시하고 숫자 점수는 숨깁니다.

보안/개인정보
-------------
- 사용자 자유문장 입력은 fallback 저장 데이터에 포함하지 않습니다.
- sessionStorage에는 episode/stage/점수/피드백/완료 여부 같은 최소 상태만 저장합니다.

검증
----
- Frontend TypeScript: `tsc -b` 통과
- Backend Python: `compileall` 통과
- MemorySessionStore fallback 상태 전환 간이 테스트 통과
- 이 실행 환경에서는 원본 node_modules가 Windows용 optional native binding이라 Vite 전체 build는 실행하지 못했습니다.
  사용자 Windows 환경에서는 `npm run build`로 최종 확인해주세요.

장애 테스트 방법
---------------
A. DB 장애 테스트
- PostgreSQL을 중지한 뒤 Backend 실행
- `/api/health` -> database: unavailable 확인
- 학생 에피소드가 계속 플레이되는지 확인

B. Backend 장애 테스트
- Frontend는 켜둔 채 FastAPI 종료
- 에피소드 진입 -> "기본 학습 모드"로 자동 전환
- 5단계 완료 및 결과 화면까지 이동 확인

C. AI 장애 테스트
- GOOGLE_API_KEY를 임시로 제거/잘못 설정한 상태에서 Backend 실행
- 답변 제출 -> Backend fallback으로 다음 단계 진행 확인
- 결과 화면에서 숫자 점수가 숨겨지는지 확인
