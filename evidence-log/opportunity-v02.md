# Opportunity (v02, proposed)

**Status:** Proposed successor to opportunity.md for team review, produced by the ERRC run on 2026-10-11. #n refers to a row in market-sources.md; participant numbers refer to the Wizard-of-Oz results in experiment-card.md

**Changes from opportunity.md:**
- The "roughly two-month gap" is qualified by programme in the Pain point, the Need and the How might we, a change the student accepted during the ERRC run: meeting cadence differs by programme (market-research.md section 5), and the two-month figure comes from one Computer Science source. In the Pain point, "two months of work" became "the work since the last meeting"
- Added: current alternatives, the strongest current alternative, competitive factors and market conventions, the value innovation hypothesis, and new open gaps
- Revised on 2026-10-12 to match the revised ERRC.md (falsifiable hypothesis, new-market intent, a tenth factor, net effect for the student) and to correct stale or overstated lines found in an independent review
- Everything else is unchanged. Jobs to Be Done unchanged after market and ERRC review, so there is no jtbd-v02.md; jtbd.md notes the cadence difference in its validation gaps

## Pain point
Students work through the gap between TFG deliverables (about two months in the Computer Science programme we heard about; cadence differs by programme) without knowing whether what they're doing still fulfils the requirements or scope of their topic, and only find out at the deliverable meeting. By then the work since the last meeting can be thrown away, and redoing it eats into the time for the next deliverable, which can stop them delivering on time. Drift can happen at other points too, but the gap between deliverables is where it hurts most.

## User, need, and insight
Final-year IE students doing their TFG, any degree, need to know, before each deliverable meeting, whether their work still fulfils the requirements or scope of their topic, through a failsafe that is not perfect but better than anything else they have, instead of finding out at the next meeting (about two months later in the Computer Science programme we heard about), because students will use AI no matter what, but they're more concerned with making the work look not-AI than with using it well, even as IE moves to "disclose it, no penalty".

## How might we
How might we help final-year IE students detect and avoid drift from their TFG's requirements and scope during the stretches of work between deliverable meetings (about two months in the Computer Science programme we heard about; cadence differs by programme)?

## Current alternatives

From market-research.md section 2. That an alternative exists does not show that IE students use it

| Category | Alternative or current approach | What it provides for the job | Evidence or source basis | Important gap |
|---|---|---|---|---|
| Direct competitor | Grammarly AI Grader, Thesify, Mattie (RSM pilot), checkers set up by instructors or publishers | Feedback on a draft against a generic rubric or one the student uploads; Mattie keeps context across drafts | Market (#47 to #67, #189). Use by IE students: UNKNOWN, since no participant or interviewee mentioned any of them | None found that checks against the student's own programme guidelines, keeps context and stays feedback-only. Mattie shows a university may build this itself |
| Indirect substitute | The student's own ChatGPT or Claude; ChatGPT Edu or IE AI Engine provided by IE | On the student's own account, fast top-model answers; it can do the check only if the student loads the guidelines and the draft. IE-provided AI is reported as outdated and little used (team member's report, unverified) | Market (#20, #24, #166). OBSERVED in the Wizard-of-Oz test: 3 of 10 opened their own AI. REPORTED by a team member (one school, unverified) | How well it checks against TFG guidelines is untested. Whether ChatGPT Edu is still live is disputed (#4, #181 against the team member's report) |
| Manual workaround | Blackboard or Campus Online documents, friends, Google, emailing the supervisor, IE Library sessions | Official answers once found; peers as a second check | Market (#104, #106, #107). OBSERVED in the Wizard-of-Oz test: 4 of 10 checked with an official source or a person. REPORTED: a student could not find a guideline document and waited for the mentor (interview-evidence.md 04) | Guidelines are scattered and differ by programme. Whether the re-checks show distrust of a tool is a HYPOTHESIS |
| Doing nothing | Wait for the supervisor's reply or the next meeting; accept rework | Nothing until the meeting | Market (#16, #82, #92, #95, #117). REPORTED second-hand (interview-evidence.md 01, 05) | How often late discovery happens at IE is unknown, and reply times vary by supervisor |

## Strongest current alternative

The general AI the student already has on their own account (ChatGPT, or a paid Claude), plus their own judgement, with the supervisor meeting as the only authoritative check. The manual route is a close second

- **Evidence basis:** chosen by the author on 2026-10-11 (market-research.md section 3). OBSERVED in the Wizard-of-Oz test (n=10, one 20-minute session): 3 of 10 used their own AI and 4 of 10 checked with an official source or a person. REPORTED by a team member (one school, unverified) and second-hand in interview-evidence.md 02. SUPPORTED: 89% of Spanish students who use AI use chat assistants (#166, not IE-specific)
- **Persona input (HYPOTHESIS only):** ai-persona-01 checks work with the same AI that drafted it, and ai-persona-02 drafts, judges and hopes. Both fit this baseline but are not independent evidence of it
- **Limitation:** a small sample and the author's judgement; market sources show what exists, not what IE students choose

## Competitive factors and market conventions

The author's nine factors plus the tenth added by the ERRC Create move (market-research.md section 4). The student's own AI scores are proposed by AI on a 0 to 5 scale and still await the team's review; for cost and effort a higher score means more cost or effort. The other alternatives' scores and TFGPT's target line are in market-research.md section 4 and value-curve.svg

| Factor | What the student receives or gives up | Student's own AI today |
|---|---|---|
| Knows my programme's TFG guidelines without being told | Correct answers without loading documents | 1 |
| Keeps my TFG context between sessions | No re-briefing | 3 |
| Checks scope and method fit before the meeting | Drift caught early | 3 |
| Starts the check without being asked (new, from ERRC Create) | Drift caught without having to remember to ask | 1 |
| Model quality | Answers as good as top general AI | 5 |
| Speed of an answer | No waiting | 5 |
| Authority | Confidence the supervisor will agree | 1 |
| Fits IE's AI rules | Feedback, not ghostwriting; a disclosure record | 3 |
| Cost to the student | Money | 2 |
| Effort to start | Setup and loading the guidelines | 3 |

**Main trade-offs:**
- No alternative scores high on programme knowledge, authority and speed together
- Every alternative scores 3 or below on keeping the student's context and on checking scope before the meeting, and 1 or below on starting the check without being asked
- Authority stays with the supervisor

**Conventions the market takes for granted** (AI-synthesised from market-research.md section 4, confirmed by the student):
- The student loads the guidelines themselves
- Grammarly and Thesify start each review from one upload (#49, #51, #53), and Mattie keeps context across drafts but only at RSM (#47); a general AI keeps context through projects or memory the student sets up (#20, #24)
- The student starts every check (scheduled tasks exist in ChatGPT Plus, #18; none found used for a guideline check, though this was not searched for specifically)
- Writing tools draft the text for the student
- One direct competitor offers a grade estimate even though it carries no standing (#53, #189)
- The supervisor is the only real check

## Value innovation hypothesis

From [ERRC.md](ERRC.md).

**Intent:** not to win the AI thesis-helper market against ChatGPT and Claude, but to open a different space, the **pre-meeting check**, between the supervisor (authoritative but slow) and the student's own AI (fast, but unaware of the programme unless the student loads it in). **Non-customers it aims to bring in (HYPOTHESIS):** students who will not use AI for the pre-meeting check, a smaller group the team says exists (nearest support, not TFG-specific: #38, #12), and students who will keep using their own option as well

Compared with the student's own general AI, TFGPT is a checker, not a writer:

- **Eliminate:** grade prediction and any overall pass/fail verdict; TFGPT flags specific guideline and scope points with the source behind each one and may suggest a fix for a flagged passage
- **Reduce:** writing, to small fixes for flagged passages; TFGPT never drafts sections or the thesis
- **Raise:** programme-guideline knowledge from 1 to 5 and keeping the student's context from 3 to 5; preloaded guidelines, rubric and dates, with no uploading and no re-briefing, in one central place for everything TFG-related
- **Create:** a check TFGPT starts itself; before each deliverable date it checks the student's work against their programme's requirements without being asked

**Net effect for the student:** no uploading, no re-briefing an AI and one central place for everything TFG-related, plus a check that starts itself; no grade, verdict or drafting inside TFGPT, and a second tool next to their own AI. **Net effect for TFGPT:** no grade predictor to build or calibrate (an avoided cost) and shorter generations than drafting (AI inference), against new costs to keep the guidelines current, store students' work and run scheduled checks; whether the total falls is untested. TFGPT is used instead of the student's AI of choice for the check and lives alongside it for everything else

**We are wrong if:** (1) students don't end up using TFGPT instead of their AI of choice for the pre-meeting check; (2) IE does not commit to the full maintenance and adoption of the tool; (3) TFGPT misses more than 40% of what a supervisor would otherwise flag as not ideal in the TFG; (4) the check can be copy-pasted into a different LLM and it does the same, in which case TFGPT has no value. "Does the same" means the same flags for the same effort; ERRC.md sets out how each is measured

This remains a hypothesis, not a validated blue ocean or confirmed business model

## Open gaps
- Insight: how students use AI and hide it is a team hypothesis. So far it rests only on informal, second-hand reports (see interview-evidence.md), and it has not been tested. "Disclose it, no penalty" is the team's paraphrase: IE's guidelines require disclosure and treat undisclosed or prohibited use as misconduct, and the AI rules differ per syllabus (market-sources.md #7, #8, #12, #13, #78)
- User: "any degree" is a hypothesis. The JTBD evidence comes from Computer Science (interview-evidence.md 01, 02, and 04 on findability), 03 is a Data student, and 05 and 06 are advisors; since opportunity.md (2026-09-21), the Wizard-of-Oz test (n=10: 5 BCSAI, 2 BBA, 2 BDBA, 1 BAM) added behaviour from other degrees, but it was one 20-minute session in a simulated tool and does not test the insight or AI payment habits by degree
- Meeting cadence by programme, especially SciTech and Computer Science (market-research.md section 8). jtbd.md keeps "two-month gaps" in its statement and notes the difference in its validation gaps
- Whether a general LLM with the guidelines and work pasted in does the check as well as TFGPT (ERRC.md validation point 1)
- Whether IE commits to maintaining and adopting TFGPT, and whether TFGPT can get, and keep current, each programme's guidelines, rubrics and dates (ERRC.md validation point 2)
- Whether TFGPT misses more than 40% of what the supervisor would otherwise flag as not ideal (ERRC.md validation point 3)
- Whether students do the check in TFGPT instead of their AI of choice in real use, not only in one session (ERRC.md validation point 4)
- Whether students given cited flags with no verdict can tell if they're ready (ERRC.md validation point 5)
- Whether IE counts a tool that flags points and may suggest a fix, with no grade and no drafting, as "feedback" (ERRC.md validation point 6)
- Whether students read and act on flags TFGPT raises unprompted, or mute them (ERRC.md validation point 7)
- Whether IE students use any direct competitor: UNKNOWN, since no participant or interviewee mentioned one
- Whether ChatGPT Edu is still live at IE, and whether anyone uses IE AI Engine
- Whether AI is allowed in each student's final-project syllabus (#7, #12, #13)
- Willingness to pay, and who would pay; IE or other universities as the buyer is a HYPOTHESIS
- Whether a tool that flags and suggests fixes but never grades stays outside EU AI Act Annex III 3(b) (legal advice needed)
- "Instead of their AI of choice" and "alongside" are reconciled as instead for the check, alongside for everything else (ERRC.md); assumptions.md records it
