# Build briefs and reports: Check again

Feature folder: `specs/2026-11-25-check-again/`. Built on 2026-11-25 with Check once, in the same session; tests written alongside the code (see `check-once.md`).

## Task group 1: Walking skeleton
Goal: open flags + revised text → the model → solved, remaining, new; flag rows updated; a re-check message in the thread
Cases to pass: V1, V2, V5
Files: `prototype/tfgpt/advisor/advisor/check.py`, `advisor/advisor/prompts/recheck.md`, `tests/test_recheck.py`
Check: `python -m pytest -q tests/test_recheck.py`
Questions for the team: none

## Task group 2: Source check and dismiss
Goal: quotes on remaining and new flags pass the source check; "Not relevant" dismisses a flag and keeps it out of the next re-check
Cases to pass: V3, V4
Files: `prototype/tfgpt/advisor/advisor/check.py`, `web/web/app.py`, `web/web/static/`, `tests/test_recheck.py`
Check: `python -m pytest -q tests/test_recheck.py`

## Report: task groups 1 and 2
Result: PASS
Cases: V1 pass, V2 pass, V3 pass, V4 pass, V5 pass; also a flag id the model invents is ignored, and a student can't dismiss someone else's flag
Earlier tests: all pass
Files changed: as above
Run it yourself: after a live check, change one flagged passage, paste the new text and press Check again: the message lists Solved, Still open and New
Deviations from the brief: tests written alongside the code
Later list: the eval CLI's re-check pairs (`eval/data/rechecks.jsonl`) in the scored run
Suggested commit message: feat(tfgpt): check again with the solved list
