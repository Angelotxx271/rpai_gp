"""Offline tests for spike.py. No model is called and nothing leaves this machine.

Run from the repo root:  private\\advisor-spike\\.venv\\Scripts\\python -I -m pytest prototype\\advisor-spike\\tests -q
Everything uses synthetic data, except two checks on the real private material that skip when it isn't there:
the prompts still match the committed hashes, and the answer key parses to the protocol's counts.
"""
from __future__ import annotations

import contextlib
import json
import pathlib
import sys
import types

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import spike  # noqa: E402

REAL_DATA = spike.DATA  # captured before any test points the module at a throwaway folder

KEY_MD = """| ID | Raised | Tag | Passage | Point | Present in | Note |
|---|---|---|---|---|---|---|
| K01 | V1 | G | Title page | Missing a required field | v1 | |
| K02 | V1 | C | Research question | Too broad | v1, v2 | |
| K03 | V2 | C | Method | Sample not justified | v1, v2, v3 | |
| K04 | V3 | G | References | Not APA | v1, v2, v3 | |
"""


@pytest.fixture
def ws(tmp_path, monkeypatch):
    """A throwaway workspace with the same layout as the real one."""
    for d in ("inputs", "context", "runs/raw", "scoring"):
        (tmp_path / d).mkdir(parents=True)
    for s in spike.STAGES:
        (tmp_path / "inputs" / f"{s}.md").write_text(f"Proposal text for {s}.", encoding="utf-8")
    (tmp_path / "context" / "guidelines.md").write_text("Guideline 1: use APA.", encoding="utf-8")
    (tmp_path / "context" / "standin.md").write_text("All programme documents.", encoding="utf-8")
    (tmp_path / "answer-key.md").write_text(KEY_MD, encoding="utf-8")
    for name, value in {"DATA": tmp_path, "INPUTS": tmp_path / "inputs", "CONTEXT": tmp_path / "context",
                        "RUNS": tmp_path / "runs", "SCORING": tmp_path / "scoring",
                        "PUBLIC_OUT": tmp_path / "public"}.items():
        monkeypatch.setattr(spike, name, value)
    return tmp_path


def raw_run(ws, engine, cond, stage, rep, text="F1 something", model="m"):
    rec = {"run_id": spike.run_id(engine, cond, stage, rep), "engine": engine, "kind": "openai", "model": model,
           "condition": cond, "stage": stage, "repeat": rep,
           "prompt_sha256": spike.sha(spike.prompt_blob(spike.build(cond, stage))),
           "turns": [spike.turn_record(text, input_tokens=100, output_tokens=10, seconds=1.0, cost_usd=0.01,
                                       stop="stop")] * 2}
    (ws / "runs" / "raw" / f"{rec['run_id']}.json").write_text(json.dumps(rec), encoding="utf-8")
    return rec["run_id"]


def verdict(caught: list[str], extra: list[str] = ()):
    flags = [{"id": f"F{i + 1}", "where": "x", "problem": "y"} for i in range(len(caught) + len(extra))]
    matches = [{"key": k, "flags": [f"F{i + 1}"]} for i, k in enumerate(caught)]
    unmatched = [{"flag": f"F{len(caught) + i + 1}", "class": c, "why": "z"} for i, c in enumerate(extra)]
    return {"flags": flags, "matches": matches, "unmatched": unmatched}


def write_verdict(ws, rid, v, judge="judge-sonnet", key_sha=None):
    d = ws / "scoring" / "judge" / judge
    d.mkdir(parents=True, exist_ok=True)
    key_sha = key_sha or spike.sha_file(ws / "answer-key.md")
    (d / f"{rid}.json").write_text(json.dumps({"run_id": rid, "key_sha256": key_sha, "verdict": v}),
                                   encoding="utf-8")


# ---------------------------------------------------------------- the frozen prompts

def test_real_prompts_still_match_the_committed_hashes():
    """The guard that matters most: no change to the harness may change what the models are sent."""
    if not (REAL_DATA / "inputs" / "v1.md").exists() or not spike.SPIKES_MD.exists():
        pytest.skip("real inputs or spikes.md not here")
    fp = spike.committed_fingerprints()
    assert len(fp["prompts"]) == 12
    assert set(fp["files"]) == {"answer-key.md", "protocol-v2.md", "protocol-v2-amendment-1.md"}
    assert spike.verify_fingerprints() == []


def test_real_answer_key_parses_to_the_protocol_counts():
    """protocol v2: 18 points, 10 from round 1, 5 from round 2, 3 from round 3; 4 G and 14 C. Counts only."""
    if not (REAL_DATA / "answer-key.md").exists():
        pytest.skip("real answer key not here")
    key = spike.parse_key()
    raised = [k["raised"] for k in key]
    assert (len(key), raised.count("v1"), raised.count("v2"), raised.count("v3")) == (18, 10, 5, 3)
    assert [k["tag"] for k in key].count("G") == 4


def test_fingerprint_parser_reads_files_and_prompts(tmp_path):
    md = tmp_path / "spikes.md"
    h = "a" * 64
    prompts = " ".join(f"`{i:012x}`" for i in range(4))
    md.write_text(f"| answer-key.md | `{h}` |\n| protocol-v2.md | `{'b' * 64}` |\n"
                  f"| Prompts, first 12 characters | C0: {prompts} · C1: {prompts} · C2: {prompts} "
                  "(rounds 1, 2, 3, approved) |\n", encoding="utf-8")
    fp = spike.committed_fingerprints(md)
    assert fp["files"] == {"answer-key.md": h, "protocol-v2.md": "b" * 64}
    assert fp["prompts"]["C2-final"] == f"{3:012x}" and len(fp["prompts"]) == 12


def test_verify_reports_a_changed_answer_key(ws, tmp_path):
    md = tmp_path / "spikes.md"
    md.write_text(f"| answer-key.md | `{'0' * 64}` |\n", encoding="utf-8")
    problems = spike.verify_fingerprints(md)
    assert any("answer-key.md" in p for p in problems)
    assert any("of 12" in p for p in problems)


def test_run_refuses_to_start_when_fingerprints_differ(ws, monkeypatch, capsys):
    monkeypatch.setattr(spike, "verify_fingerprints", lambda *a: ["prompt C0-v1 differs"])
    monkeypatch.setattr(spike, "converse", lambda *a: pytest.fail("a model was called"))
    args = types.SimpleNamespace(no_verify=False, engine=None, condition=None, stage=None, repeats=1, budget=None)
    with pytest.raises(SystemExit):
        spike.cmd_run(args)
    assert "STOP" in capsys.readouterr().out


# ---------------------------------------------------------------- engine selection

CFG = {"_groups": {"claude": ["opus", "sonnet"]},
       "opus": {"kind": "anthropic"}, "sonnet": {"kind": "anthropic"},
       "qwen": {"kind": "ollama", "enabled": False}, "judge-sonnet": {"kind": "anthropic", "role": "judge"}}


def test_engine_flag_takes_names_groups_and_all():
    assert list(spike.engines(None, CFG)) == ["opus", "sonnet"]  # qwen is off, the judge never runs as an arm
    assert list(spike.engines(["claude"], CFG)) == ["opus", "sonnet"]
    assert list(spike.engines(["qwen"], CFG)) == ["qwen"]  # naming an engine runs it even when off
    assert list(spike.engines(["all"], CFG)) == ["opus", "sonnet"]  # all = every engine that is on
    assert list(spike.engines(["opus", "claude"], CFG)) == ["opus", "sonnet"]  # no duplicates


def test_engine_flag_rejects_unknown_names_and_judges():
    with pytest.raises(SystemExit):
        spike.engines(["gpt"], CFG)
    with pytest.raises(SystemExit):
        spike.engines(["judge-sonnet"], CFG)


def test_shipped_engines_json_is_consistent():
    cfg = spike.config()
    arms = {n for n, e in cfg.items() if not n.startswith("_") and e.get("role") != "judge"}
    for g, members in cfg["_groups"].items():
        assert set(members) <= arms, g
    assert set(cfg["_groups"]["protocol-v2"]) == {"opus", "glm", "mistral", "qwen-local"}
    for n, e in cfg.items():
        if not n.startswith("_"):
            assert e["kind"] in ("anthropic", "openai", "ollama", "claude-cli"), n
    assert cfg["qwen-local"]["options"]["num_ctx"] >= 65536


# ---------------------------------------------------------------- providers (fake HTTP)

class FakeResponse:
    def __init__(self, status, data):
        self.status_code, self._data, self.text = status, data, json.dumps(data)

    def json(self):
        return self._data


def fake_post(responses, seen=None):
    it = iter(responses)

    def post(url, headers=None, json=None, timeout=None):
        if seen is not None:
            seen.append({"url": url, "headers": headers, "json": json})
        return next(it)
    return post


def test_openai_parses_glm_thinking_chunks_and_prices(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "sk-test-not-real")
    data = {"model": "zai-glm-5-3", "usage": {"prompt_tokens": 1000, "completion_tokens": 200},
            "choices": [{"finish_reason": "stop", "message": {"content": [
                {"type": "thinking", "thinking": [{"type": "text", "text": "hmm"}]},
                {"type": "text", "text": "Flag 1"}]}}]}
    seen = []
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(200, data)], seen))
    e = {"kind": "openai", "base_url": "https://api.mistral.ai/v1", "model": "zai-glm-5-3",
         "key_env": "MISTRAL_API_KEY", "price": {"input": 1.0, "output": 3.0}}
    r = spike.call_openai(e, "sys", [{"role": "user", "content": "hi"}])
    assert r["text"] == "Flag 1" and r["thinking_chars"] > 0 and r["stop"] == "stop"
    assert r["cost_usd"] == pytest.approx((1000 * 1.0 + 200 * 3.0) / 1e6)
    assert seen[0]["url"] == "https://api.mistral.ai/v1/chat/completions"
    assert seen[0]["json"]["messages"][0] == {"role": "system", "content": "sys"}


def test_openai_retries_rate_limits_then_succeeds(monkeypatch):
    monkeypatch.setattr(spike.time, "sleep", lambda s: None)
    ok = {"model": "m", "usage": {}, "choices": [{"finish_reason": "stop", "message": {"content": "fine"}}]}
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(429, {}), FakeResponse(503, {}),
                                                           FakeResponse(200, ok)]))
    e = {"kind": "openai", "base_url": "http://x/v1", "model": "m", "key_optional": True}
    assert spike.call_openai(e, "s", [{"role": "user", "content": "hi"}])["text"] == "fine"


def test_openai_client_errors_are_not_retried(monkeypatch):
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(401, {"error": "bad key"})]))
    e = {"kind": "openai", "base_url": "http://x/v1", "model": "m", "key_optional": True}
    with pytest.raises(RuntimeError, match="HTTP 401"):
        spike.call_openai(e, "s", [{"role": "user", "content": "hi"}])


def test_a_truncated_answer_fails_the_run_instead_of_being_scored(monkeypatch):
    cut = {"model": "m", "usage": {}, "choices": [{"finish_reason": "length", "message": {"content": "half a re"}}]}
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(200, cut)]))
    e = {"kind": "openai", "base_url": "http://x/v1", "model": "m", "key_optional": True}
    with pytest.raises(spike.RunError, match="output limit"):
        spike.converse(e, {"system": "s", "turns": ["a", "b"]})


def test_ollama_refuses_a_prompt_that_might_not_fit(monkeypatch):
    monkeypatch.setattr(spike.requests, "post", lambda *a, **k: pytest.fail("sent a prompt that could be cut"))
    e = {"kind": "ollama", "model": "qwen", "options": {"num_ctx": 1000, "num_predict": 500}}
    with pytest.raises(spike.RunError, match="exceeds num_ctx"):
        spike.call_ollama(e, "x" * 4000, [{"role": "user", "content": "hi"}])


def test_ollama_requires_an_explicit_context_window():
    with pytest.raises(RuntimeError, match="num_ctx"):
        spike.call_ollama({"kind": "ollama", "model": "q", "options": {}}, "s", [{"role": "user", "content": "x"}])


def test_ollama_sends_num_ctx_and_reads_counts(monkeypatch):
    data = {"model": "qwen3.6:35b-a3b", "message": {"content": "Flag", "thinking": "abc"}, "done_reason": "stop",
            "prompt_eval_count": 50, "eval_count": 20, "load_duration": 2e9, "prompt_eval_duration": 1e9}
    seen = []
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(200, data)], seen))
    e = {"kind": "ollama", "model": "qwen3.6:35b-a3b", "options": {"num_ctx": 4096, "num_predict": 100},
         "price": {"input": 0, "output": 0}}
    r = spike.call_ollama(e, "sys", [{"role": "user", "content": "hi"}])
    assert seen[0]["url"].endswith("/api/chat") and seen[0]["json"]["options"]["num_ctx"] == 4096
    assert seen[0]["json"]["stream"] is False
    assert (r["text"], r["thinking_chars"], r["input_tokens"], r["output_tokens"], r["cost_usd"]) == \
        ("Flag", 3, 50, 20, 0.0)


def test_ollama_flags_a_full_window(monkeypatch):
    data = {"model": "q", "message": {"content": "x"}, "done_reason": "stop",
            "prompt_eval_count": 4000, "eval_count": 96}
    monkeypatch.setattr(spike.requests, "post", fake_post([FakeResponse(200, data)]))
    e = {"kind": "ollama", "model": "q", "options": {"num_ctx": 4096, "num_predict": 100}}
    with pytest.raises(spike.RunError, match="may have cut"):
        spike.call_ollama(e, "s", [{"role": "user", "content": "x"}])


# ---------------------------------------------------------------- Claude through the API (fake SDK)

class FakeBlock:
    def __init__(self, type, **kw):
        self.type = type
        self.__dict__.update(kw)


class FakeAnthropic:
    """Stands in for anthropic.Anthropic and records every request."""
    instances: list = []

    def __init__(self, api_key=None, base_url=None, max_retries=None, timeout=None):
        self.api_key, self.base_url, self.calls, self.replies = api_key, base_url, [], []
        self.messages = self
        FakeAnthropic.instances.append(self)

    @contextlib.contextmanager
    def stream(self, **kw):
        self.calls.append(json.loads(json.dumps(kw)))
        reply = self.replies.pop(0) if self.replies else ("end_turn", f"answer {len(self.calls)}")
        stop, text = reply
        usage = types.SimpleNamespace(input_tokens=10, cache_creation_input_tokens=1000,
                                      cache_read_input_tokens=0, output_tokens=50)
        msg = types.SimpleNamespace(content=[FakeBlock("thinking", thinking=""), FakeBlock("text", text=text)],
                                    usage=usage, model=kw["model"], stop_reason=stop,
                                    stop_details=types.SimpleNamespace(category="cyber") if stop == "refusal" else None)
        yield types.SimpleNamespace(get_final_message=lambda: msg)


@pytest.fixture
def fake_sdk(monkeypatch):
    FakeAnthropic.instances = []
    monkeypatch.setitem(sys.modules, "anthropic", types.SimpleNamespace(Anthropic=FakeAnthropic))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-not-real")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:9/some-local-proxy")  # what the desktop app sets
    return FakeAnthropic


OPUS = {"kind": "anthropic", "model": "claude-opus-5-5", "key_env": "ANTHROPIC_API_KEY", "cache": True,
        "params": {"max_tokens": 32000}, "price": {"input": 4.0, "output": 20.0, "cache_read": 0.2, "cache_write": 5.0}}


def test_claude_goes_to_the_real_api_with_the_key_from_the_secrets(fake_sdk):
    turns = spike.converse(OPUS, {"system": "SYS", "turns": ["first", "second"]})
    c = fake_sdk.instances[0]
    assert c.base_url == "https://api.anthropic.com"  # not the ANTHROPIC_BASE_URL in the environment
    assert c.api_key == "sk-ant-test-not-real"
    first, second = c.calls
    assert first["system"] == "SYS" and first["model"] == "claude-opus-5-5" and first["max_tokens"] == 32000
    assert first["cache_control"] == {"type": "ephemeral"}
    assert "temperature" not in first and "thinking" not in first  # API defaults, as the protocol says
    assert second["messages"] == [{"role": "user", "content": "first"},
                                  {"role": "assistant", "content": "answer 1"},
                                  {"role": "user", "content": "second"}]  # turn 1's text only, like every engine
    assert [t["text"] for t in turns] == ["answer 1", "answer 2"]
    assert turns[0]["input_tokens"] == 1010 and turns[0]["cache_write_tokens"] == 1000
    assert turns[0]["cost_usd"] == pytest.approx((10 * 4.0 + 1000 * 5.0 + 50 * 20.0) / 1e6)


def test_claude_refusal_fails_the_run_and_skips_turn_two(fake_sdk, monkeypatch):
    orig = fake_sdk.__init__

    def init(self, **kw):
        orig(self, **kw)
        self.replies = [("refusal", "")]
    monkeypatch.setattr(fake_sdk, "__init__", init)
    with pytest.raises(spike.RunError, match="refused"):
        spike.converse(OPUS, {"system": "S", "turns": ["a", "b"]})
    assert len(fake_sdk.instances[0].calls) == 1


def test_claude_hitting_max_tokens_fails_the_run(fake_sdk, monkeypatch):
    orig = fake_sdk.__init__

    def init(self, **kw):
        orig(self, **kw)
        self.replies = [("max_tokens", "cut off mid")]
    monkeypatch.setattr(fake_sdk, "__init__", init)
    with pytest.raises(spike.RunError, match="output limit"):
        spike.converse(OPUS, {"system": "S", "turns": ["a", "b"]})


def test_claude_without_a_key_fails_before_any_call(fake_sdk, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(RuntimeError, match="missing key ANTHROPIC_API_KEY"):
        spike.converse(OPUS, {"system": "S", "turns": ["a"]})
    assert fake_sdk.instances == []


# ---------------------------------------------------------------- secrets and cost

def test_secrets_file_loads_without_overriding_the_environment(ws, monkeypatch):
    (ws / ".secrets.env").write_text("﻿# comment\nMISTRAL_API_KEY='from-file'\nLOCAL_MODEL=\n"
                                     "ANTHROPIC_API_KEY=file-key\n", encoding="utf-8")
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    monkeypatch.delenv("LOCAL_MODEL", raising=False)
    spike.load_secrets()
    assert spike.os.environ["MISTRAL_API_KEY"] == "from-file"
    assert spike.os.environ["ANTHROPIC_API_KEY"] == "env-key"
    assert "LOCAL_MODEL" not in spike.os.environ  # an empty value is not a value


def test_list_never_prints_a_key(ws, monkeypatch, capsys):
    secret = "sk-ant-THIS-MUST-NOT-APPEAR"
    (ws / "engines.json").write_text(json.dumps({"opus": OPUS}), encoding="utf-8")
    monkeypatch.setattr(spike, "ENGINES_JSON", ws / "engines.json")
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    spike.cmd_list(None)
    out = capsys.readouterr().out
    assert secret not in out and "set" in out


def test_cost_of_handles_unknown_prices():
    assert spike.cost_of({"price": {"input": None, "output": None}}, 1, 0, 0, 1) is None
    assert spike.cost_of({}, 1, 0, 0, 1) is None
    assert spike.cost_of({"price": {"input": 2.0, "output": 10.0}}, 1e6, 0, 1e6, 1e6) == pytest.approx(14.0)


# ---------------------------------------------------------------- run bookkeeping

def test_failed_run_is_recorded_and_cleared_on_success(ws, monkeypatch):
    calls = []

    def converse(e, p):
        calls.append(1)
        if len(calls) == 1:
            raise spike.RunError("turn 1: refused")
        return [spike.turn_record("ok", seconds=1.0, cost_usd=0.5, stop="stop")] * 2
    monkeypatch.setattr(spike, "converse", converse)
    e = {"kind": "openai", "model": "m", "base_url": "http://x/v1"}
    assert spike.one_run("m", e, "C0", "v1", 1).startswith("FAIL")
    assert (ws / "runs" / "failed" / "m__C0__v1__r1.txt").exists()
    assert spike.one_run("m", e, "C0", "v1", 1).startswith("ok")
    assert not (ws / "runs" / "failed" / "m__C0__v1__r1.txt").exists()
    assert spike.one_run("m", e, "C0", "v1", 1).startswith("skip")
    rec = json.loads((ws / "runs" / "raw" / "m__C0__v1__r1.json").read_text(encoding="utf-8"))
    assert rec["prompt_sha256"] == spike.sha(spike.prompt_blob(spike.build("C0", "v1")))


def test_budget_holds_new_runs_once_spent(ws, monkeypatch):
    monkeypatch.setattr(spike, "converse",
                        lambda e, p: [spike.turn_record("ok", seconds=1.0, cost_usd=1.0, stop="stop")] * 2)
    e = {"kind": "openai", "model": "m", "base_url": "http://x/v1"}
    b = spike.Budget(1.5)
    assert spike.one_run("m", e, "C0", "v1", 1, b).startswith("ok")  # spends $2
    assert spike.one_run("m", e, "C0", "v1", 2, b).startswith("held")


def test_a_saved_run_from_another_model_or_prompt_is_never_reused_silently(ws, monkeypatch):
    monkeypatch.setattr(spike, "converse", lambda *a: pytest.fail("a model was called"))
    raw_run(ws, "mistral", "C0", "v1", 1, model="mistral-large-latest")
    pinned = {"kind": "openai", "model": "mistral-large-2611", "base_url": "http://x/v1"}
    assert spike.one_run("mistral", pinned, "C0", "v1", 1).startswith("STALE")
    same = {"kind": "openai", "model": "mistral-large-latest", "base_url": "http://x/v1"}
    assert spike.one_run("mistral", same, "C0", "v1", 1).startswith("skip")


def test_a_half_written_run_is_run_again(ws, monkeypatch):
    (ws / "runs" / "raw" / "m__C0__v1__r1.json").write_text('{"run_id": "m__C0__v1__r1", "tur', encoding="utf-8")
    monkeypatch.setattr(spike, "converse", lambda e, p: [spike.turn_record("ok", seconds=1.0, stop="stop")] * 2)
    assert spike.one_run("m", {"kind": "openai", "model": "m", "base_url": "http://x/v1"}, "C0", "v1", 1).startswith("ok")
    assert not list((ws / "runs" / "raw").glob("*.tmp"))


def test_the_budget_counts_what_a_failed_run_spent(ws, monkeypatch):
    spent = [spike.turn_record("half", seconds=1.0, cost_usd=0.75, stop="length")]

    def converse(e, p):
        raise spike.RunError("turn 1: cut at the output limit", spent)
    monkeypatch.setattr(spike, "converse", converse)
    b = spike.Budget(10)
    spike.one_run("m", {"kind": "openai", "model": "m", "base_url": "http://x/v1"}, "C0", "v1", 1, b)
    assert b.spent == pytest.approx(0.75)


@pytest.mark.parametrize("stop", ["model_length", "model_context_window_exceeded", "pause_turn", None])
def test_only_a_clean_stop_is_scored(stop):
    rec = spike.turn_record("some text", stop={"model_length": "length"}.get(stop, stop))
    with pytest.raises(spike.RunError):
        spike.require_ok(rec, "turn 1")


def test_error_messages_lose_any_loaded_key(monkeypatch):
    monkeypatch.setenv("MISTRAL_API_KEY", "abcdefghijklmnopqrstuvwxyz123456")
    msg = spike.redact("HTTP 401: invalid key abcdefghijklmnopqrstuvwxyz123456 and sk-ant-api03-SECRETSECRETSECRET")
    assert "abcdefghijklmnop" not in msg and "SECRETSECRET" not in msg


def test_parse_key_never_drops_a_row_silently(tmp_path):
    f = tmp_path / "answer-key.md"
    f.write_text(KEY_MD + "| K05 | V2 | G/C | a | b | v2 | |\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="doesn't parse"):
        spike.parse_key(f)
    f.write_text(KEY_MD.replace("| v1, v2, v3 | |", "| v1-v3 | |", 1), encoding="utf-8")
    with pytest.raises(SystemExit, match="present in"):
        spike.parse_key(f)


def test_check_verdict_needs_every_flag_placed_once():
    ids = {"K01", "K02"}
    v = verdict(["K01"], ["correct"])
    v["flags"].append({"id": "F9", "where": "x", "problem": "y"})  # neither matched nor classed
    with pytest.raises(ValueError, match="neither matched nor classed"):
        spike.check_verdict(v, ids)
    v = verdict(["K01"], ["wrong"])
    v["unmatched"].append({"flag": "F1", "class": "taste", "why": "z"})  # F1 is matched and unmatched
    with pytest.raises(ValueError, match="both matched and unmatched"):
        spike.check_verdict(v, ids)
    ok = spike.check_verdict(verdict(["K01"]), ids)
    assert {m["key"] for m in ok["matches"]} == ids  # a key point left out counts as matched by nothing


def test_report_leaves_out_mixed_models_stale_verdicts_and_old_prompts(ws, capsys):
    for rep in (1, 2):
        write_verdict(ws, raw_run(ws, "mistral", "C0", "v1", rep, model="mistral-large-latest"), verdict([]))
    write_verdict(ws, raw_run(ws, "mistral", "C0", "v1", 3, model="mistral-large-2611"), verdict([]))
    write_verdict(ws, raw_run(ws, "opus", "C0", "v1", 1), verdict([]), key_sha="0" * 64)
    rid = raw_run(ws, "opus", "C0", "v1", 2)
    rec = json.loads((ws / "runs" / "raw" / f"{rid}.json").read_text(encoding="utf-8"))
    rec["prompt_sha256"] = "f" * 64
    (ws / "runs" / "raw" / f"{rid}.json").write_text(json.dumps(rec), encoding="utf-8")
    write_verdict(ws, rid, verdict([]))
    cells, notes = spike.load_cells(spike.parse_key(), "judge-sonnet", "judge")
    assert cells == {}
    text = " ".join(notes)
    assert "mixes models" in text and "another key" in text and "another prompt" in text


def test_run_refuses_uncommitted_harness_code(ws, monkeypatch):
    monkeypatch.setattr(spike, "verify_fingerprints", lambda *a: [])
    monkeypatch.setattr(spike, "harness_commit", lambda: ("abc123", True))
    monkeypatch.setattr(spike, "converse", lambda *a: pytest.fail("a model was called"))
    args = types.SimpleNamespace(no_verify=False, allow_dirty=False, engine=None, condition=None, stage=None,
                                 repeats=1, budget=None)
    with pytest.raises(SystemExit, match="uncommitted"):
        spike.cmd_run(args)


def test_judge_and_report_can_take_one_group(ws, monkeypatch):
    monkeypatch.setattr(spike, "config", lambda: CFG)
    for eng in ("opus", "sonnet", "qwen"):
        raw_run(ws, eng, "C0", "v1", 1)
    assert [p.name.split("__")[0] for p in spike.raw_runs(["claude"])] == ["opus", "sonnet"]
    assert len(spike.raw_runs(None)) == 3


def test_prompt_files_are_written_with_the_hashed_bytes(ws, capsys):
    spike.cmd_prompts(None)
    f = ws / "runs" / "prompts" / "C2-v1.json"
    assert spike.sha_file(f) == spike.sha(spike.prompt_blob(spike.build("C2", "v1")))
    assert b"\r\n" not in f.read_bytes()


# ---------------------------------------------------------------- judging and the report

def test_parse_key_reads_ids_rounds_tags_and_presence(ws):
    key = spike.parse_key()
    assert [k["id"] for k in key] == ["K01", "K02", "K03", "K04"]
    assert key[1]["raised"] == "v1" and key[1]["present"] == ["v1", "v2"] and key[3]["tag"] == "G"


def test_check_verdict_rejects_invented_keys_and_flags():
    ids = {"K01", "K02"}
    spike.check_verdict(verdict(["K01"], ["correct"]), ids)
    with pytest.raises(ValueError, match="unknown key"):
        spike.check_verdict(verdict(["K99"]), ids)
    bad = verdict(["K01"])
    bad["matches"][0]["flags"] = ["F9"]
    with pytest.raises(ValueError, match="undefined flags"):
        spike.check_verdict(bad, ids)
    with pytest.raises(ValueError):
        spike.check_verdict({"flags": []}, ids)


def test_score_counts_raised_early_and_carry(ws):
    key = spike.parse_key()
    rec = {"stage": "v2"}
    s = spike.score(rec, verdict(["K02", "K03", "K04"], ["correct", "wrong", "taste", "taste"]), key)
    assert (s["K"], s["N"]) == (1, 1)  # K03 is the one raised at v2
    assert s["carry"] == 1 and s["early"] == 1  # K02 carried from v1, K04 raised later at v3
    assert (s["E"], s["W"], s["T"]) == (1, 1, 2)
    human = spike.score(rec, verdict(["K03"]), key, caught=set())
    assert human["K"] == 0  # the people's matches replace the judge's


def test_majority_needs_two_of_three():
    runs = [{"caught": ["K01", "K02"]}, {"caught": ["K01"]}, {"caught": ["K02", "K03"]}]
    assert spike.majority(runs, ["K01", "K02", "K03"]) == {"K01", "K02"}


def test_report_keeps_key_ids_out_of_the_public_copy(ws, capsys):
    for rep, caught in enumerate([["K01", "K02"], ["K01"], ["K01", "K02"]], 1):
        write_verdict(ws, raw_run(ws, "opus", "C2", "v1", rep), verdict(caught, ["correct"]))
    for rep in (1, 2, 3):
        write_verdict(ws, raw_run(ws, "opus", "C0", "v1", rep), verdict([], ["wrong"]))
    args = types.SimpleNamespace(judge="judge-sonnet", source="judge", build_engine="opus", engine=None)
    spike.cmd_report(args)
    private = (ws / "results.md").read_text(encoding="utf-8")
    public = (ws / "public" / "results-public.md").read_text(encoding="utf-8")
    log = (ws / "public" / "runs-public.csv").read_text(encoding="utf-8").splitlines()
    assert len(log) == 7 and log[0].startswith("run_id,engine,model")  # header + six runs
    assert any(l.startswith("opus__C2__v1__r1,") for l in log)
    assert not __import__("re").search(r"\bK\d+\b", "\n".join(log))
    assert "F1 something" not in "\n".join(log) and "F1 something" not in public  # no review text in public
    assert public.startswith("# Advisor spike results (public: counts only)")
    assert "K01, K02" in private
    assert not __import__("re").search(r"\bK\d+\b", public)
    assert "| opus | C2 | 2 / 2 | 0 | 0% | 1 / 1 |" in public
    assert "C2 | v1 | 3 | 2 / 2 | 2, 1, 2 |" in private
    # the decision table has as many columns as the pooled one; it must survive whole in the public copy
    assert "| Engine | Route | v1 C/W vs stand-in | v2 | v3 | Same flags in | Flags half |" in public
    decision_row = [l for l in public.splitlines() if l.startswith("| opus | C0 |")][-1]
    assert decision_row.endswith("| 0 of 1 | open |")


def test_public_copy_refuses_a_key_id():
    with pytest.raises(RuntimeError, match="key-point ID"):
        spike.public_safe(["| opus | C2 | 1 / 2 |", "caught K07"])


def test_read_sheet_handles_excel_semicolons_and_several_flags(tmp_path):
    f = tmp_path / "sheet-v1.csv"
    f.write_text('﻿key;L01;L02\nK01;F1 F3;\nK02;;"F2,F4"\ndone;x;x\n\n', encoding="utf-8")
    assert spike.read_sheet(f)[0] == {"L01": {"K01"}, "L02": {"K02"}}
    f.write_text('key,L01,L02,\nK01,"F1,F3",,\nK02,,F2,\ndone,x,x,\n', encoding="utf-8")  # stray empty column
    assert spike.read_sheet(f)[0] == {"L01": {"K01"}, "L02": {"K02"}}
    f.write_bytes("key;L01\nK01;F2 (revisé)\ndone;x\n".encode("cp1252"))  # Excel's Windows-1252
    assert spike.read_sheet(f)[0] == {"L01": {"K01"}}


def test_read_sheet_leaves_out_lists_not_marked_done_and_non_numbers(tmp_path):
    f = tmp_path / "sheet-v1.csv"
    f.write_text("key,L01,L02\nK01,no,F1\nK02,-,\ndone,x,\n", encoding="utf-8")
    got, warnings = spike.read_sheet(f)
    assert got == {"L01": set()}  # L02 isn't marked done, so it is unscored, not zero catches
    assert any("L02: not marked done" in w for w in warnings)
    assert any("'no' has no flag number" in w for w in warnings)


def test_decision_rules_follow_protocol_v2(ws):
    key = spike.parse_key()
    s = lambda K, E, W: {"K": K, "E": E, "W": W, "caught": ["K01", "K02"][:K]}  # noqa: E731
    stand = [s(2, 1, 0)] * 3
    cells = {("opus", "C2", "v1"): stand,
             ("opus", "C1", "v1"): [s(1, 1, 1)] * 3,  # C 2 vs 3, W 1 vs 0: same flags
             ("opus", "C0", "v1"): [s(0, 0, 2)] * 3}  # C 0 vs 3: differs
    text = "\n".join(spike.decision_lines(cells, key, "opus"))
    assert "Falsifier 3:** not read yet" in text  # v2 and v3 aren't scored
    assert "| opus | C1 | 2.00/1.00 vs 3.00/0.00 same" in text
    assert "| opus | C0 | 0.00/2.00 vs 3.00/0.00 differs" in text


def test_same_flags_rule_is_exact_at_the_tolerance_with_thirds():
    """E is a mean of three; 1 + 1/3 against 2 + 1/3 sits exactly on 'C(route) >= C(stand-in) - 1'."""
    key = [{"id": "K01", "raised": "v1", "tag": "C", "present": ["v1"]},
           {"id": "K02", "raised": "v1", "tag": "C", "present": ["v1"]}]
    run = lambda K, E, W: {"K": K, "E": E, "W": W, "caught": ["K01", "K02"][:K]}  # noqa: E731
    stand = [run(2, 1, 0), run(2, 0, 0), run(2, 0, 0)]  # K 2, E mean 1/3
    route = [run(1, 1, 1), run(1, 0, 0), run(1, 0, 0)]  # K 1, E mean 1/3, W mean 1/3
    text = "\n".join(spike.decision_lines({("opus", "C2", "v1"): stand, ("glm", "C1", "v1"): route}, key, "opus"))
    assert "| glm | C1 | 1.33/0.33 vs 2.33/0.00 same" in text


def test_flags_half_is_decided_once_it_can_no_longer_be_reached():
    key = [{"id": "K01", "raised": s, "tag": "C", "present": [s]} for s in ("v1", "v2", "v3")]
    hit = lambda: {"K": 1, "E": 0, "W": 0, "caught": ["K01"]}  # noqa: E731
    miss = lambda: {"K": 0, "E": 0, "W": 5, "caught": []}  # noqa: E731
    cells = {("opus", "C2", s): [hit()] * 3 for s in ("v1", "v2", "v3")}
    cells |= {("glm", "C0", "v1"): [miss()] * 3, ("glm", "C0", "v2"): [miss()] * 3}
    text = "\n".join(spike.decision_lines(cells, key, "opus"))
    assert "| 0 of 2 | does not hold |" in text  # 2 of 3 can't be reached with one round left


def test_incomplete_cells_are_not_read_by_the_decision_rules():
    key = [{"id": "K01", "raised": "v1", "tag": "C", "present": ["v1"]}]
    cells = {("opus", "C2", "v1"): [{"K": 1, "E": 0, "W": 0, "caught": ["K01"]}] * 2}
    text = "\n".join(spike.decision_lines(cells, key, "opus"))
    assert "Cells not read yet" in text and "opus/C2/v1 (2)" in text


def test_falsifier_3_reads_the_pooled_miss_rate(ws):
    key = spike.parse_key()
    cells = {("opus", "C2", "v1"): [{"K": 1, "E": 0, "W": 0, "caught": ["K01"]}] * 3,
             ("opus", "C2", "v2"): [{"K": 0, "E": 0, "W": 0, "caught": []}] * 3,
             ("opus", "C2", "v3"): [{"K": 0, "E": 0, "W": 0, "caught": []}] * 3}
    text = "\n".join(spike.decision_lines(cells, key, "opus"))
    assert "caught 1 of 4, miss rate 75%" in text and "**holds**" in text


# ---------------------------------------------------------------- human sheets

def make_sheets(ws, runs):
    for i, (engine, rep) in enumerate(runs):
        raw_run(ws, engine, "C1", "v1", rep, text=f"review {i}")
    spike.cmd_sheets(types.SimpleNamespace(force=False))
    return json.loads((ws / "scoring" / "map.json").read_text(encoding="utf-8"))


def test_sheets_are_blind_and_refuse_to_renumber(ws):
    codes = make_sheets(ws, [("opus", 1), ("glm", 1)])
    sheet = (ws / "scoring" / "human" / "sheet-v1.md").read_text(encoding="utf-8")
    assert "opus" not in sheet and "glm" not in sheet and "K01" in sheet
    assert set(codes) == {"V1-L01", "V1-L02"}
    raw_run(ws, "mistral", "C1", "v1", 1)
    with pytest.raises(SystemExit):
        spike.cmd_sheets(types.SimpleNamespace(force=False))


def test_agree_combines_two_scorers_and_compares_with_the_judge(ws, capsys):
    codes = make_sheets(ws, [("opus", 1), ("glm", 1)])
    by_run = {v: k.split("-")[1] for k, v in codes.items()}
    opus_col, glm_col = by_run["opus__C1__v1__r1"], by_run["glm__C1__v1__r1"]
    head = f"key,{opus_col},{glm_col}" if opus_col < glm_col else f"key,{glm_col},{opus_col}"
    cols = head.split(",")[1:]

    def sheet(folder, marks):  # marks: {(key, col): "F1"}
        d = ws / folder
        d.mkdir()
        rows = [head] + [",".join([k] + [marks.get((k, c), "") for c in cols]) for k in ("K01", "K02", "K03", "K04")]
        rows.append(",".join(["done"] + ["x"] * len(cols)))
        (d / "sheet-v1.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        return d

    a = sheet("adri", {("K01", opus_col): "F1", ("K02", opus_col): "F2"})
    b = sheet("kristian", {("K01", opus_col): "F1"})  # disagrees on K02
    write_verdict(ws, "opus__C1__v1__r1", verdict(["K01", "K02"]))
    write_verdict(ws, "glm__C1__v1__r1", verdict([]))
    spike.cmd_agree(types.SimpleNamespace(scorers=[str(a), str(b)], judge="judge-sonnet", one=False))
    out = capsys.readouterr().out
    combined = json.loads((ws / "scoring" / "human" / "combined.json").read_text(encoding="utf-8"))["runs"]
    assert combined["opus__C1__v1__r1"] == ["K01"]  # a disagreement counts as not matched
    assert combined["glm__C1__v1__r1"] == []
    assert "1 of 8 points differ" in out  # scorer vs scorer, and judge vs the combined people
    assert out.count("1 of 8") == 2
    assert "opus: 1 of 4 differ" in out and "glm: 0 of 4 differ" in out  # agreement per engine
    with pytest.raises(SystemExit):  # the protocol needs both people
        spike.cmd_agree(types.SimpleNamespace(scorers=[str(a)], judge="judge-sonnet", one=False))
