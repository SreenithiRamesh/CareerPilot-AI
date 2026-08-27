from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base
from app.time_utils import (
    utc_now_naive,
)


class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        UniqueConstraint(
            "conversation_id",
            "request_id",
            "role",
            name=(
                "uq_messages_conversation_"
                "request_role"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    mode: Mapped[str] = mapped_column(
        String(20),
        default="chat",
        server_default="chat",
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response_payload: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        nullable=False,
        index=True,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )