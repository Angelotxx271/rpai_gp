# RPAI · Venture Skeleton v0.1 · TFG Copilot

```
rpai_gp/
├── AGENTS.md                   Persona Agent instructions from the course (synthetic persona rehearsal)
├── downloads/                  the 7 AI helpers from the course deck (inputs, do not edit)
│   ├── SKILL.md                  helper that writes ai-usage-log.md
│   ├── ai-prompt-opportunity.md
│   ├── ai-prompt-assumptions.md
│   ├── ai-prompt-goals.md
│   ├── ai-prompt-experiment-card.md
│   ├── ai-prompt-job-to-be-done.md
│   └── ai-prompt-persona-builder.md
├── evidence-log/               what we produced (outputs)
│   ├── opportunity.md          pain point, user, need, insight, HMW, open gaps
│   ├── assumptions.md          3 areas, riskiest assumption, evidence since v0
│   ├── goals.md                Product Goal, current and previous Sprint Goal
│   ├── jtbd.md                 Job to Be Done statement, eight-element table, validation gaps
│   ├── experiment-card.md      hypothesis, method, metric, threshold, evidence strength, decision rule
│   ├── recruitment.md          test access: who, how many, how, dates, consent
│   ├── interview-evidence.md   real-user evidence, anonymised (Participant 01, 02…)
│   ├── ai-usage-log.md         6-column course log, one row per meaningful AI run
│   └── personas/
│       ├── ai-persona-01..03.md  the 3 selected critical personas (not yet validated with real users)
│       ├── selection.md          how and why they were selected
│       └── drafts/               one persona hypothesis per team member
├── prototype/
│   ├── prototype-v0.pdf        Wizard-of-Oz kit: chat front, task brief, wizard protocol, observation sheet, exclusions
│   └── prototype-v0-backup.png screenshot of the chat front (page 2), in case the live version fails
├── tfgpt-landing/              fake-door landing page and signup API (deployed on Railway)
├── venture-skeleton-v0.pptx    v0 presentation (table + rough test)
└── venture-skeleton-v0.1.pptx  v0.1 presentation for the Session 8 checkpoint
```

## Adding a persona draft
Run `downloads/ai-prompt-persona-builder.md` in any AI chat with `opportunity.md`, `goals.md` and `jtbd.md` as inputs. Save the result as `evidence-log/personas/drafts/persona-hypothesis-0X.md`, add one row to `ai-usage-log.md`, and open a PR (don't merge your own). The repo is public: no real names.
