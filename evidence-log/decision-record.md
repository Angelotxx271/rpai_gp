# Decision record

**Status:** Team decision for Group Project I, recorded on 2026-10-12. Sources: experiment-card.md (decision rule and results), market-research.md section 7 (so-what), ERRC.md (falsifiable hypothesis and validation points)

## Decision

**CONTINUE**, as committed before the test: the Wizard-of-Oz test met its threshold, 6 of 10 (experiment-card.md). Build a working slice with one programme's guidelines loaded, used to run the next test, not the full product

## What the evidence changed

- "Instead of their AI of choice" became instead of it for the pre-meeting check, and alongside it for everything else. Participants 4 and 7 used their own AI alongside the chat and participant 10 did every task in Claude (experiment-card.md; market-research.md section 7)
- TFGPT flags points with the guideline section behind each one and gives no grade or overall verdict. 4 of 10 participants re-checked answers with Blackboard, a friend, Google or their supervisor (experiment-card.md; ERRC.md Eliminate)
- The two-month gap between deliverables is qualified by programme: it comes from the Computer Science programme we heard about, and cadence differs elsewhere (market-research.md section 5)

## Next test

| Field | Content |
|---|---|
| Question | Does TFGPT give the same flags as a general AI for less effort? (ERRC.md falsifier 4, validation point 1) |
| Test | The same piece of TFG work and the same programme guidelines, checked twice: in ChatGPT with the guidelines and the work pasted in, and in a TFGPT stand-in with the guidelines already loaded. Each run records the flags each tool gives, which of them are correct, and the total minutes from opening the tool to the last flag |
| Owner | Every team member runs it once, so the comparison covers several pieces of work |
| Threshold | In each run, TFGPT gives the same flags in fewer total minutes, or better flags (more of the real issues, fewer wrong ones) |
| Stop condition | ChatGPT with only the context pasted in gives the same correct flags in no more total minutes: then TFGPT adds no value (ERRC.md falsifier 4) |
| By | Friday 23 October 2026 |

How the test runs (the stand-in, scoring, who judges a flag, how many runs count) is set out in spikes.md, to be confirmed by the team before the first run

The same runs also give the miss rate against a supervisor (ERRC.md falsifier 3), and a first step checks access to each programme's guidelines (a precondition for falsifier 2); both are in spikes.md

## Would anyone invest?

**The team's answer: yes.** The student and faculty accounts and the Wizard-of-Oz test show a real pain point that needs a solution, and TFGPT is built to be that solution. The funder the team means is IE, as the sponsor of a pilot, not a venture investor

| Part of the answer | Evidence | Status |
|---|---|---|
| Students find out about drift at the meeting and redo the work | interview-evidence.md 01, one Computer Science graduate about his classmates | REPORTED, second-hand; no count of how often it happens |
| Students will do the check in a tool like this instead of their own AI | experiment-card.md: 6 of 10 in one 20-minute session, exactly the bar | OBSERVED once; evidence strength MEDIUM |
| Advisors with many TFGs lack time for each student | interview-evidence.md 05: about 10 TFGs, a few minutes per student, almost two weeks to a first reply (relayed by students); 06 is a contrast case with 2 TFGs | REPORTED, relayed by a team member; no advisor has been asked about TFGPT itself |
| IE already provides AI to everyone | market-sources.md #1, #3, #181 (ChatGPT licences for all students, faculty and staff) | SUPPORTED; who pays is not stated, and whether IE would fund this tool is untested. The same licences are also the strongest argument against: if ChatGPT gives the same flags for the same effort, IE has no reason to fund a second tool (falsifier 4) |

The yes holds only if IE commits to the full maintenance and adoption of the tool (ERRC.md falsifier 2) and the next test shows the same flags for less effort (falsifier 4). Nobody at IE has been asked yet, and money is not estimated (market-research.md section 1)

## What could make us narrow, pivot or stop

Options already in the evidence log, for the team to choose from when a result comes in; none is decided yet

| If this happens | Possible response |
|---|---|
| A general AI with the context pasted in gives the same flags for the same effort (falsifier 4) | Stop TFGPT as a separate check, or pivot to an option ERRC.md set aside: an AI-use record for IE's disclosure rules, or the supervisor view |
| TFGPT misses more than 40% of what a supervisor would flag (falsifier 3) | Narrow the check to what it flags reliably, and re-test before adding more |
| Students don't use it instead of their own AI for the check in real use (falsifier 1) | Change: reframe TFGPT as a complement used alongside their own AI, the CHANGE branch of experiment-card.md |
| IE does not commit to maintaining and adopting it (falsifier 2) | Narrow to one programme or one advisor willing to keep the guidelines current, or stop the IE-backed version |
