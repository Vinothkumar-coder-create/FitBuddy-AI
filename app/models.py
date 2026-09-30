from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    goal: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    intensity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    )

    original_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    user: Mapped[User] = relationship(
        back_populates="plans",
    )