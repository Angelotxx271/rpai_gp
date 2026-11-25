"""Claude through the official Anthropic SDK, streamed, with prompt caching, as the spike harness calls it."""
import copy
from collections.abc import Iterator

import anthropic

from ..models import Engine
from . import Call, Permanent, Result, Transient

API_URL = "https://api.anthropic.com"  # explicit, so an ANTHROPIC_BASE_URL set by another tool is ignored
RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}


def build_kwargs(engine: Engine, call: Call) -> dict:
    params = copy.deepcopy(engine.params or {})
    kwargs = {
        "model": engine.model,
        "max_tokens": call.max_tokens or params.pop("max_tokens", 16000),
        "system": call.system,
        "messages": call.messages,
    }
    params.pop("max_tokens", None)
    if call.json_schema:
        params.setdefault("output_config", {})["format"] = {"type": "json_schema", "schema": call.json_schema}
    if call.cache:
        kwargs["cache_control"] = {"type": "ephemeral"}  # caches the system prompt: the instructions and the pack
    kwargs.update(params)
    return kwargs


def stream(engine: Engine, call: Call, key: str | None) -> Iterator[str | Result]:
    if not key:
        raise Permanent(f"{engine.key_env} is not set")
    client = anthropic.Anthropic(api_key=key, base_url=API_URL, max_retries=0, timeout=600)
    try:
        with client.messages.stream(**build_kwargs(engine, call)) as s:
            for text in s.text_stream:
                yield text
            msg = s.get_final_message()
    except (anthropic.APIConnectionError, anthropic.APITimeoutError) as ex:
        raise Transient(f"connection: {type(ex).__name__}") from ex
    except anthropic.APIStatusError as ex:
        if ex.status_code in RETRYABLE:
            raise Transient(f"HTTP {ex.status_code}") from ex
        raise Permanent(f"HTTP {ex.status_code}: {str(ex)[:200]}") from ex
    except anthropic.APIError as ex:  # an error event inside the stream, such as overloaded_error
        if "overload" in str(ex).lower() or "rate" in str(ex).lower():
            raise Transient(str(ex)[:200]) from ex
        raise Permanent(str(ex)[:200]) from ex
    u = msg.usage
    read, write = u.cache_read_input_tokens or 0, u.cache_creation_input_tokens or 0
    yield Result(
        text="".join(b.text for b in msg.content if b.type == "text"),
        stop=msg.stop_reason,
        model_returned=msg.model,
        tokens_in=(u.input_tokens or 0) + read + write,
        cache_read=read,
        cache_write=write,
        tokens_out=u.output_tokens,
    )
