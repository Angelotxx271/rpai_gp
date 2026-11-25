"""The engine registry: engines.json seeded into harness.engines, plus the Railway switches."""
import json
import os
from pathlib import Path

from sqlalchemy.orm import Session

from tfgpt_shared.settings import env, env_list

from .models import Engine

DEFAULT_FILE = Path(__file__).resolve().parents[1] / "engines.json"


def load_file(path: str | Path | None = None) -> dict:
    path = Path(path or env("ENGINES_FILE") or DEFAULT_FILE)
    return json.loads(path.read_text(encoding="utf-8"))


def seed(db: Session, spec: dict) -> None:
    """Upsert every engine from the file; the file is the source of truth, the table its running copy."""
    providers = spec.get("providers", {})
    for name, e in spec["engines"].items():
        p = providers.get(e["provider"], {})
        row = db.get(Engine, name) or Engine(name=name)
        row.provider = e["provider"]
        row.kind = e.get("kind") or p.get("kind") or "openai"
        row.model, row.label, row.vendor = e["model"], e["label"], e["vendor"]
        row.offered, row.enabled = bool(e.get("offered")), bool(e.get("enabled", True))
        row.context, row.concurrency = int(e.get("context") or 0), int(e.get("concurrency") or 2)
        row.price, row.params, row.fallback = e.get("price") or {}, e.get("params") or {}, e.get("fallback") or []
        row.base_url = e.get("base_url") or p.get("base_url") or (env(p["base_url_env"]) if p.get("base_url_env") else None)
        row.key_env = e.get("key_env", p.get("key_env"))
        row.note = e.get("note")
        db.add(row)
    db.flush()


def switched_on(e: Engine) -> bool:
    """enabled in the file, not in ENGINES_OFF, or forced on with ENGINES_ON."""
    if e.name in env_list("ENGINES_OFF"):
        return False
    return e.enabled or e.name in env_list("ENGINES_ON")


def has_key(e: Engine) -> bool:
    return not e.key_env or bool(os.environ.get(e.key_env))


def default_engine() -> str | None:
    """No default until Angelotxx271 names one (tech-stack.md): then it's this one Railway variable."""
    return env("DEFAULT_ENGINE")


def cost(e: Engine, tokens_in: int | None, cache_write: int | None, cache_read: int | None,
         tokens_out: int | None) -> float | None:
    """US dollars from token counts and the engine's price table, as in the spike."""
    p = e.price or {}
    if p.get("input") is None or p.get("output") is None:
        return None
    total = (tokens_in or 0) * p["input"] + (tokens_out or 0) * p["output"]
    total += (cache_write or 0) * p.get("cache_write", p["input"])
    total += (cache_read or 0) * p.get("cache_read", p["input"])
    return round(total / 1e6, 6)
