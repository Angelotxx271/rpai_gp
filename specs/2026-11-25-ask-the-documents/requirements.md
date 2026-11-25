# Requirements: Ask the documents

Feature 3 of Phase 1 in `../roadmap.md`. Branch `dev/angel-phase-1-build`. Version 0.1, 2026-11-25. Status: draft, team review pending. Drafted by an AI coding agent from the constitution; AI-proposed lines wait for the team

## Why this feature
Students ask about their stage between checks; the Wizard-of-Oz pilot answered only from the guidelines, otherwise "that one is for your supervisor" (prototype-v0.pdf page 4) [Team decision: tech-stack.md]. Together with the continuous thread it is the "memory" half of the value the spike points to [Evidence-supported: spikes.md, falsifier 4 flags half, judge first pass]

## Clarifying questions
| # | Topic | Question | Team answer | Status |
|---|---|---|---|---|
| Q1 | Scope | Where may answers come from? | Only the loaded documents; otherwise "that one is for your supervisor" | Team decision: tech-stack.md |
| Q2 | Decisions | How is "only the documents" enforced? | The answer cites sections with a short quote; code checks each quote is in that section, and an answer with no checked source becomes the supervisor line | AI-proposed |
| Q3 | Memory | What does the model see of the thread? | Topic, open flags, the rolling summary and the recent tail | Team decision: tech-stack.md, memory |
| Q4 | Memory | When is the thread compacted? | After 5 minutes without a message, by a cheap engine (Claude Haiku 5.5); both are Railway variables | AI-proposed, team to confirm |
| Q5 | Privacy | When is the uploaded work deleted? | When the session ends: 30 minutes without activity | AI-proposed, from tech-stack.md memory row |

## Included behaviour
- A student types a question and the answer streams into the thread, with its sources under it [Team decision: tech-stack.md]
- A question the documents don't answer gets "That one is for your supervisor" [Team decision]
- The thread continues across visits: the page shows where they left off, and the model gets the rolling summary [Team decision: tech-stack.md]
- The uploaded work is deleted when the session ends; flags and their short quotes stay [Team decision: tech-stack.md]
- A thumbs up or down on each answer [AI-proposed: tech-stack.md online metrics]

## Scenarios
| # | Given | When | Then | Proved by |
|---|---|---|---|---|
| S1 | The documents state the timeline milestones | The student asks when the methodology is due | The answer streams and cites the section with a quote found in it | V1 |
| S2 | A question the documents don't cover | They ask it | "That one is for your supervisor" | V2 |
| S3 | The model cites a quote that isn't in the section | The answer ends | It is replaced by the supervisor line | V3 |
| S4 | A thread quiet for longer than the compaction time | The sweep runs | The tail is folded into the summary; the messages stay visible | V4 |
| S5 | A session quiet for longer than the session time | The sweep runs | The stored upload text is deleted; flags and quotes remain | V5 |
| S6 | A question that tells the model to ignore its rules | They ask it | It answers from the documents or gives the supervisor line; it never claims to be something else | V6 |

## Exclusions
- Questions about other programmes or later deliverables [Team decision: roadmap.md]
- Writing or rewriting thesis text [Team decision: ERRC.md]

## Inputs and outputs
- Inputs: the question, the thread's summary and tail, open flags, the document pack
- Outputs: an answer message with checked citations, or the supervisor line; a compaction row per fold

## Data, decisions and evidence
- Summaries never hold the full proposal, only what the conversation said [AI-proposed]
