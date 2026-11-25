# Web API (browser-facing)

The page talks only to the web service, same origin. Every `POST`/`PATCH` sends the header `X-TFGPT: 1` (the server refuses state-changing requests without it) and `Content-Type: application/json`, except the upload, which is `multipart/form-data` with the same header. The student is identified by an HttpOnly cookie the server sets; the page never sees it.

Errors come back as `{"error": "<code>", "message": "<text for the student>"}` with a 4xx/5xx status. Codes the page must handle: `no_student` (401: show onboarding), `choose_model` (409: open the model picker), `cap_reached` (429: show the message), `no_check_yet` (409), `too_long` (413), `unsupported_file` (415), `upstream` (502: show the message and a retry button).

## Student
- `GET /api/me` → `{"student": null}` or `{"student": {"alias": "Ana" | null, "topic": "...", "programme": "Data and Business Analytics · Full Proposal"}, "engine": "opus" | null, "resume_code": "XXXX-XXXX-XXXX"}`
- `POST /api/start` `{"topic": "...", "alias": "..." | null}` → same shape as `/api/me` (sets the cookie)
- `POST /api/resume` `{"code": "XXXX-XXXX-XXXX"}` → same shape (sets the cookie), 404 `{"error":"unknown_code"}` if wrong
- `PATCH /api/me` `{"topic": "..."}` → same shape

## Models
- `GET /api/engines` → `{"engines": [{"name": "opus", "label": "Claude Opus 5.5", "vendor": "Anthropic", "model": "claude-opus-5-5", "available": true, "note": null}], "chosen": "opus" | null, "assigned": "sonnet" | null}`. `available: false` engines are shown disabled with their `note` (for example "credits exhausted"). `assigned` is set when an experiment picked an engine for this student; the page may show "Assigned: …" but must not preselect it as a choice
- `POST /api/engine` `{"name": "opus"}` → `{"chosen": "opus"}`

## Thread
- `GET /api/thread` → `{"messages": [Message], "open_flags": 3, "summary_note": "Picked up where you left off on 24 Nov" | null}`
- `Message` = `{"id": 12, "role": "student" | "tfgpt", "kind": "text" | "work" | "check" | "recheck" | "answer" | "notice", "text": "...", "data": {...} | null, "created_at": "2026-11-25T21:00:00Z", "feedback": "up" | "down" | null}`
  - `work`: the student put in their proposal; `text` is a short label like "Proposal, 412 words"; the work itself is never sent back
  - `check`: `data = {"check_id": 3, "engine": "Claude Opus 5.5 · Anthropic", "fallback_from": null | "Claude Sonnet 5.5 · Anthropic", "flags": [Flag], "hidden": 1, "seconds": 182}`
  - `recheck`: `data = {"check_id": 4, "engine": "...", "fallback_from": null, "solved": [Flag], "remaining": [Flag], "new": [Flag], "hidden": 0, "seconds": 150}`
  - `answer`: `data = {"engine": "...", "for_supervisor": false, "citations": [{"section_id": "S12", "section": "Preliminary timeline", "quote": "..."}]}`
  - `notice`: a system line, for example a failed check; `data = {"retry": "check" | "recheck" | null}`
- `Flag` = `{"id": 41, "section_id": "S7", "section": "1. Description of the intended work", "quote": "..." | null, "missing": false, "problem": "...", "route": "...", "status": "open" | "solved" | "dismissed"}`. When `missing` is true the quote is null: the problem is something absent from the work

## Work and checks
- `POST /api/extract` multipart field `file` (.docx, .pdf, .md, .txt, at most 5 MB) → `{"text": "...", "words": 412}`. Nothing is stored; the page puts the text in the work box so the student sees what will be checked
- `POST /api/check` `{"work": "..."}` → `{"job_id": 7}` (202)
- `POST /api/recheck` `{"work": "..."}` → `{"job_id": 8}` (202), 409 `no_check_yet` if there is no earlier check
- `GET /api/jobs/{job_id}/events` → server-sent events (use `EventSource`):
  - `event: progress` `data: {"status": "queued" | "running", "seconds": 42, "step": "First pass" | "Second pass" | "Checking sources"}` about every 2 seconds
  - `event: done` `data: {"message": Message}` then the stream ends
  - `event: failed` `data: {"message": Message}` (a `notice`) then the stream ends
- `POST /api/flags/{id}/dismiss` → `{"flag": Flag}`

## Questions
- `POST /api/ask` `{"question": "..."}` → server-sent events over the POST response (read with `fetch` and a stream reader, not `EventSource`):
  - `event: start` `data: {"engine": "Claude Sonnet 5.5 · Anthropic"}`
  - `event: delta` `data: {"text": "..."}` (append; this is the draft while sources are checked)
  - `event: done` `data: {"message": Message}` (replace the draft with this final answer)
  - `event: failed` `data: {"message": Message}`
- `POST /api/messages/{id}/feedback` `{"value": "up" | "down"}` → `{"ok": true}`

## Other
- `GET /healthz` → `{"ok": true, "service": "web", "version": "abc1234"}`
- `GET /api/meta` → `{"version": "abc1234", "session_minutes": 30, "compact_minutes": 5, "max_words": 3000}`
