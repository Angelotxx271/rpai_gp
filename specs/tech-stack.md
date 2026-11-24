# Tech stack

Version 0.2, 2026-11-24. Status: preliminary, to be revisited. Nothing is being built yet

## First prototype
A Data and Business Analytics student checks their TFG work against the rubric, sees whether they're on track with their topic and requirements, gets comments on their work, and can ask for general information about the stage they're in [Team decision]

It also includes:
- After revising, the student runs the check again and sees which comments are solved [Team decision: proposed by AI, accepted]
- General information comes only from the loaded documents; otherwise the answer is "that one is for your supervisor", as in the Wizard-of-Oz protocol [Team decision: proposed by AI, accepted; prototype-v0.pdf page 4]

It starts with the proposal; what comes after is decided later [Team decision]. "On track" is shown point by point, never as an overall verdict [Team decision: ERRC.md]

## Layers
Our own approach, built from scratch: Angelotxx271's suggestion, not a reference architecture [Team decision]. His tools are added here once he writes them down

| Layer | Choice | Why | Status |
|---|---|---|---|
| Student screen | TBD | Angelotxx271's suggestion | Missing |
| Checking and answers | TBD | Angelotxx271's suggestion | Missing |
| AI model | TBD | Four are being compared: Claude Opus 5.5, GLM 5.3, a Mistral model and a local Qwen (spikes.md protocol v2) | Missing |
| Source check | Code, not AI, hides any flag whose quote or guideline section isn't real | Keeps the promise that every flag cites its source | Team decision: proposed by AI, accepted |
| Guidelines | Data and Business Analytics, proposal first | Easier to test, documents collected | Team decision |
| Student's work | Deleted after the session | Re-checking needs it only during the session; keeping it longer is Phase 2 | Team decision: proposed by AI, accepted |
| Login, IE systems | Skipped | Excluded since prototype-v0 (prototype-v0.pdf page 6) | Team decision |

## Environment and run rules
- Where it runs and how it starts: TBD
- Keys, IE documents and students' work stay out of this public repo: `prototype/.gitignore` [Team decision]

## Tools and accounts
- GitHub: owner Angelotxx271; all five members have write access (checked 2026-11-24)
- Railway: owner Angelotxx271; hosts the landing page and the pilot. Use for the prototype, limits and fallback: TBD
- AI model: provider, owner, cost, limits and free route TBD

## Dependencies
- TBD; no dependency without a reason

## Blockers
- Angelotxx271's stack suggestion is not written down in the repo. Owner Angelotxx271
- Model choice waits for the protocol v2 results. Owner Angelotxx271
- Two checks before building: does the Data and Business Analytics TFG syllabus allow student work in an AI model, and do we have the rubric (spikes.md protocol v2 doesn't list it)? Owners Angelotxx271 and adriFCM

## AI Fit Decision
AI does the check and the answers [Team decision: press-release.md]. The assessment itself is TBD. If a general AI gives the same flags for the same effort, TFGPT has no value (ERRC.md falsifier 4) [Missing]

## Architecture Decision Record log
No entries yet. Entries start with the feature specification: date, decision, why, rejected alternative, revisit if
