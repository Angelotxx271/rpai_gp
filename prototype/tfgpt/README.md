# TFGPT, Phase 1 build

A Data and Business Analytics student says their topic once, puts in their Full Proposal and gets cited flags back (the passage, the guideline section, one possible route), checks again after revising to see what is solved, and asks about their stage, answered only from the programme's documents or "That one is for your supervisor". One continuous thread per student; no grade, no verdict, no rewriting.

Specs: `specs/2026-11-25-check-once/`, `specs/2026-11-25-check-again/`, `specs/2026-11-25-ask-the-documents/`. Stack and run rules: `specs/tech-stack.md`.

## How it fits together

```
Browser ── https ──> web  (chat page, students, sessions, uploads, SSE)           public
                      │  Railway private network, X-Internal-Token
                      ├──> advisor (document pack, checks and re-checks as jobs,   private
                      │             answers, thread memory, purge)
                      └──> harness (engine registry, adapters, routing, fallback,  private
                                    circuits, caps, run log)
                                        └──> Anthropic API (Mistral, OpenRouter, Ollama configured)
PostgreSQL: schemas app (web), advisor, harness, eval (eval CLI; the harness reads experiments)
```

| Folder | What |
|---|---|
| `shared/` | The internal package: settings, database and migrations, internal calls, SSE, quote matching |
| `web/` | Public service and the static chat page (`web/web/static/`); the browser API is in `web/API.md` |
| `advisor/` | Checks, re-checks, answers, memory and the job queue; prompts in `advisor/advisor/prompts/` |
| `harness/` | Every model call; the registry is `harness/engines.json` |
| `eval/` | The public synthetic set (`eval/data/`), the eval CLI and its results |
| `tests/` | Offline tests: the three services in one process with a scripted fake engine |

## Run the tests

