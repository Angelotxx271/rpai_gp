# RPAI · Venture Skeleton v0.1 · TFGPT

```
rpai_gp/
├── agents/
│   └── persona-agent.md        Persona Agent instructions from the course (synthetic persona rehearsal). Not loaded automatically: ask the agent to read it
├── downloads/                  the 11 AI helpers from the course deck (inputs, do not edit)
│   ├── SKILL.md                  helper that writes ai-usage-log.md
│   ├── ai-prompt-opportunity.md
│   ├── ai-prompt-assumptions.md
│   ├── ai-prompt-goals.md
│   ├── ai-prompt-experiment-card.md
│   ├── ai-prompt-job-to-be-done.md
│   ├── ai-prompt-persona-builder.md
│   ├── ai-prompt-constitution.md   writes specs/mission.md, tech-stack.md and roadmap.md (v4 from the deck)
│   ├── ai-prompt-ERRC.md         writes ERRC.md and the proposed opportunity v02 from the market evidence
│   ├── ai-prompt-feature-spec.md   writes one dated feature folder in specs/ and the root AGENTS.md for coding
│   └── ai-prompt-build-loop.md     builds a reviewed feature in prototype/, one task group at a time, test first
├── evidence-log/               what we produced (outputs)
│   ├── opportunity.md          v02 (team-accepted 2026-10-12): pain point, user, need, insight, HMW, alternatives, factors, value innovation, open gaps
│   ├── assumptions.md          3 areas, riskiest assumption, evidence since v0 and since the Wizard-of-Oz test
│   ├── goals.md                Product Goal, current and previous Sprint Goal
│   ├── jtbd.md                 Job to Be Done statement, eight-element table, validation gaps
│   ├── experiment-card.md      hypothesis, method, metric, threshold, evidence strength, decision rule, Wizard-of-Oz results
│   ├── recruitment.md          test access: who, how many, how, dates, consent
│   ├── interview-evidence.md   real-user evidence, anonymised (Participant 01, 02…; Advisor A, B)
│   ├── press-release.md        Working Backwards opener with an evidence box
│   ├── market-research.md      Fermi estimate, four-category alternatives map, factors, claim table, stress test, so what
│   ├── market-sources.md       the 200 sourced desk-research claims behind market-research.md, each checked
│   ├── value-curve.svg         value curve chart with TFGPT's target line (scores and evidence in market-research.md, section 4)
│   ├── ERRC.md                 Eliminate / Reduce / Raise / Create grid, falsifiable value innovation hypothesis, validation points
│   ├── decision-record.md      decision after the Wizard-of-Oz test, what the evidence changed, next test card, invest answer, narrow / pivot / stop options
│   ├── spikes.md               technical spikes: protocol, decision rules and results (feasibility, not user validation)
│   ├── ai-usage-log.md         6-column course log, one row per meaningful AI run
│   └── personas/
│       ├── ai-persona-01..03.md  the 3 selected student personas (not yet validated with real users)
│       ├── ai-persona-04.md      stakeholder persona: the TFG advisor (grounded in two real advisors)
│       ├── selection.md          how and why they were selected
│       └── drafts/               persona hypotheses: 01-05 one per team member, 06 the TFG advisor (stakeholder)
├── prototype/
│   ├── prototype-v0.pdf        Wizard-of-Oz kit: chat front, task brief, wizard protocol, observation sheet, exclusions
│   └── prototype-v0-backup.png screenshot of the chat front (page 2), in case the live version fails
├── group-project-1-presentation/  Group Project I slides (HTML) and script, 13 Oct 2026; a record, not the final
├── tfgpt-landing/              fake-door landing page and signup API (deployed on Railway)
├── tfgpt-pilot/                Wizard-of-Oz pilot: student chat + wizard console, answered live by the team (Railway)
├── venture-skeleton-v0.pptx    v0 presentation (table + rough test)
└── venture-skeleton-v0.1.pptx  v0.1 Venture Skeleton (Session 8), updated 12 Oct 2026 for Group Project I
```

## Adding a persona draft
Run `downloads/ai-prompt-persona-builder.md` in any AI chat with `opportunity.md`, `goals.md` and `jtbd.md` as inputs. Save the result as `evidence-log/personas/drafts/persona-hypothesis-0X.md`, add one row to `ai-usage-log.md`, and open a PR (don't merge your own). The repo is public: no real names.
