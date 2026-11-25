"""Which engine answers: the student's choice, else an experiment's arm, else the default, else ask them to choose.
Then retries with backoff, the fallback chain, a circuit per provider, daily caps and a run record per engine tried."""
import hashlib
import json
import os
import random
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from tfgpt_shared.db import Database, aware, now
from tfgpt_shared.evaldb import Assignment, Experiment
from tfgpt_shared.settings import env_float, env_int, env_list

from . import adapters
from .adapters import OK_STOPS, Call, Permanent, Result, Transient
from .models import Circuit, Engine, Run
from .registry import cost, default_engine, has_key, switched_on

CHECK_TASKS = ("check", "recheck")


class RouteError(Exception):
    def __init__(self, status: int, error: str, message: str):
        super().__init__(message)
        self.status, self.error, self.message = status, error, message


@dataclass
class Request:
    task: str
    system: str
    messages: list[dict]
    student_ref: str | None = None
    request_id: str | None = None
    engine: str | None = None  # the student's choice, or the engine an internal task names
    internal: bool = False  # internal tasks (compaction, evaluation) may use engines not offered to students
    json_schema: dict | None = None
    max_tokens: int | None = None
    prompt_name: str | None = None
    cache: bool = True


@dataclass
class Route:
    primary: Engine
    chain: list[Engine]
    experiment: str | None
    arm: str | None
    chosen: bool


# ------------------------------------------------------------------ availability

def circuit_open(db: Session, provider: str) -> bool:
    c = db.get(Circuit, provider)
    if not c or c.state != "open":
        return False
    cool = timedelta(seconds=env_int("CIRCUIT_COOL_SECONDS", 120))
    return now() - aware(c.opened_at) < cool  # after the cool-down one call may try again (half-open)


def available(db: Session, e: Engine | None) -> bool:
    return bool(e) and switched_on(e) and has_key(e) and not circuit_open(db, e.provider)


def engine_note(db: Session, e: Engine) -> str | None:
    if not switched_on(e):
        return e.note or "Switched off"
    if not has_key(e):
        return "No API key configured"
    if circuit_open(db, e.provider):
        return "Temporarily unavailable: the provider is failing"
    return None


def offered(db: Session) -> list[Engine]:
    return list(db.scalars(select(Engine).where(Engine.offered.is_(True)).order_by(Engine.name)))


def record_failure(db: Session, provider: str, error: str) -> None:
    c = db.get(Circuit, provider) or Circuit(provider=provider, failures=0, state="closed")
    c.failures = (c.failures or 0) + 1
    c.last_error = error[:500]
    if c.failures >= env_int("CIRCUIT_FAILURES", 3):
        c.state, c.opened_at = "open", now()
    db.add(c)


def record_success(db: Session, provider: str) -> None:
    c = db.get(Circuit, provider)
    if c and (c.failures or c.state != "closed"):
        c.failures, c.state, c.opened_at = 0, "closed", None


# ------------------------------------------------------------------ experiments

def arm_for(exp: Experiment, student_ref: str) -> str:
    """A stable hash of student and experiment picks the arm, weighted."""
    arms = [a for a in exp.arms if a.get("weight", 1) > 0]
    total = sum(a.get("weight", 1) for a in arms)
    h = int(hashlib.sha256(f"{exp.name}:{student_ref}".encode()).hexdigest()[:12], 16) % 10_000
    point, acc = h / 10_000 * total, 0.0
    for a in arms:
        acc += a.get("weight", 1)
        if point < acc:
            return a["engine"]
    return arms[-1]["engine"]


def active_experiment(db: Session, task: str) -> Experiment | None:
    try:
        return db.scalars(select(Experiment).where(Experiment.task == task, Experiment.active.is_(True))
                          .order_by(Experiment.id.desc())).first()
    except SQLAlchemyError:  # eval schema not migrated yet: no experiments
        db.rollback()
        return None


def assign(db: Session, exp: Experiment, student_ref: str, chosen: str | None) -> str:
    arm = arm_for(exp, student_ref)
    a = db.scalars(select(Assignment).where(Assignment.experiment_id == exp.id,
                                            Assignment.student_ref == student_ref)).first()
    if not a:
        a = Assignment(experiment_id=exp.id, student_ref=student_ref, engine=arm)
        db.add(a)
    if chosen and a.chosen_engine != chosen:
        a.chosen_engine = chosen  # a choice overrides the arm and is logged, since switching is a signal
    db.flush()
    return arm


