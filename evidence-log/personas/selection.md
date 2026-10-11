# Persona selection

**Date:** 2026-09-21

**Drafts compared:** 01, 02, 03 and 04. The fifth team member's draft (05) arrived on 2026-09-22, after this comparison; see the update of 2026-10-11 below.

**Criteria:** strength of evidence; a distinct adoption logic for the same Job to Be Done; a product decision tied to the riskiest assumption (students using the tool instead of their AI of choice).

| Draft | Label | Evidence | Decision | Result |
|---|---|---|---|---|
| 01 | The AI Cross-Checker | Coursework behaviour OBSERVED by the author; TFG behaviour HYPOTHESIS | Show sources and tools behind every answer; tests switching away from her current AI | Selected as ai-persona-01.md |
| 03 | The Hopeful AI Improviser | REPORTED second-hand (interview-evidence.md 01 and 02) | Test a fair comparison with the student's familiar AI that exposes drift before the meeting | Selected as ai-persona-02.md |
| 04 | The Accidental Discoverer | First-hand episode OBSERVED and REPORTED by the author | Centralise TFG documentation, make it queryable, flag deviations before being asked | Selected as ai-persona-03.md |
| 02 | Stall-on-doubt | All HYPOTHESIS, from group projects rather than the TFG | Research what makes a source feel competent enough to act on | Not selected. Its open question is kept below |

## Overlaps and merge decisions

- 01 and 03 both rely heavily on AI but differ in adoption logic: 01 checks the AI's work, 03 drafts and hopes. Kept separate
- No drafts were merged. Drafts stay unchanged in drafts/

## Open questions carried forward

- From draft 02: whether students need a source to feel competent, not just be available, before they trust and act on it

## Validation status

Not validated with real users. On 2026-09-21 the team deferred real-user validation for lack of time. All evidence statuses stay as drafted, and no synthetic Persona output is treated as validation.

One check was made the same day: the classmate behind ai-persona-01 said she would switch if the tool kept her context (interview-evidence.md 03). That is a stated intention, not validation, and ai-persona-01.md was updated with it. Testing whether students actually switch becomes the next Sprint Goal.

## Update 2026-10-11: the advisor stakeholder persona

**Added criterion for stakeholder personas:** the stakeholder controls access or endorsement, or is the students' current alternative. The TFG advisor is both: today the only check on drift, the one who can refuse permission to present in the first call (market-sources.md #16, #82), and a likely route to IE backing (assumptions.md Area 3).

| Draft | Label | Evidence | Decision | Result |
|---|---|---|---|---|
| 06 | The Few-Minutes Advisor (stakeholder) | REPORTED by one advisor and some of his students, with a second advisor as the contrast case (interview-evidence.md 05 and 06) | A supervisor view with the platform's AI usage log, tested with advisors and students before it is built | Selected as ai-persona-04.md, labelled "Stakeholder persona: TFG advisor", with the team's agreement on 2026-10-11 |

**Validation status of ai-persona-04:** grounded in two real advisors, which is more than drafts 01 to 05. Its behaviour claims are REPORTED; its decision claims (a supervisor view saves the advisor time; students keep using the tool if their advisor can see an AI log) are not yet tested with real users. Using the same two conversations to validate it would be circular, so the next step is to take those claims back to an advisor with many students and to a few of his students.

**Draft 05 (The Unanchored Explorer)** was merged into drafts/ on 2026-10-11 (PR #10). It was not part of the 2026-09-21 comparison.
