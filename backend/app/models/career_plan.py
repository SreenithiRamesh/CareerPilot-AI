from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


from app.time_utils import (
    utc_now_naive,
)

class CareerPlan(Base):
    __tablename__ = "career_plans"

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

    job_match_result_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "job_match_results.id",
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

    readiness_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    top_priorities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    learning_order: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    practical_tasks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    portfolio_evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    interview_preparation_focus: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    action_plan_30_days: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        nullable=False,
    )