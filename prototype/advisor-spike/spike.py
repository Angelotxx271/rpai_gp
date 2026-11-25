"""Advisor spike: can a general AI find what the supervisor flagged, version by version?

The code is public (prototype/advisor-spike/); the material it reads is not. The proposal versions, the
context packs, the topic sentence, the answer key, the raw runs and the keys stay in private/advisor-spike/
(git-excluded), or wherever SPIKE_DATA points. Run from the repo root, always with -I:
  Windows:      private\\advisor-spike\\.venv\\Scripts\\python -I prototype\\advisor-spike\\spike.py <command>
  macOS/Linux:  private/advisor-spike/.venv/bin/python -I prototype/advisor-spike/spike.py <command>

Commands that call no model:
  list               engines and groups: kind, model, on or off, key set or missing (never the key itself)
  verify             the answer key, the protocol and every prompt against the hashes committed in spikes.md
  prompts            build every prompt and print its size and hash
  estimate           rough tokens and cost a run would use, per engine
  models             the model IDs an endpoint serves (no prompt text is sent)
  sheets             blinded sheets for the two human scorers
  agree              read the scorers' filled sheets, combine them, compare them with the judge
  report             aggregate the judged (or human-scored) runs into results.md and results-public.md

Commands that call models:
  check              one tiny call per engine, to test keys and endpoints (no TFG text)
  run                every engine x condition x version x repeat (skips finished runs)
  judge              score each finished run, blind, against answer-key.md

Pick engines with --engine: names or groups from engines.json, for example
  --engine opus sonnet      --engine claude      --engine local      --engine all
With no --engine, every engine that is on in engines.json runs. Judges never run as arms. judge and report take
--engine too, to score or report one group while another is still running.
Keys come only from the environment or .secrets.env in the private folder; they are never printed.
Every run records the git commit of this folder, so each scored run can be traced to the code that made it.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

import requests

CODE = pathlib.Path(__file__).resolve().parent  # public: this file, engines.json, the amendment, results/
REPO = CODE.parents[1]
DATA = pathlib.Path(os.environ.get("SPIKE_DATA") or REPO / "private" / "advisor-spike")  # private, git-excluded
INPUTS = DATA / "inputs"
CONTEXT = DATA / "context"
RUNS = DATA / "runs"
SCORING = DATA / "scoring"
ENGINES_JSON = CODE / "engines.json"
PUBLIC_OUT = CODE / "results"  # counts only: safe for the public repo
SPIKES_MD = REPO / "evidence-log" / "spikes.md"  # the public file holding the fingerprints
STAGES = ["v1", "v2", "v3", "final"]
CONDITIONS = ["C0", "C1", "C2"]
NEUTRAL_SYSTEM = "You are a helpful assistant."
ANTHROPIC_URL = "https://api.anthropic.com"  # explicit, so an ANTHROPIC_BASE_URL set by another tool is ignored
CHARS_PER_TOKEN = 3.2  # deliberately low, so token estimates err on the high side

# Frozen stand-in instructions v1, copied verbatim from evidence-log/spikes.md (committed 2026-10-12).
V1_INSTRUCTIONS = (
    "You check a final-year student's TFG work against the attached programme guidelines and their topic. "
    "List each point where the work does not fit the guidelines or the topic. For each point, quote the passage, "
    "cite the guideline section, and say in one sentence what doesn't fit. Don't give a grade or an overall verdict, "
    "and don't rewrite the text."
)
V1_FOLLOW_UP = "Anything else that doesn't fit the guidelines?"
# Topic sentence: the supervisor's own one-line description of the topic (kick-off summary, 29 Sept 2026).
# Private (spikes.md: no topic in public), so it lives with the data; `verify` fails if it is missing or changed.
_topic_file = CONTEXT / "topic.txt"
TOPIC = (_topic_file.read_text(encoding="utf-8").strip() if _topic_file.exists()
         else "<missing: private/advisor-spike/context/topic.txt>")

# C0 is the student's usual route: their own AI, no instructions, no documents.
C0_FIRST = "Here is my TFG full proposal draft. Before I send it to my supervisor, what should I fix?"
C0_FOLLOW_UP = "Anything else I should fix?"


REPEATS = 3  # protocol v2: a point is caught in a cell when at least 2 of its 3 repeats catch it
OK_STOPS = {"stop", "end_turn", "stop_sequence"}  # any other stop reason means the answer may be incomplete


class RunError(RuntimeError):
    """A turn that must not be scored: truncated, refused, empty, or cut by the context window."""

    def __init__(self, msg: str, turns: list[dict] | None = None):
        super().__init__(msg)
        self.turns = turns or []  # what was already spent, so the budget still counts it


class Transient(RuntimeError):
    """A failure worth retrying: rate limit, server error, dropped connection."""


# ---------------------------------------------------------------- helpers

def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: pathlib.Path) -> str:
    """Hash of the bytes on disk, the same value sha256sum prints."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def est_tokens(text: str) -> int:
    return int(len(text) / CHARS_PER_TOKEN) + 1


def harness_commit() -> tuple[str, bool]:
    """The commit this folder's code is at, and whether it has uncommitted changes."""
    try:
        head = subprocess.run(["git", "-C", str(CODE), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(CODE), "status", "--porcelain", "--", ".", ":(exclude)results"],
                               capture_output=True, text=True, check=True).stdout.strip() != ""  # outputs aren't code
        return head, dirty
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True


def atomic_write(path: pathlib.Path, text: str) -> None:
    """Write next to the target, then rename, so a killed process never leaves half a file that looks finished."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def redact(text: str) -> str:
    """Remove any loaded key from an error message before it is printed or saved."""
    for name, value in os.environ.items():
        if value and len(value) >= 12 and re.search(r"KEY|TOKEN|SECRET", name):
            text = text.replace(value, "[key removed]")
    return re.sub(r"\b(sk-[A-Za-z0-9_-]{6})[A-Za-z0-9_-]+", r"\1…", text)


def utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def load_secrets() -> None:
    f = DATA / ".secrets.env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip("'\"")
            if v:  # an empty value in the file never hides a value set in the environment
                os.environ.setdefault(k.strip(), v)


def config() -> dict:
    return json.loads(ENGINES_JSON.read_text(encoding="utf-8"))


def engines(only: list[str] | None = None, cfg: dict | None = None) -> dict:
    """Engines to use as arms. `only` takes engine names, group names from _groups, or 'all'."""
    cfg = cfg if cfg is not None else config()
    arms = {n: e for n, e in cfg.items() if not n.startswith("_") and e.get("role") != "judge"}
    if not only:
        return {n: e for n, e in arms.items() if e.get("enabled", True)}
    groups = cfg.get("_groups", {})
    names: list[str] = []
    for want in only:
        if want == "all":  # every engine that is on; an engine that is off runs only when named
            names += [n for n, e in arms.items() if e.get("enabled", True)]
        elif want in groups:
            names += groups[want]
        elif want in arms:
            names.append(want)
        else:
            known = ", ".join(list(arms) + list(groups) + ["all"])
            sys.exit(f"unknown engine or group {want!r}; known: {known}")
    return {n: arms[n] for n in dict.fromkeys(names)}


def resolve(e: dict, key: str) -> str | None:
    if e.get(key):
        return e[key]
    env = e.get(key + "_env")
    return os.environ.get(env) if env else None


def api_key(e: dict) -> str | None:
    env = e.get("key_env")
    return os.environ.get(env) if env else None


def cost_of(e: dict, fresh_in: int | None, cache_write: int | None, cache_read: int | None,
            out: int | None) -> float | None:
    """US dollars from token counts and the engine's price table ($ per million tokens)."""
    p = e.get("price")
    if not p or p.get("input") is None or p.get("output") is None:
        return None
    total = (fresh_in or 0) * p["input"] + (out or 0) * p["output"]
    total += (cache_write or 0) * p.get("cache_write", p["input"])
    total += (cache_read or 0) * p.get("cache_read", p["input"])
    return round(total / 1e6, 6)


def with_retries(fn, attempts: int = 4, waits: tuple = (5, 20, 60)):
    for i in range(attempts):
        try:
            return fn()
        except Transient:
            if i == attempts - 1:
                raise
            time.sleep(waits[min(i, len(waits) - 1)] * (1 + random.random() / 4))


