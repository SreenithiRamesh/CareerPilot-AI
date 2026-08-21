from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database import Base


class MockInterviewSession(Base):
    __tablename__ = "mock_interview_sessions"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # ==================================================
    # OWNERSHIP
    # ==================================================

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ==================================================
    # PROVENANCE
    # ==================================================

    resume_id: Mapped[int] = mapped_column(
        ForeignKey(
            "resumes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    job_description_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "job_descriptions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    skill_gap_report_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "skill_gap_reports.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ==================================================
    # INTERVIEW CONFIGURATION
    # ==================================================

    interview_type: Mapped[str] = mapped_column(
        String(20),
        default="mixed",
        nullable=False,
        index=True,
    )

    # ==================================================
    # SESSION STATE
    # ==================================================

    status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        nullable=False,
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    current_question_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ==================================================
    # QUESTIONS + ANSWERS
    # ==================================================
    #
    # Stored as serialized JSON in MySQL TEXT.
    #
    # Example:
    #
    # [
    #     {
    #         "question_number": 1,
    #         "question": "...",
    #         "skill_target": "CI/CD",
    #         "interview_type": "technical",
    #         "answer": "...",
    #         "feedback": "...",
    #         "score": 8.0,
    #         "strengths": [
    #             "..."
    #         ],
    #         "improvements": [
    #             "..."
    #         ],
    #         "better_answer_approach": "..."
    #     }
    # ]
    #
    # ==================================================

    questions_answers: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # FINAL INTERVIEW RESULTS
    # ==================================================

    overall_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    readiness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Serialized JSON list
    strengths: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Serialized JSON list
    weak_areas: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # TIMESTAMPS
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )