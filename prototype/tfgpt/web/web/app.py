"""Web service, the only public one: the chat page, the student's cookie, and the browser API in API.md."""
import base64
import hashlib
import hmac
import secrets
import threading
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select

from tfgpt_shared import sse, textmatch
from tfgpt_shared.db import Database, aware, make_engine, now
from tfgpt_shared.internal import HEADER, ServiceError, call, error_of, internal_token
from tfgpt_shared.migrate import prepare
from tfgpt_shared.settings import PROGRAMME, env, env_bool, env_float, env_int, version

from .extract import ExtractError, extract
from .models import SCHEMA, Base, Session, Student, TokenHash

STATIC = Path(__file__).parent / "static"
MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"
COOKIE = "tfgpt_token"
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; "
       "font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


class ApiError(Exception):
    def __init__(self, status: int, error: str, message: str):
        super().__init__(message)
        self.status, self.error, self.message = status, error, message


class StartBody(BaseModel):
    topic: str = Field(min_length=10, max_length=1000)
    alias: str | None = Field(default=None, max_length=60)


class ResumeBody(BaseModel):
    code: str = Field(max_length=40)


class TopicBody(BaseModel):
    topic: str = Field(min_length=10, max_length=1000)


class EngineBody(BaseModel):
    name: str = Field(max_length=40)


class WorkBody(BaseModel):
    work: str = Field(max_length=60000)


