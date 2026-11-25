"""The app schema: students (an opaque id, an optional alias, the topic), their token hashes and their sessions."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tfgpt_shared.db import now

SCHEMA = "app"


class Base(DeclarativeBase):
    metadata = MetaData(schema=SCHEMA)


class Student(Base):
    __tablename__ = "students"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # the student_ref the other services see
    alias: Mapped[str | None] = mapped_column(String(60), nullable=True)
    degree: Mapped[str] = mapped_column(String(120), default="Data and Business Analytics")
    topic: Mapped[str] = mapped_column(Text)
    engine_choice: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class TokenHash(Base):
    """Only the hash of the student's token is stored; the token itself lives in their cookie (and resume code)."""
    __tablename__ = "token_hashes"
    hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("app.students.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("app.students.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
