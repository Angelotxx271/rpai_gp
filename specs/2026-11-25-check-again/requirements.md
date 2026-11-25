# Requirements: Check again

Feature 2 of Phase 1 in `../roadmap.md`. Branch `dev/angel-phase-1-build`. Version 0.1, 2026-11-25. Status: draft, team review pending. Drafted by an AI coding agent from the constitution; AI-proposed lines wait for the team

## Why this feature
The re-check loop is what plain AI doesn't give for the same effort: the spike's flags half of falsifier 4 held (Opus with everything pasted and Sonnet used as usual matched the stand-in in 2 of 3 rounds), so the value has to come from the preloaded context, the memory and the re-check (`../tech-stack.md`, spike section) [Evidence-supported: spikes.md, judge first pass]. It tests whether students come back to TFGPT after revising, which is half of "coexist" [AI-proposed]

## Clarifying questions
| # | Topic | Question | Team answer | Status |
|---|---|---|---|---|
| Q1 | Scope | What does the student see after a re-check? | Which comments are solved and which remain, plus any new ones | Team decision: tech-stack.md, first prototype |
| Q2 | Decisions | Who decides "solved"? | The model, against the open flags; code then checks every quote it returns against the new text | AI-proposed |
| Q3 | Data | What is kept between the two checks? | The flags with their short quotes, as rows; not the earlier upload, which is deleted after the session | Team decision: tech-stack.md, memory row |
| Q4 | Scope | Can a student dismiss a flag? | Yes, "Not relevant": it leaves the open list and counts as a dismissal (an online metric) | AI-proposed, from tech-stack.md online metrics |

## Included behaviour
- After a first check, the student revises, puts the new version in and presses Check again [Team decision: tech-stack.md]
- They see three lists: solved, remaining, new; every remaining or new flag passes the same source check as in feature 1 [Team decision: tech-stack.md]
- They can dismiss a flag they think doesn't apply; it is not sent to the next re-check [AI-proposed]

## Scenarios
| # | Given | When | Then | Proved by |
|---|---|---|---|---|
| S1 | Two open flags from a first check | The student fixes one passage and checks again | One flag shows as solved, one as remaining | V1 |
| S2 | A re-check that finds a new problem | It finishes | The new flag is listed as new and joins the open flags | V2 |
| S3 | The model marks a flag remaining with a quote not in the new text | It finishes | The flag stays remaining without the invented quote | V3 |
| S4 | A dismissed flag | The student checks again | It is not in the re-check's input or its lists | V4 |
| S5 | No earlier check | The student presses Check again | They're told to run a first check; no model call | V5 |

## Exclusions
- Comparing the two texts line by line (a diff view): the student owns the text [AI-proposed]
- Keeping earlier uploads: deleted after the session [Team decision]

## Inputs and outputs
- Inputs: the revised proposal (pasted or uploaded), the open flags from `advisor.flags`
- Outputs: a re-check message in the thread; flag statuses updated in `advisor.flags`

## Data, decisions and evidence
- Flag statuses (open, solved, dismissed) are rows, so the solved list is a database match, not summary text [Team decision: tech-stack.md]
