# Tech stack

Version 0.4, 2026-11-25. Status: preliminary, to be revisited. The build started on 2026-11-25 on Angelotxx271's call; team lock-in of each line is still pending

## First prototype
A Data and Business Analytics student checks their TFG work against the rubric, sees whether they're on track with their topic and requirements, gets comments on their work, and can ask for general information about the stage they're in [Team decision]

It also includes:
- After revising, the student runs the check again and sees which comments are solved [Team decision: proposed by AI, accepted]
- General information comes only from the loaded documents; otherwise the answer is "that one is for your supervisor", as in the Wizard-of-Oz protocol [Team decision: proposed by AI, accepted; prototype-v0.pdf page 4]

It starts with the proposal; what comes after is decided later [Team decision]. "On track" is shown point by point, never as an overall verdict [Team decision: ERRC.md]

## Layers
Our own approach, built from scratch: Angelotxx271's suggestion, not a reference architecture [Team decision]. His tools are added here once he writes them down. Written down on 2026-11-25 (planning session with an AI assistant, logged in ai-usage-log.md once confirmed); the statuses below mark whose choice each line is, and the team locks every one

| Layer | Choice | Why | Status |
|---|---|---|---|
| Student screen | One continuous chat page, static HTML + CSS + vanilla JS served by the web service, Server-Sent Events for streaming; no new chats, the thread lives as long as the TFG | The pilot's house style, no build step, Python only behind it; the experience must be effortless: the student opens it and it picks up where they left off [Angelotxx271, 2026-11-25] | Team decision: proposed, lock-in pending |
| Checking and answers | Three FastAPI services, split from day one: web (page, sessions), advisor (checks, flags, re-checks, stage answers, jobs), harness (every model call), plus an eval CLI and one shared internal package | Angelotxx271 works that way and the advisor-spike harness already separates engines, runs and judge, so it becomes the harness service with adaptation, not a rewrite (prototype/advisor-spike/, PR #30) | Team decision: proposed, lock-in pending |
| AI model | A config-driven model registry with three adapter kinds (OpenAI-compatible, Anthropic, Ollama), adapted from the spike's engines.json through three providers: OpenRouter, Anthropic, Mistral (GLM and Mistral models; credits currently exhausted, kept configured); Ollama stays dev/benchmark only. Students see the exact model and vendor and choose from our offered list; **no default engine until Angelotxx271 names one**, which is then a registry variable change, nothing more | Vendor independence, redundancy by switching, and engine choice for students [Angelotxx271, 2026-11-25]; the registry pattern is proven (PR #30) | Team decision: proposed, lock-in pending; default engine: by Angelotxx271's call only |
| A/B testing | An experiments table assigns models per task (stable hash of student + experiment); a student's own model choice overrides the assignment and is logged; every run logs engine, prompt hash, tokens in, tokens out, seconds, cost, retries, fallback | Tests which models students actually use best, by numbers instead of opinions, and feeds cost-benchmark.md; the spike's run record is the shape | AI-proposed, lock-in pending |
| Memory, continuous chat | One long-lived thread per student and TFG, continuous from the start: topic kept, an unresolved/resolved flag ledger kept, and a rolling summary auto-compacted after a few minutes of inactivity, so the next visit resumes where it left off. The uploaded proposal itself is deleted after each session, as in v0.2, and uploaded again next visit | Angelotxx271's decision, 2026-11-25: the memory is a continuous thing, not a later phase; the student never opens a new chat. Structured state (flags as rows) is rebuilt from the database, so the compaction only carries the conversation, and the v0.2 privacy rule stands | Team decision: Angelotxx271, 2026-11-25, team lock-in pending; it moves part of roadmap.md Phase 2 into Phase 1, so the mission's "from Phase 2" line and roadmap Phase 2 are aligned at the next specs edit |
| Guidelines | Data and Business Analytics, proposal first | Easier to test, documents collected | Team decision |
| Document pack | The programme's documents are loaded by us and injected per stage as one pack (the C2 route: about 51k tokens per call on Claude, about 33k on Qwen, GLM and Mistral, whose tokenizers count fewer; spike run log, PR #31, #32); no vector database this phase | The student never uploads guidelines [Angelotxx271, 2026-11-25]; C2 fits the context windows, so retrieval can stay deterministic | Team decision: proposed, lock-in pending |
| Student's work | Deleted after the session | Re-checking needs it only during the session; keeping it longer is Phase 2 | Team decision: proposed by AI, accepted |
| Upload format | Paste or upload of the proposal (.docx, .pdf, .md), extracted to text; the proposal is the input we work with at this stage | Students write deliverables as documents, not text boxes [AI-proposed] | AI-proposed, lock-in pending |
| Login, IE systems | Skipped | Excluded since prototype-v0 (prototype-v0.pdf page 6) | Team decision |
| Database | PostgreSQL on Railway, one instance, one schema per service (app, advisor, harness, eval), SQLAlchemy + Alembic | Checks take minutes and must survive restarts, so jobs, checks, flags and runs live in the database; one instance keeps the Railway bill down, schemas keep each service's ownership clear | AI-proposed, lock-in pending |
| Tasks and jobs | A Postgres queue (SELECT … FOR UPDATE SKIP LOCKED) in the advisor service: async checks, auto-compaction, purges | A C2 check took 150–265 seconds on Claude and about 103k input tokens over its two turns in the spike (run log, PR #31), so it cannot block a request; the student sees progress | AI-proposed, lock-in pending |
| Deployment | Railway, same project as the landing page and pilot: each FastAPI service is its own Railway service, deployed by railway up from its folder; only web is public, the rest talk on the private network with a shared internal token | The landing and pilot already run there [Team decision]; internal traffic never leaves Railway, and the public repo stays clean of secrets | Team decision: proposed, lock-in pending |
| Evaluation | The eval CLI reuses the spike's method: blind judge, the 18-point ground truth plus a public synthetic set with planted issues and one prompt injection, reports per engine | Engine quality and cost by independent numbers, repeatable as models and prompts change | AI-proposed, lock-in pending |
| Source check | Code, not AI, hides any flag whose quote or guideline section isn't real | Keeps the promise that every flag cites its source | Team decision: proposed by AI, accepted |

## How the layers fit together

```
Student ─ public URL → web (chat page, sessions, SSE)
                        │ Railway private network + shared internal token
                        ├── advisor (document pack, check, re-check, stage answers,
                        │             jobs: checks, compaction, purge)
                        └── harness (registry, adapters, routing, retries, run log)
                                            │
                    OpenRouter · Anthropic API · Mistral API · Ollama (dev only)
Railway PostgreSQL ← app / advisor / harness / eval schemas
eval CLI (by hand or cron): arms, blind judge, reports
```

### Model harness
- **Registry**: the spike's engines.json pattern, seeded into the database; every engine names its key by environment variable only (never the key), context size, price per million tokens in/out, concurrency cap, enabled flag. Providers: openrouter, anthropic, mistral; Ollama engines stay off in production
- **Adapters**: OpenAI-compatible (OpenRouter, Mistral, GLM), Anthropic, Ollama, with streaming; fallback chains must cross providers, because GLM and Mistral share api.mistral.ai and one failure domain
- **Routing**: per task an ordered chain; retries with backoff on 429/5xx/timeouts, then the next engine; a circuit breaker per provider; per-student daily token/check caps; every switch is logged
- **Run log**: the spike's per-run record, kept verbatim in shape: model, prompt hash, tokens, seconds, cost, retries, fallback used, experiment, arm, status
- **Rejected**: LiteLLM proxy (a magic dependency; our adapters are about 150 lines and explainable in the presentation). Kept from the spike: the official Anthropic SDK for the Anthropic adapter (streaming, typed errors, prompt caching, as the spike harness already calls it); OpenAI-compatible and Ollama go over httpx, as the spike's plain HTTP calls do

### Memory: the continuous chat
- One thread per student and TFG, messages append-only in Postgres; the student never opens a new chat
- Context per call: narrowed instructions + document pack + topic + flag ledger + rolling summary + recent tail
- After a few minutes of inactivity (X, configurable), a job folds the tail into the rolling summary with a cheap engine; on return, the student sees where they left off
- Flags are rows, so the re-check diff ("which comments are solved") is a database match, not summary text; short quotes stay in the ledger because the diff needs them, full uploads are still deleted (v0.2 rule, team confirms)

### Model choice by students, and A/B
- The picker shows the exact model and vendor, from our offered list, and remembers the student's choice [Angelotxx271, 2026-11-25]
- Experiments assign engines per task silently; a choice overrides and is logged, and switching between models is tracked, since switching away is itself a signal
- Online metrics: flags resolved on re-check, flags dismissed, thumbs, latency, cost, revisits. Offline metrics: the eval CLI's caught / correct extra / wrong / taste against the ground truth, plus over-flagging on approved-style text
- CSV exports for the blind human scorers, as in the pilot's export

### Data model
```
app:      students (alias, degree, topic) · sessions · messages · token hashes
advisor:  programmes · doc_packs · documents · checks · flags · prompt_templates · compactions · jobs
harness:  engines · runs · circuits
eval:     experiments · assignments · ground_truth · verdicts · rollups
```
No real names beyond what the pilot already allowed; aliases in student-facing text

### What the advisor spike says so far (judge first pass; human counts pending)
Source: spikes.md, Results protocol v2 (PR #31, #32; scorer and second checker by Friday 27 November)
- **Falsifier 3**: the stand-in (C2) on Claude Opus 5.5 missed 11 of 18 points (61%), above the 40% line → if the people agree, the check is narrowed before students try it. Narrowing, as decision-record.md defines it: restrict the check to what it flags reliably (guidelines, format, scope and deliverable rules first, the G-type points) instead of claiming to catch everything a supervisor would, say so plainly in the product, and re-test the narrowed check on the ground truth before students see it. Once the product is built, the loop repeats on the real thing: re-measure the miss rate with the eval CLI, narrow again if it still misses, and re-test that too [Angelotxx271, 2026-11-25]. So the check prompt is registry-narrowable per stage and section, and that is a build input, not a nice-to-have
- **Over-flagging**: 16–36 flags on the approved version per review → narrowing also cuts noise, which trust needs
- **Cost and time**: a C2 check cost a median $0.52 on Opus ($0.37–0.72) and $0.39 on Sonnet ($0.29–0.49), took 150–265 seconds, about 103k tokens in over two turns (runs-public.csv) → async jobs, budget caps, and the pricing input for cost-benchmark.md
- **Falsifier 4, flags half**: Opus given everything pasted and Sonnet used as usual matched the stand-in in 2 of 3 rounds → plain flag quality is not the differentiator; the zero-effort preloaded context, the memory and the re-check loop are, which is what these layers build
- Mistral API credits ran out mid-run; engines stay configured, off until refilled

### Build order once the team locks the choices
1. Human counts (Friday 27 November) decide narrow-or-not; the narrowed check prompt and the ground-truth set come from the spike
2. web + advisor + harness + Postgres on Railway: check → flags with citations; re-check → solved diff; stage answers; picker, experiments, run log; the A/B data then accumulates by itself
3. Validation is roadmap.md's "coexist" test, unchanged

## Environment and run rules
- Runs on Railway, project tfgpt: services web, advisor, harness + PostgreSQL; tfgpt (landing) and tfgpt-pilot stay as they are. Deploy per service with railway up from its folder; /healthz on each
- Only web gets a public domain. Internal calls go to `advisor.railway.internal:8000` and `harness.railway.internal:8000` with a shared internal token from Railway variables
- Keys, IE documents and students' work stay out of this public repo: `prototype/.gitignore` [Team decision]. Keys exist only as Railway environment variables, named in the registry; never printed in logs or the console
- One environment, production on Railway; local development runs `uvicorn` with a private .env outside the repo. Python 3.12+, one requirements.txt per service, shared package installed editable; offline tests (no model calls) run per change, every change on a `dev/<name>` branch with a PR
- Grader-visible rule: nothing in this file is built until the choices are locked and the feature specification exists (course build loop)

## How to undo a bad change
- **Code**: every change reaches `main` through a PR, so a bad one is undone with `git revert <merge commit>` on a new branch and its own PR; never a force-push to `main`
- **Deploy**: each Railway service keeps its past deployments; roll back to the last good one in the Railway dashboard (Deployments, Redeploy) or redeploy the reverted commit with `railway up`. The `/healthz` of each service reports its version (the git commit), so we can see which code is live
- **Database**: every schema change is an Alembic migration with a working `downgrade()`; undo one with `alembic downgrade -1` for that service's schema. A migration that drops data is split in two (stop using, then drop in a later release), so a rollback never needs data back
- **Models and prompts**: an engine that misbehaves is switched off with its `enabled` flag in the registry, and a prompt is a versioned file, so the previous one is a revert, not a rewrite. Each run records its prompt hash, so a bad batch can be traced and rerun
- **Students' data**: uploads are deleted after each session, so there is nothing to restore; the flag ledger and the thread are kept in Postgres, so take a `pg_dump` before any migration that changes those tables

## Tools and accounts
- GitHub: owner Angelotxx271; all five members have write access (checked 2026-11-24)
- Railway: owner Angelotxx271; Hobby plan ($5 + usage; three FastAPI services + PostgreSQL estimated $10–20/month). Fallback if cost bites: web and advisor merge into one service, harness and eval unchanged
- OpenRouter: owner Angelotxx271, key to create; pay-as-you-go, is the cross-vendor fallback and carries the widest model list for student choice. Fallback: it ends of chains, so a failure drops to Anthropic
- Anthropic API: owner Angelotxx271, key exists (used by the spike on 2026-11-25); budget cap set in the registry. Fallback: OpenRouter covers the same models
- Mistral API: owner Angelotxx271; credits exhausted mid-spike, to be refilled or the GLM and Mistral engines stay off until it is
- Ollama (local Qwen, PR #32): Angelotxx271's own PC; free route for development and the cost benchmark, never in the production chain

## Dependencies
- Python 3.12+, FastAPI + Uvicorn, SQLAlchemy 2 + Alembic, Pydantic v2, the Anthropic SDK for Claude and httpx for every other model call and for the internal calls, sse for streaming, python-docx/pymupdf for upload extraction, pytest + respx for offline adapter tests
- One requirements.txt per service; a shared package holds the models/schemas both services speak
- Deliberately absent: Redis (Postgres queue is enough), a vector database (pack injection fits), LiteLLM, an npm pipeline (static pages), any vendor SDK other than Anthropic's

## Blockers
- Team lock-in of this write-down, line by line. Owner: the team, next meeting
- Model choice waits for the protocol v2 human counts (scorer adriFCM, second checker kristgiuff05, by Friday 27 November)
- Two checks before building: does the Data and Business Analytics TFG syllabus allow student work in an AI model, and do we have the rubric (spikes.md protocol v2 doesn't list it)? Owners Angelotxx271 and adriFCM
- Key to create: OpenRouter. Mistral credits to refill. Owner Angelotxx271
- After the counts: the narrowing decision (decision-record.md), which shapes the check prompt. Owner: the team

## AI Fit Decision
AI does the check and the answers [Team decision: press-release.md]. The assessment itself is TBD. If a general AI gives the same flags for the same effort, TFGPT has no value (ERRC.md falsifier 4) [Missing]

## Architecture Decision Record log
No entries yet. Entries start with the feature specification: date, decision, why, rejected alternative, revisit if
