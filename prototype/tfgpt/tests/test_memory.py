"""Ask the documents, task group 2: the compaction sweep and the purge of uploaded work."""
from datetime import timedelta

from sqlalchemy import select, update

from advisor import jobs, memory
from advisor.models import Check, Compaction, Flag, Message, Thread
from conftest import CASES, flag, flags_json
from harness.adapters import fake
from tfgpt_shared.db import now


def age_thread(stack, minutes: int) -> None:
    past = now() - timedelta(minutes=minutes)
    with stack.database.session() as db:
        db.execute(update(Message).values(created_at=past))
        db.execute(update(Thread).values(last_activity_at=past))


def sweep(stack) -> None:
    with stack.database.session() as db:
        jobs.enqueue(db, "sweep", {}, max_attempts=1)
    stack.run_jobs()


def test_v4_a_quiet_thread_is_folded_into_the_summary_and_stays_visible(stack):
    fake.script("fake-a", "FOR_SUPERVISOR", "FOR_SUPERVISOR")
    stack.start()
    for q in ("When is the interim report due?", "How many references do I need?"):
        with stack.web.stream("POST", "/api/ask", json={"question": q}, headers={"X-TFGPT": "1"}) as r:
            r.read()
    age_thread(stack, 40)  # past the compaction time and the session time
    fake.script("fake-compact", "The student asked about the interim report date and the reference count.")
    sweep(stack)
    with stack.database.session() as db:
        t = db.scalars(select(Thread)).one()
        assert t.summary.startswith("The student asked") and t.summary_upto > 0
        assert db.scalars(select(Compaction)).one().messages_folded == 4
    sent = next(c for c in fake.calls if c["engine"] == "fake-compact")["messages"][0]["content"]
    assert "When is the interim report due?" in sent
    thread = stack.web.get("/api/thread").json()
    assert len(thread["messages"]) == 4 and thread["summary_note"].startswith("Picking up where you left off")


def test_a_recent_thread_is_not_compacted(stack):
    fake.script("fake-a", "FOR_SUPERVISOR")
    stack.start()
    with stack.web.stream("POST", "/api/ask", json={"question": "Anything?"}, headers={"X-TFGPT": "1"}) as r:
        r.read()
    sweep(stack)
    with stack.database.session() as db:
        assert db.scalars(select(Compaction)).first() is None


def test_v5_the_work_is_deleted_when_the_session_ends_and_flags_stay(stack):
    case = CASES[0]
    p = case["planted"][0]
    fake.script("fake-a", flags_json(flag(p["passage"] or "", p["section"], missing=p["passage"] is None)), flags_json())
    stack.start(topic=case["topic"])
    stack.check(case["work"])
    with stack.database.session() as db:
        assert db.scalars(select(Check)).one().work_text
    sweep(stack)
    with stack.database.session() as db:
        assert db.scalars(select(Check)).one().work_text  # session still going: kept for now
    age_thread(stack, 31)
    fake.script("fake-compact", "Summary.")
    sweep(stack)
    with stack.database.session() as db:
        assert db.scalars(select(Check)).one().work_text is None
        f = db.scalars(select(Flag)).one()
        assert f.status == "open" and f.problem


def test_the_summary_never_carries_the_work(stack):
    case = CASES[0]
    fake.script("fake-a", flags_json(), flags_json())
    stack.start(topic=case["topic"])
    stack.check(case["work"])
    with stack.database.session() as db:
        t = db.scalars(select(Thread)).one()
        lines = "\n".join(memory.line(m) for m in db.scalars(select(Message).where(Message.thread_id == t.id)))
    assert case["work"][:60] not in lines
