"""Check and re-check: the model proposes flags, code keeps only those whose quote and section are real."""
import json
import re
import time
from dataclasses import dataclass

from tfgpt_shared import textmatch
from tfgpt_shared.db import now
from tfgpt_shared.internal import ServiceError
from tfgpt_shared.settings import env_bool, env_int

from . import memory, pack as packs, prompts
from .models import Check, Flag, Thread

MAX_FLAGS = 40


class CheckFailed(Exception):
    """A failure the student should see; retryable failures are left to the job queue."""

    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.message, self.retryable = message, retryable


@dataclass
class Checked:
    flags: list[dict]
    hidden: int


def parse_json(text: str) -> dict:
    """Structured output should already be JSON; tolerate a fenced or wrapped block from other providers."""
    try:
        return json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def clean_sid(raw) -> str:
    return str(raw or "").strip().strip("[]").upper()


def source_check(raw: list, work: str, pack: packs.Pack, seen: set | None = None) -> Checked:
    """Hide any flag whose quote isn't in the work or whose section isn't in the pack (tech-stack.md, source check)."""
    seen = set() if seen is None else seen
    kept, hidden = [], 0
    for f in raw if isinstance(raw, list) else []:
        if not isinstance(f, dict):
            hidden += 1
            continue
        sid, quote = clean_sid(f.get("section_id")), textmatch.strip_wrapping(str(f.get("quote") or ""))
        problem = str(f.get("problem") or "").strip()
        missing = bool(f.get("missing")) or not quote
        section = pack.by_id.get(sid)
        if not section or not problem or (not missing and not textmatch.find(quote, work)):
            hidden += 1
            continue
        key = (sid, textmatch.normalise(quote) if not missing else textmatch.normalise(problem)[:60])
        if key in seen:
            continue
        seen.add(key)
        kept.append({"section_id": sid, "section": section.title, "quote": None if missing else quote,
                     "missing": missing, "problem": problem, "route": str(f.get("route") or "").strip()})
    return Checked(kept[:MAX_FLAGS], hidden + max(0, len(kept) - MAX_FLAGS))


def label(r: dict) -> str:
    return f"{r['label']} · {r['vendor']}"


def first_turn(topic: str, work: str) -> str:
    return f"<topic>\n{topic}\n</topic>\n\n<proposal>\n{work}\n</proposal>\n\nCheck this"


def call_model(harness, **body) -> dict:
    try:
        return harness.generate(**body)
    except ServiceError as ex:
        raise CheckFailed(ex.message, retryable=ex.error == "upstream") from ex


def load_job(database, check_id: int):
    with database.session() as db:
        c = db.get(Check, check_id)
        t = db.get(Thread, c.thread_id)
        pack = packs.active(db)
        if not pack:
            raise CheckFailed("The programme's documents aren't loaded yet, so there is nothing to check against.")
        if not c.work_text:
            raise CheckFailed("Your work was deleted when your last session ended. Put it in again and check.")
        c.status, c.pack_id = "running", pack.id
        return c.work_text, c.topic, c.engine_choice, t.student_ref, t.id, pack


def run_check(database, harness, check_id: int, step) -> None:
    work, topic, choice, student_ref, thread_id, pack = load_job(database, check_id)
    t0, system = time.monotonic(), prompts.system("check", pack.text)
    common = {"task": "check", "system": system, "json_schema": prompts.CHECK_SCHEMA, "student_ref": student_ref,
              "request_id": f"check-{check_id}", "prompt_name": "check"}
    step("First pass")
    turns = [{"role": "user", "content": first_turn(topic, work)}]
    r1 = call_model(harness, engine=choice, messages=turns, **common)
    try:
        raw = parse_json(r1["text"]).get("flags", [])
    except ValueError as ex:
        raise CheckFailed("The model's answer couldn't be read. Please try again.", retryable=True) from ex
    seen: set = set()
    first = source_check(raw, work, pack, seen)
    flags, hidden, cost = first.flags, first.hidden, r1.get("cost_usd") or 0
    if env_bool("CHECK_FOLLOW_UP", True):  # the second turn the spike measured
        step("Second pass")
        turns += [{"role": "assistant", "content": r1["text"]}, {"role": "user", "content": prompts.FOLLOW_UP}]
        try:
            r2 = call_model(harness, engine=r1["engine"], internal=True, messages=turns, **common)
            more = source_check(parse_json(r2["text"]).get("flags", []), work, pack, seen)
            flags, hidden, cost = flags + more.flags, hidden + more.hidden, cost + (r2.get("cost_usd") or 0)
        except (CheckFailed, ValueError):
            pass  # the first pass stands on its own; the second only adds
    step("Checking sources")
    finish(database, check_id, thread_id, "check", label(r1), r1.get("fallback_from"), hidden, cost,
           time.monotonic() - t0, new=flags[:MAX_FLAGS], prompt_sha=prompts.sha12(system))


