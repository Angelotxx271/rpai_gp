"""The eval schema: experiments and assignments (read by the harness when routing), ground truth, verdicts, rollups.

It belongs to the eval CLI; the harness also migrates it at start-up because routing reads it.
"""
from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, MetaData, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .db import JSONType, now

SCHEMA = "eval"
MIGRATIONS = Path(__file__).parent / "eval_migrations"


class EvalBase(DeclarativeBase):
    metadata = MetaData(schema=SCHEMA)


class Experiment(EvalBase):
    __tablename__ = "experiments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    task: Mapped[str] = mapped_column(String(20))  # check, recheck or ask
    arms: Mapped[list] = mapped_column(JSONType)  # [{"engine": "opus", "weight": 1}, ...]
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    stopped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Assignment(EvalBase):
    __tablename__ = "assignments"
    __table_args__ = (UniqueConstraint("experiment_id", "student_ref"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("eval.experiments.id"))
    student_ref: Mapped[str] = mapped_column(String(64))
    engine: Mapped[str] = mapped_column(String(40))  # the arm the hash gave
    chosen_engine: Mapped[str | None] = mapped_column(String(40), nullable=True)  # the student's own choice, if any
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class GroundTruth(EvalBase):
    __tablename__ = "ground_truth"
    __table_args__ = (UniqueConstraint("set_name", "item_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    set_name: Mapped[str] = mapped_column(String(40))
    case_id: Mapped[str] = mapped_column(String(40))
    item_id: Mapped[str] = mapped_column(String(60))
    section: Mapped[str] = mapped_column(Text)
    passage: Mapped[str | None] = mapped_column(Text, nullable=True)
    problem: Mapped[str] = mapped_column(Text)


class Verdict(EvalBase):
    __tablename__ = "verdicts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_label: Mapped[str] = mapped_column(String(80))
    set_name: Mapped[str] = mapped_column(String(40))
    case_id: Mapped[str] = mapped_column(String(40))
    repeat: Mapped[int] = mapped_column(Integer)
    engine: Mapped[str] = mapped_column(String(40))
    commit: Mapped[str] = mapped_column(String(40))
    caught: Mapped[list] = mapped_column(JSONType)
    missed: Mapped[list] = mapped_column(JSONType)
    wrong: Mapped[int] = mapped_column(Integer)
    flags: Mapped[int] = mapped_column(Integer)
    hidden: Mapped[int] = mapped_column(Integer)
    injection_obeyed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Rollup(EvalBase):
    __tablename__ = "rollups"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    period: Mapped[str] = mapped_column(String(40))
    engine: Mapped[str] = mapped_column(String(40))
    metric: Mapped[str] = mapped_column(String(60))
    value: Mapped[float] = mapped_column(Float)
