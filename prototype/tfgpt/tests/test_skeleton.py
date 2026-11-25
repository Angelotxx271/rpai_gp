"""Check once, task group 1: the whole path once, web → advisor → harness (fake engine) → flags on the page."""
from conftest import CASES, flag, flags_json

from harness.adapters import fake


def test_every_service_reports_its_version(stack):
    for client in (stack.web, stack.advisor, stack.harness):
        body = client.get("/healthz").json()
        assert body["ok"] and body["version"] == "test123"


def test_internal_services_refuse_calls_without_the_token(stack):
    assert stack.harness.get("/v1/engines").status_code == 401
    assert stack.advisor.get("/internal/threads/abcdefgh12345678").status_code == 401
    ok = stack.harness.get("/v1/engines", headers={"X-Internal-Token": "test-internal-token"})
    assert ok.status_code == 200


def test_v1_topic_and_pasted_work_come_back_as_flags(stack):
    """check-once V1: two valid flags, each shown with its quote, section title and route."""
    case = CASES[0]
    p1, p2 = case["planted"][0], case["planted"][1]
    script = []
    for p in (p1, p2):
        script.append(flag(p["passage"] or "", p["section"], problem=p["problem"], missing=p["passage"] is None))
    fake.script("fake-a", flags_json(*script), flags_json())
    stack.start(topic=case["topic"])
    msg = stack.check(case["work"])
    assert msg["kind"] == "check"
    flags = msg["data"]["flags"]
    assert len(flags) == 2 and msg["data"]["hidden"] == 0
    for f, p in zip(flags, (p1, p2)):
        assert f["section"] == p["section"] and f["route"]
        if f["quote"]:
            assert f["quote"] in case["work"]
    assert msg["data"]["engine"] == "Fake A · Test Vendor 1"
    thread = stack.web.get("/api/thread").json()
    kinds = [m["kind"] for m in thread["messages"]]
    assert kinds == ["work", "check"] and thread["open_flags"] == 2
    assert "words" in thread["messages"][0]["text"] and case["work"][:40] not in str(thread)  # the work never comes back


def test_the_page_is_served_with_a_strict_content_security_policy(stack):
    r = stack.web.get("/")
    assert r.status_code == 200 and "<script src=\"/app.js\"></script>" in r.text
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"
