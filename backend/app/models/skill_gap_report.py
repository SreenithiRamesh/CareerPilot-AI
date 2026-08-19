from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SkillGapReport(Base):
    __tablename__ = "skill_gap_reports"

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

    existing_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    missing_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    partial_skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    priority_gaps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    learning_order: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    practice_tasks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    proof_of_skill_actions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    readiness_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )