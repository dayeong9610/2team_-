from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware
)
# python -m uvicorn app.main:app --reload 실행확인
from app.api.chat import (
    router as chat_router
)


app = FastAPI(
    title="Manyang API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    chat_router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "message":
        "Manyang API Running"
    }