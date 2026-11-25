"""Check once, task group 4: checks run as jobs in the database queue, and survive a worker that dies."""
from datetime import timedelta

from conftest import CASES, flag, flags_json

from advisor import jobs
from advisor.models import Check, Job
from harness.adapters import Transient, fake
from tfgpt_shared.db import now


def test_progress_events_then_done(stack):
    case = CASES[0]
    p = case["planted"][0]
    fake.script("fake-a", flags_json(flag(p["passage"] or "", p["section"], missing=p["passage"] is None)), flags_json())
    stack.start(topic=case["topic"])
    job_id = stack.post("/api/check", json={"work": case["work"]}).json()["job_id"]
    queued = stack.web.get(f"/api/thread").json()["messages"]
    assert queued[-1]["kind"] == "work"  # the page shows the work chip before the check finishes
    stack.run_jobs()
    events = stack.events(job_id)
    assert events[-1][0] == "done" and events[-1][1]["message"]["kind"] == "check"


def test_a_job_left_running_by_a_dead_worker_is_picked_up_again(stack):
    case = CASES[0]
    stack.start(topic=case["topic"])
    job_id = stack.post("/api/check", json={"work": case["work"]}).json()["job_id"]
    assert jobs.claim(stack.database) == job_id  # a worker takes it, then dies
    with stack.database.session() as db:
        db.get(Job, job_id).locked_at = now() - timedelta(hours=1)
    assert stack.run_jobs() == 0  # nothing is ready while it looks taken
    assert jobs.requeue_stale(stack.database) == 1
    fake.script("fake-a", flags_json(), flags_json())
    assert stack.run_jobs() == 1
    with stack.database.session() as db:
        assert db.get(Job, job_id).status == "done" and db.get(Job, job_id).attempts == 2


def test_an_upstream_failure_is_retried_once_then_shown(stack, monkeypatch):
    monkeypatch.setenv("RETRY_SECONDS", "3600")
    stack.start()
    job_id = stack.post("/api/check", json={"work": "A proposal long enough to be checked."}).json()["job_id"]
    fake.script("fake-a", *[Transient("HTTP 503")] * 3)
    fake.script("fake-b", *[Transient("HTTP 503")] * 3)
    stack.run_jobs()
    with stack.database.session() as db:
        j = db.get(Job, job_id)
        assert j.status == "queued" and j.attempts == 1  # back in the queue for its second attempt
        j.run_after = now()
    fake.script("fake-a", *[Transient("HTTP 503")] * 3)
    fake.script("fake-b", *[Transient("HTTP 503")] * 3)
    stack.run_jobs()
    msg = stack.events(job_id)[-1][1]["message"]
    assert msg["kind"] == "notice" and msg["data"]["retry"] == "check"
    with stack.database.session() as db:
        assert db.get(Check, db.get(Job, job_id).payload["check_id"]).status == "failed"


def test_a_student_cannot_follow_someone_elses_job(stack):
    stack.start()
    job_id = stack.post("/api/check", json={"work": "A proposal long enough to be checked."}).json()["job_id"]
    stack.web.cookies.clear()
    stack.start(topic="A different student with another topic entirely")
    assert stack.web.get(f"/api/jobs/{job_id}/events").status_code == 502
