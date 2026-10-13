# Press release: TFGPT, working backwards

**Status:** Lean Working Backwards opener for Group Project I. It tells the future customer story, and the dateline is illustrative, not a launch plan. The evidence status of every claim is in the box beside it, and evidence that contradicts the promise changes the release

---

## TFGPT lets final-year IE students catch drift in their TFG before the deliverable meeting, not at it

**Check your TFG against your topic and the IE TFG guidelines in one AI that already knows both, instead of re-explaining them to a general AI each time**

MADRID, September 2027. TFGPT today launched an AI agent that checks final-year IE students' TFG work against their topic and the IE TFG guidelines between deliverable meetings. Students catch drift while it is still cheap to fix, get a first check without waiting on a supervisor's reply, and keep writing knowing their work still fits their topic, instead of hoping it holds at the meeting.

**The problem.** Final-year IE students can work through the whole stretch between TFG deliverables, about two months in the Computer Science programme we heard about, without knowing whether their work still fits the requirements and scope of their topic, and only find out at the deliverable meeting. By then the work since the last meeting can be thrown away, and redoing it eats into the time for the next deliverable. Today they draft with the AI they already use, judge the result themselves and hope it holds at the meeting. When a supervisor has many TFGs, a reply can take more than a week, so in between, students wait.

**The solution.** TFGPT keeps everything TFG-related for the student's programme in one place: the guidelines, the rubric and the dates. Before each deliverable it checks the student's work against their topic and those guidelines on its own, flags what doesn't fit with the guideline section behind each point, and can suggest a fix for a flagged passage. It never drafts sections, grades the work or approves it: that stays with the supervisor. Drift shows up while it is still cheap to fix, not at the meeting.

"No TFG student should have to wait until the next meeting, or more than a week for an email, to find out they're off track. TFGPT checks the work against the guidelines while there's still time to fix it." — The TFGPT team

**How it works.** Give TFGPT your topic and draft once; it keeps them, so you never upload the guidelines or re-brief an AI. Before each deliverable, TFGPT checks your work and tells you what doesn't fit, so you don't have to remember to ask. You can also ask at any time: does this fit my topic, what does the TFG need, when is it due, does this paragraph meet the guidelines? Fix what it flags, then go into the meeting with your own check done.

"The peace of mind of not finding out at the meeting that my work was faulty, and being able to focus on the next phase of the deliverable instead of redoing it." — Participant 01, IE Computer Science graduate, describing what would have helped him during his TFG. He has not used TFGPT; this is not an endorsement

Final-year IE student? Tell us whether this would have saved you from redoing work at your last deliverable, or why not: tfgpt-production.up.railway.app

---

## Beside the release: what is proven and what is not

| Claim in the release | Evidence status today | Source, and what would change it |
|---|---|---|
| Students can work through the stretch between deliverables without knowing if they're on track, and find out at the meeting | Supported, second-hand | jtbd.md; interview-evidence.md 01: one IE Computer Science graduate about his classmates. Not counted. About two months is reported for that programme only; meeting cadence differs by programme (market-research.md section 5) |
| Today's alternative: their own AI drafts the work, they judge it themselves and hope it holds at the meeting | Supported, second-hand | jtbd.md (Solution hired); interview-evidence.md 02, informal reports, count not recorded |
| A supervisor with many TFGs can take more than a week to reply | REPORTED, one advisor's students | interview-evidence.md 05: some of his students, count not recorded, relayed by one team member. Another student reports a few days (ai-persona-03), and the contrast case (entry 06) shows it depends on the supervisor |
| Students re-explain their topic and context to a general AI each time | REPORTED, one student | interview-evidence.md 03: implied by the condition she set for switching away from Claude |
| Students check their TFG in TFGPT instead of their own AI (for the check; they keep their own AI for everything else) | OBSERVED in one 20-minute Wizard-of-Oz session; still the riskiest assumption for real use | experiment-card.md: 6 of 10 completed all three tasks without opening their own AI, exactly the threshold, so the decision is CONTINUE. 3 of the other 4 opened their own AI: two used it alongside the chat (ChatGPT, Claude) and one did all the tasks in Claude. One session with a simulated tool (evidence strength MEDIUM); repeated use over a whole TFG is untested. ERRC.md: the hypothesis is wrong if students don't end up using TFGPT instead of their AI of choice for the check. The landing-page signups lean the other way when asked in general: 2 of 19 said instead, 11 alongside (stated intention; recruitment.md) |
| TFGPT catches drift against the topic and guidelines | HYPOTHESIS, untested | assumptions.md Area 2. ERRC.md: the hypothesis is wrong if TFGPT misses more than 40% of what a supervisor would otherwise flag as not ideal, or if the check can be copy-pasted into a different LLM and it gives the same flags for the same effort, in which case TFGPT has no value |
| TFGPT checks before each deliverable without being asked | HYPOTHESIS, untested | ERRC.md (Create). The Wizard-of-Oz test covered checks the student started; nobody has tried flags they didn't ask for |
| Flags with the guideline section and a suggested fix at most; no grade, verdict or drafting | HYPOTHESIS | ERRC.md (Eliminate, Reduce). The 6 of 10 was observed with a chat that gave fit answers, so it doesn't cover a no-verdict TFGPT |
| One central place for everything TFG-related | HYPOTHESIS | ERRC.md (Raise). TFG documents are scattered (ai-persona-03; interview-evidence.md 04; market-sources.md #104, #106) |
| TFGPT keeps the student's topic and draft between sessions | HYPOTHESIS, untested | assumptions.md Area 2. prototype-v0 excluded memory across sessions, and the single-session test does not check it |
| TFGPT covers the IE TFG guidelines for each degree | HYPOTHESIS | prototype-v0 loaded them by hand; no guideline text is in the repo yet |
| IE backing | Not claimed; HYPOTHESIS, untested | assumptions.md Area 3; the landing page says "Not an official IE tool (yet)". ERRC.md: the hypothesis is wrong if IE doesn't commit to the full maintenance and adoption of the tool |
| The team quote | The team's vision, not a recorded statement | Written by the team |
| The customer quote | Real words, not an endorsement | Participant 01 on what would have helped him: a first-person version of the team's note of the conversation (interview-evidence.md 01), with its final clause omitted. He has not used TFGPT |
| The link | A demand check, not a product | tfgpt-production.up.railway.app is the fake-door landing page; TFGPT doesn't exist yet. By 2026-10-13: 19 signups: 2 said they'd use it instead of their own AI, 11 alongside it, 6 probably not (recruitment.md; a signal, not a test) |

**Name:** TFGPT. prototype-v0 and the v0 deck used the earlier working name TFG Copilot