def run_recheck(database, harness, check_id: int, step) -> None:
    work, topic, choice, student_ref, thread_id, pack = load_job(database, check_id)
    with database.session() as db:
        open_ = memory.open_flags(db, thread_id)
        points = memory.open_points_json(open_)
        open_ids = {f.id for f in open_}
    t0, system = time.monotonic(), prompts.system("recheck", pack.text)
    step("Re-checking")
    user = (f"<topic>\n{topic}\n</topic>\n\n<open_points>\n{points}\n</open_points>\n\n"
            f"<proposal>\n{work}\n</proposal>\n\nCheck again")
    r = call_model(harness, task="recheck", engine=choice, system=system, json_schema=prompts.RECHECK_SCHEMA,
                   messages=[{"role": "user", "content": user}], student_ref=student_ref,
                   request_id=f"recheck-{check_id}", prompt_name="recheck")
    try:
        out = parse_json(r["text"])
    except ValueError as ex:
        raise CheckFailed("The model's answer couldn't be read. Please try again.", retryable=True) from ex
    step("Checking sources")
    results = {}
    for x in out.get("results", []) if isinstance(out.get("results"), list) else []:
        try:
            fid = int(x.get("flag_id"))
        except (TypeError, ValueError, AttributeError):
            continue
        if fid in open_ids:
            results[fid] = x
    seen = {(f.section_id, textmatch.normalise(f.quote or "") if not f.missing else textmatch.normalise(f.problem)[:60])
            for f in open_}
    new = source_check(out.get("new_flags", []), work, pack, seen)
    finish(database, check_id, thread_id, "recheck", label(r), r.get("fallback_from"), new.hidden,
           r.get("cost_usd") or 0, time.monotonic() - t0, new=new.flags, results=results, work=work,
           prompt_sha=prompts.sha12(system))


def finish(database, check_id, thread_id, kind, engine, fallback_from, hidden, cost, seconds, new,
           results=None, work=None, prompt_sha=None) -> None:
    with database.session() as db:
        c, t = db.get(Check, check_id), db.get(Thread, thread_id)
        solved, remaining = [], []
        if kind == "recheck":
            for f in memory.open_flags(db, thread_id):
                r = (results or {}).get(f.id)
                if r and r.get("status") == "solved":
                    f.status, f.solved_in = "solved", check_id
                    solved.append(f)
                    continue
                q = textmatch.strip_wrapping(str((r or {}).get("quote") or ""))
                if q and work and textmatch.find(q, work):
                    f.quote, f.missing = q, False  # the passage moved: show where it is now
                remaining.append(f)
        rows = [Flag(thread_id=thread_id, check_id=check_id, status="open", **f) for f in new]
        db.add_all(rows)
        db.flush()
        data = {"check_id": check_id, "engine": engine,
                "fallback_from": None if not fallback_from else fallback_from, "hidden": hidden,
                "seconds": round(seconds)}
        if kind == "check":
            data["flags"] = [memory.flag_json(f) for f in rows]
            text = f"{len(rows)} points to look at"
        else:
            data.update(solved=[memory.flag_json(f) for f in solved],
                        remaining=[memory.flag_json(f) for f in remaining], new=[memory.flag_json(f) for f in rows])
            text = f"{len(solved)} solved, {len(remaining)} still open, {len(rows)} new"
        m = memory.add(db, t, "tfgpt", kind, text, data)
        c.status, c.engine, c.fallback_from, c.hidden = "done", engine, fallback_from, hidden
        c.seconds, c.cost_usd, c.message_id, c.finished_at, c.prompt_sha12 = round(seconds, 1), cost, m.id, now(), prompt_sha


def fail(database, check_id: int, message: str) -> None:
    with database.session() as db:
        c = db.get(Check, check_id)
        if not c or c.status == "done":
            return
        t = db.get(Thread, c.thread_id)
        m = memory.add(db, t, "tfgpt", "notice", f"The check didn't finish: {message}", {"retry": c.kind})
        c.status, c.error, c.message_id, c.finished_at = "failed", message[:1000], m.id, now()


def max_words() -> int:
    return env_int("MAX_WORDS", 3000)
