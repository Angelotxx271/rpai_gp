# Spikes

**Status:** Protocol for the team's technical spikes, written on 2026-10-12 before any run. A spike tests feasibility on the team's own work. It does not prove that students want TFGPT, so as value evidence it is LOW. Sources: ERRC.md (falsifiers 2 to 4, validation points 1 to 3) and decision-record.md (next test)

## Why these three

| Spike | Roadblock it checks | ERRC.md falsifier | Decision it can change |
|---|---|---|---|
| A. Same flags, less effort | Does a general AI given the same context already do the check as well, for the same effort? | 4 | Stop or pivot |
| B. Miss rate | Does the check catch what a supervisor flags as not ideal? | 3 | Narrow the check |
| C. Getting the guidelines | Are each programme's guidelines, rubric and dates available as usable text? | Precondition for 2 | Blocker for the working slice |

## Before the first run

1. Freeze the stand-in instructions below as v1, with today's date. Any later change is v2, and v1 and v2 runs are reported separately
2. Commit this file before run 1, so the git timestamp shows the rules came before the results

**Stand-in instructions v1** (pasted as the project instructions in Arm A and as the first message in Arm B):

> You check a final-year student's TFG work against the attached programme guidelines and their topic. List each point where the work does not fit the guidelines or the topic. For each point, quote the passage, cite the guideline section, and say in one sentence what doesn't fit. Don't give a grade or an overall verdict, and don't rewrite the text.

## Each member, before the timer starts

- **IE's AI rules:** check the AI line in your TFG syllabus (2 minutes). If AI is banned or it's unclear, don't put TFG work into any tool: do Spike C only, or ask your supervisor first
- **The piece of work:** the most recent piece your supervisor commented on in writing, with at least 3 written comments. Use the clean version you sent, with no comments or tracked changes, at most 10 pages, and no section with personal, interview or company data
- **The answer key:** from the written comments only, one line per point, each tagged G (guidelines, format, scope or a deliverable rule) or C (content or taste). Timestamp it before opening any tool. Never paste the supervisor's comments into a tool
- **Settings:** training off ("Improve the model for everyone"), memory and custom instructions off. Same account, plan and model in both arms; write the model name down
- **Order:** the first run does Arm A first, then Arm B, so any learning favours ChatGPT and works against TFGPT. The other members alternate the order

## Spike C: getting the guidelines (run first, 30-minute box)

Find your programme's current TFG guidelines, rubric and deliverable dates on Campus Online or Blackboard. For each record: found or not, where, format (copyable text or a scan), version or academic year, who publishes it, minutes to find. "Current" means it states 2026-27 or is the latest published version; "usable" means the text can be copied. Merge the three into one text document for the stand-in

Spike C shows what a student can find. It does not show whether IE will commit (falsifier 2), which stays open until someone at IE is asked

## Spike A: same flags, less effort

**Setup, once per programme (about 10 minutes):** a ChatGPT project with the merged guidelines document and the v1 instructions. On an account without ChatGPT projects, use a Claude project and run both arms in Claude

- **Arm A, TFGPT stand-in:** open the project, paste your work and one sentence stating your topic, send "Check this". At most one follow-up: "Anything else that doesn't fit the guidelines?". 15-minute cap
- **Arm B, plain chat:** a temporary chat on the same model. Paste the v1 instructions, the merged guidelines, the same work and the same topic sentence, then the same single follow-up. 15-minute cap
- **Timing:** a lap stopwatch per arm with laps for finding, pasting or uploading, prompting, waiting for the model and reading. Minutes M = student-active minutes, every lap except waiting. Arm B is reported twice: as run, and with the cold find time from Spike C added
- **Optional noise check (3 minutes):** repeat Arm A's first message in a fresh chat (A2), untimed, and score it the same way

## Scoring (about 10 minutes per run)

- Paste both flag lists into one table as List 1 and List 2 in random order with the same formatting, and score before checking which is which
- **Match:** a flag matches a key point when it points at the same passage and the same problem. When in doubt it is not a match, for both lists
- **Correct extra flag:** the cited guideline section exists and the passage really fails it. **Wrong flag:** the section doesn't exist or is misquoted, or the passage meets it. Taste comments are not counted
- A second teammate repeats the match step from the answer key and the flag lists only. Disagreements count as not matched
- **Per list:** K = key points caught, E = extra correct flags, C = K + E, W = wrong flags, M = student-active minutes, S = steps

## Decision rules (proposed by AI, accepted by the student on 2026-10-12 before any run; the team can still change them before run 1)

**Each run:**
- **A wins** when C(A) ≥ C(B) − 1, W(A) ≤ W(B) + 1, and A saves at least 2 minutes and at least 25% of M(B). A also wins on better flags when C(A) ≥ C(B) + 2 and W(A) ≤ W(B)
- **B holds**, the stop case in decision-record.md, when C(B) ≥ C(A) − 1 and M(B) ≤ M(A) + 1
- Anything else is **mixed**
- If A2 differs from A by more than 1 correct flag, a difference of 1 between A and B counts as the same

**Over all runs (at least 4):**
- **Continue** if A wins in at least 4 of 5 runs
- **Stop or pivot** (falsifier 4; options in decision-record.md) if B holds in at least 3 of 5
- Otherwise **inconclusive**: TFGPT has not been shown to add value; add runs before 23 October

**Spike B, pooled over all runs:** miss rate = key points the stand-in missed ÷ all key points, reported with the number of points N, and the G-only rate beside it. Falsifier 3 holds above 40%. Read it only once N is at least 15; below that, run the stand-in alone on more commented pieces (about 10 minutes each)

## Field comparison (run before this protocol was written)

Two team members, their own TFG proposals, over a two-week stretch before 2026-10-12. Both used Claude with Opus 5.5. The judges were their own advisors (two advisors), through their corrections on the proposals as submitted

| | Team member 1 (Data) | Team member 2 (Computer Science) |
|---|---|---|
| How the proposal was checked | TFGPT stand-in: a Claude project with all the programme documents and context, and instructions never to write sentences, only to give guidance and flag what might be wrong. All the text came from the student | The usual route: a plain Claude chat with no instructions, and only the documents she could find |
| Advisor's corrections on the submitted proposal | 4, all minor: two punctuation fixes, one word choice, and one passage to simplify because it was too technical | 9, mostly major: the methodology, the research question and similar |
| Her original proposal run through the stand-in afterwards | | The stand-in flagged all 9 of the advisor's points |
| Her advisor on the version revised with the stand-in | | Only small fixes, like team member 1's |

**What it shows:** with the programme documents and fixed instructions preloaded, the stand-in caught every major point one advisor raised, and work checked with it came back from two advisors with only minor corrections. For ERRC.md falsifier 3, the stand-in missed 0 of 9 advisor points on one proposal

**What it does not show:**
- Two students, two programmes, two advisors and two topics: part of the difference can come from the person or the topic, not the tool
- A team member built the stand-in, and the team judged that its flags matched the 9 points after the advisor's comments were known, not blind
- 9 advisor points is below the 15 the rules below need before the miss rate is read: it is a first data point, not a result
- Team member 2's route had only part of the documents and no instructions, so it does not test a student who pastes everything into a general AI (falsifier 4)
- Team members on their own work: feasibility, not demand

Status: OBSERVED by the team on its own work, n = 2; evidence strength LOW as value evidence. Both runs are AI use on a TFG and go in each member's TFG AI declaration

## Results

### Spike C

| Run | Programme | Guidelines | Rubric | Dates | Format | Version | Minutes to find |
|---|---|---|---|---|---|---|---|

### Spikes A and B

| Run | Programme | Model | Stand-in | Order | Key points G / C | K A / B | E A / B | W A / B | M A / B (B with find) | Steps A / B | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|

## What goes where

- **Public, this file:** run numbers (Run 1 to 5), programme code, section type and pages, the counts, minutes, model, labels. No topic, no supervisor name, no quoted comments or flags
- **Private, a team folder outside the repo:** the work, the supervisor's comments, the answer key, the flag lists and the screenshots, available to the professor on request
- **AI use:** each run is AI use on your TFG. Add a line to your own TFG AI declaration (tool, model, flags only, no text adopted) and a row to ai-usage-log.md

## How to present it on Tuesday

- Spike A: "It asks only whether plain ChatGPT, given the same instructions and guidelines, gives the same flags for the same effort. It is a feasibility check on our own work, not proof that students want TFGPT"
- After one run: "Protocol and rules committed on [date]; one run done to test the procedure; results due 23 October; each outcome maps to continue, narrow, pivot or stop". One run is never shown as a pass or a stop
- Spike C: "Findable by a student in [n] programmes; whether IE commits is a separate question"
- Field comparison: "Two of us, two advisors: the stand-in caught all 9 of one advisor's points, and work checked with it came back with only minor corrections. Two people, so it shows the mechanism works, not that students want it"
