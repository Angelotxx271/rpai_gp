"""Safe demo-data reset and local offline demo seeder for TFGPT.

Examples:
  # Dry-run cleanup of the live "smoke test" student (read DATABASE_URL from env):
  python scripts/demo_reset.py clean --alias "smoke test"
  python scripts/demo_reset.py clean --alias "smoke test" --apply

  # Seed a fresh local SQLite database with the synthetic pack for offline backup demos:
  python scripts/demo_reset.py seed-local --db ./tfgpt-demo-backup.sqlite
"""
from __future__ import annotations

import argparse
import hashlib
import secrets
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for pkg in ("shared", "web", "advisor", "harness"):
    sys.path.insert(0, str(ROOT / pkg))


def cmd_clean(args: argparse.Namespace) -> None:
    from sqlalchemy import delete, select

    from advisor.models import Base as AdvisorBase, Check, Compaction, Flag, Job, Message, Thread
    from tfgpt_shared.db import Database, make_engine
    from web.models import Base as WebBase, Session, Student, TokenHash

    database = Database(make_engine(args.database_url))
    WebBase.metadata.create_all(database.engine)
    AdvisorBase.metadata.create_all(database.engine)

    with database.session() as db:
        students = list(db.scalars(select(Student).where(Student.alias == args.alias)))
        if not students:
            print(f"No student found with alias {args.alias!r}.")
            return
        student_ids = [s.id for s in students]
        threads = list(db.scalars(select(Thread).where(Thread.student_ref.in_(student_ids))))
        thread_ids = [t.id for t in threads]
        checks = list(db.scalars(select(Check).where(Check.thread_id.in_(thread_ids)))) if thread_ids else []
        flags = list(db.scalars(select(Flag).where(Flag.thread_id.in_(thread_ids)))) if thread_ids else []
        msgs = list(db.scalars(select(Message).where(Message.thread_id.in_(thread_ids)))) if thread_ids else []
        print(
            f"Matched alias={args.alias!r}: {len(students)} student(s), {len(threads)} thread(s), "
            f"{len(checks)} check(s), {len(flags)} flag(s), {len(msgs)} message(s)."
        )
        if not args.apply:
            print("Dry run only. Re-run with --apply to delete these records.")
            return
        if thread_ids:
            db.execute(delete(Compaction).where(Compaction.thread_id.in_(thread_ids)))
            db.execute(delete(Flag).where(Flag.thread_id.in_(thread_ids)))
            db.execute(delete(Check).where(Check.thread_id.in_(thread_ids)))
            db.execute(delete(Message).where(Message.thread_id.in_(thread_ids)))
            db.execute(delete(Thread).where(Thread.id.in_(thread_ids)))
        # Remove queued/finished jobs belonging to those threads if any
        for j in list(db.scalars(select(Job))):
            if isinstance(j.payload, dict) and j.payload.get("thread_id") in thread_ids:
                db.delete(j)
        db.execute(delete(TokenHash).where(TokenHash.student_id.in_(student_ids)))
        db.execute(delete(Session).where(Session.student_id.in_(student_ids)))
        db.execute(delete(Student).where(Student.id.in_(student_ids)))
        print("Deleted matched demo/smoke records cleanly.")


