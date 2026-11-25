# Plan: Check once

Version 0.1, 2026-11-25. Ordered task groups, each small and reviewable. Requirements live in `requirements.md`; this file only sequences the work

## Working location
- `prototype/tfgpt/`: `shared/` (internal package), `web/`, `advisor/`, `harness/`, `eval/`, `tests/`. Python 3.12, one requirements.txt per service, offline tests per change; deploy per service with `railway up` to project tfgpt (`../tech-stack.md`, Environment and run rules)
- Deviation to confirm: the thread's messages live in the `advisor` schema, not `app`, because the advisor builds every call's context and compacts the thread; with them in `app`, web and advisor would have to call each other [AI-proposed]

## Task group 1: Walking skeleton
- [x] web serves the chat page; advisor and harness answer `/healthz` with their version; internal calls need the shared token
- [x] A topic and a pasted proposal go web → advisor → harness (fake engine in tests) → flags back on the page
- Files: `shared/tfgpt_shared/`, `web/web/`, `advisor/advisor/`, `harness/harness/`, `tests/test_skeleton.py`
- Check: `python -m pytest -q tests/test_skeleton.py`
- Done when: S1 runs end to end with the fake engine (V1)

## Task group 2: Model harness
- [x] Registry seeded from `harness/engines.json`; adapters: Anthropic (SDK), OpenAI-compatible and Ollama (httpx)
- [x] Routing: chosen engine, else experiment arm, else default, else "choose a model"; retries with backoff, fallback chain, circuit breaker per provider, daily caps and budget; a run record per attempt
- Files: `harness/harness/`, `tests/test_harness.py`
- Check: `python -m pytest -q tests/test_harness.py`
- Done when: S5, S6, S7 (V6, V7, V8)

## Task group 3: Document pack and source check
- [x] Load the pack into `advisor.documents` with numbered sections; the check prompt from `advisor/prompts/`; JSON output checked in code; flags whose quote or section isn't real are hidden and counted
- Files: `advisor/advisor/pack.py`, `advisor/advisor/check.py`, `advisor/advisor/prompts/`, `tests/test_check.py`
- Check: `python -m pytest -q tests/test_check.py`
- Done when: S1, S2, S3 (V2, V3, V4)

## Task group 4: Uploads, jobs and progress
- [x] Upload extraction in web; checks run as jobs in a Postgres queue (`FOR UPDATE SKIP LOCKED`) that survive restarts; the page follows progress over server-sent events
- Files: `web/web/extract.py`, `advisor/advisor/jobs.py`, `tests/test_jobs.py`, `tests/test_extract.py`
- Check: `python -m pytest -q tests/test_jobs.py tests/test_extract.py`
- Done when: S4 (V5), and a check survives a worker restart

## Task group 5: Picker and experiments
- [x] The page lists the offered engines with model and vendor; the choice is remembered; an active experiment assigns an arm by a stable hash, and a choice overrides it and is logged
- Files: `harness/harness/routing.py`, `web/web/static/`, `tests/test_harness.py`
- Check: `python -m pytest -q tests/test_harness.py -k experiment`
- Done when: S5 (V6) with an experiment and without

## Task group 6: Evaluation and deploy
- [x] `eval/` CLI: runs the check on the public synthetic set, scores planted issues and the injection in code, writes `eval/results/<date>-<engine>.json`
- [x] Deploy web, advisor, harness and Postgres on Railway; load the pack from `private/`; `/healthz` on each
- Files: `eval/`, `*/Dockerfile`, `prototype/tfgpt/README.md`
- Check: `python -m pytest -q`, then the live `/healthz` and one check on a synthetic proposal
- Done when: V1 passes on the live URL with a real engine; the evaluation threshold is set by the team before its first scored run
