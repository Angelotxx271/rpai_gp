"""The harness schema: the engine registry, one run record per engine tried, and a circuit per provider."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, MetaData, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tfgpt_shared.db import JSONType, now

SCHEMA = "harness"


class Base(DeclarativeBase):
    metadata = MetaData(schema=SCHEMA)


class Engine(Base):
    __tablename__ = "engines"
    name: Mapped[str] = mapped_column(String(40), primary_key=True)
    provider: Mapped[str] = mapped_column(String(40))
    kind: Mapped[str] = mapped_column(String(20))  # anthropic, openai, ollama, fake
    model: Mapped[str] = mapped_column(String(120))
    label: Mapped[str] = mapped_column(String(120))
    vendor: Mapped[str] = mapped_column(String(120))
    offered: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    context: Mapped[int] = mapped_column(Integer, default=0)
    concurrency: Mapped[int] = mapped_column(Integer, default=2)
    price: Mapped[dict] = mapped_column(JSONType, default=dict)
    params: Mapped[dict] = mapped_column(JSONType, default=dict)
    fallback: Mapped[list] = mapped_column(JSONType, default=list)
    base_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    key_env: Mapped[str | None] = mapped_column(String(60), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Run(Base):
    """One engine tried for one request: the spike's run record, plus routing fields."""
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    task: Mapped[str] = mapped_column(String(20))
    request_id: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    student_ref: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    engine: Mapped[str] = mapped_column(String(40))
    provider: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    model_returned: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prompt_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    prompt_sha12: Mapped[str] = mapped_column(String(12))
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cache_read: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cache_write: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, default=0)
    fallback_used: Mapped[bool] = mapped_column(Boolean, default=False)
    fallback_from: Mapped[str | None] = mapped_column(String(40), nullable=True)
    experiment: Mapped[str | None] = mapped_column(String(80), nullable=True)
    arm: Mapped[str | None] = mapped_column(String(40), nullable=True)
    chosen: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20))  # ok, error
    stop: Mapped[str | None] = mapped_column(String(40), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Circuit(Base):
    __tablename__ = "circuits"
    provider: Mapped[str] = mapped_column(String(40), primary_key=True)
    state: Mapped[str] = mapped_column(String(10), default="closed")  # closed, open
    failures: Mapped[int] = mapped_column(Integer, default=0)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
