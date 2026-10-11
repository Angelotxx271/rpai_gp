# Opportunity (v02, proposed)

**Status:** Proposed successor to opportunity.md for team review, produced by the ERRC run on 2026-10-11. #n refers to a row in market-sources.md; participant numbers refer to the Wizard-of-Oz results in experiment-card.md

**Changes from opportunity.md:**
- The "roughly two-month gap" is qualified by programme in the Pain point, the Need and the How might we, a change the student accepted during the ERRC run: meeting cadence differs by programme (market-research.md section 5), and the two-month figure comes from one Computer Science source. In the Pain point, "two months of work" became "the work since the last meeting"
- Added: current alternatives, the strongest current alternative, competitive factors and market conventions, the value innovation hypothesis, and new open gaps
- Everything else is unchanged. Jobs to Be Done unchanged after market and ERRC review, so there is no jtbd-v02.md

## Pain point
Students work through the gap between TFG deliverables (about two months in the source programme; cadence differs by programme) without knowing whether what they're doing still fulfils the requirements or scope of their topic, and only find out at the deliverable meeting. By then the work since the last meeting can be thrown away, and redoing it eats into the time for the next deliverable, which can stop them delivering on time. Drift can happen at other points too, but the gap between deliverables is where it hurts most.

## User, need, and insight
Final-year IE students doing their TFG, any degree, need to know, before each deliverable meeting, whether their work still fulfils the requirements or scope of their topic, through a failsafe that is not perfect but better than anything else they have, instead of finding out at the next meeting (about two months later in the source programme), because students will use AI no matter what, but they're more concerned with making the work look not-AI than with using it well, even as IE moves to "disclose it, no penalty".

## How might we
How might we help final-year IE students detect and avoid drift from their TFG's requirements and scope during the stretches of work between deliverable meetings (about two months in the source programme; cadence differs by programme)?

## Current alternatives

From market-research.md section 2. That an alternative exists does not show that IE students use it

