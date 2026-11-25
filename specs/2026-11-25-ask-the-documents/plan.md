# Plan: Ask the documents

Version 0.1, 2026-11-25. Requirements live in `requirements.md`; this file only sequences the work

## Working location
- `prototype/tfgpt/`, as in `../2026-11-25-check-once/plan.md`

## Task group 1: Walking skeleton
- [ ] Ask streams web → advisor → harness and back over server-sent events; sources parsed and checked at the end; the supervisor line when none holds
- Files: `advisor/advisor/ask.py`, `advisor/advisor/prompts/ask.md`, `web/web/app.py`, `tests/test_ask.py`
- Check: `python -m pytest -q tests/test_ask.py`
- Done when: S1, S2, S3, S6 (V1, V2, V3, V6)

## Task group 2: Memory sweeps
- [ ] Compaction sweep folds the tail into the rolling summary with the compaction engine; purge sweep deletes upload text after the session time; both run in the job worker
- Files: `advisor/advisor/memory.py`, `advisor/advisor/jobs.py`, `tests/test_memory.py`
- Check: `python -m pytest -q tests/test_memory.py`
- Done when: S4, S5 (V4, V5)
