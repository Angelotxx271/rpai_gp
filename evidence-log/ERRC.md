# Eliminate-Reduce-Raise-Create Grid

**Status:** Confirmed value innovation hypothesis requiring evidence

**Sources:** Run on 2026-10-11 with the course ERRC prompt (downloads/ai-prompt-ERRC.md). Baseline from market-research.md sections 2 to 4; context from opportunity.md, jtbd.md, assumptions.md, experiment-card.md and personas/ai-persona-01 to 04. #n refers to a row in market-sources.md; participant numbers refer to the Wizard-of-Oz results in experiment-card.md. The student chose every strategic move and confirmed every cell, mostly by selecting from AI-proposed options

**Target user:** Final-year IE students doing their TFG, any degree ("any degree" is a hypothesis; see opportunity-v02.md)

**Job to Be Done:** When final-year IE students work on their TFG through two-month gaps between deliverable meetings without knowing whether they're on track, finding out at a meeting that the last two months of work were faulty prompts them to seek a way to go into each meeting already knowing their work meets what's required, so they can move on to the next phase

**Strongest current alternative:** The general AI the student already has on their own account (ChatGPT, or a paid Claude), plus their own judgement, with the supervisor meeting as the only authoritative check. The manual route (Blackboard or Campus Online, friends, the supervisor by email) is a close second