def assigned_engine(db: Session, task: str, student_ref: str | None) -> str | None:
    exp = active_experiment(db, task)
    return arm_for(exp, student_ref) if exp and student_ref else None


# ------------------------------------------------------------------ caps

def day_start() -> datetime:
    t = now()
    return t.replace(hour=0, minute=0, second=0, microsecond=0)


def reset_text() -> str:
    reset = day_start() + timedelta(days=1)
    return reset.strftime("%H:%M UTC")


def check_caps(db: Session, req: Request) -> None:
    since = day_start()
    spent = db.scalar(select(func.coalesce(func.sum(Run.cost_usd), 0.0)).where(Run.created_at >= since)) or 0.0
    if spent >= env_float("DAILY_BUDGET_USD", 15.0):
        raise RouteError(429, "cap_reached", f"TFGPT has used today's budget. It resets at {reset_text()}.")
    if not req.student_ref or req.internal:
        return
    mine = Run.student_ref == req.student_ref
    tokens = db.scalar(select(func.coalesce(func.sum(Run.tokens_in + Run.tokens_out), 0))
                       .where(mine, Run.created_at >= since, Run.tokens_in.is_not(None),
                              Run.tokens_out.is_not(None))) or 0
    if tokens >= env_int("TOKENS_PER_STUDENT_DAY", 1_500_000):
        raise RouteError(429, "cap_reached", f"You've reached today's limit. It resets at {reset_text()}.")
    if req.task in CHECK_TASKS:
        done = set(db.scalars(select(Run.request_id).where(mine, Run.created_at >= since,
                                                            Run.task.in_(CHECK_TASKS), Run.status == "ok")))
        if req.request_id not in done and len(done) >= env_int("CHECKS_PER_STUDENT_DAY", 10):
            raise RouteError(429, "cap_reached",
                             f"You've run today's {len(done)} checks. More from {reset_text()}.")


# ------------------------------------------------------------------ the route

def route(db: Session, req: Request) -> Route:
    chosen = None
    if req.engine:
        e = db.get(Engine, req.engine)
        if e and (req.internal or e.offered):
            chosen = e.name
    exp = active_experiment(db, req.task) if req.student_ref and not req.internal else None
    arm = assign(db, exp, req.student_ref, chosen) if exp else None
    primary = chosen or arm or default_engine()
    if not primary:
        raise RouteError(409, "choose_model", "Choose a model first.")
    first = db.get(Engine, primary)
    if not first:
        raise RouteError(409, "choose_model", "That model isn't on the list any more. Choose another.")
    names = [primary] + [n for n in (first.fallback or []) if n != primary]
    chain = [e for n in names if (e := db.get(Engine, n)) and available(db, e)]
    if not chain:
        raise RouteError(502, "upstream", f"{first.label} isn't available right now ({engine_note(db, first)}).")
    return Route(first, chain, exp.name if exp else None, arm, chosen is not None)


