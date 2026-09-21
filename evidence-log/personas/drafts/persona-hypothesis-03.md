# Persona Hypothesis 02: The Hopeful AI Improviser

> Status: HYPOTHESIS FOR REAL-USER VALIDATION
> Evidence boundary: This draft is based on one graduate's first-hand account, his second-hand account of classmates, and informal second-hand reports. It is not customer evidence.

## Behavioural focus

This Persona represents a final-year IE student who relies heavily on a familiar AI while working through the long gap between TFG deliverables, but has no dependable way to check whether the work still matches the requirements or scope.

The defining pattern is not simply "uses AI". It is: **draft with the familiar AI, make a personal judgement about whether the result is right, rewrite it so it does not look AI-generated, and hope it survives the next deliverable meeting.**

## Situation and job

During roughly two months between deliverable meetings, the student needs to make progress on the TFG while also completing other subjects. The feared outcome is discovering at the meeting that weeks of work were faulty and must be redone.

The progress they want is to enter the meeting with enough confidence that the work meets what is required, so they can move to the next phase instead of repeating the previous one.

## What this student does

- **REPORTED, second-hand:** Relies heavily on AI to write or develop the thesis work.
- **REPORTED, second-hand:** Checks the AI output personally rather than using a dependable external scope or requirements check.
- **REPORTED, second-hand:** Rewrites the output so it will not be flagged as AI writing, then hopes it holds up at the meeting.
- **HYPOTHESIS:** Notices the risk only weakly, or too late, because the current workflow gives no clear signal that the work has drifted.
- **HYPOTHESIS:** Values reassurance before the meeting more than another general-purpose writing assistant.

## Current approach and constraints

- **REPORTED, second-hand:** Keeps using the AI already used for most work because it is the best-known option and may be the one already paid for.
- **REPORTED, second-hand:** Trusts personal judgement and the next supervisor meeting as the practical quality check.
- **REPORTED, second-hand:** Worries that a university-provided alternative may be inferior because university tools often use outdated models.
- **SUPPORTED:** Has limited time because TFG work competes with other subjects, and rework can consume the next deliverable period.
- **UNKNOWN:** Whether this pattern is common outside Computer Science, and whether students would actually use a university tool during the gap.

## Decision consequence

The product should first test whether it can provide a fair, credible comparison against the student's familiar AI and expose requirement or scope drift before the meeting. A generic AI chat experience is unlikely to change this student's routine. The test should measure whether the student uses the tool on a real TFG task and whether its feedback changes what they do, rather than asking whether they like the idea.

## Critical uncertainty

The central uncertainty is whether this student experiences a recognisable problem during the two-month gap, or only after a supervisor points out the problem at the meeting. If students do not seek or trust an earlier check, this Persona's proposed behaviour and the product entry point may be wrong.

## Validation needed

Interview and observe final-year students from more than Computer Science. Ask them to reconstruct a recent TFG work session between meetings: what they produced, which AI or other tools they used, how they checked alignment with requirements, and what happened when the work was reviewed. Do not treat stated willingness to switch as evidence of actual use.