"""
SQLAlchemy ORM models, matching schema.sql table-for-table.

These are what the app actually queries against. schema.sql exists
alongside these as a plain-SQL reference and for setting up the database
by hand if you'd rather not rely on create_all() — see app/db.py.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    ARRAY, Boolean, CheckConstraint, DateTime, ForeignKey, Integer,
    Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="student")
    plan: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="user")
    certificates: Mapped[list["Certificate"]] = relationship(back_populates="user")
    subscription: Mapped["Subscription"] = relationship(back_populates="user", uselist=False)


class Academy(Base):
    __tablename__ = "academies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    courses: Mapped[list["Course"]] = relationship(back_populates="academy")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    academy_id: Mapped[int] = mapped_column(ForeignKey("academies.id"), nullable=False)
    instructor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    # ARRAY(String) is a genuine PostgreSQL type. It will fail against the
    # SQLite fallback in app/db.py — that fallback is only good enough for
    # the User/auth tables below, not the full schema. Point DATABASE_URL at
    # real Postgres before touching courses/lessons.
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Numeric(8, 2), default=0)  # 0 = included in plans, not sold individually
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    learn_outcomes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    academy: Mapped["Academy"] = relationship(back_populates="courses")
    instructor: Mapped["User | None"] = relationship()
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="course", order_by="Lesson.position")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("course_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)

    course: Mapped["Course"] = relationship(back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    progress_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")


class Certificate(Base):
    __tablename__ = "certificates"
    __table_args__ = (CheckConstraint("score BETWEEN 0 AND 100"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    certificate_id: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="certificates")
    course: Mapped["Course"] = relationship()


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_provider_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscription")


class AIConversationLog(Base):
    __tablename__ = "ai_conversation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    flag_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
