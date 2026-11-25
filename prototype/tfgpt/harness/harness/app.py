"""Harness API, internal only: the engine list, one-shot generation and streamed generation."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from tfgpt_shared import evaldb, sse
from tfgpt_shared.db import Database, make_engine
from tfgpt_shared.internal import require_internal
from tfgpt_shared.migrate import prepare
from tfgpt_shared.settings import version

from . import registry
from .models import SCHEMA, Base
from .routing import Request, RouteError, assigned_engine, available, engine_note, execute, offered

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class Message(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class GenerateBody(BaseModel):
    task: str = Field(pattern="^(check|recheck|ask|compact|eval)$")
    system: str
    messages: list[Message]
    student_ref: str | None = None
    request_id: str | None = None
    engine: str | None = None
    internal: bool = False
    json_schema: dict | None = None
    max_tokens: int | None = None
    prompt_name: str | None = None
    cache: bool = True

    def request(self) -> Request:
        return Request(task=self.task, system=self.system, messages=[m.model_dump() for m in self.messages],
                       student_ref=self.student_ref, request_id=self.request_id, engine=self.engine,
                       internal=self.internal, json_schema=self.json_schema, max_tokens=self.max_tokens,
                       prompt_name=self.prompt_name, cache=self.cache)


def error(ex: RouteError) -> JSONResponse:
    return JSONResponse({"detail": {"error": ex.error, "message": ex.message}}, status_code=ex.status)


def create_app(database: Database | None = None, engines_spec: dict | None = None) -> FastAPI:
    database = database or Database(make_engine())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        prepare(database.engine, Base.metadata, MIGRATIONS, SCHEMA)
        prepare(database.engine, evaldb.EvalBase.metadata, evaldb.MIGRATIONS, evaldb.SCHEMA)
        with database.session() as db:
            registry.seed(db, engines_spec or registry.load_file())
        yield

    app = FastAPI(title="TFGPT harness", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.database = database
    guard = [Depends(require_internal)]

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "service": "harness", "version": version()}

    @app.get("/v1/engines", dependencies=guard)
    def engines(student_ref: str | None = None):
        with database.session() as db:
            rows = [{"name": e.name, "label": e.label, "vendor": e.vendor, "model": e.model,
                     "available": available(db, e), "note": engine_note(db, e)} for e in offered(db)]
            return {"engines": rows, "assigned": assigned_engine(db, "check", student_ref)}

    @app.post("/v1/generate", dependencies=guard)
    def generate(body: GenerateBody):
        try:
            for name, data in execute(database, body.request()):
                if name == "end":
                    return data
        except RouteError as ex:
            return error(ex)
        return error(RouteError(502, "upstream", "No answer."))

    @app.post("/v1/stream", dependencies=guard)
    def stream(body: GenerateBody):
        events = execute(database, body.request(), live=True)
        try:  # caps, routing and the first engine's errors come back as a plain error, before any stream
            first = next(events)
        except RouteError as ex:
            return error(ex)

        def gen():
            yield sse.event(*first)
            try:
                for name, data in events:
                    yield sse.event(name, data)
            except RouteError as ex:
                yield sse.event("error", {"error": ex.error, "message": ex.message})

        return StreamingResponse(gen(), media_type="text/event-stream")

    return app

