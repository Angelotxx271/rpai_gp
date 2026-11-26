# Security & Safety Audit Record

**Last audited:** 2026-11-26  
**Audited commit on `main`:** `135115b` (PR #37, Phase 1 build)  
**Purpose:** Evidence record for the Security controls required in `downloads/final-project-guide.md` (Section 6) and Definition of Done in `specs/2026-11-25-*/validation.md`.

---

## 1. Secrets Check of Code and Full Git History

### Recorded `gitleaks` scans

| Date (UTC) | Tool & version | Scope | Result | Notes |
|---|---|---|---|---|
| 2026-11-25 | `gitleaks` (PR #37 pre-merge check) | Full history at PR #37 (`82` commits reported in PR #37) | 0 leaks | Reported in PR #37 description |
| 2026-11-26 | `gitleaks v8.30.1` | `main` (`135115b`: 79 non-merge commits / 118 total incl. merges, 1.84 MB) | **0 leaks** (`exit 0`) | Command: `gitleaks git --log-opts="main" --redact --verbose` |
| 2026-11-26 | `gitleaks v8.30.1` | `--all` refs (85 non-merge commits, 1.87 MB) | **0 leaks** (`exit 0`) | Command: `gitleaks git --log-opts="--all" --redact --verbose` |

### Historical finding disclosed and remediated (`STATS_KEY`)

- **What happened:** Prior to commit `aaa529f` (2026-11-23, PR #23), `tfgpt-landing/server.js` and `tfgpt-landing/README.md` contained a hardcoded fallback string for `STATS_KEY`. Because this repository is public, that fallback literal remains visible in pre-`aaa529f` git history (it is a short non-standard string, so generic secret scanners do not flag it).
- **Remediation in code (`aaa529f`):** Removed the default completely (`STATS_KEY` defaults to `""`). `/stats` and `/export.csv` stay disabled (`404`) unless `STATS_KEY` is explicitly configured to at least 12 characters, compared with constant-time SHA-256 `crypto.timingSafeEqual`, and served with `Cache-Control: no-store`.
- **Operational requirement:** Railway's live `STATS_KEY` on the `tfgpt` landing service must differ from the pre-`aaa529f` fallback (never printed in logs or committed).

### Repository-level GitHub security controls (enabled 2026-11-26)

| Control | Status | Verification / Config |
|---|---|---|
| GitHub Secret Scanning | **Enabled** (`0` alerts) | Checked via GitHub API on 2026-11-26 |
| GitHub Secret Scanning Push Protection | **Enabled** | Blocks pushes containing recognised provider secrets before they reach GitHub |
| GitHub Dependabot Vulnerability Alerts | **Enabled** (`0` alerts) | Checked via GitHub API on 2026-11-26 |
| GitHub Dependabot Automated Security Updates | **Enabled** | Auto-opens security PRs for vulnerable dependencies |
| Dependabot Version Updates | **Configured** | `.github/dependabot.yml` (pip across all 5 Python manifests, npm for `tfgpt-landing` & `tfgpt-pilot`, 3 Dockerfiles, GitHub Actions) |
| GitHub CodeQL (Python + JS) | **Configured** | `.github/workflows/codeql.yml` |
| CI Full-History `gitleaks` + Hygiene + Bandit + `pip-audit` + `npm audit` | **Configured** | `.github/workflows/security.yml` (uploads JSON reports as 90-day artifacts + writes step summary) |
| CI Offline Regression Suite (SQLite + Postgres 17 + Spike) | **Configured** | `.github/workflows/ci.yml` |
| Secret exclusion rules | **Configured** | `prototype/.gitignore`, `tfgpt-landing/.gitignore`, `tfgpt-pilot/.gitignore`, `.git/info/exclude`, and root `.gitignore` (PR #39) |

### API Keys & Provider Status (Recorded Operational Note)

- **Active in Railway `harness` service:** `ANTHROPIC_API_KEY` (stored only as a Railway variable; referenced by env var name in `prototype/tfgpt/harness/engines.json`).
- **Pending upload / refill (intentionally disabled for now):** `OPENROUTER_API_KEY` has not been created/uploaded yet, and Mistral API credits (`MISTRAL_API_KEY` covering `mistral-large-4` and `zai-glm-5-3`) need a refill. Both engines stay `"enabled": false` in `prototype/tfgpt/harness/engines.json` until uploaded and enabled via Railway variables — no placeholder keys exist in the repository.

---

## 2. Bounded Permissions & Service Isolation

Verified directly against `prototype/tfgpt/` on commit `135115b`:

- **Network boundary:** Only `web` has a public Railway domain. `advisor` (`advisor.railway.internal:8000`) and `harness` (`harness.railway.internal:8000`) have no public URLs and communicate only over Railway's private network.
- **Internal service auth (`prototype/tfgpt/shared/tfgpt_shared/internal.py`):** Every internal endpoint on `advisor` and `harness` enforces `Depends(require_internal)` checking `X-Internal-Token` with constant-time `hmac.compare_digest`; missing or mismatched tokens return `401`.
- **Admin pack loader (`prototype/tfgpt/web/web/app.py:340-351`):** `POST /api/admin/pack` checks `x-admin-token` against `ADMIN_TOKEN` using `hmac.compare_digest`, returns `404` when unset or invalid (hiding the endpoint), and enforces a 2 MB size cap (`413`).
- **Browser & transport hardening (`prototype/tfgpt/web/web/app.py:33-34,131-143,178-180`):**
  - OpenAPI/Swagger UI disabled in production (`docs_url=None, redoc_url=None, openapi_url=None`).
  - Strict Content-Security-Policy: `default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'`.
  - Additional headers: `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY`, and `Cache-Control: no-store` on `/api/*`.
  - CSRF defence: state-changing requests (`POST`, `PATCH`, `PUT`, `DELETE`) under `/api/` require the custom header `x-tfgpt: 1`, otherwise return `403`.
  - Session cookies: 80-bit random token (`secrets.token_bytes(10)`), stored in Postgres only as a SHA-256 hash (`app.token_hashes`), sent with `HttpOnly`, `SameSite=Lax`, and `Secure` (on Railway).
  - Resume-code brute-force throttle: `Throttle` limits tries to `RESUME_TRIES_PER_HOUR` (default `20/hour`, returns `429`).
  - Upload cap: `POST /api/extract` caps uploads at 5 MB; `WorkBody` caps proposal text at 60,000 chars (`MAX_WORDS=3000`).
- **Container & CI least privilege:** All three Dockerfiles (`web`, `advisor`, `harness`) create and run as non-root user `tfgpt`. GitHub Actions workflows declare explicit minimal `permissions: contents: read` (and `security-events: write` only in `codeql.yml`).
- **Spending & abuse caps (`prototype/tfgpt/harness/harness/routing.py`):** Per-student daily limits (`CHECKS_PER_STUDENT_DAY=10`, `TOKENS_PER_STUDENT_DAY=1500000`), total daily spend cap (`DAILY_BUDGET_USD=15`), and per-provider circuit breakers.

---

## 3. Untrusted Input Handled as Data, Never Instructions

- **Prompt isolation (`prototype/tfgpt/advisor/advisor/prompts/`):** All four prompts (`check.md`, `recheck.md`, `ask.md`, `compact.md`) wrap loaded guidelines in `<project_documents>...</project_documents>` and explicitly instruct the model to treat student topics, proposal drafts, open flags, summaries, and questions as untrusted data — ignoring embedded attempts to force approval, alter rules, or leak prompts.
- **Deterministic post-check in code (`advisor/check.py`, `advisor/ask.py`, `tfgpt_shared/textmatch.py`):**
  - Checks/re-checks parse strict JSON schema; code verifies every returned flag's quote exists in the student's text and its `section_id` exists in the active document pack, hiding and counting any unverified flag.
  - Stage answers verify every cited `[S##]` quote exists in that section; if zero verified citations survive, code replaces the response with `"That one is for your supervisor"`.
- **Prompt-injection evaluation cases:** Included in the public synthetic evaluation set (`prototype/tfgpt/eval/data/cases.jsonl` case `c14` and `questions.jsonl` question `q10`) and tested offline in `tests/test_check.py` (V4) and `tests/test_ask.py` (V6).

---

## 4. Human Approval for Consequential Actions

- **Academic / thesis boundary:** TFGPT never assigns grades, gives pass/fail verdicts, or drafts/rewrites thesis text (`specs/mission.md`, `evidence-log/ERRC.md`). Every revision decision stays with the student; every academic approval stays with the human supervisor.
- **Code & deployment governance (`AGENTS.md`, `specs/tech-stack.md`):** Every change reaches `main` via a branch and PR with human review (no force-pushes to `main`). Loading programme documents (`advisor.loadpack`), naming `DEFAULT_ENGINE`, enabling/disabling engines (`ENGINES_OFF`/`ENGINES_ON`), and starting/stopping A/B experiments (`tfgpt_eval experiment`) are manual human actions.

---

## 5. Personal Data & Privacy Boundaries

- **Public repository:** Contains only aliases (`Participant 01`, `Advisor A`, GitHub handles) and fictional synthetic evaluation data (`Northfield School of Business` in `prototype/tfgpt/eval/data/`). Real IE guidelines, real student proposals, supervisor comments, and the advisor-spike answer key remain exclusively in git-excluded `private/`.
- **Runtime retention:** Uploaded proposal text (`advisor.checks.work_text`) is purged by the background sweep after `SESSION_MINUTES` (default `30` minutes) of inactivity; only short flag quotes remain in the thread's flag ledger. Live purge verification on Railway remains tracked in `specs/2026-11-25-ask-the-documents/validation.md` DoD.
- **Syllabus / external LLM clearance (Angelotxx271 note, 2026-11-26):** Because this prototype is being built and tested strictly as an internal university course project, the syllabus external-model blocker (`specs/tech-stack.md` Blockers, `specs/2026-11-25-check-once/requirements.md` Q6) is treated as resolved for course-project testing; formal institutional data-processing clearance remains required before any real IE-wide rollout (recorded alongside Falsifier 2).
- **Professor assumptions email:** `private/email-professor-assumptions.draft.md` has not yet been sent.