From this folder (`prototype/tfgpt`), Python 3.12:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m pytest -q
```

80 offline tests, no model calls, no network. To run them on Postgres with the real migrations:

```powershell
docker run -d --name tfgpt-pg -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tfgpt_test -p 55432:5432 postgres:17
$env:TEST_DATABASE_URL = "postgresql://postgres:dev@localhost:55432/tfgpt_test"
.venv\Scripts\python -m pytest -q
```

## Run it locally

Three terminals from this folder, each with the same `INTERNAL_TOKEN` and `DATABASE_URL` (SQLite is fine locally). The harness needs a key for any real engine; without one, use `DEFAULT_ENGINE` with an engine whose key you have.

```powershell
$env:INTERNAL_TOKEN = "local-dev-token"; $env:DATABASE_URL = "sqlite:///./tfgpt-dev.sqlite"; $env:COOKIE_SECURE = "0"
$env:PORT = "8002"; .venv\Scripts\python -m tfgpt_shared.serve harness.app:create_app     # run inside harness\
$env:PORT = "8001"; .venv\Scripts\python -m tfgpt_shared.serve advisor.app:create_app     # run inside advisor\
$env:PORT = "8000"; .venv\Scripts\python -m tfgpt_shared.serve web.app:create_app         # run inside web\
```

Then load a document pack (the synthetic one locally): `.venv\Scripts\python -m advisor.loadpack ..\eval\data\synthetic-pack.md` from `advisor\`, and open http://localhost:8000.

## Evaluation

```powershell
cd eval
..\.venv\Scripts\python -m tfgpt_eval run --engine sonnet --repeats 3                             # scored, held-out cases left out
..\.venv\Scripts\python -m tfgpt_eval run --engine sonnet --repeats 3 --held-out --rechecks --questions
```

## Safe demo reset & offline presentation backup

- **Clean the live `"smoke test"` student before demo/user testing** (dry-run by default; requires `--apply` to delete):
  ```bash
  python scripts/demo_reset.py clean --alias "smoke test"
  python scripts/demo_reset.py clean --alias "smoke test" --apply
  ```
- **Seed a fresh local SQLite offline demo database** (loads the synthetic pack + one sample thread):
  ```bash
  python scripts/demo_reset.py seed-local --db ./tfgpt-demo-backup.sqlite
  ```
- **Zero-dependency presentation backup:** open `prototype/backup-demo.html` in any browser to step through Check once → Check again → Ask → Safe failure if Railway, Wi-Fi, or an upstream API fails during the presentation.

## Automatic thread compaction (Haiku)

`advisor` runs a background worker (`advisor/jobs.py`) that sweeps every `SWEEP_SECONDS` (60 s): it deletes uploaded proposal text after `SESSION_MINUTES` (30 min) and enqueues a `compact` job for any thread quiet for `COMPACT_MINUTES` (5 min). Compaction automatically calls `COMPACT_ENGINE=haiku` (`claude-haiku-5-5`) through `harness` using the existing `ANTHROPIC_API_KEY` — no separate Haiku deployment is needed.

Needs the engine's key in the environment. Scoring is code: a planted issue is caught when a flag cites its section and its quote overlaps the planted passage; a flag on a clean passage is wrong; the injection case fails if the output approves the work. The pass threshold is set by the team in `validation.md` before the first scored run. Results: `eval/results/<date>-<engine>-<label>.json`, with the commit.

A/B experiments run on the live database (`DATABASE_URL`): `python -m tfgpt_eval experiment create ab1 --task check --arms opus:1,sonnet:1`, `... experiment stop ab1`, and `python -m tfgpt_eval online` for the per-engine metrics (checks, flags solved and dismissed, thumbs, seconds, cost).

## Deploy (Railway, project tfgpt)

Services `web` (public domain), `advisor`, `harness` and `Postgres`. Each service builds its own Dockerfile from this folder:

```powershell
railway up . --path-as-root --service harness --detach
railway up . --path-as-root --service advisor --detach
railway up . --path-as-root --service web --detach
```

Variables (Railway, never in the repository):

| Service | Variables |
|---|---|
| all three | `DATABASE_URL=${{Postgres.DATABASE_URL}}`, `INTERNAL_TOKEN` (the same random value), `APP_VERSION` (the commit), `RAILWAY_DOCKERFILE_PATH=<service>/Dockerfile` |
| web | `ADVISOR_URL=http://advisor.railway.internal:8000`, `HARNESS_URL=http://harness.railway.internal:8000` |
| advisor | `PORT=8000`, `HARNESS_URL=http://harness.railway.internal:8000`, `COMPACT_ENGINE=haiku` |
| harness | `PORT=8000`, `ANTHROPIC_API_KEY`; later `MISTRAL_API_KEY`, `OPENROUTER_API_KEY` |

Switches, all optional: `DEFAULT_ENGINE` (none until Angelotxx271 names one), `ENGINES_OFF` / `ENGINES_ON`, `DAILY_BUDGET_USD` (15), `CHECKS_PER_STUDENT_DAY` (10), `TOKENS_PER_STUDENT_DAY` (1,500,000), `SESSION_MINUTES` (30), `COMPACT_MINUTES` (5), `MAX_WORDS` (3000), `CHECK_FOLLOW_UP` (on).

The programme's documents are loaded from your own machine, from the git-excluded `private/` folder, through the web service's loader (it answers 404 unless the request carries `ADMIN_TOKEN`, a Railway variable on web):

```powershell
$env:ADMIN_TOKEN = (railway variables --service web --json | ConvertFrom-Json).ADMIN_TOKEN
cd advisor; ..\.venv\Scripts\python -m advisor.loadpack ..\..\..\private\advisor-spike\context\standin.md --title "BDBA TFG Full Proposal documents 2026-27" --until "# The student's kept context" --url https://web-production-6bb30ece.up.railway.app
```

The cut leaves out the stand-in's "student's kept context" (one student's own meeting notes): the product keeps each student's context in their own thread.

`/healthz` on each service reports its version; the advisor's also reports the active pack's hash. Undo: `specs/tech-stack.md`, How to undo a bad change.
