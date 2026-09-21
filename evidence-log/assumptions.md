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
