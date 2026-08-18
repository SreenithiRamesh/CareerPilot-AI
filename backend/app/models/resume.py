from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

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

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    s3_object_key: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    vector_collection_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    upload_timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )