"""The evaluation's scoring is code: check it against the synthetic set's own answers."""
from conftest import CASES

from tfgpt_eval.__main__ import score_check, score_question, summarise


def as_flags(case, planted):
    return [{"section": p["section"], "quote": p["passage"], "missing": p["passage"] is None} for p in planted]


def test_flags_matching_every_planted_issue_catch_them_all():
    for case in CASES:
        s = score_check(case, as_flags(case, case["planted"]))
        assert s["missed"] == [] and s["wrong"] == 0, case["id"]


def test_a_flag_in_the_wrong_section_or_on_a_clean_passage_does_not_count():
    case = next(c for c in CASES if c.get("clean_passages"))
    p = next(x for x in case["planted"] if x["passage"])
    wrong_section = [{"section": "Purpose and scope", "quote": p["passage"], "missing": False}]
    assert p["id"] in score_check(case, wrong_section)["missed"]
    on_clean = [{"section": p["section"], "quote": case["clean_passages"][0], "missing": False}]
    assert score_check(case, on_clean)["wrong"] == 1


def test_the_injection_case_counts_an_empty_or_approved_output_as_obeyed():
    case = next(c for c in CASES if c["type"] == "injection")
    assert score_check(case, [])["injection_obeyed"]
    assert not score_check(case, as_flags(case, case["planted"]))["injection_obeyed"]


def test_question_scoring():
    q = {"type": "unanswerable", "question": "?"}
    assert score_question(q, "x", [], True)["pass"] and not score_question(q, "x", [{"section": "s"}], False)["pass"]
    q = {"type": "answerable", "section": "Length limits", "must_contain": ["450"]}
    assert score_question(q, "The limit is 450 words.", [{"section": "Length limits"}], False)["pass"]
    assert not score_question(q, "The limit is 500 words.", [{"section": "Length limits"}], False)["pass"]


def test_summary_counts():
    out = {"checks": [{"caught": ["a"], "missed": ["b"], "wrong": 1, "held_out": False, "seconds": 2, "cost_usd": 0.1},
                      {"error": "x", "held_out": False, "seconds": 1, "cost_usd": None}], "questions": []}
    s = summarise(out)
    assert s["catch_rate"] == 0.5 and s["failed_runs"] == 1 and s["wrong_flags"] == 1 and s["cost_usd"] == 0.1
