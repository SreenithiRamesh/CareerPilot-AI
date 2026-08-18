from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CareerProfile(Base):
    __tablename__ = "career_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    education: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    graduation_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    target_role: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    career_goal: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="career_profile",
    )