def post_json(url: str, headers: dict, body: dict, timeout: float) -> dict:
    try:
        r = requests.post(url, headers=headers, json=body, timeout=timeout)
    except (requests.ConnectionError, requests.Timeout) as ex:
        raise Transient(f"connection: {type(ex).__name__}") from ex
    if r.status_code == 429 or r.status_code >= 500:
        raise Transient(f"HTTP {r.status_code}: {r.text[:200]}")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    return r.json()


# ---------------------------------------------------------------- prompts (frozen: changing these changes the hashes)

def build(condition: str, stage: str) -> dict:
    """Return {system, turns[2]} for one condition and version. Same text for every engine."""
    work = (INPUTS / f"{stage}.md").read_text(encoding="utf-8").strip()
    wrapped = f"<proposal>\n{work}\n</proposal>"
    if condition == "C0":
        return {"system": NEUTRAL_SYSTEM, "turns": [f"{C0_FIRST}\n\n{wrapped}", C0_FOLLOW_UP]}
    if condition == "C1":  # spikes.md Arm B: everything pasted into a plain chat
        guidelines = (CONTEXT / "guidelines.md").read_text(encoding="utf-8")
        first = (f"{V1_INSTRUCTIONS}\n\n<guidelines>\n{guidelines}\n</guidelines>\n\n{TOPIC}\n\n"
                 f"{wrapped}\n\nCheck this")
        return {"system": NEUTRAL_SYSTEM, "turns": [first, V1_FOLLOW_UP]}
    if condition == "C2":  # spikes.md Arm A: instructions and documents preloaded, like a project
        custom = CONTEXT / "standin-instructions.txt"
        instructions = custom.read_text(encoding="utf-8").strip() if custom.exists() else V1_INSTRUCTIONS
        docs = (CONTEXT / "standin.md").read_text(encoding="utf-8")
        system = f"{instructions}\n\n<project_documents>\n{docs}\n</project_documents>"
        return {"system": system, "turns": [f"{TOPIC}\n\n{wrapped}\n\nCheck this", V1_FOLLOW_UP]}
    raise ValueError(condition)


def prompt_blob(p: dict) -> str:
    return json.dumps(p, ensure_ascii=False, indent=1)


def cmd_prompts(_args) -> None:
    out = RUNS / "prompts"
    out.mkdir(parents=True, exist_ok=True)
    src = CONTEXT / "standin-instructions.txt"
    print(f"C2 instructions: {'standin-instructions.txt (from the owner)' if src.exists() else 'frozen v1 (fallback)'}")
    for c in CONDITIONS:
        for s in STAGES:
            p = build(c, s)
            blob = prompt_blob(p)
            # newline="\n" keeps the file bytes equal to the hashed text on Windows too
            (out / f"{c}-{s}.json").write_text(blob, encoding="utf-8", newline="\n")
            words = len((p["system"] + " ".join(p["turns"])).split())
            print(f"{c}-{s}: ~{words} words, ~{est_tokens(p['system'] + ''.join(p['turns']))} tokens, "
                  f"sha256 {sha(blob)[:12]}")


# ---------------------------------------------------------------- fingerprints (the rules came before the results)

def committed_fingerprints(path: pathlib.Path = SPIKES_MD) -> dict:
    """Read the hashes committed in spikes.md: answer key, protocol, any amendment, and the 12 prompt prefixes."""
    text = path.read_text(encoding="utf-8")
    files = dict(re.findall(r"\|\s*([\w.-]+\.md)\b[^|]*\|\s*`([0-9a-f]{64})`\s*\|", text))
    prompts = {}
    m = re.search(r"C0:(.*?)·\s*C1:(.*?)·\s*C2:(.*?)\(rounds", text)
    if m:
        for cond, part in zip(CONDITIONS, m.groups()):
            for stage, h in zip(STAGES, re.findall(r"`([0-9a-f]{12})`", part)):
                prompts[f"{cond}-{stage}"] = h
    return {"files": files, "prompts": prompts}


def verify_fingerprints(path: pathlib.Path = SPIKES_MD) -> list[str]:
    """Return the problems found; an empty list means everything matches what was committed."""
    if not path.exists():
        return [f"{path} not found: can't check the committed hashes"]
    fp = committed_fingerprints(path)
    problems = []
    for name, want in fp["files"].items():
        f = DATA / name if (DATA / name).exists() else CODE / name
        if not f.exists():
            problems.append(f"{name}: committed but missing here")
        elif sha_file(f) != want:
            problems.append(f"{name}: sha256 {sha_file(f)[:12]} differs from the committed {want[:12]}")
    if len(fp["prompts"]) != len(CONDITIONS) * len(STAGES):
        problems.append(f"found {len(fp['prompts'])} of 12 committed prompt hashes in spikes.md")
    for cell, want in fp["prompts"].items():
        c, s = cell.split("-")
        got = sha(prompt_blob(build(c, s)))[:12]
        if got != want:
            problems.append(f"prompt {cell}: {got} differs from the committed {want}")
    return problems


def cmd_verify(_args) -> None:
    problems = verify_fingerprints()
    if problems:
        print("STOP, these differ from what was committed (tell the owner, Angelotxx271, before any run):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    fp = committed_fingerprints()
    print(f"ok: {', '.join(fp['files'])} and all {len(fp['prompts'])} prompts match spikes.md")


# ---------------------------------------------------------------- engines

def turn_record(text: str, **kw) -> dict:
    rec = {"text": (text or "").strip(), "thinking_chars": None, "model_returned": None, "input_tokens": None,
           "cache_write_tokens": None, "cache_read_tokens": None, "output_tokens": None, "seconds": None,
           "cost_usd": None, "stop": None}
    rec.update(kw)
    return rec


def require_ok(rec: dict, where: str) -> dict:
    """Refuse to keep a turn the scorers would misread as the engine's whole answer."""
    if rec["stop"] == "length":
        raise RunError(f"{where}: cut at the output limit (raise max_tokens / num_predict and rerun)")
    if rec["stop"] == "refusal":
        raise RunError(f"{where}: refused ({rec.get('stop_detail')})")
    if rec["stop"] not in OK_STOPS:
        raise RunError(f"{where}: stopped with {rec['stop']!r}, so the answer may be incomplete")
    if not rec["text"]:
        raise RunError(f"{where}: empty answer (stop {rec['stop']})")
    return rec


def call_openai(e: dict, system: str, messages: list[dict]) -> dict:
    """Any OpenAI-compatible chat endpoint: Mistral (also serving GLM), vLLM, llama.cpp."""
    base = resolve(e, "base_url")
    if not base:
        raise RuntimeError(f"no base_url (set {e.get('base_url_env')})")
    model = resolve(e, "model")
    key = api_key(e)
    if not key and not e.get("key_optional"):
        raise RuntimeError(f"missing key {e.get('key_env')}")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = {"model": model, "messages": [{"role": "system", "content": system}] + messages}
    body.update(e.get("params", {}))
    t0 = time.time()
    d = with_retries(lambda: post_json(f"{base.rstrip('/')}/chat/completions", headers, body, e.get("timeout", 900)))
    secs = time.time() - t0
    choice = d["choices"][0]
    msg = choice["message"]
    content = msg.get("content")
    thinking = msg.get("reasoning_content") or msg.get("reasoning") or ""
    if isinstance(content, list):  # e.g. GLM on Mistral: thinking and text chunks
        texts, thoughts = [], []
        for ch in content:
            if ch.get("type") == "text":
                texts.append(ch.get("text", ""))
            elif ch.get("type") == "thinking":
                th = ch.get("thinking")
                thoughts.append(th if isinstance(th, str) else json.dumps(th, ensure_ascii=False))
        content, thinking = "\n".join(texts), "\n".join(thoughts)
    u = d.get("usage", {}) or {}
    prompt = u.get("prompt_tokens")
    cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
    out = u.get("completion_tokens")
    finish = choice.get("finish_reason")
    return turn_record(content, thinking_chars=len(thinking), model_returned=d.get("model"), input_tokens=prompt,
                       cache_read_tokens=cached or None, output_tokens=out, seconds=round(secs, 1),
                       cost_usd=cost_of(e, (prompt or 0) - cached, 0, cached, out),
                       stop={"length": "length", "model_length": "length",
                             "content_filter": "refusal"}.get(finish, finish))


def call_ollama(e: dict, system: str, messages: list[dict]) -> dict:
    """Ollama's own chat API, so the context window is set per request and nothing is cut silently."""
    base = (resolve(e, "base_url") or "http://127.0.0.1:11434").rstrip("/")
    opts = dict(e.get("options", {}))
    num_ctx, reserve = opts.get("num_ctx"), opts.get("num_predict", 0)
    if not num_ctx:
        raise RuntimeError("set options.num_ctx: Ollama's default window would cut the C2 prompt")
    prompt_est = est_tokens(system + "".join(m["content"] for m in messages))
    if prompt_est + max(reserve, 0) > num_ctx:
        raise RunError(f"prompt ~{prompt_est} tokens + {reserve} for the answer exceeds num_ctx {num_ctx}; "
                       "raise num_ctx rather than let Ollama cut the prompt")
    body = {"model": resolve(e, "model"), "stream": False, "options": opts,
            "messages": [{"role": "system", "content": system}] + messages}
    if "think" in e:
        body["think"] = e["think"]
    if "keep_alive" in e:
        body["keep_alive"] = e["keep_alive"]
    t0 = time.time()
    d = with_retries(lambda: post_json(f"{base}/api/chat", {"Content-Type": "application/json"}, body,
                                       e.get("timeout", 3600)), attempts=2)
    secs = time.time() - t0
    msg = d.get("message", {})
    pin, out = d.get("prompt_eval_count"), d.get("eval_count")
    if pin is not None and out is not None and pin + out >= num_ctx:
        raise RunError(f"used {pin + out} of num_ctx {num_ctx}: the window may have cut the prompt")
    return turn_record(msg.get("content"), thinking_chars=len(msg.get("thinking") or ""),
                       model_returned=d.get("model"), input_tokens=pin, output_tokens=out,
                       seconds=round(secs, 1), cost_usd=cost_of(e, pin, 0, 0, out),
                       stop={"length": "length"}.get(d.get("done_reason"), d.get("done_reason")),
                       load_seconds=round((d.get("load_duration") or 0) / 1e9, 1),
                       prompt_seconds=round((d.get("prompt_eval_duration") or 0) / 1e9, 1))


def anthropic_client(e: dict):
    import anthropic  # only the Claude engines need the SDK

    key = api_key(e)
    if not key:
        raise RuntimeError(f"missing key {e.get('key_env')}")
    return anthropic.Anthropic(api_key=key, base_url=e.get("base_url", ANTHROPIC_URL),
                               max_retries=4, timeout=e.get("timeout", 900))


def call_anthropic(e: dict, system: str, turns: list[str]) -> list[dict]:
    """Claude through the Messages API with the official SDK. Turn 2 gets turn 1's text, as every other engine
    does. No server-side fallbacks: a refused run must fail visibly, not quietly switch to another model."""
    client = anthropic_client(e)
    params = dict(e.get("params", {}))
    max_tokens = params.pop("max_tokens", 32000)
    extra = {}
    if e.get("cache", True):
        extra["cache_control"] = {"type": "ephemeral"}  # cost only: the model sees the same text
    msgs, out = [], []
    for turn in turns:
        msgs.append({"role": "user", "content": turn})
        t0 = time.time()
        with client.messages.stream(model=e["model"], max_tokens=max_tokens, system=system, messages=msgs,
                                    **extra, **params) as stream:
            m = stream.get_final_message()
        secs = time.time() - t0
        text = "".join(b.text for b in m.content if b.type == "text")
        thinking = sum(len(getattr(b, "thinking", "") or "") for b in m.content if b.type == "thinking")
        u = m.usage
        fresh = u.input_tokens or 0
        cw, cr = u.cache_creation_input_tokens or 0, u.cache_read_input_tokens or 0
        detail = getattr(m, "stop_details", None)
        rec = turn_record(text, thinking_chars=thinking, model_returned=m.model, input_tokens=fresh + cw + cr,
                          cache_write_tokens=cw, cache_read_tokens=cr, output_tokens=u.output_tokens,
                          seconds=round(secs, 1), cost_usd=cost_of(e, fresh, cw, cr, u.output_tokens),
                          stop={"max_tokens": "length"}.get(m.stop_reason, m.stop_reason),
                          stop_detail=getattr(detail, "category", None) if detail else None,
                          request_id=getattr(m, "_request_id", None))
        out.append(rec)
        if rec["stop"] not in OK_STOPS or not rec["text"]:
            return out  # converse() rejects it; no point sending turn 2
        msgs.append({"role": "assistant", "content": rec["text"]})  # the same stripped text every engine gets
    return out


def claude_bin() -> str:
    return os.environ.get("CLAUDE_BIN") or shutil.which("claude") or "claude"


def call_claude(e: dict, system: str, turns: list[str]) -> list[dict]:
    """Two turns through the Claude Code CLI with no tools, no CLAUDE.md, no memory, in an empty folder.
    Needs a CLI recent enough to have --safe-mode and --system-prompt-file (run `claude update`)."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE") or k.startswith("ANTHROPIC_BASE") or k.startswith("USE_"))}
    out = []
    with tempfile.TemporaryDirectory(prefix="spike-claude-") as tmp:
        sysfile = pathlib.Path(tmp) / "system.txt"
        sysfile.write_text(system, encoding="utf-8")
        session = None
        for turn in turns:
            cmd = [claude_bin(), "-p", "--safe-mode", "--tools", "", "--strict-mcp-config",
                   "--model", e["model"], "--output-format", "json", "--system-prompt-file", str(sysfile)]
            if session:
                cmd += ["--resume", session]
            t0 = time.time()
            p = subprocess.run(cmd, input=turn, capture_output=True, text=True, encoding="utf-8", cwd=tmp,
                               env=env, timeout=e.get("timeout", 900))
            secs = time.time() - t0
            try:
                d = json.loads(p.stdout)
            except json.JSONDecodeError:
                raise RuntimeError(f"claude CLI gave no JSON (exit {p.returncode}): {p.stderr[:300]}")
            if d.get("is_error"):
                raise RuntimeError(f"claude CLI error: {str(d.get('result'))[:300]}")
            session = d.get("session_id")
            u = d.get("usage", {})
            out.append(turn_record(d.get("result"), model_returned=",".join(d.get("modelUsage", {}).keys()),
                                   input_tokens=(u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0)
                                   + (u.get("cache_creation_input_tokens") or 0),
                                   cache_write_tokens=u.get("cache_creation_input_tokens"),
                                   cache_read_tokens=u.get("cache_read_input_tokens"),
                                   output_tokens=u.get("output_tokens"), seconds=round(secs, 1),
                                   cost_usd=d.get("total_cost_usd"), stop=d.get("stop_reason") or "end_turn"))
    return out


def converse(e: dict, prompt: dict) -> list[dict]:
    kind = e["kind"]
    if kind == "anthropic":
        out = call_anthropic(e, prompt["system"], prompt["turns"])
    elif kind == "claude-cli":
        out = call_claude(e, prompt["system"], prompt["turns"])
    elif kind in ("openai", "ollama"):
        call = call_openai if kind == "openai" else call_ollama
        msgs, out = [], []
        for turn in prompt["turns"]:
            msgs.append({"role": "user", "content": turn})
            try:
                r = call(e, prompt["system"], msgs)
            except RunError as ex:
                raise RunError(str(ex), out) from ex
            out.append(r)
            if r["stop"] not in OK_STOPS or not r["text"]:
                break  # rejected below; no point sending the next turn
            msgs.append({"role": "assistant", "content": r["text"]})
    else:
        raise ValueError(f"unknown engine kind {kind!r}")
    try:
        for i, r in enumerate(out):
            require_ok(r, f"turn {i + 1}")
        if len(out) != len(prompt["turns"]):
            raise RunError(f"{len(out)} of {len(prompt['turns'])} turns came back")
    except RunError as ex:
        raise RunError(str(ex), out) from None
    return out


# ---------------------------------------------------------------- run

class Budget:
    """Stops new runs once the money spent in this command reaches the limit (runs already started finish)."""

    def __init__(self, limit: float | None):
        self.limit, self.spent, self.lock = limit, 0.0, threading.Lock()

    def ok(self) -> bool:
        with self.lock:
            return self.limit is None or self.spent < self.limit

    def add(self, usd: float | None) -> None:
        with self.lock:
            self.spent += usd or 0


def run_id(engine: str, c: str, s: str, rep: int) -> str:
    return f"{engine}__{c}__{s}__r{rep}"


def one_run(name: str, e: dict, c: str, s: str, rep: int, budget: Budget | None = None) -> str:
    rid = run_id(name, c, s, rep)
    path = RUNS / "raw" / f"{rid}.json"
    failed = RUNS / "failed" / f"{rid}.txt"
    prompt = build(c, s)
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            old = None  # half-written by a killed process: run it again
        if old is not None:
            if old.get("prompt_sha256") != sha(prompt_blob(prompt)) or old.get("model") != resolve(e, "model"):
                return (f"STALE {rid}: saved with model {old.get('model')} or another prompt; move it out of "
                        "runs/raw to rerun it (nothing was sent)")
            return f"skip {rid}"
    if budget and not budget.ok():
        return f"held {rid}: budget of ${budget.limit} reached"
    started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    try:
        turns = converse(e, prompt)
    except Exception as ex:  # keep failures visible, never silent
        if budget:
            budget.add(sum(t.get("cost_usd") or 0 for t in getattr(ex, "turns", [])))
        msg = redact(f"{type(ex).__name__}: {ex}")
        atomic_write(failed, f"{started}\n{msg}\n")
        return f"FAIL {rid}: {msg[:160]}"
    rec = {"run_id": rid, "engine": name, "kind": e["kind"], "model": resolve(e, "model"),
           "endpoint_host": (re.sub(r"^https?://([^/]+).*", r"\1", resolve(e, "base_url") or
                                    {"anthropic": ANTHROPIC_URL, "claude-cli": "claude-cli",
                                     "ollama": "127.0.0.1:11434"}.get(e["kind"], "?"))),
           "condition": c, "stage": s, "repeat": rep, "started_utc": started,
           "prompt_sha256": sha(prompt_blob(prompt)),
           "settings": {k: e[k] for k in ("params", "options", "think", "cache") if k in e},
           "history": "turn 2 receives turn 1's text only", "harness_commit": RUN_COMMIT, "turns": turns}
    atomic_write(path, json.dumps(rec, ensure_ascii=False, indent=1))
    failed.unlink(missing_ok=True)
    cost = [t["cost_usd"] for t in turns if t["cost_usd"] is not None]
    if budget:
        budget.add(sum(cost))
    secs = sum(t["seconds"] or 0 for t in turns)
    return f"ok   {rid} ({secs:.0f}s{f', ${sum(cost):.3f}' if cost else ''})"


RUN_COMMIT = "unknown"  # set by `run`: the harness commit every saved run records


def cmd_run(args) -> None:
    global RUN_COMMIT
    load_secrets()
    if not args.no_verify:
        problems = verify_fingerprints()
        if problems:
            print("STOP: the prompts or rules differ from what spikes.md committed:")
            for p in problems:
                print(f"  - {p}")
            sys.exit("Nothing was sent. Tell the owner (Angelotxx271); --no-verify skips this check for test runs only.")
    head, dirty = harness_commit()
    if dirty and not args.allow_dirty:
        sys.exit(f"the harness in {CODE} has uncommitted changes, so these runs couldn't be traced to a commit. "
                 "Commit first (or --allow-dirty for a trial). Nothing was sent.")
    RUN_COMMIT = head + ("+uncommitted" if dirty else "")
    print(f"harness commit {RUN_COMMIT[:12]}")
    eng = engines(args.engine)
    conds = args.condition or CONDITIONS
    stages = args.stage or STAGES
    jobs = [(n, e, c, s, r) for n, e in eng.items() for c in conds for s in stages
            for r in range(1, args.repeats + 1)]
    budget = Budget(args.budget)
    print(f"{len(jobs)} runs on {', '.join(eng)}" + (f", budget ${args.budget}" if args.budget else ""))
    unpriced = [n for n, e in eng.items() if cost_of(e, 0, 0, 0, 0) is None]
    if args.budget and unpriced:
        print(f"note: the budget can't count {', '.join(unpriced)} (no price in engines.json)")
    pools = {n: cf.ThreadPoolExecutor(max_workers=e.get("concurrency", 2)) for n, e in eng.items()}
    futs = [pools[j[0]].submit(one_run, *j, budget) for j in jobs]
    try:
        for f in cf.as_completed(futs):
            print(f.result(), flush=True)
    except KeyboardInterrupt:
        print("stopping: runs not yet started are cancelled; runs already sent finish and are saved", flush=True)
        raise
    finally:
        for p in pools.values():
            p.shutdown(wait=True, cancel_futures=True)  # never keep spending after a stop or a crash
        if args.budget:
            print(f"spent about ${budget.spent:.2f} of ${args.budget}")


def cmd_check(args) -> None:
    load_secrets()
    for name, e in engines(args.engine).items():
        try:
            r = converse(e, {"system": NEUTRAL_SYSTEM, "turns": ["Reply with the single word: ready"]})[0]
            print(f"{name}: ok, said {r['text'][:30]!r}, model {r['model_returned']}, {r['seconds']}s, "
                  f"stop {r['stop']}")
        except Exception as ex:
            print(f"{name}: FAILED {redact(str(ex))[:200]}")


def cmd_list(_args) -> None:
    load_secrets()
    cfg = config()
    print(f"{'engine':16} {'on':4} {'kind':11} {'model':28} {'key':12} price $/M in/out")
    for name, e in cfg.items():
        if name.startswith("_"):
            continue
        on = "judge" if e.get("role") == "judge" else ("yes" if e.get("enabled", True) else "no")
        env = e.get("key_env")
        key = ("set" if os.environ.get(env) else ("optional" if e.get("key_optional") else "MISSING")) if env \
            else "not needed"
        p = e.get("price") or {}
        price = f"{p.get('input')}/{p.get('output')}" if p else "unknown"
        model = resolve(e, "model") or f"<{e.get('model_env')} not set>"
        print(f"{name:16} {on:4} {e['kind']:11} {model[:28]:28} {key:12} {price}")
    for g, members in cfg.get("_groups", {}).items():
        print(f"group {g}: {', '.join(members)}")


def cmd_models(args) -> None:
    load_secrets()
    for name, e in engines(args.engine).items():
        try:
            if e["kind"] == "openai":
                headers = {"Authorization": f"Bearer {api_key(e)}"} if api_key(e) else {}
                r = requests.get(f"{resolve(e, 'base_url').rstrip('/')}/models", headers=headers, timeout=30)
                r.raise_for_status()
                ids = sorted(m["id"] for m in r.json().get("data", []))
            elif e["kind"] == "ollama":
                base = (resolve(e, "base_url") or "http://127.0.0.1:11434").rstrip("/")
                ids = sorted(m["name"] for m in requests.get(f"{base}/api/tags", timeout=30).json().get("models", []))
            elif e["kind"] == "anthropic":
                ids = sorted(m.id for m in anthropic_client(e).models.list())
            else:
                print(f"{name}: no model listing for kind {e['kind']}")
                continue
        except Exception as ex:
            print(f"{name}: FAILED {redact(str(ex))[:200]}")
            continue
        if args.filter:
            ids = [i for i in ids if args.filter.lower() in i.lower()]
        print(f"{name} ({len(ids)}): {', '.join(ids)}")


def cmd_estimate(args) -> None:
    """Upper-bound guess from prompt sizes and an assumed answer length; real counts come from the runs."""
    eng = engines(args.engine)
    conds, stages = args.condition or CONDITIONS, args.stage or STAGES
    print(f"Assumes {args.answer_tokens} output tokens per turn (thinking included) and ~{CHARS_PER_TOKEN} "
          "characters per token. Cached = Claude's prompt cache on the repeats and turn 2.")
    grand = 0.0
    for name, e in eng.items():
        priced = cost_of(e, 0, 0, 0, 0) is not None
        caches = e["kind"] == "anthropic" and e.get("cache", True)
        tin = tout = 0
        cost = 0.0
        for c in conds:
            for s in stages:
                p = build(c, s)
                t1 = est_tokens(p["system"] + p["turns"][0])  # turn 1 prompt
                t2 = t1 + args.answer_tokens // 2 + est_tokens(p["turns"][1])  # turn 2 resends turn 1 and its answer
                out = 2 * args.answer_tokens
                tin += (t1 + t2) * args.repeats
                tout += out * args.repeats
                if not priced:
                    continue
                if not caches:
                    cost += cost_of(e, t1 + t2, 0, 0, out) * args.repeats
                    continue
                turn2 = cost_of(e, t2 - t1, 0, t1, 0)  # turn 2 reads turn 1's prompt from the cache
                cost += cost_of(e, 0, t1, 0, out) + turn2  # repeat 1 writes the cache
                cost += (cost_of(e, 0, 0, t1, out) + turn2) * (args.repeats - 1)  # later repeats read it
        n = len(conds) * len(stages) * args.repeats
        size = f"{name}: {n} runs, ~{tin / 1e6:.2f}M tokens in / {tout / 1e6:.2f}M out"
        if not priced:
            print(f"{size}, cost unknown (no price in engines.json)")
            continue
        grand += cost
        print(f"{size}, ~${cost:.2f}{' with the prompt cache' if caches else ''}")
    print(f"total of the priced engines: ~${grand:.2f}")


# ---------------------------------------------------------------- judge

def parse_key(path: pathlib.Path | None = None) -> list[dict]:
    f = path or DATA / "answer-key.md"
    if not f.exists():
        sys.exit("answer-key.md not found: confirm answer-key.draft.md and rename it first")
    rows = []
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(K\d+)\s*\|\s*(V\d)\s*\|\s*([GC])\s*\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|", line)
        if m:
            present = [p.strip().lower() for p in m.group(6).split(",")]
            bad = [p for p in present if p not in STAGES]
            if bad or m.group(2).lower() not in present:
                sys.exit(f"answer key row {m.group(1)}: 'present in' must list versions from {STAGES} and include "
                         f"the round it was raised (got {', '.join(present)})")
            rows.append({"id": m.group(1), "raised": m.group(2).lower(), "tag": m.group(3),
                         "passage": m.group(4).strip(), "point": m.group(5).strip(), "present": present,
                         "note": m.group(7).strip()})
        elif re.match(r"\|\s*K\d+\s*\|", line):  # looks like a key row but doesn't parse: never drop it silently
            sys.exit(f"answer key row doesn't parse (a '|' inside a cell, or an unknown tag?): {line[:12]}…")
    if not rows:
        sys.exit("no key points parsed from the answer key")
    return rows


JUDGE_TASK = """You are scoring one AI review of a student's thesis proposal against a fixed answer key. The key was written from the supervisor's comments on this version and on later versions. You don't know which AI wrote the review, and it doesn't matter.

Work in three steps.

1. Split the review (both turns) into atomic flags: each distinct problem it raises about a passage or about the whole document. Merge a flag repeated in turn 2. Number them F1, F2, and so on, and give each a short quote or location and the problem in a few words.

2. For each answer-key point, list the flags that point at the same passage AND the same problem. A flag on the same passage about a different problem is not a match. A generic flag ("improve clarity", "proofread") is not a match for a specific point. When in doubt, it is not a match.

3. Classify each flag that matched no key point:
   - "correct": a real problem in this version: the guideline it relies on exists in the guidelines below and the passage really fails it, or the passage is clearly wrong (fact, logic, grammar, a missing required element)
   - "wrong": it misquotes the document or the guidelines, cites a rule that doesn't exist, or the passage actually meets the rule
   - "taste": a preference, a suggestion to add more, or a rewrite that fixes nothing that is wrong

Return only a JSON object, no prose, with this shape:
{"flags": [{"id": "F1", "where": "...", "problem": "..."}],
 "matches": [{"key": "K01", "flags": ["F3"]}],
 "unmatched": [{"flag": "F2", "class": "correct|wrong|taste", "why": "..."}]}
Every key point appears in "matches" (with an empty list when nothing matches). Every flag appears either in a match or in "unmatched"."""


def judge_prompt(stage: str, key: list[dict], review: list[str]) -> str:
    doc = (INPUTS / f"{stage}.md").read_text(encoding="utf-8")
    guidelines = (CONTEXT / "guidelines.md").read_text(encoding="utf-8")
    pts = [k for k in key if stage in k["present"]]
    lines = "\n".join(f"- {k['id']}: passage {k['passage']}. Point: {k['point']}" for k in pts)
    rev = "\n\n".join(f"[Turn {i + 1}]\n{t}" for i, t in enumerate(review))
    return (f"{JUDGE_TASK}\n\n<guidelines>\n{guidelines}\n</guidelines>\n\n<document_version>\n{doc}\n"
            f"</document_version>\n\n<answer_key>\n{lines}\n</answer_key>\n\n<review>\n{rev}\n</review>")


def check_verdict(v: dict, key_ids: set[str]) -> dict:
    """A verdict the report can trust: the three lists, only real key IDs, only flags it defined."""
    if not all(isinstance(v.get(f), list) for f in ("flags", "matches", "unmatched")):
        raise ValueError("verdict lacks flags, matches or unmatched")
    flag_ids = {f.get("id") for f in v["flags"]}
    matched: set = set()
    for m in v["matches"]:
        if m.get("key") not in key_ids:
            raise ValueError(f"unknown key point {m.get('key')!r}")
        if not set(m.get("flags", [])) <= flag_ids:
            raise ValueError(f"match on undefined flags {m.get('flags')}")
        matched |= set(m.get("flags", []))
    unmatched = [u.get("flag") for u in v["unmatched"]]
    for u in v["unmatched"]:
        if u.get("class") not in ("correct", "wrong", "taste"):
            raise ValueError(f"unknown class {u.get('class')!r}")
    if set(unmatched) & matched or len(unmatched) != len(set(unmatched)):
        raise ValueError("a flag is both matched and unmatched, or classed twice")
    if set(unmatched) | matched != flag_ids:
        raise ValueError(f"flags neither matched nor classed: {sorted(flag_ids - matched - set(unmatched))}")
    listed = {m.get("key") for m in v["matches"]}
    v["matches"] += [{"key": k, "flags": []} for k in sorted(key_ids - listed)]  # a key point left out matched nothing
    return v


def one_judge(raw: pathlib.Path, key: list[dict], je: dict, jname: str) -> str:
    rec = json.loads(raw.read_text(encoding="utf-8"))
    out = SCORING / "judge" / jname / raw.name
    if out.exists():
        return f"skip {raw.stem}"
    prompt = judge_prompt(rec["stage"], key, [t["text"] for t in rec["turns"]])
    ids = {k["id"] for k in key if rec["stage"] in k["present"]}
    err: Exception | None = None
    for _attempt in range(3):
        try:
            r = converse(je, {"system": NEUTRAL_SYSTEM, "turns": [prompt]})[0]
            m = re.search(r"\{.*\}", r["text"], re.S)
            verdict = check_verdict(json.loads(m.group(0)), ids)
            break
        except Exception as ex:
            err = ex
    else:
        return f"FAIL {raw.stem}: {redact(str(err))[:160]}"
    atomic_write(out, json.dumps({"run_id": rec["run_id"], "judge": jname, "judge_model": je["model"],
                                  "key_sha256": sha_file(DATA / "answer-key.md"),
                                  "judge_cost_usd": r["cost_usd"], "judge_tokens_in": r["input_tokens"],
                                  "judge_tokens_out": r["output_tokens"], "verdict": verdict},
                                 ensure_ascii=False, indent=1))
    return f"ok   {raw.stem}"


def raw_runs(only: list[str] | None) -> list[pathlib.Path]:
    """Saved runs, optionally only those of some engines (names or groups, as for run)."""
    raws = sorted((RUNS / "raw").glob("*.json"))
    if not only:
        return raws
    names = set(engines(only))
    return [p for p in raws if p.name.split("__")[0] in names]


def cmd_judge(args) -> None:
    load_secrets()
    key = parse_key()
    cfg = config()
    if args.judge not in cfg:
        sys.exit(f"no judge {args.judge!r} in engines.json")
    je = cfg[args.judge]
    raws = raw_runs(args.engine)
    random.Random(7).shuffle(raws)  # order carries no information about the engine
    print(f"judging {len(raws)} runs with {args.judge} ({je['model']})")
    with cf.ThreadPoolExecutor(max_workers=je.get("concurrency", 2)) as pool:
        for res in pool.map(lambda p: one_judge(p, key, je, args.judge), raws):
            print(res, flush=True)
    jdir = SCORING / "judge" / args.judge
    spent = [json.loads(f.read_text(encoding="utf-8")).get("judge_cost_usd") or 0 for f in jdir.glob("*.json")]
    print(f"judge verdicts saved: {len(spent)}, about ${sum(spent):.2f} in total")


# ---------------------------------------------------------------- report

def score(rec: dict, verdict: dict | None, key: list[dict], caught: set[str] | None = None) -> dict:
    """Counts for one run. `caught` overrides the judge's matches (the human scores); E, W, T stay the judge's."""
    stage = rec["stage"]
    verdict = verdict or {}
    matched = caught if caught is not None else {m["key"] for m in verdict.get("matches", []) if m.get("flags")}
    raised = [k for k in key if k["raised"] == stage]
    early = [k for k in key if stage in k["present"] and STAGES.index(k["raised"]) > STAGES.index(stage)]
    carry = [k for k in key if stage in k["present"] and STAGES.index(k["raised"]) < STAGES.index(stage)]
    cls = [u.get("class") for u in verdict.get("unmatched", [])]
    return {"caught": sorted(matched), "K": len([k for k in raised if k["id"] in matched]), "N": len(raised),
            "KG": len([k for k in raised if k["id"] in matched and k["tag"] == "G"]),
            "NG": len([k for k in raised if k["tag"] == "G"]),
            "early": len([k for k in early if k["id"] in matched]), "carry": len([k for k in carry if k["id"] in matched]),
            "flags": len(verdict.get("flags", [])), "E": cls.count("correct"), "W": cls.count("wrong"),
            "T": cls.count("taste")}


def majority(runs: list[dict], ids: list[str]) -> set:
    need = len(runs) // 2 + 1
    return {i for i in ids if sum(i in r["caught"] for r in runs) >= need}


PUBLIC_RUN_FIELDS = ["run_id", "engine", "model", "model_returned", "condition", "stage", "repeat", "started_utc",
                     "harness_commit", "prompt_sha12", "tokens_in", "cache_read", "cache_write", "tokens_out",
                     "thinking_chars", "seconds", "cost_usd", "stops", "scored", "K", "N", "early", "carry",
                     "flags", "E", "W", "T"]


def public_row(rec: dict, s: dict | None) -> dict:
    """One run for the public log: counts, tokens, time and cost. No text, no key-point IDs."""
    t = rec["turns"]
    costs = [x.get("cost_usd") for x in t]
    row = {"run_id": rec["run_id"], "engine": rec["engine"], "model": rec["model"],
           "model_returned": t[0].get("model_returned"), "condition": rec["condition"], "stage": rec["stage"],
           "repeat": rec["repeat"], "started_utc": rec.get("started_utc"),
           "harness_commit": (rec.get("harness_commit") or "unknown")[:12],
           "prompt_sha12": (rec.get("prompt_sha256") or "")[:12],
           "tokens_in": sum(x.get("input_tokens") or 0 for x in t),
           "cache_read": sum(x.get("cache_read_tokens") or 0 for x in t),
           "cache_write": sum(x.get("cache_write_tokens") or 0 for x in t),
           "tokens_out": sum(x.get("output_tokens") or 0 for x in t),
           "thinking_chars": sum(x.get("thinking_chars") or 0 for x in t),
           "seconds": round(sum(x.get("seconds") or 0 for x in t), 1),
           "cost_usd": round(sum(costs), 6) if all(c is not None for c in costs) else "",
           "stops": "/".join(str(x.get("stop")) for x in t), "scored": "yes" if s else "no"}
    for f in ("K", "N", "early", "carry", "flags", "E", "W", "T"):
        row[f] = s[f] if s else ""
    return row


def load_cells(key: list[dict], judge: str, source: str, only: list[str] | None = None,
               rows: list[dict] | None = None) -> tuple[dict[tuple, list], list[str]]:
    """Scored runs per (engine, condition, version), plus notes on every run left out and why.
    `only` limits it to some engines; `rows`, when given, collects one public row per saved run."""
    jdir = SCORING / "judge" / judge
    key_hash = sha_file(DATA / "answer-key.md")
    human, notes = {}, []
    if source == "human":
        f = SCORING / "human" / "combined.json"
        if not f.exists():
            sys.exit("no scoring/human/combined.json yet: run `agree` on the scorers' sheets first")
        human = {rid: set(ids) for rid, ids in json.loads(f.read_text(encoding="utf-8"))["runs"].items()}
    want = {(c, s): sha(prompt_blob(build(c, s))) for c in CONDITIONS for s in STAGES}
    cells: dict[tuple, list] = {}
    models: dict[tuple, set] = {}
    skipped = {"another prompt": [], "no judge verdict": [], "verdict from another key": [], "not human-scored": []}
    for raw in raw_runs(only):
        rec = json.loads(raw.read_text(encoding="utf-8"))
        if rows is not None:
            rows.append(public_row(rec, None))  # filled in below once the run is scored
        if rec.get("prompt_sha256") != want.get((rec["condition"], rec["stage"])):
            skipped["another prompt"].append(raw.stem)
            continue
        jf = jdir / raw.name
        verdict = None
        if jf.exists():
            j = json.loads(jf.read_text(encoding="utf-8"))
            if j.get("key_sha256") == key_hash:
                verdict = j["verdict"]
            else:
                skipped["verdict from another key"].append(raw.stem)
                continue
        if verdict is None:  # E, W and T always come from the judge, so a run without a verdict can't be read
            skipped["no judge verdict"].append(raw.stem)
            continue
        if source == "human" and raw.stem not in human:
            skipped["not human-scored"].append(raw.stem)
            continue
        cell_key = (rec["engine"], rec["condition"], rec["stage"])
        models.setdefault(cell_key, set()).add(rec.get("model"))
        s = score(rec, verdict, key, human.get(raw.stem))
        costs = [t["cost_usd"] for t in rec["turns"] if t.get("cost_usd") is not None]
        s.update(tokens_in=sum(t["input_tokens"] or 0 for t in rec["turns"]),
                 tokens_out=sum(t["output_tokens"] or 0 for t in rec["turns"]),
                 seconds=sum(t["seconds"] or 0 for t in rec["turns"]),
                 cost=sum(costs) if len(costs) == len(rec["turns"]) else None, judged=verdict is not None)
        cells.setdefault(cell_key, []).append(s)
        if rows is not None:
            rows[-1] = public_row(rec, s)
    for cell_key, ms in models.items():
        if len(ms) > 1:  # e.g. -latest pinned halfway through: the repeats aren't the same engine any more
            notes.append(f"{'/'.join(cell_key)} mixes models {sorted(map(str, ms))}: left out")
            cells.pop(cell_key, None)
    for why, ids in skipped.items():
        if ids:
            notes.append(f"{len(ids)} run(s) left out, {why}: {', '.join(ids[:6])}{' …' if len(ids) > 6 else ''}")
    return cells, notes


def decision_lines(cells: dict, key: list[dict], build_engine: str) -> list[str]:
    """The protocol v2 rules applied to these counts. Provisional: the humans' counts are the headline."""
    def cell(eng, c, st):
        runs = cells.get((eng, c, st))
        if not runs or len(runs) != REPEATS:  # an incomplete cell would quietly change the 2-of-3 rule
            return None
        raised = [k["id"] for k in key if k["raised"] == st]
        ks = [r["K"] for r in runs]
        e_mean = sum(r["E"] for r in runs) / len(runs)
        return {"K": len(majority(runs, raised)), "E": e_mean, "W": sum(r["W"] for r in runs) / len(runs),
                "noisy": max(ks) - min(ks) > 1, "n": len(runs)}

    eps = 1e-9  # E and W are means of three, so compare with a tolerance instead of exact floats
    rounds = ["v1", "v2", "v3"]
    lines = ["", "## Decision rules (protocol v2), provisional", "",
             f"Stand-in = C2 on {build_engine}. C = K (majority) + E (mean), W = mean wrong flags. "
             "A noisy cell (K varies by more than 1 across repeats) widens the C tolerance from 1 to 2. "
             f"Only cells with all {REPEATS} repeats scored are read.", ""]
    incomplete = sorted(f"{e}/{c}/{s} ({len(r)})" for (e, c, s), r in cells.items() if len(r) != REPEATS)
    if incomplete:
        lines += [f"Cells not read yet, scored repeats in brackets: {', '.join(incomplete)}", ""]
    stand = {st: cell(build_engine, "C2", st) for st in rounds}
    if all(stand.values()):
        caught = sum(s["K"] for s in stand.values())
        total = sum(len([k for k in key if k["raised"] == st]) for st in rounds)
        miss = 1 - caught / total if total else 0
        lines.append(f"- **Falsifier 3:** C2 on {build_engine} caught {caught} of {total}, miss rate {miss:.0%}: "
                     + ("**holds** (above 40%): narrow the check" if miss > 0.40 else "does not hold (40% or less)"))
    else:
        lines.append(f"- **Falsifier 3:** not read yet: C2 on {build_engine} lacks a scored round")
    lines += ["", "| Engine | Route | v1 C/W vs stand-in | v2 | v3 | Same flags in | Flags half |", "|---|---|---|---|---|---|---|"]
    for eng in sorted({k[0] for k in cells}):
        for c in ("C0", "C1"):
            parts, same, scored = [], 0, 0
            for st in rounds:
                r, s = cell(eng, c, st), stand[st]
                if not r or not s:
                    parts.append("n/a")
                    continue
                scored += 1
                tol = 2 if (r["noisy"] or s["noisy"]) else 1
                ok = (r["K"] + r["E"] >= s["K"] + s["E"] - tol - eps) and (r["W"] <= s["W"] + 1 + eps)
                same += ok
                parts.append(f"{r['K'] + r['E']:.2f}/{r['W']:.2f} vs {s['K'] + s['E']:.2f}/{s['W']:.2f} "
                             f"{'same' if ok else 'differs'}{' (noisy)' if tol == 2 else ''}")
            if scored:
                left = len(rounds) - scored
                verdict = "holds" if same >= 2 else ("does not hold" if same + left < 2 else "open")
                lines.append(f"| {eng} | {c} | {' | '.join(parts)} | {same} of {scored} | {verdict} |")
    return lines


def cmd_report(args) -> None:
    key = parse_key()
    rows: list[dict] = []
    cells, notes = load_cells(key, args.judge, args.source, args.engine, rows)
    names = set(engines(args.engine)) if args.engine else None
    failed = sorted(p.stem for p in (RUNS / "failed").glob("*.txt")
                    if names is None or p.stem.split("__")[0] in names) if (RUNS / "failed").exists() else []
    scope = ", ".join(sorted({r["engine"] for r in rows})) or "none"
    commits = ", ".join(sorted({r["harness_commit"] for r in rows})) or "none"
    lines = ["# Advisor spike results (private)", "",
             f"Matches from: {'the two human scorers (E, W, T from the judge)' if args.source == 'human' else 'judge ' + args.judge + ', a first pass: the human scores are the headline'}. "
             f"Generated {dt.datetime.now().isoformat(timespec='minutes')}. Engines: {scope}. "
             f"Harness commit: {commits}. "
             "A point counts as caught in a cell when a majority of repeats caught it. "
             f"Failed runs not scored: {len(failed)}. Notes on runs left out: {len(notes)}.", "",
             "| Engine | Cond | Version | Repeats | Caught / raised (majority) | K per repeat | G caught | Early (mean) | Carry (mean) | Flags (mean) | Correct extra | Wrong | Taste | Tokens in/out (mean) | s (mean) | $ (mean) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    pooled: dict[tuple, list] = {}
    for (eng, c, st), runs in sorted(cells.items(), key=lambda x: (x[0][0], x[0][1], STAGES.index(x[0][2]))):
        raised = [k["id"] for k in key if k["raised"] == st]
        maj = majority(runs, raised)
        g = [k["id"] for k in key if k["raised"] == st and k["tag"] == "G"]

        def mean(f: str) -> float:
            return sum(r[f] for r in runs) / len(runs)

        cost = [r["cost"] for r in runs if r["cost"] is not None]
        reps = f"{len(runs)}" if len(runs) == REPEATS else f"{len(runs)} (incomplete)"
        lines.append(f"| {eng} | {c} | {st} | {reps} | {len(maj)} / {len(raised)} | "
                     f"{', '.join(str(r['K']) for r in runs)} | {len(maj & set(g))} / {len(g)} | "
                     f"{mean('early'):.1f} | {mean('carry'):.1f} | {mean('flags'):.1f} | {mean('E'):.1f} | "
                     f"{mean('W'):.1f} | {mean('T'):.1f} | {mean('tokens_in'):.0f} / {mean('tokens_out'):.0f} | "
                     f"{mean('seconds'):.0f} | {f'{sum(cost) / len(cost):.3f}' if cost else 'n/a'} |")
        if st != "final" and len(runs) == REPEATS:  # pool complete cells only
            pooled.setdefault((eng, c), []).append((maj, raised, g))
    # The public copy (for spikes.md) is built beside the private one: counts only, never key-point IDs
    title = ["", "## Pooled over V1 to V3 (falsifier 3 reads the miss rate)", "",
             f"Complete cells only ({REPEATS} scored repeats); a row with fewer than three rounds shows fewer points.",
             ""]
    head = "| Engine | Cond | Caught | Missed | Miss rate | G caught |"
    private = lines + title + [head + " Points caught |", "|---" * 7 + "|"]
    public = lines + title + [head, "|---" * 6 + "|"]
    for (eng, c), parts in sorted(pooled.items()):
        caught = set().union(*[p[0] for p in parts])
        allp = [i for p in parts for i in p[1]]
        allg = [i for p in parts for i in p[2]]
        miss = 1 - len(caught) / len(allp) if allp else 0
        row = (f"| {eng} | {c} | {len(caught)} / {len(allp)} | {len(allp) - len(caught)} | {miss:.0%} | "
               f"{len(caught & set(allg))} / {len(allg)} |")
        private.append(f"{row} {', '.join(sorted(caught))} |")
        public.append(row)
    decisions = decision_lines(cells, key, args.build_engine)
    private += decisions
    public += decisions
    if notes:
        private += ["", "## Runs left out of scoring", ""] + [f"- {n}" for n in notes]
    if failed:
        private += ["", "## Failed runs (rerun with `run`)", ""] + [f"- {f}" for f in failed]
    public[0] = "# Advisor spike results (public: counts only)"
    public += ["", f"Per-run tokens, time, cost and counts: runs-public.csv ({len(rows)} runs, {len(failed)} failed "
               "and not saved). The proposal text, the answer key and the reviews stay private."]
    for f in ("results-public.md", "runs-public.csv"):
        (PUBLIC_OUT / f).unlink(missing_ok=True)  # never leave an old public copy behind
    atomic_write(DATA / "results.md", "\n".join(private) + "\n")
    atomic_write(PUBLIC_OUT / "results-public.md", "\n".join(public_safe(public)) + "\n")
    buf = __import__("io").StringIO()
    w = csv.DictWriter(buf, fieldnames=PUBLIC_RUN_FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(sorted(rows, key=lambda r: r["run_id"]))
    atomic_write(PUBLIC_OUT / "runs-public.csv", "\n".join(public_safe(buf.getvalue().splitlines())) + "\n")
    print("\n".join(private))


def public_safe(lines: list[str]) -> list[str]:
    """Last safety net before anything is copied into the public repo: no key-point ID may appear."""
    leaks = [l for l in lines if re.search(r"\bK\d+\b", l)]
    if leaks:
        raise RuntimeError(f"a key-point ID would reach the public copy: {leaks[0][:80]}")
    return lines


# ---------------------------------------------------------------- human sheets

def cmd_sheets(args) -> None:
    key = parse_key()
    raws = sorted((RUNS / "raw").glob("*.json"))
    rng = random.Random(42)
    codes = {}
    out = SCORING / "human"
    out.mkdir(parents=True, exist_ok=True)
    pages = {}
    for st in STAGES:
        recs = [json.loads(p.read_text(encoding="utf-8")) for p in raws if f"__{st}__" in p.name]
        rng.shuffle(recs)
        pts = [k for k in key if st in k["present"]]
        md = [f"# Scoring sheet, version {st.upper()}", "",
              "Match each key point to the flags in each list. Same passage and same problem; when in doubt, no match.",
              "Write the flag numbers in the CSV next to this file (several in one cell: separate them with spaces).",
              "Leave a cell empty when nothing matches. When a list is fully scored, put an x in its 'done' row:",
              "lists not marked done are left out. Do not open map.json.", "", "## Key points", ""]
        md += [f"- **{k['id']}** ({k['tag']}): {k['passage']} — {k['point']}" for k in pts]
        grid = ["key," + ",".join(f"L{i + 1:02d}" for i in range(len(recs)))]
        grid += [k["id"] + "," * len(recs) for k in pts] + [DONE_ROW + "," * len(recs)]
        for i, r in enumerate(recs):
            code = f"{st.upper()}-L{i + 1:02d}"
            codes[code] = r["run_id"]
            md += ["", f"## List L{i + 1:02d}", ""]
            for t, turn in enumerate(r["turns"]):
                md += [f"**Turn {t + 1}**", "", turn["text"], ""]
        pages[st] = ("\n".join(md), "\n".join(grid) + "\n")
    mapf = SCORING / "map.json"
    if mapf.exists() and json.loads(mapf.read_text(encoding="utf-8")) != codes and not args.force:
        sys.exit("scoring/map.json already exists and these sheets would number the lists differently, so filled "
                 "sheets would no longer match. Finish scoring the old sheets, or rerun with --force to replace them.")
    for st, (md, grid) in pages.items():
        atomic_write(out / f"sheet-{st}.md", md)
        atomic_write(out / f"sheet-{st}.csv", grid)
    mapf.write_text(json.dumps(codes, indent=1), encoding="utf-8")
    print(f"wrote {len(STAGES)} sheets for {len(raws)} runs to {out}; the code map is scoring/map.json")


DONE_ROW = "done"  # the scorer marks this row under each list once it is fully scored


def read_sheet(path: pathlib.Path) -> tuple[dict[str, set[str]], list[str]]:
    """A filled CSV: rows are key points, columns are lists; a flag number in a cell (3, F3, "F1 F4") means
    matched. Only lists marked in the last row ("done") count as scored, so a list nobody scored never reads as
    zero catches. Reads commas or semicolons (Excel in a Spanish locale saves with ';'), UTF-8 or Windows-1252.
    Returns the scored lists and the warnings."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    first = text.splitlines()[0] if text else ""
    delim = ";" if first.count(";") > first.count(",") else ","
    rows = [r for r in csv.reader(text.splitlines(), delimiter=delim) if any(c.strip() for c in r)]
    head = [h.strip() for h in rows[0]]
    cols = [(i, h) for i, h in enumerate(head) if i > 0 and h]  # a stray empty column is ignored
    body = [r for r in rows[1:] if r[0].strip().lower() != DONE_ROW]
    done_row = next((r for r in rows[1:] if r[0].strip().lower() == DONE_ROW), None)
    warnings, got = [], {}
    for i, col in cols:
        if done_row is None or i >= len(done_row) or not done_row[i].strip():
            warnings.append(f"{path.name} {col}: not marked done, left out")
            continue
        got[col] = set()
        for r in body:
            cell = r[i].strip() if i < len(r) else ""
            if re.search(r"[1-9]", cell):
                got[col].add(r[0].strip())
            elif cell:
                warnings.append(f"{path.name} {col} {r[0].strip()}: {cell!r} has no flag number, read as no match")
    return got, warnings


def cmd_agree(args) -> None:
    key = parse_key()
    codes = json.loads((SCORING / "map.json").read_text(encoding="utf-8"))
    scorers = [pathlib.Path(d) for d in args.scorers]
    if len(scorers) != 2 and not args.one:
        sys.exit("the protocol needs the scorer and the second checker: give two folders (or --one for a trial)")
    per: list[dict[str, set]] = []
    for d in scorers:
        got = {}
        for st in STAGES:
            f = d / f"sheet-{st}.csv"
            if f.exists():
                lists, warnings = read_sheet(f)
                for w in warnings:
                    print(f"  {d.name}: {w}")
                for col, ids in lists.items():
                    got[codes[f"{st.upper()}-{col}"]] = ids
        per.append(got)
        print(f"{d}: {len(got)} lists scored and marked done")
    runs = set.intersection(*[set(p) for p in per]) if per else set()
    only_one = set().union(*[set(p) for p in per]) - runs
    if only_one:
        print(f"{len(only_one)} list(s) scored by only one person are left out until both have scored them")
    # Disagreements count as not matched (spikes.md): the people's count is what both of them matched
    combined = {rid: sorted(set.intersection(*[p[rid] for p in per])) for rid in sorted(runs)}
    recs = {rid: json.loads((RUNS / "raw" / f"{rid}.json").read_text(encoding="utf-8")) for rid in runs}
    present = {rid: [k["id"] for k in key if recs[rid]["stage"] in k["present"]] for rid in runs}
    if len(per) == 2:
        pairs = sum(len(present[r]) for r in runs)
        between = sum((i in per[0][r]) != (i in per[1][r]) for r in runs for i in present[r])
        if pairs:
            print(f"scorer vs scorer: {between} of {pairs} points differ ({between / pairs:.0%}); "
                  "those count as not matched")
    atomic_write(SCORING / "human" / "combined.json",
                 json.dumps({"scorers": [d.name for d in scorers], "runs": combined}, indent=1))
    jdir = SCORING / "judge" / args.judge
    by_engine: dict[str, list[int]] = {}
    for rid, caught in combined.items():
        jf = jdir / f"{rid}.json"
        if not jf.exists():
            continue
        v = json.loads(jf.read_text(encoding="utf-8"))["verdict"]
        judged = {m["key"] for m in v.get("matches", []) if m.get("flags")}
        tally = by_engine.setdefault(recs[rid]["engine"], [0, 0])
        tally[0] += sum((i in judged) != (i in caught) for i in present[rid])
        tally[1] += len(present[rid])
    diff, total = sum(t[0] for t in by_engine.values()), sum(t[1] for t in by_engine.values())
    if total:
        verdict = ("over 1 in 5: report only the runs people scored (report --source human)" if diff / total > 0.2
                   else "within 1 in 5: the judge's counts may stand beside the people's")
        print(f"judge vs people: {diff} of {total} points differ ({diff / total:.0%}), {verdict}")
        for eng, (d_, t_) in sorted(by_engine.items()):
            print(f"  {eng}: {d_} of {t_} differ ({d_ / t_:.0%})")
    print(f"wrote scoring/human/combined.json for {len(combined)} runs")


def main() -> None:
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prompts")
    sub.add_parser("verify")
    sub.add_parser("list")
    for name in ["check", "run", "estimate", "models"]:
        p = sub.add_parser(name)
        p.add_argument("--engine", nargs="*", help="engine names, group names, or all")
        if name in ("run", "estimate"):
            p.add_argument("--condition", nargs="*", choices=CONDITIONS)
            p.add_argument("--stage", nargs="*", choices=STAGES)
            p.add_argument("--repeats", type=int, default=3)
        if name == "run":
            p.add_argument("--budget", type=float, help="stop starting new runs after this many US dollars")
            p.add_argument("--no-verify", action="store_true", help="skip the fingerprint check (test runs only)")
            p.add_argument("--allow-dirty", action="store_true", help="run with uncommitted harness changes (trials)")
        if name == "estimate":
            p.add_argument("--answer-tokens", type=int, default=6000)
        if name == "models":
            p.add_argument("--filter")
    for name in ["judge", "report", "agree"]:
        p = sub.add_parser(name)
        p.add_argument("--judge", default="judge-sonnet")
        if name in ("judge", "report"):
            p.add_argument("--engine", nargs="*", help="only these engines' runs (names, groups or all)")
        if name == "report":
            p.add_argument("--source", choices=["judge", "human"], default="judge")
            p.add_argument("--build-engine", default="opus", help="the engine whose C2 is the stand-in")
        if name == "agree":
            p.add_argument("scorers", nargs="+", help="one folder per scorer holding their filled sheet-*.csv")
            p.add_argument("--one", action="store_true", help="allow a single scorer (a trial, not the headline)")
    p = sub.add_parser("sheets")
    p.add_argument("--force", action="store_true")
    args = ap.parse_args()
    {"prompts": cmd_prompts, "verify": cmd_verify, "list": cmd_list, "check": cmd_check, "run": cmd_run,
     "estimate": cmd_estimate, "models": cmd_models, "judge": cmd_judge, "report": cmd_report,
     "sheets": cmd_sheets, "agree": cmd_agree}[args.cmd](args)


if __name__ == "__main__":
    main()
