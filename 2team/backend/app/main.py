from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import episodes, chat


app = FastAPI(
    title="Manyang Backend",
    version="0.1.0"
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
    episodes.router,
    prefix="/api"
)

app.include_router(
    chat.router,
    prefix="/api"
)

@app.get("/")
def root():
    return {
        "message": "Manyang Backend Running"
    }