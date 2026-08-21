"""add interview type to mock interview sessions

Revision ID: d9ea5cda33ff
Revises: 1b7602d943e0
Create Date: 2026-08-21 14:21:32.211585

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision: str = "d9ea5cda33ff"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "1b7602d943e0"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """Add interview type to mock interview sessions."""

    op.add_column(
        "mock_interview_sessions",
        sa.Column(
            "interview_type",
            sa.String(length=20),
            nullable=False,
            server_default="mixed",
        ),
    )

    op.create_index(
        op.f(
            "ix_mock_interview_sessions_interview_type"
        ),
        "mock_interview_sessions",
        [
            "interview_type",
        ],
        unique=False,
    )

    # The default is useful while migrating any
    # existing rows, but the application model
    # already provides the Python-side default.
    #
    # Remove the database default after migration
    # so the schema stays aligned with the model.

    op.alter_column(
        "mock_interview_sessions",
        "interview_type",
        server_default=None,
        existing_type=sa.String(
            length=20
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Remove interview type from mock interview sessions."""

    op.drop_index(
        op.f(
            "ix_mock_interview_sessions_interview_type"
        ),
        table_name=(
            "mock_interview_sessions"
        ),
    )

    op.drop_column(
        "mock_interview_sessions",
        "interview_type",
    )