| Category | Alternative or current approach | What it provides for the job | Evidence or source basis | Important gap |
|---|---|---|---|---|
| Direct competitor | Grammarly AI Grader, Thesify, Mattie (RSM pilot), checkers set up by instructors or publishers | Feedback on a draft against a generic rubric or one the student uploads; Mattie keeps context across drafts | Market (#47 to #67, #189). Use by IE students: UNKNOWN, since no participant or interviewee mentioned any of them | None found that checks against the student's own programme guidelines, keeps context and stays feedback-only. Mattie shows a university may build this itself |
| Indirect substitute | The student's own ChatGPT or Claude; ChatGPT Edu or IE AI Engine provided by IE | Fast, top-model answers; it can do the check only if the student loads the guidelines and the draft | Market (#20, #24, #166). OBSERVED in the Wizard-of-Oz test: 3 of 10 opened their own AI. REPORTED by a team member (one school, unverified) | How well it checks against TFG guidelines is untested. Whether ChatGPT Edu is still live is disputed (#4, #181 against the team member's report) |
| Manual workaround | Blackboard or Campus Online documents, friends, Google, emailing the supervisor, IE Library sessions | Official answers once found; peers as a second check | Market (#104, #106, #107). OBSERVED in the Wizard-of-Oz test: 4 of 10 checked with an official source or a person. REPORTED: a student could not find a guideline document and waited for the mentor (interview-evidence.md 04) | Guidelines are scattered and differ by programme. Whether the re-checks show distrust of a tool is a HYPOTHESIS |
| Doing nothing | Wait for the supervisor's reply or the next meeting; accept rework | Nothing until the meeting | Market (#16, #82, #92, #95, #117). REPORTED second-hand (interview-evidence.md 01, 05) | How often late discovery happens at IE is unknown, and reply times vary by supervisor |

## Strongest current alternative

The general AI the student already has on their own account (ChatGPT, or a paid Claude), plus their own judgement, with the supervisor meeting as the only authoritative check. The manual route is a close second

- **Evidence basis:** chosen by the author on 2026-10-11 (market-research.md section 3). OBSERVED in the Wizard-of-Oz test (n=10, one 20-minute session): 3 of 10 used their own AI and 4 of 10 checked with an official source or a person. REPORTED by a team member (one school, unverified) and second-hand in interview-evidence.md 02. SUPPORTED: 89% of Spanish students who use AI use chat assistants (#166, not IE-specific)
- **Persona input (HYPOTHESIS only):** ai-persona-01 checks work with the same AI that drafted it, and ai-persona-02 drafts, judges and hopes. Both fit this baseline but are not independent evidence of it
- **Limitation:** a small sample and the author's judgement; market sources show what exists, not what IE students choose

## Competitive factors and market conventions

The author's nine factors (market-research.md section 4). The student's own AI scores are proposed by AI on a 0 to 5 scale and still await the team's review; for cost and effort a higher score means more cost or effort

| Factor | What the student receives or gives up | Student's own AI today |
|---|---|---|
| Knows my programme's TFG guidelines without being told | Correct answers without loading documents | 1 |
| Keeps my TFG context between sessions | No re-briefing | 3 |
| Checks scope and method fit before the meeting | Drift caught early | 3 |
| Model quality | Answers as good as top general AI | 5 |
| Speed of an answer | No waiting | 5 |
| Authority | Confidence the supervisor will agree | 1 |
| Fits IE's AI rules | Feedback, not ghostwriting; a disclosure record | 3 |
| Cost to the student | Money | 2 |
| Effort to start | Setup and loading the guidelines | 3 |

**Main trade-offs:**
- No alternative scores high on programme knowledge, authority and speed together
- Every alternative scores 3 or below on keeping the student's context and on checking scope before the meeting
- Authority stays with the supervisor

**Conventions the market takes for granted:**
- The student loads the guidelines themselves
- Each review starts from zero, with one upload per review
- Writing tools draft the text for the student
- Grade estimates are offered even though they carry no standing
- The supervisor is the only real check

## Value innovation hypothesis

From [ERRC.md](ERRC.md). Compared with the student's own general AI, TFGPT is a checker, not a writer:

- **Eliminate:** grade prediction and any overall pass/fail verdict; TFGPT only flags specific guideline and scope points, with the source behind each one
- **Reduce:** writing, to small fixes for flagged passages; TFGPT never drafts sections or the thesis
- **Raise:** programme-guideline knowledge from 1 to 5; TFGPT comes preloaded with the student's current programme TFG guidelines, rubric and dates
- **Create:** proactive drift flags; before each deliverable, TFGPT compares the student's work with their programme's requirements without being asked

Dropping grading and drafting removes the cost of building a grade predictor and likely lowers regulatory, rule and reputation risk (legal advice is needed on the EU AI Act part). Keeping the guidelines up to date and storing students' work are the new costs. The value TFGPT aims for is catching drift before the meeting, which no alternative found in the market scan does unprompted. TFGPT lives alongside the student's own AI rather than replacing it

This remains a hypothesis, not a validated blue ocean or confirmed business model

## Open gaps
- Insight: how students use AI and hide it is a team hypothesis. So far it rests only on informal, second-hand reports (see interview-evidence.md), and it has not been tested
- User: "any degree" is a hypothesis. So far all the evidence comes from Computer Science, and AI habits (who pays for AI) may differ by degree. Not yet tested
- Since v01, the Wizard-of-Oz test included BBA, BAM and BDBA students as well as BCSAI (experiment-card.md), so behaviour evidence no longer comes only from Computer Science. It was one 20-minute session in a simulated tool and does not test the insight or AI payment habits by degree
- Meeting cadence by programme, especially SciTech and Computer Science (market-research.md section 8). jtbd.md still says "two-month gaps"
- Whether a general AI with the guidelines uploaded does the check well enough (ERRC.md validation point 1)
- Whether TFGPT can get, and keep current, each programme's guidelines, rubrics and dates (ERRC.md validation point 2)
- Whether IE students use any direct competitor: UNKNOWN, since no participant or interviewee mentioned one
- Whether ChatGPT Edu is still live at IE, and whether anyone uses IE AI Engine
- Whether AI is allowed in each student's final-project syllabus (#7, #12, #13)
- Willingness to pay, and who would pay; IE or other universities as the buyer is a HYPOTHESIS
- Whether a check-only tool stays outside EU AI Act Annex III 3(b) (legal advice needed)
- "Instead of their AI of choice" (assumptions.md, goals.md, experiment-card.md) against "alongside" (market-research.md section 7): the team decides the wording
