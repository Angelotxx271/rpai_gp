"""OpenAI-compatible chat completions over httpx: Mistral, GLM on Mistral, OpenRouter."""
import json
from collections.abc import Iterator

import httpx

from ..models import Engine
from . import Call, Permanent, Result, Transient

STOPS = {"stop": "stop", "length": "max_tokens", "model_length": "max_tokens", "content_filter": "refusal"}


def text_of(content) -> str:
    """Content is a string, or (Mistral's reasoning models) a list of thinking and text chunks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def body(engine: Engine, call: Call) -> dict:
    params = dict(engine.params or {})
    b = {
        "model": engine.model,
        "messages": [{"role": "system", "content": call.system}, *call.messages],
        "max_tokens": call.max_tokens or params.pop("max_tokens", 16000),
        "stream": True,
    }
    params.pop("max_tokens", None)
    if call.json_schema:
        b["response_format"] = {"type": "json_object"}
    b.update(params)
    return b


def stream(engine: Engine, call: Call, key: str | None) -> Iterator[str | Result]:
    if not key:
        raise Permanent(f"{engine.key_env} is not set")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    parts, stop, model, usage = [], None, None, {}
    try:
        with httpx.stream("POST", f"{engine.base_url}/chat/completions", headers=headers,
                          json=body(engine, call), timeout=httpx.Timeout(600, connect=15)) as r:
            if r.status_code == 429 or r.status_code >= 500:
                raise Transient(f"HTTP {r.status_code}")
            if r.status_code != 200:
                r.read()
                raise Permanent(f"HTTP {r.status_code}: {r.text[:200]}")
            for line in r.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                model = chunk.get("model", model)
                usage = chunk.get("usage") or usage
                for choice in chunk.get("choices", []):
                    piece = text_of((choice.get("delta") or {}).get("content"))
                    if piece:
                        parts.append(piece)
                        yield piece
                    if choice.get("finish_reason"):
                        stop = STOPS.get(choice["finish_reason"], choice["finish_reason"])
    except httpx.TimeoutException as ex:
        raise Transient("timeout") from ex
    except httpx.TransportError as ex:
        raise Transient(f"connection: {type(ex).__name__}") from ex
    yield Result(text="".join(parts), stop=stop, model_returned=model,
                 tokens_in=usage.get("prompt_tokens"), tokens_out=usage.get("completion_tokens"))
