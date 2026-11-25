"""Check again: open flags + revised text → solved, remaining, new; quotes checked in code; dismissed flags left out."""
import json

from conftest import CASES, flag, flags_json

from harness.adapters import fake

RECHECKS = None


def first_check(stack, case):
    a, b = case["planted"][0], case["planted"][1]
    fake.script("fake-a", flags_json(flag(a["passage"] or "", a["section"], missing=a["passage"] is None),
                                     flag(b["passage"] or "", b["section"], missing=b["passage"] is None)), flags_json())
    stack.start(topic=case["topic"])
    msg = stack.check(case["work"])
    return [f["id"] for f in msg["data"]["flags"]]


def recheck_reply(results, new=()):
    return json.dumps({"results": results, "new_flags": list(new)})


def test_v1_one_solved_one_remaining(stack):
    case = CASES[1]
    f1, f2 = first_check(stack, case)
    fake.script("fake-a", recheck_reply([{"flag_id": f1, "status": "solved", "quote": "", "note": "Fixed."},
                                         {"flag_id": f2, "status": "remaining", "quote": "", "note": "Still."}]))
    msg = stack.check(case["work"], kind="recheck")
    d = msg["data"]
    assert [f["id"] for f in d["solved"]] == [f1] and [f["id"] for f in d["remaining"]] == [f2] and d["new"] == []
    assert stack.web.get("/api/thread").json()["open_flags"] == 1


def test_v2_a_new_flag_is_listed_as_new_and_stays_open(stack):
    case = CASES[1]
    f1, f2 = first_check(stack, case)
    third = case["planted"][2] if len(case["planted"]) > 2 else case["planted"][0]
    new = flag(third["passage"] or "", third["section"], problem="A new point.", missing=third["passage"] is None)
    if third is case["planted"][0]:
        new["problem"], new["missing"], new["quote"] = "A new missing element.", True, ""
    fake.script("fake-a", recheck_reply([], [new]))
    d = stack.check(case["work"], kind="recheck")["data"]
    assert len(d["new"]) == 1 and len(d["remaining"]) == 2
    assert stack.web.get("/api/thread").json()["open_flags"] == 3


def test_v3_an_invented_quote_on_a_remaining_flag_is_dropped(stack):
    case = CASES[0]
    f1, f2 = first_check(stack, case)
    before = stack.web.get("/api/thread").json()["messages"][-1]["data"]["flags"][1]["quote"]
    fake.script("fake-a", recheck_reply([{"flag_id": f2, "status": "remaining",
                                          "quote": "A sentence the student never wrote.", "note": "x"}]))
    d = stack.check(case["work"], kind="recheck")["data"]
    remaining = {f["id"]: f for f in d["remaining"]}
    assert remaining[f2]["quote"] == before and "never wrote" not in json.dumps(d)


def test_v4_a_dismissed_flag_is_not_sent_or_listed(stack):
    case = CASES[2]
    f1, f2 = first_check(stack, case)
    r = stack.post(f"/api/flags/{f1}/dismiss")
    assert r.status_code == 200 and r.json()["flag"]["status"] == "dismissed"
    fake.calls.clear()
    fake.script("fake-a", recheck_reply([{"flag_id": f1, "status": "solved", "quote": "", "note": ""}]))
    d = stack.check(case["work"], kind="recheck")["data"]
    sent = fake.calls[0]["messages"][0]["content"]
    assert f'"flag_id": {f1}' not in sent and f'"flag_id": {f2}' in sent
    listed = [f["id"] for k in ("solved", "remaining", "new") for f in d[k]]
    assert f1 not in listed


def test_v5_no_earlier_check_asks_for_a_first_one(stack):
    stack.start()
    r = stack.post("/api/recheck", json={"work": "Some revised work."})
    assert r.status_code == 409 and r.json()["error"] == "no_check_yet"
    assert fake.calls == []


def test_an_unknown_flag_id_from_the_model_is_ignored(stack):
    case = CASES[0]
    f1, f2 = first_check(stack, case)
    fake.script("fake-a", recheck_reply([{"flag_id": 99999, "status": "solved", "quote": "", "note": ""}]))
    d = stack.check(case["work"], kind="recheck")["data"]
    assert d["solved"] == [] and len(d["remaining"]) == 2


def test_dismissing_another_students_flag_is_refused(stack):
    case = CASES[0]
    f1, _ = first_check(stack, case)
    stack.web.cookies.clear()
    stack.start(topic="Somebody else's topic, long enough")
    assert stack.post(f"/api/flags/{f1}/dismiss").status_code == 502
