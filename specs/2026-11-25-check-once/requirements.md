# Requirements: Check once

Feature 1 of Phase 1 in `../roadmap.md`. Branch `dev/angel-phase-1-build`. Version 0.1, 2026-11-25. Status: draft, team review pending. Drafted by an AI coding agent from the constitution on Angelotxx271's instruction to start building (2026-11-25); every line marked AI-proposed waits for the team

## Why this feature
The riskiest unknown is whether students' own AI and TFGPT coexist (`../roadmap.md` Phase 1) [Team decision: assumptions.md]. A real check is the first thing the "coexist" validation needs: until a student can put their proposal in and get cited flags back, there is nothing to coexist with [AI-proposed]. It also carries the spike's warning: the stand-in missed 61% of advisor points on the judge's first pass, so the check must show its sources and be narrowable (`../tech-stack.md`, spike section) [Evidence-supported: spikes.md, judge first pass; human counts pending]

## Clarifying questions
| # | Topic | Question | Team answer | Status |
|---|---|---|---|---|
| Q1 | Scope | Which programme and deliverable? | Data and Business Analytics, Full Proposal | Team decision: tech-stack.md |
| Q2 | Decisions | Which instructions does the check use? | The frozen stand-in instructions v1 (spikes.md), plus an output format so code can check every flag | Team decision for v1 (spikes.md); output format AI-proposed |
| Q3 | Decisions | Which model runs by default? | None until Angelotxx271 names one: the student picks from the offered list, or an active experiment assigns one | Team decision: tech-stack.md |
| Q4 | Context | Does the check take two turns, as in the spike? | Yes: the check, then "Anything else that doesn't fit the guidelines?", so the product matches what the spike measured | AI-proposed |
| Q5 | Limits | Daily caps per student and in total? | 10 checks and 1.5M tokens per student per day, $15 a day in total, all Railway variables | Team decision: confirmed by Angelotxx271 (2026-11-26) |
| Q6 | Privacy | May students' work go to an outside model? | Cleared for this internal university course prototype; formal IE institutional clearance stays part of Falsifier 2 before any real campus rollout | Team decision: Angelotxx271 (2026-11-26) |

## Included behaviour
- A student opens one page, says their topic once, and stays in one continuous thread from then on [Team decision: tech-stack.md, memory row]
- They paste their proposal or upload it (.docx, .pdf, .md, .txt) and press Check [AI-proposed: tech-stack.md upload row]
- They see the progress while the check runs (it takes minutes), and can leave and come back [Team decision: tech-stack.md, jobs row]
- They get flags point by point, each with the quoted passage, the guideline section and one possible route, never a grade or an overall verdict [Team decision: ERRC.md, mission.md]
- A flag whose quote isn't in their work, or whose section isn't in the loaded documents, is never shown; the page says how many were hidden [Team decision: tech-stack.md, source check row]
- They see the exact model and vendor that ran the check, and can choose it from the offered list [Team decision: tech-stack.md, AI model row]

## Scenarios
| # | Given | When | Then | Proved by |
|---|---|---|---|---|
| S1 | A new student on the page | They give a topic and paste a proposal, pick a model and press Check | Within the run time they see a list of flags, each with a quote from their text, a section from the documents and a route | V1, V2 |
| S2 | The model returns a flag quoting text that isn't in the proposal, or citing a section that doesn't exist | The check finishes | That flag is not shown and the hidden count says 1 | V3 |
| S3 | A proposal that tells the checker to approve it | The check runs | The flags still come back as flags; no approval, grade or verdict is shown | V4 |
| S4 | A student uploads a .docx or .pdf | They press Check | The text extracted from the file is what gets checked | V5 |
| S5 | No model chosen, no experiment and no default | They press Check | They are asked to choose a model; nothing is sent | V6 |
| S6 | The chosen model's provider fails | The check runs | It retries, then either uses the next engine in the chain, saying which one answered, or says the check failed and can be retried | V7 |
| S7 | A student reaches the daily cap | They press Check | They're told the cap is reached and when it resets; nothing is sent | V8 |

## Exclusions
- Re-checking and the solved list: feature 2, `../2026-11-25-check-again/`
- Questions about the stage: feature 3, `../2026-11-25-ask-the-documents/`
- Login and IE systems: excluded since prototype-v0 [Team decision]
- Deliverables after the proposal, and other programmes [Team decision: roadmap.md]
- Grades, verdicts, drafting or rewriting the student's text [Team decision: ERRC.md]

## Inputs and outputs
- Inputs: a topic sentence, the proposal text (pasted or extracted), the student's model choice. Tests and the public evaluation use synthetic proposals and a synthetic document pack only (`prototype/tfgpt/eval/`)
- Outputs: flags in the thread (quote, section, problem, route), the hidden count, the engine that answered; one run record per model call in `harness.runs`

## Data, decisions and evidence
- The proposal text is kept only while the session lasts; flags keep short quotes [Team decision: tech-stack.md, memory row]
- The programme's documents are loaded by us into `advisor.documents` from the private folder and never committed [Team decision: tech-stack.md]
- Students are an opaque id plus an optional alias; no names or emails are asked for [Team decision: tech-stack.md, data model]
- The spike's C2 route is the basis: instructions and documents preloaded (spikes.md, protocol v2) [Evidence-supported: spikes.md]
