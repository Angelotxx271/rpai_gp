"""Check once, task groups 2 and 5: routing, retries, fallback, circuits, caps, experiments, run records."""
import pytest
from sqlalchemy import func, select

from harness.adapters import Permanent, Transient, fake
from harness.models import Circuit, Run
from harness.routing import arm_for
from tfgpt_shared.evaldb import Assignment, Experiment

H = {"X-Internal-Token": "test-internal-token"}


def gen(stack, **body):
    body = {"task": "ask", "system": "s", "messages": [{"role": "user", "content": "hi"}], **body}
    return stack.harness.post("/v1/generate", json=body, headers=H)


def runs(stack, **where):
    with stack.database.session() as db:
        q = select(Run)
        for k, v in where.items():
            q = q.where(getattr(Run, k) == v)
        return list(db.scalars(q.order_by(Run.id)))


def test_v6_no_choice_no_experiment_no_default_asks_for_a_model(stack):
    r = gen(stack, student_ref="student-0001")
    assert r.status_code == 409 and r.json()["detail"]["error"] == "choose_model"
    assert runs(stack) == []


def test_v6_through_the_page_nothing_is_sent_without_a_model(stack):
    stack.start(engine=None)
    r = stack.post("/api/check", json={"work": "My proposal text, long enough to check."})
    assert r.status_code == 202
    stack.run_jobs()
    msg = stack.events(r.json()["job_id"])[-1][1]["message"]
    assert msg["kind"] == "notice" and "Choose a model" in msg["text"]
    assert runs(stack) == []


def test_a_default_engine_is_one_variable(stack, monkeypatch):
    monkeypatch.setenv("DEFAULT_ENGINE", "fake-b")
    fake.script("fake-b", "hello")
    r = gen(stack, student_ref="student-0001")
    assert r.status_code == 200 and r.json()["engine"] == "fake-b"


def test_v7_retries_then_the_fallback_answers_and_is_named(stack):
    fake.script("fake-a", Transient("HTTP 529"), Transient("HTTP 529"), Transient("HTTP 529"))
    fake.script("fake-b", "from the fallback")
    r = gen(stack, engine="fake-a", student_ref="student-0001", request_id="ask-1")
    assert r.status_code == 200
    body = r.json()
    assert body["engine"] == "fake-b" and body["fallback_from"] == "Fake A · Test Vendor 1"
    failed, ok = runs(stack)
    assert failed.status == "error" and failed.retries == 2 and failed.engine == "fake-a"
    assert ok.status == "ok" and ok.fallback_used and ok.fallback_from == "fake-a"


def test_a_permanent_error_skips_retries(stack):
    fake.script("fake-a", Permanent("HTTP 401"))
    fake.script("fake-b", "ok")
    gen(stack, engine="fake-a", student_ref="student-0001")
    assert runs(stack)[0].retries == 0


def test_a_truncated_or_refused_answer_is_not_accepted(stack):
    fake.script("fake-a", {"text": "half an answ", "stop": "max_tokens"})
    fake.script("fake-b", {"text": "", "stop": "end_turn"})
    r = gen(stack, engine="fake-a", student_ref="student-0001")
    assert r.status_code == 502
    assert [x.status for x in runs(stack)] == ["error", "error"]


def test_the_circuit_opens_after_repeated_failures_and_the_engine_shows_unavailable(stack, monkeypatch):
    monkeypatch.setenv("CIRCUIT_FAILURES", "2")
    for _ in range(2):
        fake.script("fake-b", Permanent("HTTP 402"))
        gen(stack, engine="fake-b", student_ref="student-0001")
    with stack.database.session() as db:
        assert db.get(Circuit, "fake2").state == "open"
    engines = {e["name"]: e for e in stack.harness.get("/v1/engines", headers=H).json()["engines"]}
    assert not engines["fake-b"]["available"] and "failing" in engines["fake-b"]["note"]
    assert engines["fake-a"]["available"]


def test_switched_off_and_keyless_engines_are_listed_but_unavailable(stack, monkeypatch):
    engines = {e["name"]: e for e in stack.harness.get("/v1/engines", headers=H).json()["engines"]}
    assert engines["fake-off"]["note"] == "Credits exhausted" and not engines["fake-off"]["available"]
    assert not engines["fake-keyed"]["available"] and "key" in engines["fake-keyed"]["note"]
    assert "fake-compact" not in engines  # not offered to students
    monkeypatch.setenv("ENGINES_OFF", "fake-a")
    engines = {e["name"]: e for e in stack.harness.get("/v1/engines", headers=H).json()["engines"]}
    assert not engines["fake-a"]["available"]


