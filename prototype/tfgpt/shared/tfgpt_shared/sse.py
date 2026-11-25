"""Server-sent events: write them, and read them back from another service's stream."""
import json
from collections.abc import Iterable, Iterator


def event(name: str, data: dict) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def parse(lines: Iterable[str]) -> Iterator[tuple[str, dict]]:
    """Turn the lines of an SSE stream into (event, data) pairs."""
    name, data = "message", []
    for line in lines:
        line = line.rstrip("\r")
        if not line:
            if data:
                yield name, json.loads("\n".join(data))
            name, data = "message", []
        elif line.startswith("event:"):
            name = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:].lstrip())
    if data:
        yield name, json.loads("\n".join(data))
