# RPAI · Venture Skeleton v0.1 · TFGPT

```
rpai_gp/
├── AGENTS.md                   Persona Agent instructions from the course (synthetic persona rehearsal)
├── downloads/                  the 9 AI helpers from the course deck (inputs, do not edit)
│   ├── SKILL.md                  helper that writes ai-usage-log.md
│   ├── ai-prompt-opportunity.md
│   ├── ai-prompt-assumptions.md
│   ├── ai-prompt-goals.md
│   ├── ai-prompt-experiment-card.md
│   ├── ai-prompt-job-to-be-done.md
│   ├── ai-prompt-persona-builder.md
│   ├── ai-prompt-constitution.md
│   └── ai-prompt-ERRC.md         writes ERRC.md and opportunity-v02.md from the market evidence
├── evidence-log/               what we produced (outputs)
│   ├── opportunity.md          pain point, user, need, insight, HMW, open gaps
│   ├── opportunity-v02.md      proposed update from ERRC; becomes opportunity.md when the team accepts it
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
│   ├── ai-usage-log.md         6-column course log, one row per meaningful AI run
│   └── personas/
│       ├── ai-persona-01..03.md  the 3 selected student personas (not yet validated with real users)
│       ├── ai-persona-04.md      stakeholder persona: the TFG advisor (grounded in two real advisors)
│       ├── selection.md          how and why they were selected
│       └── drafts/               persona hypotheses: 01-05 one per team member, 06 the TFG advisor (stakeholder)
├── prototype/
│   ├── prototype-v0.pdf        Wizard-of-Oz kit: chat front, task brief, wizard protocol, observation sheet, exclusions
│   └── prototype-v0-backup.png screenshot of the chat front (page 2), in case the live version fails
├── tfgpt-landing/              fake-door landing page and signup API (deployed on Railway)
├── tfgpt-pilot/                Wizard-of-Oz pilot: student chat + wizard console, answered live by the team (Railway)
├── venture-skeleton-v0.pptx    v0 presentation (table + rough test)
└── venture-skeleton-v0.1.pptx  v0.1 presentation for the Session 8 checkpoint
```

## Adding a persona draft
Run `downloads/ai-prompt-persona-builder.md` in any AI chat with `opportunity.md`, `goals.md` and `jtbd.md` as inputs. Save the result as `evidence-log/personas/drafts/persona-hypothesis-0X.md`, add one row to `ai-usage-log.md`, and open a PR (don't merge your own). The repo is public: no real names.
