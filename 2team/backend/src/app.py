from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database.connection import conn
from routes.admin_route import router

from routes.chat import router as chat_router
from routes.episodes import router as episode_router
from routes.sessions import router as session_router


# Resolve paths from this file instead of from the shell's current directory.
# React source files under src/ are not browser-ready files; Vite's build output
# under dist/ is what FastAPI should serve.
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"

@asynccontextmanager
async def lifespan(_: FastAPI):
    # 관리자 DB가 아직 준비되지 않았더라도 학생용 에피소드/AI API까지
    # 함께 죽지 않도록 DB 초기화 실패를 분리합니다.
    # DB 기능을 사용할 때는 PostgreSQL 연결을 반드시 정상화해야 합니다.
    try:
        conn()
        print("[DB] connection ready")
    except Exception as exc:
        print(f"[DB] startup warning: {type(exc).__name__}: {exc}")

    yield


app = FastAPI(title="2Team API", lifespan=lifespan)


app.add_middleware(
    # 프론트엔드 개발 서버에서 백엔드 API를 호출할 수 있도록 CORS를 설정합니다.
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(chat_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.include_router(episode_router, prefix="/api")

if (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )

@app.get("/")
async def frontend_index():
    if not FRONTEND_INDEX.is_file():
        return {
            "message": "Frontend build not found. Run `npm run build` in frontend/ first."
        }
    return FileResponse(FRONTEND_INDEX)


@app.get("/{path:path}")
async def frontend_spa_fallback(path: str):
    """Let React Router handle client-side routes after a page refresh."""
    if not FRONTEND_INDEX.is_file():
        return {
            "message": "Frontend build not found. Run `npm run build` in frontend/ first."
        }
    return FileResponse(FRONTEND_INDEX)


if __name__ == "__main__":
    uvicorn.run(
                "app:app",
                host="127.0.0.1",
                port=8000,
                # Directly executing this file from an IDE can make uvicorn
                # watch an unrelated workspace root. Use the stable single
                # process mode here; use `uvicorn app:app --reload` from
                # backend/src when file watching is desired.
                reload=False
                )
