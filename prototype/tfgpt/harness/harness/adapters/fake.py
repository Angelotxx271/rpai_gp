"""A scripted engine for offline tests and for running the app with no key. It never calls a network."""
import json
from collections import defaultdict, deque
from collections.abc import Iterator

from ..models import Engine
from . import Call, Permanent, Result, Transient

_scripts: dict[str, deque] = defaultdict(deque)
calls: list[dict] = []  # every call the fake received, so tests can check what was sent


def script(engine: str, *replies) -> None:
    """Queue replies for one engine: a str (the text), a dict (Result fields) or an exception to raise."""
    _scripts[engine].extend(replies)


def reset() -> None:
    _scripts.clear()
    calls.clear()


def default_reply(call: Call) -> str:
    if call.json_schema:
        props = call.json_schema.get("properties", {})
        return json.dumps({k: [] for k in props})
    return "FOR_SUPERVISOR"


def stream(engine: Engine, call: Call, key: str | None) -> Iterator[str | Result]:
    calls.append({"engine": engine.name, "system": call.system, "messages": call.messages,
                  "json_schema": call.json_schema})
    reply = _scripts[engine.name].popleft() if _scripts[engine.name] else default_reply(call)
    if isinstance(reply, (Transient, Permanent)):
        raise reply
    fields = reply if isinstance(reply, dict) else {"text": reply}
    text = fields.get("text", "")
    for i in range(0, len(text), 40):
        yield text[i:i + 40]
    yield Result(text=text, stop=fields.get("stop", "end_turn"), model_returned=engine.model,
                 tokens_in=fields.get("tokens_in", 1000), cache_read=0, cache_write=0,
                 tokens_out=fields.get("tokens_out", 100))
