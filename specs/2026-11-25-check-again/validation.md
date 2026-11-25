# Validation: Check again

Version 0.1, 2026-11-25. Written before implementation. Data: synthetic proposals and their revised versions (`prototype/tfgpt/eval/`)

## Checks
- Automated: `python -m pytest -q tests/test_recheck.py`, scripted fake engine
- Repeated trials: the eval CLI's re-check pairs (a synthetic proposal and a revision that fixes some planted issues), 3 runs each. Pass threshold: Missing, set by the team before the first scored run
- Manual: on the live URL, check a synthetic proposal, fix one flagged passage, check again, and confirm the lists

## Evaluation seed
| ID | Type | Situation or input | Expected behaviour | Pass condition | Proves |
|---|---|---|---|---|---|
| V1 | Happy path | 2 open flags; fake engine marks #1 solved, #2 remaining | Lists show 1 solved, 1 remaining | Flag rows: #1 solved, #2 open; message lists match | S1 |
| V2 | Happy path | Fake engine returns one new flag with a real quote | Listed as new, now open | A new open flag row; message's new list has 1 | S2 |
| V3 | Failure | Fake engine returns remaining #2 with a quote not in the text | #2 remaining, quote dropped | Flag #2 open, its stored quote unchanged; no invented quote shown | S3 |
| V4 | Edge | Flag #1 dismissed before the re-check | Not sent, not listed | The model's input holds no flag #1; the lists don't name it | S4 |
| V5 | Failure | No earlier check | Asked to run a first check | Advisor answers 409; 0 run records | S5 |

## Definition of Done
- [ ] Every scenario passes its named case; results are recorded
- [ ] Evidence links in `requirements.md` still hold
- [ ] Human review: Angelotxx271 reads 3 live re-checks
- [ ] Privacy and security: no secrets or real personal data in the repository
- [ ] Accessibility: the three lists are headed and readable with a screen reader
- [ ] Failure and fallback behaviour checked
- [ ] `roadmap.md` Current behaviour updated
- [ ] Reviewed files committed
