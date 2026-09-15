from sqlmodel import SQLModel, Field, Column, BigInteger, CheckConstraint, UniqueConstraint

class Score(SQLModel, table=True):
    __tablename__ = "SCORE"
    __table_args__ = (
        CheckConstraint(
            "category = 'risk_awareness' OR category = 'refusal' OR category = 'help_request'",
            name="CHK_SCORE_CATEGORY",
        ),
        CheckConstraint(
            "score >= 0 AND score <= 3",
            name="CHK_SCORE_RANGE",
        ),
        UniqueConstraint("chat_id", "category", name="UK_SCORE_CHAT_CATEGORY"),
    )

    score_id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )
    chat_id: int = Field(foreign_key="CHATTING.chat_id", nullable=False)
    category: str = Field(max_length=50, nullable=False)
    score: int = Field(nullable=False)