class AskBody(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class FeedbackBody(BaseModel):
    value: str = Field(pattern="^(up|down)$")


# ------------------------------------------------------------------ tokens

def new_token() -> str:
    return base64.b32encode(secrets.token_bytes(10)).decode("ascii")  # 16 characters, 80 bits


def code_of(token: str) -> str:
    return "-".join(token[i:i + 4] for i in range(0, len(token), 4))


def token_of(code: str) -> str:
    return "".join(ch for ch in code.upper() if ch.isalnum())


def hash_of(token: str) -> str:
    return hashlib.sha256(token.encode("ascii", errors="ignore")).hexdigest()


class Throttle:
    """At most `limit` tries per key per hour (resume codes), in memory."""

    def __init__(self, limit: int):
        self.limit, self.hits, self.lock = limit, defaultdict(list), threading.Lock()

    def allow(self, key: str) -> bool:
        with self.lock:
            cutoff = time.monotonic() - 3600
            self.hits[key] = [t for t in self.hits[key] if t > cutoff]
            if len(self.hits[key]) >= self.limit:
                return False
            self.hits[key].append(time.monotonic())
            return True


def create_app(database: Database | None = None, advisor: httpx.Client | None = None,
               harness: httpx.Client | None = None) -> FastAPI:
    database = database or Database(make_engine())
    advisor = advisor or httpx.Client(base_url=env("ADVISOR_URL", "http://localhost:8001"), timeout=30)
    harness = harness or httpx.Client(base_url=env("HARNESS_URL", "http://localhost:8002"), timeout=30)
    poll = env_float("JOB_POLL_SECONDS", 2.0)
    secure_cookie = env_bool("COOKIE_SECURE", True)
    throttle = Throttle(env_int("RESUME_TRIES_PER_HOUR", 20))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        prepare(database.engine, Base.metadata, MIGRATIONS, SCHEMA)
        yield

    app = FastAPI(title="TFGPT", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(ApiError)
    def api_error(_req, ex: ApiError):
        return JSONResponse({"error": ex.error, "message": ex.message}, status_code=ex.status)

    @app.exception_handler(ServiceError)
    def service_error(_req, ex: ServiceError):
        status = ex.status if ex.status in (409, 413, 422, 429) else 502
        return JSONResponse({"error": ex.error, "message": ex.message}, status_code=status)

    @app.middleware("http")
    async def guard(request: Request, call_next):
        if request.method in ("POST", "PATCH", "PUT", "DELETE") and request.url.path.startswith("/api/"):
            if request.headers.get("x-tfgpt") != "1":  # a cross-site form can't set this header
                return JSONResponse({"error": "forbidden", "message": "Refused."}, status_code=403)
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = CSP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    # ------------------------------------------------------------------ the student

    def student_of(request: Request) -> tuple[Student, str, int] | None:
        token = request.cookies.get(COOKIE)
        if not token:
            return None
        with database.session() as db:
            th = db.get(TokenHash, hash_of(token))
            if not th:
                return None
            th.last_used_at = now()
            s = db.get(Student, th.student_id)
            sess = db.scalars(select(Session).where(Session.student_id == s.id)
                              .order_by(Session.id.desc())).first()
            if not sess or now() - aware(sess.last_seen_at) > timedelta(minutes=env_int("SESSION_MINUTES", 30)):
                sess = Session(student_id=s.id)
                db.add(sess)
            sess.last_seen_at = now()
            db.flush()
            return s, token, sess.id

    def need(request: Request) -> tuple[Student, str, int]:
        found = student_of(request)
        if not found:
            raise ApiError(401, "no_student", "Tell TFGPT your topic first.")
        return found

    def me_json(s: Student | None, token: str | None) -> dict:
        if not s:
            return {"student": None}
        return {"student": {"alias": s.alias, "topic": s.topic, "programme": PROGRAMME}, "engine": s.engine_choice,
                "resume_code": code_of(token)}

    def set_cookie(resp: JSONResponse, token: str) -> JSONResponse:
        resp.set_cookie(COOKIE, token, max_age=400 * 24 * 3600, httponly=True, secure=secure_cookie, samesite="lax")
        return resp

    def advisor_call(method: str, path: str, **kw) -> dict:
        return call(advisor, method, path, **kw)

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "service": "web", "version": version()}

    @app.get("/api/meta")
    def meta():
        return {"version": version(), "session_minutes": env_int("SESSION_MINUTES", 30),
                "compact_minutes": env_int("COMPACT_MINUTES", 5), "max_words": env_int("MAX_WORDS", 3000)}

    @app.get("/api/me")
    def me(request: Request):
        found = student_of(request)
        return me_json(found[0], found[1]) if found else {"student": None}

    @app.post("/api/start")
    def start(body: StartBody):
        token = new_token()
        with database.session() as db:
            s = Student(id=uuid.uuid4().hex, alias=(body.alias or "").strip() or None, topic=body.topic.strip())
            db.add(s)
            db.flush()
            db.add(TokenHash(hash=hash_of(token), student_id=s.id))
            out = me_json(s, token)
        return set_cookie(JSONResponse(out), token)

    @app.post("/api/resume")
    def resume(body: ResumeBody, request: Request):
        if not throttle.allow(request.client.host if request.client else "?"):
            raise ApiError(429, "cap_reached", "Too many tries. Wait an hour and try again.")
        token = token_of(body.code)
        with database.session() as db:
            th = db.get(TokenHash, hash_of(token)) if len(token) == 16 else None
            if not th:
                raise ApiError(404, "unknown_code", "That code doesn't match a TFGPT thread.")
            out = me_json(db.get(Student, th.student_id), token)
        return set_cookie(JSONResponse(out), token)

    @app.patch("/api/me")
    def update_me(body: TopicBody, found=Depends(need)):
        s, token, _ = found
        with database.session() as db:
            s = db.get(Student, s.id)
            s.topic = body.topic.strip()
            return me_json(s, token)

    # ------------------------------------------------------------------ models

    def engines_for(student_ref: str) -> dict:
        return call(harness, "GET", "/v1/engines", params={"student_ref": student_ref})

    @app.get("/api/engines")
    def engines(found=Depends(need)):
        s = found[0]
        e = engines_for(s.id)
        return {"engines": e["engines"], "chosen": s.engine_choice, "assigned": e.get("assigned")}

    @app.post("/api/engine")
    def choose(body: EngineBody, found=Depends(need)):
        offered = {e["name"]: e for e in engines_for(found[0].id)["engines"]}
        if body.name not in offered or not offered[body.name]["available"]:
            raise ApiError(409, "choose_model", "That model isn't available. Choose another.")
        with database.session() as db:
            db.get(Student, found[0].id).engine_choice = body.name
        return {"chosen": body.name}

    # ------------------------------------------------------------------ thread, work, checks

    @app.get("/api/thread")
    def thread(found=Depends(need)):
        return advisor_call("GET", f"/internal/threads/{found[0].id}")

    @app.post("/api/extract")
    async def upload(file: UploadFile = File(...), found=Depends(need)):
        data = await file.read(5 * 1024 * 1024 + 1)
        try:
            text = extract(file.filename or "", data)
        except ExtractError as ex:
            raise ApiError(ex.status, ex.error, ex.message) from ex
        return {"text": text, "words": textmatch.words(text)}

    def start_check(kind: str, body: WorkBody, found) -> JSONResponse:
        s, _, session_id = found
        out = advisor_call("POST", "/internal/checks", json={
            "student_ref": s.id, "session_id": str(session_id), "topic": s.topic, "work": body.work,
            "kind": kind, "engine": s.engine_choice})
        return JSONResponse({"job_id": out["job_id"]}, status_code=202)

    @app.post("/api/check")
    def check(body: WorkBody, found=Depends(need)):
        return start_check("check", body, found)

    @app.post("/api/recheck")
    def recheck(body: WorkBody, found=Depends(need)):
        return start_check("recheck", body, found)

    @app.get("/api/jobs/{job_id}/events")
    def job_events(job_id: int, found=Depends(need)):
        student_ref = found[0].id
        advisor_call("GET", f"/internal/jobs/{job_id}", params={"student_ref": student_ref})  # 404 if not theirs

        def gen():
            deadline = time.monotonic() + env_int("JOB_STREAM_SECONDS", 900)
            while time.monotonic() < deadline:
                try:
                    v = advisor_call("GET", f"/internal/jobs/{job_id}", params={"student_ref": student_ref})
                except ServiceError:
                    time.sleep(poll)
                    continue
                if v["status"] in ("done", "failed") and v.get("message"):
                    yield sse.event("done" if v["status"] == "done" else "failed", {"message": v["message"]})
                    return
                yield sse.event("progress", {"status": v["status"], "seconds": v["seconds"], "step": v.get("step")})
                time.sleep(poll)
            yield sse.event("progress", {"status": "running", "seconds": -1, "step": "Still running: reload later"})

        return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-store"})

    @app.post("/api/flags/{flag_id}/dismiss")
    def dismiss(flag_id: int, found=Depends(need)):
        return advisor_call("POST", f"/internal/flags/{flag_id}/dismiss", json={"student_ref": found[0].id})

    @app.post("/api/messages/{message_id}/feedback")
    def feedback(message_id: int, body: FeedbackBody, found=Depends(need)):
        return advisor_call("POST", f"/internal/messages/{message_id}/feedback",
                            json={"student_ref": found[0].id, "value": body.value})

    # ------------------------------------------------------------------ questions

    @app.post("/api/ask")
    def ask(body: AskBody, found=Depends(need)):
        s, _, session_id = found
        payload = {"student_ref": s.id, "session_id": str(session_id), "topic": s.topic,
                   "question": body.question, "engine": s.engine_choice}
        req = advisor.build_request("POST", "/internal/ask", json=payload, headers={HEADER: internal_token()},
                                    timeout=httpx.Timeout(900, connect=10))
        try:
            r = advisor.send(req, stream=True)
        except httpx.HTTPError as ex:
            raise ApiError(502, "upstream", "TFGPT couldn't reach its advisor. Please try again.") from ex
        if r.status_code >= 400:
            r.read()
            r.close()
            raise error_of(r)

        def gen():
            try:
                for chunk in r.iter_text():
                    yield chunk
            finally:
                r.close()

        return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-store"})

    # ------------------------------------------------------------------ loading the programme's documents

    @app.post("/api/admin/pack")
    async def load_pack(request: Request, file: UploadFile = File(...)):
        """For the team only: the documents go straight to the database, never into the repository."""
        expected, given = env("ADMIN_TOKEN"), request.headers.get("x-admin-token") or ""
        if not expected or not hmac.compare_digest(given, expected):
            raise ApiError(404, "not_found", "Not found.")
        data = await file.read(2_000_001)
        if len(data) > 2_000_000:
            raise ApiError(413, "too_long", "Pack over 2 MB.")
        title = request.headers.get("x-pack-title") or (file.filename or "pack")
        return advisor_call("POST", "/internal/packs", json={"title": title, "markdown": data.decode("utf-8")},
                            timeout=120)

    app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
    return app

