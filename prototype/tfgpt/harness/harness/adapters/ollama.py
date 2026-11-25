"""A local model through Ollama's native /api/chat: development and the cost benchmark only."""
import json
from collections.abc import Iterator

import httpx

from ..models import Engine
from . import Call, Permanent, Result, Transient


def stream(engine: Engine, call: Call, key: str | None) -> Iterator[str | Result]:
    if not engine.base_url:
        raise Permanent("OLLAMA_URL is not set")
    options = dict((engine.params or {}).get("options") or {})
    if call.max_tokens:
        options["num_predict"] = call.max_tokens
    body = {"model": engine.model, "stream": True, "options": options,
            "messages": [{"role": "system", "content": call.system}, *call.messages]}
    if call.json_schema:
        body["format"] = call.json_schema
    parts, final = [], {}
    try:
        with httpx.stream("POST", f"{engine.base_url}/api/chat", json=body,
                          timeout=httpx.Timeout(1800, connect=10)) as r:
            if r.status_code >= 500:
                raise Transient(f"HTTP {r.status_code}")
            if r.status_code != 200:
                r.read()
                raise Permanent(f"HTTP {r.status_code}: {r.text[:200]}")
            for line in r.iter_lines():
                if not line.strip():
                    continue
                chunk = json.loads(line)
                piece = (chunk.get("message") or {}).get("content") or ""
                if piece:
                    parts.append(piece)
                    yield piece
                if chunk.get("done"):
                    final = chunk
    except httpx.TimeoutException as ex:
        raise Transient("timeout") from ex
    except httpx.TransportError as ex:
        raise Transient(f"connection: {type(ex).__name__}") from ex
    pin, out = final.get("prompt_eval_count"), final.get("eval_count")
    ctx = options.get("num_ctx")
    stop = final.get("done_reason") or "stop"
    if ctx and pin and out and pin + out >= ctx:
        stop = "max_tokens"  # the window filled up: the answer may be cut, as the spike checks
    yield Result(text="".join(parts), stop="max_tokens" if stop == "length" else stop,
                 model_returned=engine.model, tokens_in=pin, tokens_out=out)
