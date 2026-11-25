"""The advisor schema: document packs, the continuous thread, checks, flags, compactions and the job queue."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tfgpt_shared.db import JSONType, now

SCHEMA = "advisor"


class Base(DeclarativeBase):
    metadata = MetaData(schema=SCHEMA)


class Programme(Base):
    __tablename__ = "programmes"
    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))


class DocPack(Base):
    __tablename__ = "doc_packs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    programme: Mapped[str] = mapped_column(ForeignKey("advisor.programmes.code"))
    stage: Mapped[str] = mapped_column(String(40))  # proposal first
    title: Mapped[str] = mapped_column(String(200))
    sha12: Mapped[str] = mapped_column(String(12))
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    sections: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Document(Base):
    """One numbered section of a pack (S1, S2, ...), the unit a flag or an answer cites."""
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pack_id: Mapped[int] = mapped_column(ForeignKey("advisor.doc_packs.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    sid: Mapped[str] = mapped_column(String(10))
    level: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    path: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    sha12: Mapped[str] = mapped_column(String(12))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Thread(Base):
    """One continuous thread per student and TFG: the student never opens a new chat."""
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_ref: Mapped[str] = mapped_column(String(64), unique=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_upto: Mapped[int] = mapped_column(Integer, default=0)  # last message id folded into the summary
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("advisor.threads.id"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # student, tfgpt
    kind: Mapped[str] = mapped_column(String(10))  # text, work, check, recheck, answer, notice
    text: Mapped[str] = mapped_column(Text, default="")
    data: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Check(Base):
    __tablename__ = "checks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("advisor.threads.id"), index=True)
    kind: Mapped[str] = mapped_column(String(10))  # check, recheck
    status: Mapped[str] = mapped_column(String(10), default="queued")  # queued, running, done, failed
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    engine_choice: Mapped[str | None] = mapped_column(String(40), nullable=True)
    topic: Mapped[str] = mapped_column(Text, default="")
    work_text: Mapped[str | None] = mapped_column(Text, nullable=True)  # deleted when the session ends
    work_words: Mapped[int] = mapped_column(Integer, default=0)
    pack_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_sha12: Mapped[str | None] = mapped_column(String(12), nullable=True)
    engine: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fallback_from: Mapped[str | None] = mapped_column(String(200), nullable=True)
    hidden: Mapped[int] = mapped_column(Integer, default=0)
    seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Flag(Base):
    """A flag is a row, so the re-check's solved list is a database match, not summary text."""
    __tablename__ = "flags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("advisor.threads.id"), index=True)
    check_id: Mapped[int] = mapped_column(ForeignKey("advisor.checks.id"))
    section_id: Mapped[str] = mapped_column(String(10))
    section: Mapped[str] = mapped_column(Text)
    quote: Mapped[str | None] = mapped_column(Text, nullable=True)  # a short quote: kept, unlike the upload
    missing: Mapped[bool] = mapped_column(Boolean, default=False)
    problem: Mapped[str] = mapped_column(Text)
    route: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(10), default="open")  # open, solved, dismissed
    solved_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Compaction(Base):
    __tablename__ = "compactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("advisor.threads.id"), index=True)
    upto_message_id: Mapped[int] = mapped_column(Integer)
    messages_folded: Mapped[int] = mapped_column(Integer)
    summary_chars: Mapped[int] = mapped_column(Integer)
    engine: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Job(Base):
    """The Postgres queue: workers take jobs with SELECT ... FOR UPDATE SKIP LOCKED, so jobs survive restarts."""
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_ready", "status", "run_after"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))  # check, recheck, compact, sweep
    payload: Mapped[dict] = mapped_column(JSONType, default=dict)
    status: Mapped[str] = mapped_column(String(10), default="queued")  # queued, running, done, failed
    step: Mapped[str | None] = mapped_column(String(60), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=2)
    run_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_by: Mapped[str | None] = mapped_column(String(60), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
