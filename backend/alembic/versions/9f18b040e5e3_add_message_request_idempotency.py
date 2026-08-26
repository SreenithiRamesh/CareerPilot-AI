"""add message request idempotency

Revision ID: 9f18b040e5e3
Revises: b41f8c7a2d10
Create Date: 2026-08-26 20:58:56.320294

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = "9f18b040e5e3"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "b41f8c7a2d10"

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
    op.add_column(
        "messages",
        sa.Column(
            "request_id",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_messages_request_id",
        "messages",
        ["request_id"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_messages_conversation_request_role",
        "messages",
        [
            "conversation_id",
            "request_id",
            "role",
        ],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_messages_conversation_request_role",
        "messages",
        type_="unique",
    )

    op.drop_index(
        "ix_messages_request_id",
        table_name="messages",
    )

    op.drop_column(
        "messages",
        "request_id",
    )