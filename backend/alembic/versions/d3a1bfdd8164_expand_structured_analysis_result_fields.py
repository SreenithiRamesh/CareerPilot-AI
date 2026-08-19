"""expand structured analysis result fields

Revision ID: d3a1bfdd8164
Revises: 85666655fd18
Create Date: 2026-08-19 16:20:31.241725

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d3a1bfdd8164"
down_revision: Union[str, Sequence[str], None] = "85666655fd18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Career Plan structured-output fields
    op.add_column(
        "career_plans",
        sa.Column(
            "practical_tasks",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "career_plans",
        sa.Column(
            "portfolio_evidence",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "career_plans",
        sa.Column(
            "interview_preparation_focus",
            sa.Text(),
            nullable=True,
        ),
    )

    # Job Match structured-output fields
    op.add_column(
        "job_match_results",
        sa.Column(
            "priority_actions",
            sa.Text(),
            nullable=True,
        ),
    )

    # Skill Gap structured-output fields
    op.add_column(
        "skill_gap_reports",
        sa.Column(
            "practice_tasks",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "skill_gap_reports",
        sa.Column(
            "proof_of_skill_actions",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "skill_gap_reports",
        sa.Column(
            "readiness_summary",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Skill Gap fields
    op.drop_column(
        "skill_gap_reports",
        "readiness_summary",
    )

    op.drop_column(
        "skill_gap_reports",
        "proof_of_skill_actions",
    )

    op.drop_column(
        "skill_gap_reports",
        "practice_tasks",
    )

    # Job Match fields
    op.drop_column(
        "job_match_results",
        "priority_actions",
    )

    # Career Plan fields
    op.drop_column(
        "career_plans",
        "interview_preparation_focus",
    )

    op.drop_column(
        "career_plans",
        "portfolio_evidence",
    )

    op.drop_column(
        "career_plans",
        "practical_tasks",
    )