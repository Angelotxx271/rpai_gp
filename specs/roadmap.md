# Roadmap

Version 0.1, 2026-11-24. Status: preliminary, to be revisited

## Current behaviour
- Nothing built yet. The landing page and the Wizard-of-Oz pilot are tests, with no AI behind them

The phases say what we plan to build; this section says what the product does today. It changes only when a feature passes its validation

## Phase 1: Pre-meeting check (detailed)
Goal: a Data and Business Analytics student gives their topic and work, gets cited flags with possible routes, revises, checks again, and can ask about their stage [Team decision: tech-stack.md]. It starts with the proposal, whose documents we have (spikes.md) [Team decision]

Tests: students' own AI and TFGPT will coexist, the riskiest assumption as recorded on 2026-11-24 [Team decision: assumptions.md]. Signals only: 11 of 19 signups said alongside (recruitment.md), and 8 of 10 did all three tasks in the simulated chat, 2 of them with their own AI open (experiment-card.md, counted afterwards). With a real tool [Missing]

Why first: a self-starting check is more impressive, but it needs stored work and matters only if students use the check at all [AI-proposed]

Candidate features, each end to end; order decided when we build [AI-proposed, from the first-prototype sentence]:
- Check once: topic and pasted work in; flags out, each with the passage, the guideline section and a possible route
- Check again: the revised work in; which flags are solved and which remain
- Ask: a question in; an answer citing the loaded documents, or "that one is for your supervisor"

Entry check: the stand-in misses at most 40% of advisor points (decision-record.md, Test 1). Above that, narrow the check before students try it

Validation, "coexist": 10 final-year Data and Business Analytics students check their own work with their own AI free to use [Team decision]. At least 6 finish the check in TFGPT and change something because of a flag. Opening their own AI doesn't count against us; doing the whole check there does. We record what each tool was used for. Fewer than 10 students: no decision yet [AI-proposed: commit the rule before the test]

## Later phases (outline) [Team decision]
- Phase 2: Remembers. Topic and work kept between sessions, a student's stated condition for switching (interview-evidence.md 03). Validation, "second visit": a student returns another day and checks new work without giving the topic again
- Phase 3: Starts itself. A check before a deliverable without being asked; needs Phase 2. Validation, "unasked flag": a student opens an unrequested flag and changes their work because of it
- Phase 4: Second programme. Validation, "right rules": for a student of that programme, every flag cites only that programme's documents

## Not in this prototype
- Deliverables after the proposal: decided later [Team decision]
- Grades or an overall verdict: the supervisor decides [Team decision: ERRC.md]
- Drafting or rewriting the work: the student owns the text [Team decision: ERRC.md]
- Supervisor view: waits for Test 2 with advisors [Team decision: decision-record.md]
- Login and IE systems: excluded since prototype-v0, and nobody at IE has been asked yet [Team decision: prototype-v0.pdf page 6; decision-record.md]
