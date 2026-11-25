# Plan: Check again

Version 0.1, 2026-11-25. Requirements live in `requirements.md`; this file only sequences the work

## Working location
- `prototype/tfgpt/`, as in `../2026-11-25-check-once/plan.md`

## Task group 1: Walking skeleton
- [x] Re-check job: open flags + revised text → model → solved, remaining, new; flag rows updated; message in the thread
- Files: `advisor/advisor/check.py`, `advisor/advisor/prompts/recheck.md`, `tests/test_recheck.py`
- Check: `python -m pytest -q tests/test_recheck.py`
- Done when: S1, S2, S5 (V1, V2, V5)

## Task group 2: Source check and dismiss
- [x] Quotes returned for remaining and new flags pass the source check; dismiss endpoint and button; dismissed flags left out of the input
- Files: `advisor/advisor/check.py`, `web/web/app.py`, `web/web/static/`, `tests/test_recheck.py`
- Check: `python -m pytest -q tests/test_recheck.py`
- Done when: S3, S4 (V3, V4)