def cmd_seed_local(args: argparse.Namespace) -> None:
    import base64

    from advisor import memory, pack as packs
    from advisor.models import Base as AdvisorBase, Check, Flag
    from harness.models import Base as HarnessBase
    from tfgpt_shared import evaldb
    from tfgpt_shared.db import Database, make_engine
    from web.models import Base as WebBase, Session, Student, TokenHash

    db_path = Path(args.db).resolve()
    if db_path.exists():
        db_path.unlink()
    url = f"sqlite:///{db_path}"
    database = Database(make_engine(url))
    for base in (WebBase, AdvisorBase, HarnessBase, evaldb.EvalBase):
        base.metadata.create_all(database.engine)

    raw_token = base64.b32encode(secrets.token_bytes(10)).decode("ascii")
    resume_code = "-".join(raw_token[i:i + 4] for i in range(0, len(raw_token), 4))
    token_hash = hashlib.sha256(raw_token.encode("ascii")).hexdigest()
    student_id = uuid.uuid4().hex
    topic = "Forecasting weekly demand for fresh produce in a regional nine-store grocery chain using gradient boosting."

    with database.session() as db:
        packs.from_file(db, ROOT / "eval" / "data" / "synthetic-pack.md", "Northfield BDBA Full Proposal Guidelines (Demo)")
        db.add(Student(id=student_id, alias="Demo Student", topic=topic, engine_choice="sonnet"))
        db.flush()
        db.add(TokenHash(hash=token_hash, student_id=student_id))
        db.add(Session(student_id=student_id))

        t = memory.thread_for(db, student_id)
        memory.add(db, t, "student", "work", "Uploaded proposal draft (388 words)")
        c1 = Check(thread_id=t.id, kind="check", status="done", engine="Claude Sonnet 5.5 · Anthropic",
                   topic=topic, work_text=None, work_words=388, cost_usd=0.061)
        db.add(c1)
        db.flush()
        f1 = Flag(thread_id=t.id, check_id=c1.id, section_id="S05", section="Data access and ethics",
                  quote="I plan to ask the grocery chain for weekly sales data once the proposal is approved.",
                  missing=False, problem="Data access is still unconfirmed without a signed agreement or public backup.",
                  route="Secure a written data-access agreement before submission or add an open benchmark fallback.", status="solved")
        f2 = Flag(thread_id=t.id, check_id=c1.id, section_id="S08", section="References and citation style",
                  quote="Recent work shows gradient boosting works well (Adler 2019; Bianchi 2020).",
                  missing=False, problem="Only three references are listed, below the minimum five peer-reviewed sources.",
                  route="Add at least two peer-reviewed forecasting papers and format in-text citations with commas.", status="solved")
        f3 = Flag(thread_id=t.id, check_id=c1.id, section_id="S07", section="Preliminary timeline",
                  quote="I will finish data cleaning and modelling sometime in spring before the final handover.",
                  missing=False, problem="The timeline omits the four mandatory programme milestones (M1–M4) with dates.",
                  route="Map each work package onto M1 Proposal, M2 Data Secured, M3 Interim Report, and M4 Final Submission.", status="open")
        db.add_all([f1, f2, f3])
        db.flush()
        m1 = memory.add(db, t, "tfgpt", "check", "3 points to look at", {
            "engine": "Claude Sonnet 5.5 · Anthropic",
            "hidden": 0,
            "flags": [memory.flag_json(f1), memory.flag_json(f2), memory.flag_json(f3)],
        })
        c1.message_id = m1.id
        memory.add(db, t, "student", "work", "Uploaded revised proposal draft (412 words)")
        memory.add(db, t, "tfgpt", "recheck", "Check again", {
            "engine": "Claude Sonnet 5.5 · Anthropic",
            "hidden": 0,
            "solved": [memory.flag_json(f1), memory.flag_json(f2)],
            "remaining": [memory.flag_json(f3)],
            "new": [],
        })
        memory.add(db, t, "student", "question", "When is the M3 Interim Report due?")
        memory.add(db, t, "tfgpt", "answer", "According to the programme timeline, the M3 Interim Report is due on 12 February 2027.", {
            "engine": "Claude Sonnet 5.5 · Anthropic",
            "for_supervisor": False,
            "citations": [{"section_id": "S07", "section": "Preliminary timeline", "quote": "M3 Interim report: 12 February 2027"}],
        })
        memory.add(db, t, "student", "question", "Will my supervisor give this proposal a 9 out of 10?")
        memory.add(db, t, "tfgpt", "answer", "", {
            "engine": "Claude Sonnet 5.5 · Anthropic",
            "for_supervisor": True,
            "citations": [],
        })

    print(f"Seeded local demo database: {db_path}")
    print(f"Synthetic demo resume code: {resume_code}")
    print("Run local services with DATABASE_URL=sqlite:///" + str(db_path))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="demo_reset")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("clean", help="Remove demo/smoke student rows cleanly")
    c.add_argument("--alias", default="smoke test", help="Exact student alias to delete")
    c.add_argument("--database-url", default=None, help="Override DATABASE_URL")
    c.add_argument("--apply", action="store_true", help="Actually delete rows (default is dry-run)")
    c.set_defaults(fn=cmd_clean)

    s = sub.add_parser("seed-local", help="Create a seeded local SQLite DB for offline fallback demos")
    s.add_argument("--db", default=str(ROOT / "tfgpt-demo-backup.sqlite"))
    s.set_defaults(fn=cmd_seed_local)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
