"""Prompts live in their own files, so a change shows in the diff and every run records the prompt's hash."""
import hashlib
from functools import lru_cache
from pathlib import Path

DIR = Path(__file__).parent / "prompts"
NAMES = ("check", "recheck", "ask", "compact")

FOLLOW_UP = ("Anything else that doesn't fit the guidelines? List only points you haven't listed yet, "
             "in the same JSON format, or an empty list if there are none.")
SUPERVISOR_LINE = "That one is for your supervisor: the loaded documents don't answer it."

FLAG = {
    "type": "object",
    "properties": {
        "quote": {"type": "string"},
        "missing": {"type": "boolean"},
        "section_id": {"type": "string"},
        "problem": {"type": "string"},
        "route": {"type": "string"},
    },
    "required": ["quote", "missing", "section_id", "problem", "route"],
    "additionalProperties": False,
}
CHECK_SCHEMA = {
    "type": "object",
    "properties": {"flags": {"type": "array", "items": FLAG}},
    "required": ["flags"],
    "additionalProperties": False,
}
RECHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "flag_id": {"type": "integer"},
                "status": {"type": "string", "enum": ["solved", "remaining"]},
                "quote": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["flag_id", "status", "quote", "note"],
            "additionalProperties": False,
        }},
        "new_flags": {"type": "array", "items": FLAG},
    },
    "required": ["results", "new_flags"],
    "additionalProperties": False,
}


@lru_cache
def template(name: str) -> str:
    return (DIR / f"{name}.md").read_text(encoding="utf-8").strip()


def sha12(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def system(name: str, pack_text: str = "") -> str:
    return template(name).replace("{pack}", pack_text)
