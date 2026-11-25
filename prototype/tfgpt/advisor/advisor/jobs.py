"""The job queue in Postgres: checks, compactions and sweeps run here, not in a request, and survive restarts."""
import logging
import os
import socket
import threading
import time
from datetime import timedelta

from sqlalchemy import select

from tfgpt_shared.db import aware, now
from tfgpt_shared.internal import ServiceError
from tfgpt_shared.settings import env_int

from . import check, memory
from .models import Job

log = logging.getLogger("advisor.jobs")
WORKER = f"{socket.gethostname()}-{os.getpid()}"


def enqueue(db, kind: str, payload: dict, delay_seconds: int = 0, max_attempts: int = 2) -> Job:
    j = Job(kind=kind, payload=payload, status="queued", max_attempts=max_attempts,
            run_after=now() + timedelta(seconds=delay_seconds))
    db.add(j)
    db.flush()
    return j


def claim(database) -> int | None:
    with database.session() as db:
        q = (select(Job).where(Job.status == "queued", Job.run_after <= now()).order_by(Job.id).limit(1)
             .with_for_update(skip_locked=True))
        j = db.scalars(q).first()
        if not j:
            return None
        j.status, j.locked_at, j.locked_by, j.attempts = "running", now(), WORKER, j.attempts + 1
        j.started_at = j.started_at or now()
        return j.id


def requeue_stale(database) -> int:
    """A job left running by a worker that died goes back in the queue (or fails after its last attempt)."""
    cutoff = now() - timedelta(minutes=env_int("JOB_STALE_MINUTES", 20))
    n = 0
    with database.session() as db:
        for j in db.scalars(select(Job).where(Job.status == "running", Job.locked_at < cutoff).with_for_update(skip_locked=True)):
            n += 1
            if j.attempts < j.max_attempts:
                j.status, j.locked_at, j.locked_by = "queued", None, None
            else:
                j.status, j.error, j.finished_at = "failed", "worker stopped", now()
                if j.kind in ("check", "recheck"):
                    check.fail(database, j.payload["check_id"], "it stopped part-way. Please try again.")
    return n


def set_step(database, job_id: int, step: str) -> None:
    with database.session() as db:
        db.get(Job, job_id).step = step


def handle(database, harness, job: Job) -> None:
    kind, p = job.kind, job.payload
    step = lambda s: set_step(database, job.id, s)  # noqa: E731
    if kind == "check":
        check.run_check(database, harness, p["check_id"], step)
    elif kind == "recheck":
        check.run_recheck(database, harness, p["check_id"], step)
    elif kind == "compact":
        memory.compact(database.session, harness, p["thread_id"])
    elif kind == "sweep":
        with database.session() as db:
            memory.purge(db)
            for thread_id in memory.due_for_compaction(db):
                enqueue(db, "compact", {"thread_id": thread_id}, max_attempts=1)
    else:
        raise ValueError(f"unknown job kind {kind!r}")


def run_one(database, harness) -> bool:
    job_id = claim(database)
    if job_id is None:
        return False
    with database.session() as db:
        job = db.get(Job, job_id)
        db.expunge(job)
    try:
        handle(database, harness, job)
        outcome, error = "done", None
    except check.CheckFailed as ex:
        outcome, error = ("retry" if ex.retryable else "failed"), ex.message
    except ServiceError as ex:
        outcome, error = ("retry" if ex.error == "upstream" else "failed"), ex.message
    except Exception as ex:  # a bug must not kill the worker; the job fails visibly
        log.exception("job %s failed", job_id)
        outcome, error = "failed", "something went wrong on our side."
    with database.session() as db:
        j = db.get(Job, job_id)
        if outcome == "retry" and j.attempts < j.max_attempts:
            j.status, j.error, j.run_after, j.locked_at = "queued", error, now() + timedelta(seconds=env_int("RETRY_SECONDS", 30)), None
            return True
        j.status = "done" if outcome == "done" else "failed"
        j.error, j.finished_at = error, now()
    if j.status == "failed" and job.kind in ("check", "recheck"):
        check.fail(database, job.payload["check_id"], error or "unknown error")
    return True


def run_all(database, harness, limit: int = 100) -> int:
    """Run every ready job now (tests and one-off use)."""
    n = 0
    while n < limit and run_one(database, harness):
        n += 1
    return n


class Worker(threading.Thread):
    def __init__(self, database, harness, threads: int = 1):
        super().__init__(daemon=True, name="advisor-worker")
        self.database, self.harness, self.stop = database, harness, threading.Event()
        self.pool = [threading.Thread(target=self.loop, daemon=True, name=f"advisor-worker-{i}") for i in range(threads)]

    def run(self):
        for t in self.pool:
            t.start()
        while not self.stop.wait(env_int("SWEEP_SECONDS", 60)):
            try:
                requeue_stale(self.database)
                with self.database.session() as db:
                    pending = db.scalars(select(Job).where(Job.kind == "sweep", Job.status.in_(("queued", "running")))).first()
                    if not pending:
                        enqueue(db, "sweep", {}, max_attempts=1)
            except Exception:
                log.exception("sweep scheduling failed")

    def loop(self):
        while not self.stop.is_set():
            try:
                if not run_one(self.database, self.harness):
                    self.stop.wait(1.0)
            except Exception:
                log.exception("worker loop error")
                self.stop.wait(5.0)


def job_view(database, job_id: int, student_ref: str) -> dict | None:
    from .models import Check, Message, Thread

    with database.session() as db:
        j = db.get(Job, job_id)
        if not j or j.kind not in ("check", "recheck"):
            return None
        c = db.get(Check, j.payload["check_id"])
        t = db.get(Thread, c.thread_id)
        if t.student_ref != student_ref:
            return None
        out = {"status": c.status if c.status in ("done", "failed") else j.status, "step": j.step,
               "seconds": round((now() - aware(j.created_at)).total_seconds())}
        if c.message_id:
            out["message"] = memory.message_json(db, db.get(Message, c.message_id))
        return out
