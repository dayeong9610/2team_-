[Failed to fetch 수정사항]

1) frontend/src/services/api.ts
- localhost:8000 하드코딩 제거
- 기본 /api 상대경로 사용
- 네트워크 실패 시 원인을 알 수 있는 한국어 오류 메시지 표시

2) frontend/vite.config.ts
- /api -> http://127.0.0.1:8000 개발 프록시 추가

3) backend/src/app.py
- PostgreSQL 연결 실패 때문에 전체 FastAPI 서버가 종료되지 않도록 분리
- localhost/127.0.0.1 CORS 모두 허용

4) frontend/src/pages/PlayPage.tsx
- 플레이 페이지 진입 시 scrollTop 초기화
- 상단 Episode/Progress가 잘려 보이는 현상 방지

[실행]
프로젝트 루트에서:
  npm run dev

또는 터미널 2개:
  cd backend
  npm run dev

  cd frontend
  npm run dev

[확인]
브라우저에서 다음 주소가 열려야 합니다.
  http://127.0.0.1:8000/docs

만약 Backend 터미널에 DB 경고가 보이면 학생 게임 API는 실행되지만,
관리자 회원/대시보드 기능을 위해 PostgreSQL DATABASE_URL은 별도로 정상화해야 합니다.
