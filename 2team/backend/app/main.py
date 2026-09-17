# FastAPI 애플리케이션을 생성하고 라우터를 등록하는 진입점입니다.
from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware
)
# python -m uvicorn app.main:app --reload 실행확인
from app.api.chat import (
    router as chat_router
)

from app.api.sessions import (
    router as session_router
)

from app.api.episodes import (
    router as episode_router
)

app = FastAPI(
    # API 문서에 표시될 애플리케이션 이름입니다.
    title="Manyang API"
)


app.add_middleware(
    # 프론트엔드 개발 서버에서 백엔드 API를 호출할 수 있도록 CORS를 설정합니다.
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    # 채팅 API를 /api 경로 아래에 등록합니다.
    chat_router,
    prefix="/api"
)


app.include_router(
    # Session API를 /api 경로 아래에 등록합니다.
    session_router,
    prefix="/api"
)

app.include_router(
    # 에피소드 API를 /api 경로 아래에 등록합니다.
    episode_router,
    prefix="/api"
)

@app.get("/")
def root():
    # 서버가 실행 중인지 간단히 확인하는 기본 응답입니다.
    return {
        "message":
        "Manyang API Running"
    }

@app.get(
    "/api/health",
    tags=["System"]
)
def health_check():
    # 모니터링이나 프론트엔드에서 사용할 상태 확인용 엔드포인트입니다.
    return {
        "status": "ok"
    }
