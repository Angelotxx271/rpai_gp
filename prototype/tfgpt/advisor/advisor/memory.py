"""The continuous thread: messages, the flag ledger, the rolling summary, and the two sweeps (compact, purge)."""
import json
from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from tfgpt_shared.db import aware, now
from tfgpt_shared.settings import env, env_int

from . import prompts
from .models import Check, Compaction, Flag, Job, Message, Thread

TAIL = 12  # recent messages sent with each question, besides the summary


def session_minutes() -> int:
    return env_int("SESSION_MINUTES", 30)


def compact_minutes() -> int:
    return env_int("COMPACT_MINUTES", 5)


def thread_for(db: Session, student_ref: str, create: bool = True) -> Thread | None:
    t = db.scalars(select(Thread).where(Thread.student_ref == student_ref)).first()
    if not t and create:
        t = Thread(student_ref=student_ref, summary_upto=0)
        db.add(t)
        db.flush()
    return t


def touch(t: Thread, session_id: str | None) -> None:
    t.last_activity_at = now()
    if session_id:
        t.session_id = session_id


def add(db: Session, t: Thread, role: str, kind: str, text: str = "", data: dict | None = None) -> Message:
    m = Message(thread_id=t.id, role=role, kind=kind, text=text, data=data)
    db.add(m)
    db.flush()
    return m


def flag_json(f: Flag) -> dict:
    return {"id": f.id, "section_id": f.section_id, "section": f.section, "quote": f.quote, "missing": f.missing,
            "problem": f.problem, "route": f.route, "status": f.status}


def message_json(db: Session, m: Message) -> dict:
    data = m.data
    if data and m.kind in ("check", "recheck"):  # flag statuses change (dismissed, solved): read them fresh
        data = dict(data)
        for key in ("flags", "solved", "remaining", "new"):
            if key in data:
                ids = [f["id"] for f in data[key]]
                rows = {f.id: f for f in db.scalars(select(Flag).where(Flag.id.in_(ids)))} if ids else {}
                data[key] = [flag_json(rows[i]) if i in rows else f for i, f in zip(ids, data[key])]
    return {"id": m.id, "role": m.role, "kind": m.kind, "text": m.text, "data": data,
            "created_at": aware(m.created_at).isoformat().replace("+00:00", "Z"), "feedback": m.feedback}


def open_flags(db: Session, thread_id: int) -> list[Flag]:
    return list(db.scalars(select(Flag).where(Flag.thread_id == thread_id, Flag.status == "open").order_by(Flag.id)))


def view(db: Session, student_ref: str) -> dict:
    t = thread_for(db, student_ref, create=False)
    if not t:
        return {"messages": [], "open_flags": 0, "summary_note": None}
    msgs = list(db.scalars(select(Message).where(Message.thread_id == t.id).order_by(Message.id)))
    note = None
    if msgs and now() - aware(t.last_activity_at) > timedelta(minutes=session_minutes()):
        note = f"Picking up where you left off on {aware(t.last_activity_at).strftime('%d %b')}."
    return {"messages": [message_json(db, m) for m in msgs], "open_flags": len(open_flags(db, t.id)),
            "summary_note": note}


def line(m: Message) -> str:
    """A message as the model sees it in the tail or the compaction: never the student's full work."""
    who = "Student" if m.role == "student" else "TFGPT"
    if m.kind in ("check", "recheck") and m.data:
        d = m.data
        if m.kind == "check":
            ids = ", ".join(f["section_id"] for f in d.get("flags", []))
            return f"{who}: ran a check, {len(d.get('flags', []))} points ({ids})"
        return (f"{who}: re-check, {len(d.get('solved', []))} solved, {len(d.get('remaining', []))} still open, "
                f"{len(d.get('new', []))} new")
    if m.kind == "answer" and m.data:
        cites = ", ".join(c["section_id"] for c in m.data.get("citations", []))
        return f"{who}: {m.text}" + (f" (sources {cites})" if cites else "")
    return f"{who}: {m.text}"


def context(db: Session, t: Thread) -> dict:
    tail = list(db.scalars(select(Message).where(Message.thread_id == t.id, Message.id > t.summary_upto)
                           .order_by(Message.id.desc()).limit(TAIL)))[::-1]
    flags = [{"flag_id": f.id, "section_id": f.section_id, "problem": f.problem} for f in open_flags(db, t.id)]
    return {"summary": t.summary or "", "tail": "\n".join(line(m) for m in tail), "open_flags": flags}


# ------------------------------------------------------------------ sweeps

def purge(db: Session) -> int:
    """Delete the uploaded work once its session is over: SESSION_MINUTES without activity, or a newer session."""
    cutoff = now() - timedelta(minutes=session_minutes())
    stale = select(Thread.id).where(Thread.last_activity_at < cutoff)
    n = db.execute(update(Check).where(Check.work_text.is_not(None), Check.status.in_(("done", "failed")),
                                       Check.thread_id.in_(stale)).values(work_text=None)).rowcount or 0
    for t_id, sess in db.execute(select(Thread.id, Thread.session_id)):
        n += db.execute(update(Check).where(Check.thread_id == t_id, Check.work_text.is_not(None),
                                            Check.status.in_(("done", "failed")), Check.session_id.is_not(None),
                                            Check.session_id != sess).values(work_text=None)).rowcount or 0
    return n


def due_for_compaction(db: Session) -> list[int]:
    cutoff = now() - timedelta(minutes=compact_minutes())
    last = (select(Message.thread_id, func.max(Message.id).label("last_id"), func.max(Message.created_at).label("at"))
            .group_by(Message.thread_id).subquery())
    rows = db.execute(select(Thread.id).join(last, last.c.thread_id == Thread.id)
                      .where(last.c.last_id > Thread.summary_upto, last.c.at < cutoff))
    queued = {j.payload.get("thread_id") for j in db.scalars(select(Job).where(Job.kind == "compact",
                                                                                Job.status.in_(("queued", "running"))))}
    return [r[0] for r in rows if r[0] not in queued]


def compact(db_session_factory, harness, thread_id: int) -> None:
    """Fold the tail into the rolling summary with the compaction engine. The messages stay visible."""
    with db_session_factory() as db:
        t = db.get(Thread, thread_id)
        msgs = list(db.scalars(select(Message).where(Message.thread_id == t.id, Message.id > t.summary_upto)
                               .order_by(Message.id)))
        if not msgs:
            return
        previous, upto, student_ref = t.summary or "(none yet)", msgs[-1].id, t.student_ref
        new_lines = "\n".join(line(m) for m in msgs)
    r = harness.generate(task="compact", internal=True, engine=env("COMPACT_ENGINE", "haiku"),
                         student_ref=student_ref, request_id=f"compact-{thread_id}-{upto}",
                         system=prompts.system("compact"), prompt_name="compact", max_tokens=1200, cache=False,
                         messages=[{"role": "user", "content":
                                    f"<summary>\n{previous}\n</summary>\n\n<new_messages>\n{new_lines}\n</new_messages>"}])
    with db_session_factory() as db:
        t = db.get(Thread, thread_id)
        if t.summary_upto >= upto:
            return
        t.summary, t.summary_upto = r["text"].strip(), upto
        db.add(Compaction(thread_id=t.id, upto_message_id=upto, messages_folded=len(msgs),
                          summary_chars=len(t.summary), engine=f"{r['label']} · {r['vendor']}"))


def open_points_json(flags: list[Flag]) -> str:
    return json.dumps([{"flag_id": f.id, "section_id": f.section_id, "quote": f.quote or "", "problem": f.problem}
                       for f in flags], ensure_ascii=False, indent=1)
