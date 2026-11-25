"""Advisor API, internal only: the thread, checks and re-checks as jobs, questions as a stream, flags, feedback."""
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select

from tfgpt_shared import textmatch
from tfgpt_shared.db import Database, make_engine
from tfgpt_shared.internal import ServiceError, require_internal
from tfgpt_shared.migrate import prepare
from tfgpt_shared.settings import env, env_int, version

from . import ask, check, jobs, memory, pack as packs
from .harness_client import Harness
from .models import SCHEMA, Base, Check, Flag, Message

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class CheckBody(BaseModel):
    student_ref: str = Field(min_length=8, max_length=64)
    session_id: str | None = None
    topic: str = Field(default="", max_length=2000)
    work: str = Field(max_length=60000)
    kind: str = Field(pattern="^(check|recheck)$")
    engine: str | None = None


class AskBody(BaseModel):
    student_ref: str = Field(min_length=8, max_length=64)
    session_id: str | None = None
    topic: str = Field(default="", max_length=2000)
    question: str = Field(min_length=1, max_length=2000)
    engine: str | None = None


class PackBody(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    markdown: str = Field(min_length=100, max_length=2_000_000)


class Owner(BaseModel):
    student_ref: str


class Feedback(Owner):
    value: str = Field(pattern="^(up|down)$")


def fail(status: int, error: str, message: str) -> JSONResponse:
    return JSONResponse({"detail": {"error": error, "message": message}}, status_code=status)


def create_app(database: Database | None = None, harness: Harness | None = None, start_worker: bool = True) -> FastAPI:
    database = database or Database(make_engine())
    harness = harness or Harness(httpx.Client(base_url=env("HARNESS_URL", "http://localhost:8002")))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        prepare(database.engine, Base.metadata, MIGRATIONS, SCHEMA)
        worker = None
        if start_worker:
            worker = jobs.Worker(database, harness, threads=env_int("WORKER_THREADS", 2))
            worker.start()
        yield
        if worker:
            worker.stop.set()

    app = FastAPI(title="TFGPT advisor", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.database, app.state.harness = database, harness
    guard = [Depends(require_internal)]

    @app.get("/healthz")
    def healthz():
        with database.session() as db:
            p = packs.active(db)
        return {"ok": True, "service": "advisor", "version": version(), "pack": p.sha12 if p else None}

    @app.post("/internal/packs", dependencies=guard)
    def load_pack(body: PackBody):
        with database.session() as db:
            p = packs.load(db, body.markdown, body.title)
            return {"id": p.id, "sha12": p.sha12, "sections": p.sections}

    @app.get("/internal/threads/{student_ref}", dependencies=guard)
    def thread(student_ref: str):
        with database.session() as db:
            return memory.view(db, student_ref)

    @app.post("/internal/checks", dependencies=guard, status_code=202)
    def create_check(body: CheckBody):
        work = body.work.strip()
        if not work:
            return fail(422, "empty", "Paste or upload your proposal first.")
        n = textmatch.words(work)
        if n > check.max_words():
            return fail(413, "too_long", f"That's {n} words; TFGPT checks up to {check.max_words()} at a time.")
        with database.session() as db:
            t = memory.thread_for(db, body.student_ref)
            if body.kind == "recheck" and not db.scalars(select(Check).where(Check.thread_id == t.id,
                                                                           Check.status == "done")).first():
                return fail(409, "no_check_yet", "Run a first check before checking again.")
            memory.touch(t, body.session_id)
            memory.add(db, t, "student", "work", f"Proposal, {n} words")
            c = Check(thread_id=t.id, kind=body.kind, session_id=body.session_id, engine_choice=body.engine,
                      topic=body.topic, work_text=work, work_words=n)
            db.add(c)
            db.flush()
            j = jobs.enqueue(db, body.kind, {"check_id": c.id})
            return {"job_id": j.id, "check_id": c.id}

    @app.get("/internal/jobs/{job_id}", dependencies=guard)
    def job(job_id: int, student_ref: str):
        v = jobs.job_view(database, job_id, student_ref)
        return v if v else fail(404, "not_found", "No such check.")

    @app.post("/internal/ask", dependencies=guard)
    def ask_(body: AskBody):
        try:
            stream = ask.start(database, harness, body.student_ref, body.session_id, body.topic, body.question,
                               body.engine)
        except ServiceError as ex:
            return fail(ex.status, ex.error, ex.message)
        return StreamingResponse(stream, media_type="text/event-stream")

    @app.post("/internal/flags/{flag_id}/dismiss", dependencies=guard)
    def dismiss(flag_id: int, body: Owner):
        with database.session() as db:
            f = db.get(Flag, flag_id)
            t = memory.thread_for(db, body.student_ref, create=False)
            if not f or not t or f.thread_id != t.id:
                return fail(404, "not_found", "No such flag.")
            if f.status == "open":
                f.status = "dismissed"
            return {"flag": memory.flag_json(f)}

    @app.post("/internal/messages/{message_id}/feedback", dependencies=guard)
    def feedback(message_id: int, body: Feedback):
        with database.session() as db:
            m = db.get(Message, message_id)
            t = memory.thread_for(db, body.student_ref, create=False)
            if not m or not t or m.thread_id != t.id or m.role != "tfgpt":
                return fail(404, "not_found", "No such message.")
            m.feedback = body.value
            return {"ok": True}

    return app

