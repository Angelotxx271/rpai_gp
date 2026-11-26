"""The public side: the cookie, resume codes, the CSRF header, topics, errors in the shape the page expects."""


def test_no_cookie_means_onboarding(stack):
    assert stack.web.get("/api/me").json() == {"student": None}
    r = stack.web.get("/api/thread")
    assert r.status_code == 401 and r.json()["error"] == "no_student"


def test_state_changing_calls_need_the_page_header(stack):
    r = stack.web.post("/api/start", json={"topic": "A topic that is long enough"})
    assert r.status_code == 403


def test_start_sets_an_httponly_cookie_and_returns_a_resume_code(stack):
    r = stack.post("/api/start", json={"topic": "A topic that is long enough", "alias": "Sam"})
    body = r.json()
    assert body["student"]["alias"] == "Sam" and len(body["resume_code"]) == 19
    assert "httponly" in r.headers["set-cookie"].lower() and "samesite=lax" in r.headers["set-cookie"].lower()


def test_the_resume_code_restores_the_thread_on_another_device(stack):
    code = stack.start()["resume_code"]
    stack.web.cookies.clear()
    assert stack.web.get("/api/me").json() == {"student": None}
    r = stack.post("/api/resume", json={"code": code.lower().replace("-", " ")})
    assert r.status_code == 200 and r.json()["resume_code"] == code
    assert stack.web.get("/api/me").json()["student"]["topic"]


def test_a_wrong_resume_code_is_refused_and_tries_are_limited(stack, monkeypatch):
    r = stack.post("/api/resume", json={"code": "AAAA-BBBB-CCCC-DDDD"})
    assert r.status_code == 404 and r.json()["error"] == "unknown_code"


def test_the_topic_can_change(stack):
    stack.start()
    r = stack.web.patch("/api/me", json={"topic": "A new topic, also long enough"}, headers={"X-TFGPT": "1"})
    assert r.json()["student"]["topic"] == "A new topic, also long enough"


def test_a_too_short_topic_is_refused(stack):
    assert stack.post("/api/start", json={"topic": "short"}).status_code == 422


def test_meta_reports_version_and_limits(stack):
    body = stack.web.get("/api/meta").json()
    assert body["version"] == "test123" and body["session_minutes"] == 30


def test_the_engine_list_shows_model_and_vendor(stack):
    stack.start(engine=None)
    names = {e["name"]: e for e in stack.web.get("/api/engines").json()["engines"]}
    assert names["fake-a"]["label"] == "Fake A" and names["fake-a"]["vendor"] == "Test Vendor 1"
    assert stack.post("/api/engine", json={"name": "fake-a"}).json() == {"chosen": "fake-a"}
    assert stack.web.get("/api/engines").json()["chosen"] == "fake-a"


def test_the_pack_loader_is_hidden_without_the_admin_token(stack, monkeypatch):
    files = {"file": ("pack.md", "# Rules" + chr(10) + "A rule that is long enough to count as a document. " * 5)}
    assert stack.post("/api/admin/pack", files=files).status_code == 404  # no ADMIN_TOKEN set: no loader at all
    monkeypatch.setenv("ADMIN_TOKEN", "a-long-admin-token-for-tests")
    wrong = stack.web.post("/api/admin/pack", files=files, headers={"X-TFGPT": "1", "X-Admin-Token": "wrong"})
    assert wrong.status_code == 404
    r = stack.web.post("/api/admin/pack", files=files,
                       headers={"X-TFGPT": "1", "X-Admin-Token": "a-long-admin-token-for-tests", "X-Pack-Title": "Test"})
    assert r.status_code == 200 and r.json()["sections"] == 1
    assert stack.advisor.get("/healthz").json()["pack"] == r.json()["sha12"]


def test_woff2_fonts_serve_with_font_woff2_content_type(stack):
    r = stack.web.get("/fonts/newsreader-latin-500-normal.woff2")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("font/woff2")


def test_brand_logo_and_favicon_are_served(stack):
    logo = stack.web.get("/logo.png")
    assert logo.status_code == 200 and logo.headers["content-type"].startswith("image/png")
    fav = stack.web.get("/favicon.svg")
    assert fav.status_code == 200 and "image/svg+xml" in fav.headers["content-type"]


def test_resume_code_input_accepts_full_19_char_code_and_page_meets_a11y_csp(stack):
    r = stack.web.get("/")
    assert r.status_code == 200
    assert "default-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-frame-options"] == "DENY"
    html = r.text
    assert 'id="resumeCode"' in html
    assert 'maxlength="14"' not in html
    assert 'placeholder="XXXX-XXXX-XXXX-XXXX"' in html
    assert 'aria-live="polite"' in html and 'role="tablist"' in html and 'role="log"' in html
    assert "<script>" not in html  # strict CSP: external /app.js only

