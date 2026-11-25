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
| Advisor's corrections on the submitted proposal | 17 written comments over three rounds of drafts, then approved: 9 on draft 1, including one methodology point and the reference format; 5, all minor, on draft 2 (punctuation, one word, long sentences, layout); 3 on draft 3. Which drafts were checked with the stand-in before sending was not recorded | 9, mostly major: the methodology, the research question and similar |
| Her original proposal run through the stand-in afterwards | | The stand-in flagged all 9 of the advisor's points |
| Her advisor on the version revised with the stand-in | | Only small fixes |

**What it shows:** with the programme documents and fixed instructions preloaded, the stand-in caught every major point one advisor raised, and team member 2's version revised with it came back with only small fixes. For ERRC.md falsifier 3, the stand-in missed 0 of 9 advisor points on one proposal

**Correction (2026-11-24):** this section first said team member 1's advisor made 4 corrections, all minor. The shared draft holds 17 written comments over three rounds, which the team member confirmed are the full set, so the claim that work checked with the stand-in came back from both advisors with only minor corrections is withdrawn. Protocol v2 below scores the stand-in against all three rounds

**What it does not show:**
- Two students, two programmes, two advisors and two topics: part of the difference can come from the person or the topic, not the tool
- A team member built the stand-in, and the team judged that its flags matched the 9 points after the advisor's comments were known, not blind
- 9 advisor points is below the 15 the rules below need before the miss rate is read: it is a first data point, not a result
- Team member 2's route had only part of the documents and no instructions, so it does not test a student who pastes everything into a general AI (falsifier 4)
- Team members on their own work: feasibility, not demand

Status: OBSERVED by the team on its own work, n = 2; evidence strength LOW as value evidence. Both runs are AI use on a TFG and go in each member's TFG AI declaration

## Advisor comparison (protocol v2, accepted on 2026-11-24 before any run)

Owner Angelotxx271; scorer and second checker as in decision-record.md. Results by Friday 27 November 2026. Reported separately from v1 runs. Proposed by AI, accepted by the student on 2026-11-24

**Question:** on one real proposal with three rounds of written supervisor comments, how much of what the supervisor flagged does each route find, round by round? It reads falsifier 3 (the 40% miss rate) and the flags half of falsifier 4. The effort half (minutes) stays with Spike A

**Material (private, team folder outside the repo):** four versions of one BDBA Full Proposal (rounds 1 to 3 and the approved version) and an answer key of 18 points written from the supervisor's written comments: 10 from round 1, 5 from round 2, 3 from round 3; 4 G and 14 C. The student confirmed the key before any run. The comments themselves never go into any tool, the judge included

| Route | What the model gets | Maps to |
|---|---|---|
| C0, own AI as usual | The proposal and one plain request to check it before sending it to the supervisor, then one follow-up | The usual route, with no documents |
| C1, own AI with everything pasted | Stand-in instructions v1, the merged guidelines (template, syllabus Full Proposal section and APA rule, Module 1 lessons 2 to 6), the topic sentence, the work, then the v1 follow-up | Arm B |
| C2, TFGPT stand-in | Instructions v1 and every programme document preloaded, plus the student's two meeting summaries (names replaced by roles), then the topic, the work and the follow-up | Arm A |

