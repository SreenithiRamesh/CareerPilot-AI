from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JobMatchResult(Base):
    __tablename__ = "job_match_results"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_description_id: Mapped[int] = mapped_column(
        ForeignKey(
            "job_descriptions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    match_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    strong_matches: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    partial_matches: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    missing_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resume_improvements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )