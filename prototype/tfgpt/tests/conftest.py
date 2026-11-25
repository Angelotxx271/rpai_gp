"""The three services wired together in one process, on one database, with the scripted fake engine.
No test calls a model or the network. Set TEST_DATABASE_URL to run the same tests on Postgres."""
import json
import os
from pathlib import Path

import pytest

HERE = Path(__file__).parent
ROOT = HERE.parent
os.environ.update({
    "INTERNAL_TOKEN": "test-internal-token",
    "RETRY_WAITS": "0,0",
    "RETRY_SECONDS": "0",
    "JOB_POLL_SECONDS": "0.01",
    "COOKIE_SECURE": "0",
    "ENGINES_FILE": str(HERE / "fixtures" / "engines.json"),
    "COMPACT_ENGINE": "fake-compact",
    "APP_VERSION": "test123",
})
for name in ("DEFAULT_ENGINE", "ENGINES_OFF", "ENGINES_ON", "TFGPT_TEST_MISSING_KEY"):
    os.environ.pop(name, None)

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from advisor import pack as packs  # noqa: E402
from advisor.app import create_app as advisor_app  # noqa: E402
from advisor.harness_client import Harness  # noqa: E402
from harness.adapters import fake  # noqa: E402
from harness.app import create_app as harness_app  # noqa: E402
from tfgpt_shared.db import SCHEMAS, Database, make_engine  # noqa: E402
from web.app import create_app as web_app  # noqa: E402

PACK = ROOT / "eval" / "data" / "synthetic-pack.md"
CASES = [json.loads(x) for x in (ROOT / "eval" / "data" / "cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]


def fresh_database() -> Database:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        return Database(make_engine("sqlite://"))
    engine = make_engine(url)
    with engine.begin() as c:
        for s in SCHEMAS:
            c.execute(text(f'DROP SCHEMA IF EXISTS "{s}" CASCADE'))
    return Database(engine)


class Stack:
    def __init__(self, database, harness, advisor, web, advisor_app):
        self.database, self.harness, self.advisor, self.web = database, harness, advisor, web
        self.advisor_app = advisor_app

    def run_jobs(self) -> int:
        from advisor import jobs

        return jobs.run_all(self.database, self.advisor_app.state.harness)

    def start(self, topic: str = "Forecasting weekly demand for a fictional café chain with public weather data",
              engine: str | None = "fake-a") -> dict:
        r = self.web.post("/api/start", json={"topic": topic}, headers={"X-TFGPT": "1"})
        assert r.status_code == 200, r.text
        if engine:
            assert self.web.post("/api/engine", json={"name": engine}, headers={"X-TFGPT": "1"}).status_code == 200
        return r.json()

    def post(self, path: str, **kw):
        return self.web.post(path, headers={"X-TFGPT": "1"}, **kw)

    def events(self, job_id: int) -> list[tuple[str, dict]]:
        from tfgpt_shared import sse

        with self.web.stream("GET", f"/api/jobs/{job_id}/events") as r:
            return list(sse.parse(r.iter_lines()))

    def check(self, work: str, kind: str = "check") -> dict:
        r = self.post(f"/api/{kind}", json={"work": work})
        assert r.status_code == 202, r.text
        self.run_jobs()
        events = self.events(r.json()["job_id"])
        return events[-1][1]["message"]


@pytest.fixture
def stack():
    fake.reset()
    database = fresh_database()
    h_app = harness_app(database, engines_spec=json.loads((HERE / "fixtures" / "engines.json").read_text()))
    with TestClient(h_app) as h:
        a_app = advisor_app(database, Harness(h), start_worker=False)
        with TestClient(a_app) as a:
            with database.session() as db:
                packs.from_file(db, PACK, "Synthetic pack")
            w_app = web_app(database, advisor=a, harness=h)
            with TestClient(w_app) as w:
                yield Stack(database, h, a, w, a_app)
    fake.reset()


def sid_for(heading: str) -> str:
    """The section id the pack gives a heading."""
    for s in packs.parse(PACK.read_text(encoding="utf-8")):
        if s.title == heading:
            return s.sid
    raise KeyError(heading)


def flags_json(*flags) -> str:
    return json.dumps({"flags": list(flags)})


def flag(quote: str, heading: str, problem: str = "Doesn't fit.", route: str = "Look at the rule.",
         missing: bool = False) -> dict:
    return {"quote": quote, "missing": missing, "section_id": sid_for(heading), "problem": problem, "route": route}