**Engines:** Claude Opus 5.5 (Claude Code CLI with no tools, project files or memory), GLM 5.3 and a Mistral model (Mistral's API), and a Qwen model on a team member's own computer. Same prompt text for every engine, default sampling, 3 repeats per cell: 144 runs. Each run records its model ID, prompt hash, tokens, seconds and cost

**Amendment 1 (accepted by Angelotxx271 on 2026-11-25, before any run):** five engines, 180 runs. Claude Opus 5.5 (effort medium) and Claude Sonnet 5.5 through the Anthropic API instead of the CLI; GLM 5.3 (`zai-glm-5-3`) and Mistral Large 4 (`mistral-large-4`) on Mistral's API; Qwen 3.6 35B-A3B through Ollama on the team member's RTX 5070. A truncated, refused or empty answer is a failed run, rerun and never scored. It also writes down how the harness reads the decision rules where this protocol leaves them open, for example that falsifier 4's stand-in is C2 on Claude Opus 5.5 for every route. The harness, its tests and the amendment are public in `prototype/advisor-spike/`; the material stays private

**Scoring:** a blind first-pass judge (Claude Sonnet 5.5, one call per review, no engine or route label) matches each review's flags to the key points whose passage is in that version: same passage and same problem; when in doubt, no match. Every other flag is classed correct, wrong or taste. The scorer and second checker then score blind sheets; disagreements count as not matched. The headline counts are theirs. If the judge and the people disagree on more than 1 point in 5, only the runs people scored are reported

**Decision rules:**
- A point counts as caught in a cell when at least 2 of its 3 repeats catch it
- **Falsifier 3:** pooled over rounds 1 to 3 (18 points), the stand-in (C2) on Claude Opus 5.5 misses more than 40% → falsifier 3 holds: narrow the check (decision-record.md). The G-only rate is reported beside it and not read alone (4 points)
- **Falsifier 4, flags half:** per round, a general route (C0 or C1, any engine) gives the same flags as the stand-in when C(route) ≥ C(stand-in) − 1 and W(route) ≤ W(stand-in) + 1, with C = K + E as above. Same flags in at least 2 of 3 rounds → the flags half holds for that route, and falsifier 4 then turns on effort alone
- **Noise:** if a cell's K varies by more than 1 across its repeats, a difference of 1 between routes counts as the same
- **Approved version:** flags are counted with no threshold, to show how much a route over-flags work the supervisor accepted
- Also reported: early catches (a point the supervisor raised in a later round whose passage was already there), and tokens, time and cost per run for the cost benchmark

**Fingerprints:** SHA-256 of the private files, so anyone given them can check the rules and key came before the results

| File | SHA-256 |
|---|---|
| answer-key.md | `ec2fc84eaf51ef5225187a376b42c94081b06592a0aef081b1e654d565592f6c` |
| protocol-v2.md | `2681f93c6c16f9e9057c10c1f3e4c9b3b4453d1ba01310d551114286e68e3b99` |
| protocol-v2-amendment-1.md (public, `prototype/advisor-spike/`) | `f30501b1b0a8ac4830b8df95eabf2c4380b39830d25836865b7d9c593668ead6` |
| Prompts, first 12 characters | C0: `1f5943b97318` `9cc36aa8441c` `36a59c87574a` `f9d0afe24506` · C1: `53ec74b8aff1` `0ef86fb3019f` `ece414baec1d` `bf1047281bba` · C2: `ce1a68528674` `60671ac4feb3` `e9d4289d472a` `1233ac6c3c58` (rounds 1, 2, 3, approved) |

**What it can't show:** one student, one topic, one supervisor and one proposal, so the 18 points aren't independent. The supervisor's comments are a floor, not every problem in the text. It measures no effort, real use or demand, and says nothing about falsifiers 1 and 2. Claude Code built the key and the pipeline after reading the comments; the student confirmed the key, and the arm prompts come from text written before (instructions v1 above)

### Results, protocol v2

Run on 2026-11-25 on harness commit `8b8c8cf` (`prototype/advisor-spike/`). These are the blind judge's first-pass counts (Claude Sonnet 5.5); the scorer's and second checker's counts are the headline and are still to come. A point counts as caught when at least 2 of 3 repeats catch it. Correct extra and wrong are means per review over rounds 1 to 3; flags on the approved version are a mean per review. Tokens are both turns together. The Mistral API credits ran out during the C2 runs, so 7 runs failed with "API budget exhausted" and are not scored; the cells they leave short are marked and not read by the decision rules. Per-run detail: `prototype/advisor-spike/results/`

| Engine | Route | Caught round 1 / 2 / 3 | Pooled miss rate | Correct extra | Wrong | Flags on approved version | Tokens and cost per run | Label |
|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 | C0 own AI | 2 / 2 / 1 (of 10 / 5 / 3) | 72% (13 of 18) | 6.4 | 0.6 | 32 | 7k in / 8k out, $0.17 | Judge first pass; human scoring pending |
| Claude Opus 5.5 | C1 everything pasted | 4 / 0 / 2 (of 10 / 5 / 3) | 67% (12 of 18) | 7.1 | 1.3 | 30 | 43k in / 21k out, $0.47 | Judge first pass; human scoring pending |
| Claude Opus 5.5 | C2 stand-in | 3 / 2 / 2 (of 10 / 5 / 3) | 61% (11 of 18) | 8.6 | 1.1 | 29 | 103k in / 21k out, $0.54 | Judge first pass; human scoring pending |
| Claude Sonnet 5.5 | C0 own AI | 3 / 2 / 3 (of 10 / 5 / 3) | 56% (10 of 18) | 6.4 | 0.7 | 36 | 7k in / 9k out, $0.10 | Judge first pass; human scoring pending |
| Claude Sonnet 5.5 | C1 everything pasted | 3 / 1 / 1 (of 10 / 5 / 3) | 72% (13 of 18) | 6.4 | 0.9 | 24 | 42k in / 28k out, $0.30 | Judge first pass; human scoring pending |
| Claude Sonnet 5.5 | C2 stand-in | 3 / 0 / 1 (of 10 / 5 / 3) | 78% (14 of 18) | 7.4 | 0.6 | 24 | 102k in / 34k out, $0.39 | Judge first pass; human scoring pending |
| GLM 5.3 | C0 own AI | 3 / 0 / 1 (of 10 / 5 / 3) | 78% (14 of 18) | 4.2 | 1.3 | 35 | 5k in / 24k out, not yet priced | Judge first pass; human scoring pending |
| GLM 5.3 | C1 everything pasted | 2 / 1 / 0 (of 10 / 5 / 3) | 83% (15 of 18) | 4.6 | 1.1 | 16 | 28k in / 70k out, not yet priced | Judge first pass; human scoring pending |
| GLM 5.3 | C2 stand-in | 4 / 2 / 0 (of 10 / 5 / 3) | 67% (12 of 18) | 4.3 | 0.4 | – (1 of 3 repeats) | 66k in / 73k out, not yet priced | Judge first pass; approved version short: credits ran out |
| Mistral Large 4 | C0 own AI | 4 / 1 / 1 (of 10 / 5 / 3) | 67% (12 of 18) | 1.8 | 3.9 | 25 | 5k in / 15k out, not yet priced | Judge first pass; human scoring pending |
| Mistral Large 4 | C1 everything pasted | 1 / 0 / 0 (of 10 / 5 / 3) | 94% (17 of 18) | 4.4 | 3.6 | 19 | 28k in / 29k out, not yet priced | Judge first pass; human scoring pending |
| Mistral Large 4 | C2 stand-in | 1 / 0 / – (of 10 / 5 / –) | 93% (14 of 15, rounds 1 and 2) | 4.2 | 2.5 | – (0 of 3 repeats) | 65k in / 31k out, not yet priced | Judge first pass; round 3 and approved version short: credits ran out |
| Qwen 3.6 35B-A3B (local) | C0 own AI | 0 / 0 / 1 (of 10 / 5 / 3) | 94% (17 of 18) | 0.4 | 6.1 | 18 | 5k in / 7k out, $0 (local), 1.6 min | Judge first pass; human scoring pending |
| Qwen 3.6 35B-A3B (local) | C1 everything pasted | 1 / 0 / 0 (of 10 / 5 / 3) | 94% (17 of 18) | 2.9 | 3.7 | 14 | 28k in / 13k out, $0 (local), 3.1 min | Judge first pass; human scoring pending |
| Qwen 3.6 35B-A3B (local) | C2 stand-in | 1 / 1 / 0 (of 10 / 5 / 3) | 89% (16 of 18) | 2.3 | 3.3 | 11 | 68k in / 13k out, $0 (local), 3.5 min | Judge first pass; human scoring pending |

**Reading, provisional (judge first pass only; it changes no decision until the people's counts are in):**
- **Falsifier 3:** the stand-in (C2) on Claude Opus 5.5 missed 11 of the 18 points (61%), above the 40% line. If the people's counts agree, falsifier 3 holds and the check is narrowed (decision-record.md)
- **Falsifier 4, flags half:** Claude Opus 5.5 with everything pasted (C1) and Claude Sonnet 5.5 used as usual (C0) gave the same flags as the stand-in in 2 of 3 rounds, so for those two routes the flags half holds and falsifier 4 would turn on effort alone. Opus used as usual (C0) and Sonnet with everything pasted (C1) matched in 1 round, and the GLM and Mistral routes in none
- Every route also raised correct problems the supervisor didn't comment on (1.8 to 8.6 per review), and flagged the approved version 16 to 36 times per review
- **Local engine:** Qwen 3.6 35B-A3B on one RTX 5070 (12 GB) caught 1 or 2 of the 18 points on every route (89 to 94% missed) and made the most wrong flags (3.3 to 6.1 per review). At about 1.6 to 3.5 minutes a run it costs nothing per call (1.7 hours for all 36), but on this proposal it is not a candidate engine for the check
- Claude cost $23.80 for 72 runs; judging all 173 scored runs cost $13.13; GLM and Mistral costs come from the Mistral console

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
- Field comparison: "Two of us, two advisors: the stand-in caught all 9 of one advisor's points. Two people, so it shows the mechanism works, not that students want it" (the line first added that work checked with it came back with only minor corrections, withdrawn on 2026-11-24)
