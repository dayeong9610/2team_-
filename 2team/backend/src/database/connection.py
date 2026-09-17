from pathlib import Path
from pydantic.v1 import BaseSettings
from sqlmodel import SQLModel, Session, create_engine
from model import Admin, ChatRoom, Chatting, LlmRole

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = PROJECT_ROOT / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
engine_url = create_engine(settings.DATABASE_URL, echo=True)


def conn():
    SQLModel.metadata.create_all(engine_url)

def get_session():
    with Session(engine_url) as session:
        yield session