**Evidence basis for the baseline:** Chosen by the author on 2026-10-11 (market-research.md section 3). OBSERVED in the Wizard-of-Oz test: 3 of 10 used their own AI and 4 of 10 checked with an official source or a person (one 20-minute session, n=10). REPORTED by a team member about classmates in one technical school (unverified) and second-hand in interview-evidence.md 02. SUPPORTED: 89% of Spanish students who use AI use chat assistants (#166, not IE-specific). Limitation: a small sample and the author's judgement; market sources show what exists, not what IE students choose

## ERRC Grid

| Action | Strategic move | Assumption challenged | Cost effect | Buyer value effect | Evidence status | What must be verified |
|---|---|---|---|---|---|---|
| Eliminate | Eliminate grade prediction and any overall pass/fail verdict: TFGPT only flags specific guideline and scope points, with the source behind each one | That an overall verdict ("this is fine") is more useful than knowing exactly which guideline or scope point the work does or doesn't fit | Lower: no need to collect real grades or calibrate a predictor for each programme and supervisor; likely lower regulatory and liability risk by avoiding the clearest "evaluating learning outcomes" case under the EU AI Act (#194–#196), though whether a check-only tool also stays outside the rules is UNKNOWN and needs legal advice | Higher: no false reassurance from a grade that the supervisor may not share, so there's less risk of being caught out at the meeting | Plausible hypothesis: the market side is supported (#189; #16, #82), but no student has been asked whether they'd miss a grade, and the EU AI Act benefit is directional only | With students: give them cited point-by-point flags with no verdict, and see whether they can tell if they're ready or keep asking "so is it OK?" |
| Reduce | Reduce writing to small, flagged-point help: TFGPT may suggest how to fix a specific flagged passage, but never drafts sections or the thesis | That students need one tool to both write and check (participant 7 already split it: Claude generated, the copilot checked) | Lower rule and reputation risk: TFGPT stays on the "feedback" side of IE's AI guidelines (#76) and avoids becoming a ghostwriting tool, which matters for IE backing (assumptions.md Area 3) | Higher: the student gets a concrete fix for each flagged point without the work being written for them, so they still own the text they'll have to defend and disclose (#8, #78) | Plausible hypothesis: IE's rules are evidence-supported (#8, #76, #78) and the write-elsewhere, check-here split was observed once (participant 7); whether students value owning the text, and whether IE sees this as lower risk, is untested | With IE staff or supervisors: whether a flagged-point-only tool counts as "feedback" under IE's AI guidelines and makes IE more willing to back it |
| Raise | Raise programme-guideline knowledge from 1 to 5: TFGPT comes preloaded with the student's current programme TFG guidelines, rubric and dates, with no uploading | That a general AI with a rubric uploaded is "good enough" for programme-specific questions (market-research.md section 6, Substitution); how well it actually checks is untested | Higher risk: an out-of-date guideline gives a confident wrong answer, so TFGPT needs a check that its documents are current | Higher: less searching and less conflicting advice (participant 3's classmates disagreed on format; the person behind ai-persona-03 found a key document only through a friend) | Evidence-supported for the problem (#104, #106; participant 3; ai-persona-03 episode); plausible hypothesis for the value | With IE: whether TFGPT can get current guidelines, rubrics and dates for each programme from Campus Online, and who keeps them up to date |
| Create | Create proactive drift flags: before each deliverable, TFGPT compares the student's work with their programme's requirements without being asked, and flags drift before the meeting | That checking is something the student starts: today checks happen only when the student remembers or worries enough to ask, even when the guidelines are at hand | Higher for TFGPT: it has to store the student's work or topic and run checks on a schedule, not only when asked, which brings new privacy and storage exposure and more model runs | Higher: drift is caught between meetings without the student having to think of asking, so there's less risk of finding out at the meeting and redoing the work (the Push in jtbd.md) | Plausible hypothesis: late discovery is reported second-hand (interview-evidence 01) and not knowing what to ask is one first-hand episode (ai-persona-03); no alternative offering unprompted flags was found; whether students want them and whether TFGPT detects drift accurately are untested | With supervisors: whether TFGPT's drift flags match what the supervisor would have raised at the meeting (accuracy) |

## Value innovation hypothesis

Compared with the student's own general AI, TFGPT is a checker, not a writer:

| | Student's own AI | TFGPT |
|---|---|---|
| Writing | Drafts freely | Writes only small fixes to flagged points |
| Grading | Can estimate a grade if asked | Never grades or gives an overall verdict |
| Programme knowledge | Only if the student uploads the guidelines | Preloaded with the student's programme guidelines, rubric and dates |
| Who starts the check | Waits to be asked | Flags drift before each deliverable without being asked |

- **What TFGPT drops:** grading and drafting. This removes the cost of building a grade predictor and likely lowers regulatory, rule and reputation risk (legal advice is needed on the EU AI Act part)
- **What it adds:** two new costs, keeping the guidelines up to date and storing students' work
- **The value it aims for:** catching drift before the meeting. The market scan found no alternative that does this unprompted
- **Positioning:** TFGPT lives alongside the student's own AI rather than replacing it

This remains a hypothesis, not a validated blue ocean or confirmed business model

## Critical outstanding validation points

1. **Own AI against TFGPT:** give students the same check task in their own AI with the guidelines uploaded and in TFGPT with them preloaded, and compare the answers and the effort (Raise; the first gap in market-research.md section 8)
2. **Access to guidelines:** whether TFGPT can get current guidelines, rubrics and dates for each programme from Campus Online, and who keeps them up to date (Raise; also a precondition for Create)
3. **Accuracy of flags:** whether TFGPT's drift flags match what the supervisor would have raised (Create)
4. **No verdict:** whether students who get cited flags with no verdict can tell if they're ready (Eliminate)
5. **Counts as feedback:** whether IE counts a tool that only flags points as "feedback", and whether that makes IE more willing to back it (Reduce)

## Evidence boundaries

**Based on real evidence**
- Wizard-of-Oz test (experiment-card.md: 10 final-year classmates across BCSAI, BBA, BAM and BDBA, one 20-minute session in a simulated chat): 3 of 10 opened their own AI; 4 of 10 checked with Blackboard, a friend, Google or the supervisor; participant 7 generated ideas in Claude and checked them in the chat; participant 3 got conflicting format advice from classmates
- Sourced market facts (market-sources.md): TFG format and citation rules differ by programme (#104) and the rubrics sit on Campus Online (#106); IE allows AI for feedback and requires disclosure (#8, #76, #78); Grammarly's grade estimate is explicitly not a grade (#189); the supervisor decides permission to present (#16, #82); AI that evaluates learning outcomes is high-risk under the EU AI Act (#194–#196)
- Late discovery at the meeting is REPORTED second-hand (interview-evidence.md 01)

**Based on Persona, team or AI inference**
- The value-curve scores the moves start from (for example programme-guideline knowledge at 1 for the student's own AI) were proposed by AI and still await the team's review
- "Students can't ask about documents they don't know exist" rests on one first-hand episode, written up as ai-persona-03
- The candidate moves came from the team's notes (market-research.md sections 4 and 7); most cell wording is AI-proposed options that the student selected and confirmed
- The EU AI Act benefit of eliminating grading is directional only; whether a check-only tool stays outside Annex III 3(b) is UNKNOWN and needs legal advice
- No row claims willingness to pay or to switch; both remain untested

**Shifted costs (kept out of the grid cells by the student's choice, recorded here)**

| Row | Shifted cost |
|---|---|
| Eliminate | The student has to judge for themselves whether the flagged points add up to "ready" |
| Reduce | Drafting moves to the student's own AI, which may be paid (#24), with the effort of moving between tools |
| Raise | Someone has to obtain, load and update every programme's guidelines, rubrics and dates each year (#104, #106), with a dependency on IE for access to Campus Online |
| Create | Unwanted or wrong flags could annoy students and push them back to their own AI |

**Contradictions and unresolved gaps**
- "Instead of their AI of choice" (assumptions.md, goals.md, experiment-card.md) against the author's decision to live alongside general AI (market-research.md section 7)
- Concealment: the opportunity insight (a team hypothesis) says students care most about making work look not-AI. Create needs TFGPT to store the student's work, and an AI log the advisor can see may push real AI work back to students' own AI (ai-persona-04)
- Participant 10 did all three tasks in Claude: the negative case for a tool that won't draft
- Meeting cadence differs by programme (#14, #15, #89, #96, #97, #105), which affects when "before each deliverable" falls. jtbd.md still says "two-month gaps", while opportunity-v02.md qualifies it by programme
- Whether ChatGPT Edu is still live at IE is disputed (#4, #181, #188 against the team member's report)
- Willingness to pay, and who would pay, is untested
