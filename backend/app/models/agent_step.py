from datetime import datetime

from sqlalchemy import (
    DateTime,
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


class AgentStep(Base):
    __tablename__ = "agent_steps"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    agent_run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "agent_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    planned_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tool_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    tool_input: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    observation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )