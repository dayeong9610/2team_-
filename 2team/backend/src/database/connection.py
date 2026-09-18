from pathlib import Path
from pydantic.v1 import BaseSettings
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import text
from model import Admin, ChatRoom, Chatting, LlmRole

from core.flow_trace import trace_flow


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE = "backend/src/database/connection.py"


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
engine_url = create_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


# =====================================================================
# DB 담당 참고
# ---------------------------------------------------------------------
# conn()         : SQLModel 테이블 생성/초기화 진입점
# get_session()  : 관리자 등 실제 SQLModel CRUD에서 사용하는 DB Session
# database_is_available(): FastAPI가 DB 장애와 무관하게 뜰 수 있도록 상태 확인
#
# 중요: 학생용 /api/sessions, /api/chat 흐름은 현재 이 get_session()을 사용하지
# 않고 core/session_store.py 메모리 저장소를 사용합니다.
# =====================================================================


def conn():
    trace_flow(
        FILE,
        "conn",
        "IN",
        {"action": "SQLModel.metadata.create_all"},
    )

    SQLModel.metadata.create_all(bind=engine_url)

    trace_flow(
        FILE,
        "conn",
        "OUT",
        {"tables_ready": True},
    )


def get_session():
    trace_flow(
        FILE,
        "get_session",
        "OPEN",
        {"session": "SQLModel Session"},
    )

    with Session(engine_url) as session:
        try:
            yield session
        finally:
            trace_flow(
                FILE,
                "get_session",
                "CLOSE",
                {"session": "SQLModel Session"},
            )


def database_is_available() -> bool:
    """DB 장애 여부를 빠르게 확인. 실패를 밖으로 전파하지 않습니다."""
    try:
        with engine_url.connect() as connection:
            connection.execute(text("SELECT 1"))

        trace_flow(
            FILE,
            "database_is_available",
            "OUT",
            {"available": True},
        )
        return True
    except Exception as exc:
        trace_flow(
            FILE,
            "database_is_available",
            "OUT",
            {
                "available": False,
                "error_type": type(exc).__name__,
            },
        )
        return False
