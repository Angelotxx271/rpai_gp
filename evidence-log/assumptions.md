# Assumptions

## Area 1: Student situation and adoption
- Must be true:
  - Students drift from the requirements or scope of their topic and detect it late (from experience, not yet proven)
  - Students will use AI for their TFG and accept it as a regular tool in their project
  - Students are willing to use this instead of their AI of choice
  - Most students don't pay for an AI subscription, so a good free tool is an advantage, not just a substitute
- Evidence needed: Interviews with final-year students about their last drift and how they use AI, plus observed use instead of their AI of choice, since saying and doing differ here

## Area 2: Product quality and feasibility
- Must be true:
  - It's at least as good as the models students already have, not inferior
  - It holds the student's context (topic, draft, guidelines) across sessions so they don't re-supply it
  - With skills and maybe MCP it can think like a supervisor and catch drift
- Evidence needed: A technical test that it keeps context across sessions and catches drift against real IE guidelines

## Area 3: IE backing
- Must be true:
  - IE tailors the knowledge base for the TFG context and what it considers best
  - IE invests in it
  - IE accepts it as a regular tool
  - IE promotes it as part of the official tools, not a mere testimonial
- Evidence needed: Conversations with supervisors and IE staff about tailoring, investing and promoting

## Riskiest assumption
Students will use it instead of their AI of choice. If this is false the tool is pointless: students keep the freedom to work as they please unless IE fully enforces it. IE approval is a gate, but adoption is the risk that survives the gate.

Re-checked on 2026-09-21 after the JTBD and persona work: still the riskiest. Switching is what separates this from the other tools IE has shipped that students never moved to. The evidence so far ties it to Area 2: the one student asked would switch only if the tool keeps her context across sessions, and students worry university tools run outdated models.

## Evidence since v0 (2026-09-21)
Sources: interview-evidence.md, jtbd.md, personas/. Nothing here is validated; statuses as recorded there.
- Drift detected late: reported second-hand by Participant 01 about his classmates (found out at the meeting, redid the work)
- Students use AI for their TFG: reported by Participant 01 and in informal reports from other students
- Instead of their AI of choice: one stated, conditional yes (Participant 02: if it keeps her context). Against it: students stick with the AI they already know, and worry university tools run outdated models
- Most students don't pay for AI: partly contradicted. Most Computer Science students pay; most others use free or cheap plans (informal reports)
- As good as their current models, and holds context across sessions: untested, now conditions for switching
- Catches drift like a supervisor: untested. ai-persona-01 checks with the same AI that drafted the work; ai-persona-03 needs problems flagged before the student knows to ask
- IE knowledge base: ai-persona-03 shows TFG documents are scattered across courses and emails (first-hand); nothing new on whether IE will tailor, invest or promote

## Evidence since 2026-10-11
Sources: experiment-card.md (Wizard-of-Oz, 10 final-year students), market-research.md, ERRC.md. Statuses as recorded there; nothing here is validated in real use.
- Instead of their AI of choice: in one 20-minute Wizard-of-Oz session, 6 of 10 completed all three tasks in the chat without opening their own AI, exactly the committed threshold, so the decision was CONTINUE (experiment-card.md). 3 of the other 4 opened their own AI: participants 4 and 7 used ChatGPT or Claude alongside the chat, and participant 10 did all three tasks in Claude. This is one session with a simulated chat, not use over a real deliverable
- Instead or alongside, as stated on the landing page (REPORTED, stated intention, not behaviour): 19 signups: 2 said they'd use it instead of their own AI, 11 alongside it, 6 probably not (recruitment.md, read on 2026-10-13). The question was not limited to the pre-meeting check, no bar was set beforehand, and it went to the same class group as the Wizard-of-Oz participants. It leans towards alongside, which fits the scope ERRC.md gives "instead"
- Scope of "instead": ERRC.md narrows it to the pre-meeting check. Students use TFGPT instead of their AI of choice for the check and keep their own AI for everything else (market-research.md section 7). The riskiest assumption above is read with that scope
- Re-checked on 2026-10-12: still the riskiest. The Wizard-of-Oz result cleared the bar once; ERRC.md falsifier 1 restates it for real use
- What would prove these areas wrong (the falsifiers in ERRC.md):
  - Area 1: students don't end up using TFGPT instead of their AI of choice for the pre-meeting check (ERRC.md proposes measuring it in real use against the committed 6-of-10 bar)
  - Area 2: TFGPT misses more than 40% of what a supervisor would otherwise flag as not ideal in the TFG; or the check can be copy-pasted into a different LLM and it gives the same flags for the same effort, in which case TFGPT has no value
  - Area 3: IE does not commit to the full maintenance and adoption of the tool
- New must-be-true items from ERRC.md (HYPOTHESIS, untested):
  - Area 1: students read and act on flags TFGPT raises without being asked, rather than muting them
  - Area 1: students still use it when it stores their topic and work between sessions (ERRC.md notes a tension with concealment)
  - Area 2: TFGPT can get each programme's current guidelines, rubrics and dates from Campus Online or Blackboard, and someone keeps them up to date
  - Area 3: IE counts a tool that flags points and may suggest a fix for a flagged passage, with no grade and no drafting, as feedback under its AI rules