def test_v8_the_daily_check_cap_refuses_before_any_call(stack, monkeypatch):
    monkeypatch.setenv("CHECKS_PER_STUDENT_DAY", "1")
    fake.script("fake-a", '{"flags": []}', '{"flags": []}')
    assert gen(stack, task="check", engine="fake-a", student_ref="s-00000001", request_id="check-1").status_code == 200
    assert gen(stack, task="check", engine="fake-a", student_ref="s-00000001", request_id="check-1").status_code == 200
    before = len(runs(stack))
    r = gen(stack, task="check", engine="fake-a", student_ref="s-00000001", request_id="check-2")
    assert r.status_code == 429 and r.json()["detail"]["error"] == "cap_reached" and "UTC" in r.json()["detail"]["message"]
    assert len(runs(stack)) == before


def test_the_daily_budget_stops_everyone(stack, monkeypatch):
    fake.script("fake-a", {"text": "costly", "tokens_in": 1_000_000, "tokens_out": 0})
    gen(stack, engine="fake-a", student_ref="s-00000001")
    monkeypatch.setenv("DAILY_BUDGET_USD", "0.5")
    r = gen(stack, engine="fake-a", student_ref="s-00000002")
    assert r.status_code == 429


def test_run_records_carry_cost_tokens_and_prompt_hash(stack):
    fake.script("fake-a", {"text": "x", "tokens_in": 2000, "tokens_out": 500})
    gen(stack, engine="fake-a", student_ref="s-00000001", prompt_name="ask")
    (run,) = runs(stack)
    assert run.cost_usd == pytest.approx((2000 * 1.0 + 500 * 2.0) / 1e6)
    assert len(run.prompt_sha12) == 12 and run.prompt_name == "ask" and run.seconds is not None


def test_streaming_sends_deltas_then_the_end(stack):
    from tfgpt_shared import sse

    fake.script("fake-a", "x" * 100)
    body = {"task": "ask", "system": "s", "messages": [{"role": "user", "content": "q"}], "engine": "fake-a",
            "student_ref": "s-00000001"}
    with stack.harness.stream("POST", "/v1/stream", json=body, headers=H) as r:
        events = list(sse.parse(r.iter_lines()))
    names = [e[0] for e in events]
    assert names[0] == "start" and names[-1] == "end" and names.count("delta") == 3


def add_experiment(stack, task="check", arms=None):
    with stack.database.session() as db:
        db.add(Experiment(name="ab1", task=task, arms=arms or [{"engine": "fake-a", "weight": 1},
                                                               {"engine": "fake-b", "weight": 1}]))


def test_experiment_assigns_a_stable_arm_and_records_it(stack):
    add_experiment(stack)
    for ref in ("student-aaaa", "student-bbbb", "student-cccc", "student-dddd"):
        fake.script("fake-a", "{}")
        fake.script("fake-b", "{}")
        r = gen(stack, task="check", student_ref=ref, request_id=f"check-{ref}")
        assert r.status_code == 200
        with stack.database.session() as db:
            exp = db.scalars(select(Experiment)).one()
            assert r.json()["engine"] == arm_for(exp, ref)
    with stack.database.session() as db:
        assert db.scalar(select(func.count()).select_from(Assignment)) == 4
    assert all(x.experiment == "ab1" and not x.chosen for x in runs(stack))


def test_experiment_a_choice_overrides_the_arm_and_is_logged(stack):
    add_experiment(stack, arms=[{"engine": "fake-b", "weight": 1}])
    fake.script("fake-a", "{}")
    r = gen(stack, task="check", engine="fake-a", student_ref="student-aaaa", request_id="check-x")
    assert r.json()["engine"] == "fake-a"
    with stack.database.session() as db:
        a = db.scalars(select(Assignment)).one()
        assert a.engine == "fake-b" and a.chosen_engine == "fake-a"
    (run,) = runs(stack)
    assert run.chosen and run.arm == "fake-b"


def test_experiment_the_page_shows_the_assignment_without_choosing_it(stack):
    add_experiment(stack, arms=[{"engine": "fake-b", "weight": 1}])
    stack.start(engine=None)
    body = stack.web.get("/api/engines").json()
    assert body["assigned"] == "fake-b" and body["chosen"] is None


def test_the_page_refuses_an_unavailable_choice(stack):
    stack.start(engine=None)
    r = stack.post("/api/engine", json={"name": "fake-off"})
    assert r.status_code == 409 and r.json()["error"] == "choose_model"