def prompt_sha12(req: Request) -> str:
    blob = json.dumps({"system": req.system, "messages": req.messages}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


_slots: dict[str, threading.BoundedSemaphore] = {}
_slots_lock = threading.Lock()


def slot(e: Engine) -> threading.BoundedSemaphore:
    with _slots_lock:
        if e.name not in _slots:
            _slots[e.name] = threading.BoundedSemaphore(max(1, e.concurrency or 1))
        return _slots[e.name]


def waits() -> list[float]:
    raw = env_list("RETRY_WAITS") or ["2", "8"]
    return [float(x) for x in raw]


def execute(database: Database, req: Request, live: bool = False) -> Iterator[tuple[str, dict]]:
    """Run the request down its chain. Yields ("start", info), ("delta", {"text"}), then ("end", result).
    Raises RouteError when nothing could answer. When live (streamed to a student), an engine that already sent
    text is never swapped for another mid-answer."""
    with database.session() as db:
        check_caps(db, req)
        r = route(db, req)
        chain = [(e.name, e.provider, e.kind) for e in r.chain]
        first_name, first_label = r.primary.name, f"{r.primary.label} · {r.primary.vendor}"
    sha = prompt_sha12(req)
    call = Call(system=req.system, messages=req.messages, max_tokens=req.max_tokens,
                json_schema=req.json_schema, cache=req.cache)
    last_error = "no engine"
    for name, provider, _ in chain:
        with database.session() as db:
            e = db.get(Engine, name)
            db.expunge(e)
        key = os.environ.get(e.key_env) if e.key_env else None
        retries, started_stream = 0, False
        for attempt in range(len(waits()) + 1):
            t0 = time.monotonic()
            try:
                with slot(e):
                    gen = adapters.stream(e, call, key)
                    result = None
                    for piece in gen:
                        if isinstance(piece, Result):
                            result = piece
                            break
                        if not started_stream:
                            started_stream = True
                            yield "start", {"engine": e.name, "label": e.label, "vendor": e.vendor, "model": e.model,
                                            "fallback_from": None if name == first_name else first_label}
                        yield "delta", {"text": piece}
                if result is None:
                    raise Transient("the stream ended without a result")
                if result.stop not in OK_STOPS:
                    raise Permanent(f"stopped with {result.stop!r}: the answer may be incomplete or refused")
                if not result.text.strip():
                    raise Permanent("empty answer")
                seconds = round(time.monotonic() - t0, 2)
                with database.session() as db:
                    fresh = (result.tokens_in or 0) - (result.cache_read or 0) - (result.cache_write or 0)
                    run = Run(task=req.task, request_id=req.request_id, student_ref=req.student_ref, engine=e.name,
                              provider=e.provider, model=e.model, model_returned=result.model_returned,
                              prompt_name=req.prompt_name, prompt_sha12=sha, tokens_in=result.tokens_in,
                              cache_read=result.cache_read, cache_write=result.cache_write,
                              tokens_out=result.tokens_out, seconds=seconds,
                              cost_usd=cost(e, fresh, result.cache_write, result.cache_read, result.tokens_out),
                              retries=retries, fallback_used=name != first_name,
                              fallback_from=None if name == first_name else first_name,
                              experiment=r.experiment, arm=r.arm, chosen=r.chosen, status="ok", stop=result.stop)
                    db.add(run)
                    record_success(db, provider)
                    db.flush()
                    run_id, run_cost = run.id, run.cost_usd
                if not started_stream:
                    yield "start", {"engine": e.name, "label": e.label, "vendor": e.vendor, "model": e.model,
                                    "fallback_from": None if name == first_name else first_label}
                yield "end", {"text": result.text, "engine": e.name, "label": e.label, "vendor": e.vendor,
                              "model": e.model, "model_returned": result.model_returned, "run_id": run_id,
                              "tokens_in": result.tokens_in, "tokens_out": result.tokens_out,
                              "cache_read": result.cache_read, "cost_usd": run_cost, "seconds": seconds,
                              "fallback_from": None if name == first_name else first_label, "stop": result.stop}
                return
            except (Transient, Permanent) as ex:
                last_error = f"{type(ex).__name__}: {ex}"
                transient = isinstance(ex, Transient)
                committed = live and started_stream
                if committed or not transient or attempt == len(waits()):
                    with database.session() as db:
                        db.add(Run(task=req.task, request_id=req.request_id, student_ref=req.student_ref,
                                   engine=e.name, provider=e.provider, model=e.model, prompt_name=req.prompt_name,
                                   prompt_sha12=sha, seconds=round(time.monotonic() - t0, 2), retries=retries,
                                   fallback_used=name != first_name,
                                   fallback_from=None if name == first_name else first_name,
                                   experiment=r.experiment, arm=r.arm, chosen=r.chosen, status="error",
                                   error=last_error[:1000]))
                        record_failure(db, provider, last_error)
                    if committed:  # text already reached the student: never switch engines mid-answer
                        raise RouteError(502, "upstream", "The answer was cut off. Please try again.") from ex
                    break
                retries += 1
                w = waits()[attempt]
                time.sleep(w * (1 + random.random() / 4) if w else 0)
    raise RouteError(502, "upstream", f"No model could answer just now. Please try again in a minute. ({last_error[:120]})")
