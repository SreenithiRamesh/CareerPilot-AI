"""add persistent chat messages

Revision ID: b41f8c7a2d10
Revises: 7ad6513dc957
Create Date: 2026-08-26

"""

from typing import (
    Sequence,
    Union,
)

from alembic import op
import sqlalchemy as sa


revision: str = "b41f8c7a2d10"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "7ad6513dc957"

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
        "conversations",
        sa.Column(
            "resume_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_conversations_resume_id",
        "conversations",
        ["resume_id"],
        unique=False,
    )

    op.create_index(
        "ix_conversations_updated_at",
        "conversations",
        ["updated_at"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_conversations_resume_id_resumes",
        "conversations",
        "resumes",
        ["resume_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    op.create_index(
        "ix_messages_conversation_id",
        "messages",
        ["conversation_id"],
        unique=False,
    )

    op.create_index(
        "ix_messages_created_at",
        "messages",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_messages_created_at",
        table_name="messages",
    )

    op.drop_index(
        "ix_messages_conversation_id",
        table_name="messages",
    )

    op.drop_table(
        "messages",
    )

    op.drop_constraint(
        "fk_conversations_resume_id_resumes",
        "conversations",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_conversations_updated_at",
        table_name="conversations",
    )

    op.drop_index(
        "ix_conversations_resume_id",
        table_name="conversations",
    )

    op.drop_column(
        "conversations",
        "resume_id",
    )