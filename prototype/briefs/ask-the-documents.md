# Build briefs and reports: Ask the documents

Feature folder: `specs/2026-11-25-ask-the-documents/`. Built on 2026-11-25 with Check once, in the same session; tests written alongside the code (see `check-once.md`).

## Task group 1: Walking skeleton
Goal: a question streams web → advisor → harness and back; sources parsed and checked at the end; the supervisor line when none holds
Cases to pass: V1, V2, V3, V6
Files: `prototype/tfgpt/advisor/advisor/ask.py`, `advisor/advisor/prompts/ask.md`, `web/web/app.py`, `tests/test_ask.py`
Check: `python -m pytest -q tests/test_ask.py`
Questions for the team: none

## Task group 2: Memory sweeps
Goal: the compaction sweep folds a quiet thread into the rolling summary with the compaction engine; the purge deletes uploaded work when the session ends
Cases to pass: V4, V5
Files: `prototype/tfgpt/advisor/advisor/memory.py`, `advisor/advisor/jobs.py`, `tests/test_memory.py`
Check: `python -m pytest -q tests/test_memory.py`
Questions for the team: the compaction engine and times (Q4, Q5 in requirements.md)

## Report: task groups 1 and 2
Result: PASS
Cases: V1 pass, V2 pass, V3 pass, V4 pass, V5 pass, V6 pass (offline: an uncited answer is never shown)
Earlier tests: all pass
Files changed: as above
Run it yourself: on the live URL, ask "What is the maximum length of the full proposal?": the answer streams in and lists its sources; ask "Is my supervisor strict?": "That one is for your supervisor"
Deviations from the brief: tests written alongside the code
Later list: the question set in the scored evaluation (`--questions`)
Suggested commit message: feat(tfgpt): ask the documents, with memory

## Live result, 2026-11-25 (not a scored run)
- Live URL, Sonnet: "What is the maximum length of the full proposal?" streamed in 37 pieces in 3 s, with 4 checked sources
