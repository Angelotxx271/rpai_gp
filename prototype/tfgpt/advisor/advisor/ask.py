"""Ask: an answer from the loaded documents only, streamed; code checks every source, or it's the supervisor line."""
import json
import re
from collections.abc import Iterator

from tfgpt_shared import sse, textmatch
from tfgpt_shared.internal import ServiceError

from . import memory, pack as packs, prompts

MARKER = "SOURCES:"
SUPERVISOR = "FOR_SUPERVISOR"
CITE = re.compile(r"\[(S\d+)\]\s*[\"“”']([^\"“”\n]{3,400})[\"“”']")


def parse_answer(text: str, pack: packs.Pack) -> tuple[str, list[dict], bool]:
    """(answer, checked citations, for_supervisor). No checked source means the supervisor line."""
    t = text.strip()
    if not t or t.upper().startswith(SUPERVISOR):
        return prompts.SUPERVISOR_LINE, [], True
    i = t.rfind(MARKER)
    answer, sources = (t[:i].strip(), t[i + len(MARKER):]) if i >= 0 else (t, "")
    cites, seen = [], set()
    for sid, quote in CITE.findall(sources):
        if (sid, quote) not in seen and packs.quote_in_section(pack, sid, quote):
            seen.add((sid, quote))
            cites.append({"section_id": sid, "section": pack.by_id[sid].title, "quote": quote.strip()})
    if not cites or not answer or SUPERVISOR in answer.upper():
        return prompts.SUPERVISOR_LINE, [], True
    return answer, cites, False


class Visible:
    """Streams only the answer part: holds back text that may turn into the SOURCES: marker or FOR_SUPERVISOR."""

    def __init__(self):
        self.full, self.sent = "", 0

    def feed(self, piece: str) -> str:
        self.full += piece
        head = self.full.lstrip().upper()
        if SUPERVISOR.startswith(head) or head.startswith(SUPERVISOR):
            return ""  # this may still be, or is, the supervisor token: nothing to show yet
        end = self.full.find(MARKER)
        limit = end if end >= 0 else len(self.full) - len(MARKER)
        if limit <= self.sent:
            return ""
        out, self.sent = self.full[self.sent:limit], limit
        return out


def user_turn(topic: str, ctx: dict, question: str) -> str:
    return (f"<topic>\n{topic}\n</topic>\n\n<open_points>\n{json.dumps(ctx['open_flags'], ensure_ascii=False)}\n"
            f"</open_points>\n\n<summary>\n{ctx['summary'] or '(none yet)'}\n</summary>\n\n"
            f"<recent_messages>\n{ctx['tail'] or '(none)'}\n</recent_messages>\n\n<question>\n{question}\n</question>")


def start(database, harness, student_ref: str, session_id: str | None, topic: str, question: str,
          engine: str | None) -> Iterator[str]:
    """Opens the model stream first, so a refusal (choose a model, a cap) comes back as an error before any event.
    Returns an iterator of SSE strings."""
    with database.session() as db:
        t = memory.thread_for(db, student_ref)
        pack = packs.active(db)
        ctx = memory.context(db, t)
        thread_id = t.id
    if not pack:
        raise ServiceError(503, "upstream", "The programme's documents aren't loaded yet.")
    system = prompts.system("ask", pack.text)
    events = harness.stream(task="ask", engine=engine, student_ref=student_ref, system=system, prompt_name="ask",
                            messages=[{"role": "user", "content": user_turn(topic, ctx, question)}])
    first = next(events)  # raises ServiceError when the harness refuses
    with database.session() as db:
        t = memory.thread_for(db, student_ref)
        memory.touch(t, session_id)
        memory.add(db, t, "student", "text", question)
    return _relay(database, thread_id, pack, first, events)


def _relay(database, thread_id, pack, first, events) -> Iterator[str]:
    vis, engine = Visible(), None
    for name, data in _chain(first, events):
        if name == "start":
            engine = f"{data['label']} · {data['vendor']}"
            yield sse.event("start", {"engine": engine})
        elif name == "delta":
            out = vis.feed(data["text"])
            if out:
                yield sse.event("delta", {"text": out})
        elif name == "end":
            answer, cites, sup = parse_answer(data["text"], pack)
            with database.session() as db:
                t = db.get(memory.Thread, thread_id)
                m = memory.add(db, t, "tfgpt", "answer", answer,
                               {"engine": engine, "for_supervisor": sup, "citations": cites})
                yield sse.event("done", {"message": memory.message_json(db, m)})
            return
        elif name == "error":
            break
    with database.session() as db:
        t = db.get(memory.Thread, thread_id)
        m = memory.add(db, t, "tfgpt", "notice", "The answer didn't finish. Please ask again.", {"retry": None})
        yield sse.event("failed", {"message": memory.message_json(db, m)})


def _chain(first, rest):
    yield first
    try:
        yield from rest
    except ServiceError:
        yield "error", {}
