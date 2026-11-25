# Build briefs and reports: Check once

Feature folder: `specs/2026-11-25-check-once/`. Built on 2026-11-25 by an AI coding agent (Claude Code, Opus 5.5) on Angelotxx271's instruction to build the whole tech stack at once. Deviation from the build loop, stated plainly: the six task groups were built in one session, and each group's tests were written alongside its code rather than run red first. Every case below has a test that fails without the code it names.

## Task group 1: Walking skeleton
Goal: the whole path once, web → advisor → harness (fake engine) → flags on the page
Cases to pass: V1
Files: `prototype/tfgpt/shared/`, `web/`, `advisor/`, `harness/`, `tests/test_skeleton.py`
Not in this group: real engines, uploads, the queue's restart handling
Test first: `tests/test_skeleton.py` (version on `/healthz`, the internal token, V1, the page's security headers)
Check: `python -m pytest -q tests/test_skeleton.py`
Data: `prototype/tfgpt/eval/data/` (synthetic)
Questions for the team: none

## Task group 2: Model harness
Goal: the registry, three real adapters, routing with retries, fallback, circuits, caps and a run record per engine tried
Cases to pass: V6, V7, V8
Files: `prototype/tfgpt/harness/`, `tests/test_harness.py`
Check: `python -m pytest -q tests/test_harness.py`
Questions for the team: the cap values (Q5 in requirements.md)

## Task group 3: Document pack and source check
Goal: numbered sections, the check prompt in its own file, JSON checked in code, invented quotes and sections hidden and counted
Cases to pass: V2 (model, see the evaluation), V3, V4
Files: `prototype/tfgpt/advisor/advisor/pack.py`, `check.py`, `prompts/`, `tests/test_check.py`
Check: `python -m pytest -q tests/test_check.py`

## Task group 4: Uploads, jobs and progress
Goal: .docx, .pdf, .md and .txt extraction; checks as Postgres jobs that survive a dead worker; progress over server-sent events
Cases to pass: V5, plus a job left by a dead worker is picked up again
Files: `prototype/tfgpt/web/web/extract.py`, `advisor/advisor/jobs.py`, `tests/test_extract.py`, `tests/test_jobs.py`
Check: `python -m pytest -q tests/test_extract.py tests/test_jobs.py`

## Task group 5: Picker and experiments
Goal: the offered engines with model and vendor, the remembered choice, stable experiment arms, a choice overriding the arm and logged
Cases to pass: V6 with and without an experiment
Files: `prototype/tfgpt/harness/harness/routing.py`, `web/web/static/`, `tests/test_harness.py`
Check: `python -m pytest -q tests/test_harness.py -k experiment`

## Task group 6: Evaluation and deploy
Goal: the eval CLI on the public synthetic set; web, advisor, harness and Postgres live on Railway with the programme's documents loaded
Cases to pass: V1 on the live URL with a real engine
Files: `prototype/tfgpt/eval/`, `*/Dockerfile`, `prototype/tfgpt/README.md`
Check: `python -m pytest -q`, the live `/healthz`, one live check on a synthetic proposal
Questions for the team: the evaluation's pass threshold, before the first scored run

## Report: task groups 1 to 6
Result: PASS, except V2, which waits for the team's threshold
Cases: V1 pass (offline and live), V3 pass, V4 pass (offline: the work stays data, output stays the flag schema; the model's behaviour is the evaluation's injection case), V5 pass, V6 pass, V7 pass, V8 pass; V2 not scored yet
Earlier tests: all pass, 77 offline tests on SQLite and on Postgres 17 with the real migrations; every schema migrates down to base and back up
Files changed: `prototype/tfgpt/` (new), `prototype/briefs/`
Run it yourself: open https://web-production-6bb30ece.up.railway.app, give a topic, choose a model, paste a synthetic proposal from `prototype/tfgpt/eval/data/cases.jsonl` and press Check: in one to two minutes you see the flags, each with a quote from your text, a section of the documents and a route
Deviations from the brief: tests written alongside the code, not before it; the thread's messages live in the advisor schema (plan.md, Working location); a token-protected loader on web, because the live database has no public address
Later list: the private 18-point set through the spike's blind judge; a re-check pair and the questions in the scored evaluation; the woff2 content type; rename the Railway domain
Suggested commit message: feat(tfgpt): check once, end to end

## Live results, 2026-11-25 (not a scored run)
- Smoke, eval CLI, Sonnet, synthetic case c01, 1 repeat: 3 of 3 planted issues caught, 0 wrong flags, 35 s, $0.06 (`prototype/tfgpt/eval/results/2026-11-25-sonnet-smoke.json`)
- Live URL, Sonnet, the real programme documents (13 sections) and synthetic case c01: 9 flags in 65 s, every quote found in the text, 0 hidden. Checked as a "smoke test" student
