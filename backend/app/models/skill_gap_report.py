from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database import Base


class SkillGapReport(Base):
    __tablename__ = "skill_gap_reports"

    # ==================================================
    # PRIMARY KEY
    # ==================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # ==================================================
    # RELATIONSHIPS
    # ==================================================

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

    # ==================================================
    # SKILL ANALYSIS
    # ==================================================

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

    # ==================================================
    # PRIORITY ANALYSIS
    # ==================================================

    priority_gaps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    learning_order: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # ACTION PLAN
    # ==================================================

    practice_tasks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    proof_of_skill_actions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # PORTFOLIO PROJECT RECOMMENDATIONS
    # ==================================================
    #
    # Stored as JSON text.
    #
    # Expected structure:
    #
    # [
    #     {
    #         "target_skill": "Docker",
    #         "project_title": "Containerized Task API",
    #         "project_goal": "...",
    #         "suggested_stack": [
    #             "Java",
    #             "Spring Boot",
    #             "MySQL",
    #             "Docker"
    #         ],
    #         "implementation_steps": [
    #             "...",
    #             "..."
    #         ],
    #         "portfolio_evidence": [
    #             "...",
    #             "..."
    #         ]
    #     }
    # ]
    #
    # We keep this as Text because the existing
    # SkillGapReport persistence layer stores
    # structured lists as serialized JSON.
    #
    # The API/service layer is responsible for:
    #
    # Python list[dict]
    #       ↓
    # json.dumps(...)
    #       ↓
    # MySQL TEXT
    #
    # When reading:
    #
    # MySQL TEXT
    #       ↓
    # json.loads(...)
    #       ↓
    # Python list[dict]
    #
    # ==================================================

    portfolio_project_prompts: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # SUMMARY
    # ==================================================

    readiness_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ==================================================
    # TIMESTAMP
    # ==================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )