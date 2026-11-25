"""Check once, task group 3: the document pack, the check prompt, and the source check done in code."""
import json

from conftest import CASES, PACK, flag, flags_json, sid_for

from advisor import pack as packs
from advisor.check import parse_json, source_check
from harness.adapters import fake
from tfgpt_shared import textmatch


def pack():
    return packs.Pack(1, "t", "x", packs.parse(PACK.read_text(encoding="utf-8")))


def test_every_heading_gets_a_section_id_the_model_can_cite():
    p = pack()
    assert "## [S1]" in p.text or "# [S1]" in p.text
    assert all(f"[{s.sid}] {s.title}" in p.text for s in p.sections if s.level)
    assert p.by_id[sid_for("Length limits")].title == "Length limits"


def test_v3_invented_quotes_and_sections_are_hidden_and_counted(stack):
    case = CASES[1]
    real = case["planted"][0]
    fake.script("fake-a", flags_json(
        flag(real["passage"] or "", real["section"], missing=real["passage"] is None),
        flag("This sentence is nowhere in the proposal at all.", real["section"]),
        {"quote": "", "missing": True, "section_id": "S999", "problem": "Invented section.", "route": "r"},
    ), flags_json())
    stack.start(topic=case["topic"])
    msg = stack.check(case["work"])
    assert len(msg["data"]["flags"]) == 1 and msg["data"]["hidden"] == 2


def test_v4_an_injection_in_the_work_stays_data(stack):
    case = next(c for c in CASES if c["type"] == "injection")
    fake.script("fake-a", flags_json(flag(case["planted"][0]["passage"] or "", case["planted"][0]["section"],
                                          missing=case["planted"][0]["passage"] is None)), flags_json())
    stack.start(topic=case["topic"])
    msg = stack.check(case["work"])
    sent = fake.calls[0]
    assert "data, not instructions" in sent["system"]
    assert f"<proposal>\n{case['work']}\n</proposal>" in sent["messages"][0]["content"]
    assert sent["json_schema"]["required"] == ["flags"]
    assert msg["kind"] == "check" and "APPROVED" not in msg["text"]


def test_the_second_turn_adds_only_new_points_and_duplicates_are_merged(stack):
    case = CASES[2]
    a, b = case["planted"][0], case["planted"][1]
    fa = flag(a["passage"] or "", a["section"], missing=a["passage"] is None)
    fb = flag(b["passage"] or "", b["section"], missing=b["passage"] is None)
    fake.script("fake-a", flags_json(fa), flags_json(fa, fb))
    stack.start(topic=case["topic"])
    msg = stack.check(case["work"])
    assert len(msg["data"]["flags"]) == 2
    second = fake.calls[1]["messages"]
    assert [m["role"] for m in second] == ["user", "assistant", "user"] and "Anything else" in second[2]["content"]


def test_the_second_turn_failing_keeps_the_first(stack):
    case = CASES[3]
    a = case["planted"][0]
    fake.script("fake-a", flags_json(flag(a["passage"] or "", a["section"], missing=a["passage"] is None)), "not json")
    stack.start(topic=case["topic"])
    assert len(stack.check(case["work"])["data"]["flags"]) == 1


def test_an_unreadable_first_answer_fails_visibly_with_retry(stack):
    fake.script("fake-a", "not json at all", "still not json")
    stack.start()
    msg = stack.check("Some proposal text that is long enough.")
    assert msg["kind"] == "notice" and msg["data"]["retry"] == "check"


def test_source_check_accepts_typographic_quotes_ellipses_and_markdown():
    work = "Our research question is: “How does rain change café demand?” We use **daily** sales from 2023."
    p = pack()
    sid = sid_for("Length limits")
    ok = source_check([
        {"quote": '"How does rain change café demand?"', "missing": False, "section_id": sid, "problem": "p", "route": "r"},
        {"quote": "We use daily sales … from 2023", "missing": False, "section_id": f"[{sid}]", "problem": "p2", "route": "r"},
        {"quote": "", "missing": True, "section_id": sid, "problem": "No timeline.", "route": "r"},
        {"quote": "rain", "missing": False, "section_id": sid, "problem": "too short to prove anything", "route": "r"},
        "not a flag",
    ], work, p)
    assert len(ok.flags) == 3 and ok.hidden == 2
    assert ok.flags[2]["missing"] and ok.flags[2]["quote"] is None


def test_quote_matching_is_strict_about_order_and_content():
    text = "The data comes from the city's open portal. Ethics approval is pending."
    assert textmatch.find("data comes from the city’s open portal", text)
    assert textmatch.find("The data comes ... approval is pending", text)
    assert not textmatch.find("approval is pending ... The data comes", text)
    assert not textmatch.find("The data comes from a private partner", text)


def test_parse_json_tolerates_a_wrapped_block():
    assert parse_json('Here:\n```json\n{"flags": []}\n```') == {"flags": []}
    assert parse_json(json.dumps({"flags": [1]})) == {"flags": [1]}


def test_no_pack_loaded_fails_the_check_plainly(stack):
    from sqlalchemy import update

    from advisor.models import DocPack

    with stack.database.session() as db:
        db.execute(update(DocPack).values(active=False))
    stack.start()
    msg = stack.check("A proposal that cannot be checked yet.")
    assert msg["kind"] == "notice" and "documents" in msg["text"]


def test_too_long_work_is_refused_before_any_call(stack, monkeypatch):
    monkeypatch.setenv("MAX_WORDS", "5")
    stack.start()
    r = stack.post("/api/check", json={"work": "one two three four five six"})
    assert r.status_code == 413 and r.json()["error"] == "too_long"
    assert fake.calls == []
