"""Adapters turn one normalised call into one provider's API. Each yields text deltas, then one Result."""
from collections.abc import Iterator
from dataclasses import dataclass, field

from ..models import Engine


class Transient(Exception):
    """Worth retrying: rate limits, overload, server errors, timeouts."""


class Permanent(Exception):
    """Not worth retrying on this engine (bad key, no credits, bad request); the chain may still move on."""


@dataclass
class Call:
    system: str
    messages: list[dict]  # [{"role": "user" | "assistant", "content": str}]
    max_tokens: int | None = None
    json_schema: dict | None = None
    cache: bool = True


@dataclass
class Result:
    text: str
    stop: str | None = None
    model_returned: str | None = None
    tokens_in: int | None = None  # all input tokens, cached ones included
    cache_read: int | None = None
    cache_write: int | None = None
    tokens_out: int | None = None
    extra: dict = field(default_factory=dict)


OK_STOPS = {"end_turn", "stop", "stop_sequence"}  # anything else may be an incomplete answer, as in the spike


def stream(engine: Engine, call: Call, key: str | None) -> Iterator[str | Result]:
    from . import anthropic_adapter, fake, ollama, openai_compat

    kinds = {"anthropic": anthropic_adapter.stream, "openai": openai_compat.stream,
             "ollama": ollama.stream, "fake": fake.stream}
    if engine.kind not in kinds:
        raise Permanent(f"unknown adapter kind {engine.kind!r}")
    return kinds[engine.kind](engine, call, key)
