<p align="left">
  <img src="assets/tfgpt-logo.png" alt="TFGPT emblem" width="76" height="76">
</p>

# TFGPT — Pre-Meeting TFG Guideline & Scope Checker

**Rapid Prototyping with AI · Group 5 · IE University**

TFGPT helps final-year IE students check their TFG (Capstone) proposal against their programme's official guidelines **before** deliverable meetings — pointing out specific issues with the exact passage, the guideline section behind it, and one possible route forward. It gives **no grade**, **no overall verdict**, and **never writes or rewrites thesis text**: the student owns the text, the supervisor decides, and TFGPT coexists alongside the student's own AI.

Phase 1 (Data and Business Analytics · Full Proposal) implements one critical feature split into three end-to-end sub-features in one continuous thread:

1. **Check once** (`specs/2026-11-25-check-once/`): give a topic once, paste or upload a proposal (`.docx`, `.pdf`, `.md`, `.txt`), get cited flags checked in code (invented quotes or sections are hidden and counted).
2. **Check again** (`specs/2026-11-25-check-again/`): revise and re-check to see what is **Solved**, **Still open**, and **New**, or dismiss flags that do not apply.
3. **Ask the documents** (`specs/2026-11-25-ask-the-documents/`): ask stage questions and receive streamed, code-verified cited answers — or `"That one is for your supervisor"` when the documents do not cover it — with automatic rolling thread memory and 30-minute upload purging.

---

## Submission & Demo Links (Group Presentation II)

| Deliverable | Link / Location | Status |
|---|---|---|
| **Repository** | https://github.com/Angelotxx271/rpai_gp | Live (public) |
| **`final` tag** | `final` *(due 30 Nov 2026, 23:59 Madrid)* | Pending final merge & deploy |
| **Live Phase 1 Build (Railway)** | https://web-production-6bb30ece.up.railway.app (`/healthz` reports live commit) | Live (redeploy on `final` commit before deadline) |
| **Group Presentation II Slides** | *Pending* | Not yet created |
| **Offline Backup Demo** | [`prototype/backup-demo.html`](prototype/backup-demo.html) · [`prototype/tfgpt/scripts/demo_reset.py`](prototype/tfgpt/scripts/demo_reset.py) | Ready (self-contained replay + local SQLite seeder) |
| **Test 2 Advisor Mock-Up** | [`prototype/advisor-view-mockup.html`](prototype/advisor-view-mockup.html) | Ready for `adriFCM` advisor interviews |
| **Earlier prototypes (historical)** | Fake-door landing (`tfgpt-landing/`) · Wizard-of-Oz pilot (`tfgpt-pilot/`) · GP I slides (`group-project-1-presentation/`) | Preserved as record |

---

## Phase Evidence Pack (Where Everything Lives)

### 1. Venture & Strategy (`evidence-log/`)
- **Problem, Job & Personas:** [`evidence-log/opportunity.md`](evidence-log/opportunity.md) · [`evidence-log/jtbd.md`](evidence-log/jtbd.md) · [`evidence-log/personas/selection.md`](evidence-log/personas/selection.md) (`ai-persona-01..04.md` + retained `drafts/`) · [`evidence-log/interview-evidence.md`](evidence-log/interview-evidence.md)
- **Goals, Assumptions & Decisions:** [`evidence-log/goals.md`](evidence-log/goals.md) · [`evidence-log/assumptions.md`](evidence-log/assumptions.md) · [`evidence-log/decision-record.md`](evidence-log/decision-record.md) · [`evidence-log/press-release.md`](evidence-log/press-release.md)
- **Market & Strategy:** [`evidence-log/market-research.md`](evidence-log/market-research.md) · [`evidence-log/market-sources.md`](evidence-log/market-sources.md) · [`evidence-log/value-curve.svg`](evidence-log/value-curve.svg) · [`evidence-log/ERRC.md`](evidence-log/ERRC.md)
- **Experiments & Technical Spikes:** [`evidence-log/experiment-card.md`](evidence-log/experiment-card.md) · [`evidence-log/recruitment.md`](evidence-log/recruitment.md) · [`evidence-log/spikes.md`](evidence-log/spikes.md) · [`prototype/advisor-spike/results/results-public.md`](prototype/advisor-spike/results/results-public.md)

### 2. Specification, Coding Rules & Build Trail (`specs/`, `AGENTS.md`, `prototype/briefs/`)
- **Constitution:** [`specs/mission.md`](specs/mission.md) · [`specs/tech-stack.md`](specs/tech-stack.md) *(architecture, run rules, undo rules)* · [`specs/roadmap.md`](specs/roadmap.md) *(phases & Current behaviour)*
- **Coding-Agent Rules:** [`AGENTS.md`](AGENTS.md)
- **Phase 1 Sub-Feature Specs (`requirements.md`, `plan.md`, `validation.md`):**
  - [`specs/2026-11-25-check-once/`](specs/2026-11-25-check-once/)
  - [`specs/2026-11-25-check-again/`](specs/2026-11-25-check-again/)
  - [`specs/2026-11-25-ask-the-documents/`](specs/2026-11-25-ask-the-documents/)
- **Task-Group Briefs & Reports:** [`prototype/briefs/check-once.md`](prototype/briefs/check-once.md) · [`prototype/briefs/check-again.md`](prototype/briefs/check-again.md) · [`prototype/briefs/ask-the-documents.md`](prototype/briefs/ask-the-documents.md)

### 3. Prototype, Evaluation & Economics (`prototype/`, `evidence-log/`)
- **Phase 1 Build & Run Guide:** [`prototype/tfgpt/README.md`](prototype/tfgpt/README.md) · [`prototype/tfgpt/web/API.md`](prototype/tfgpt/web/API.md)
- **Public Synthetic Ground Truth & Eval CLI:** [`prototype/tfgpt/eval/data/README.md`](prototype/tfgpt/eval/data/README.md) · [`prototype/tfgpt/eval/results/2026-11-25-sonnet-smoke.json`](prototype/tfgpt/eval/results/2026-11-25-sonnet-smoke.json) *(full scored runs pending team pass threshold)*
- **Advisor Spike Harness (Protocol v2):** [`prototype/advisor-spike/README.md`](prototype/advisor-spike/README.md) · [`prototype/advisor-spike/SCORING.md`](prototype/advisor-spike/SCORING.md) · [`prototype/advisor-spike/results/runs-public.csv`](prototype/advisor-spike/results/runs-public.csv)
- **Cost Benchmark:** [`prototype/cost-benchmark.md`](prototype/cost-benchmark.md) *(measured spike + smoke costs, Segovia RTX 5070 power/hardware math, Railway vs. AWS `eu-south-2` 100/1,000/2,000-student scaling, 6 cost levers)*
- **Pricing & Metrics:** [`evidence-log/pricing-and-metrics.md`](evidence-log/pricing-and-metrics.md) *(delivery price floor, institutional B2B hypothesis, PMF evidence, 1 main metric + 3 guardrails)*
- **Offline Backup & Advisor Mock-Up:** [`prototype/backup-demo.html`](prototype/backup-demo.html) · [`prototype/advisor-view-mockup.html`](prototype/advisor-view-mockup.html) · [`prototype/tfgpt/scripts/demo_reset.py`](prototype/tfgpt/scripts/demo_reset.py)
- **User Testing & Iteration:** `evidence-log/user-feedback.md` *(pending two prototype testing rounds + retest)*

### 4. Security, Safety & AI Traceability
- **Security Policy & Recorded Audit:** [`SECURITY.md`](SECURITY.md) · [`evidence-log/security-audit.md`](evidence-log/security-audit.md) *(recorded `gitleaks` full-history scan, `aaa529f` historical remediation, network/permission boundaries, injection guards)*
- **Automated CI & Security Workflows:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) · [`.github/workflows/security.yml`](.github/workflows/security.yml) · [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml) · [`.github/dependabot.yml`](.github/dependabot.yml)
- **AI Usage Log:** [`evidence-log/ai-usage-log.md`](evidence-log/ai-usage-log.md)

### 5. Agent Use & Orchestration Rationale
- **Lead agent vs. subagents & model roles:** Frontier lead agents (Claude Opus 5.5, Gemini high) handled architecture, specs, multi-service implementation, and security audits; bounded review subagents (Claude Sonnet 5.5) checked scripts, market sources (200 claims), and the advisor-spike harness (catching real scoring/resume/budget bugs); Mistral Vibe (`GLM 5.3`) drafted the v0.3 tech stack and v0.1 cost benchmark; **Claude Haiku 5.5** handles automatic runtime thread compaction (`~\$0.00035/fold`).
- **Agent-stack choices:** Used [`AGENTS.md`](AGENTS.md) + [`CLAUDE.md`](CLAUDE.md) (`@AGENTS.md`), course helper prompts in `downloads/`, and targeted review subagents. Intentionally omitted custom MCP servers, custom hooks, and multi-agent runtime orchestration inside TFGPT itself because single-pack deterministic injection (`C2`) + Python post-verification + Postgres job queue solve the problem with lower latency, cost, and failure surface.
- **Verification:** Every delegated output was verified mechanically (80 offline `tfgpt` tests on SQLite & Postgres 17, 55 offline spike tests, `gitleaks`, YAML/link checks) or reviewed by a human before merge (`evidence-log/ai-usage-log.md`).

---

## Current Operational Notes & Known Open Items

- **Model providers (`prototype/tfgpt/harness/engines.json`):** Anthropic (`Claude Opus 5.5`, `Claude Sonnet 5.5`, `Claude Haiku 5.5` for compaction) is live on Railway. **OpenRouter** (`OPENROUTER_API_KEY`) and **Mistral AI** (`MISTRAL_API_KEY` credit refill for `Mistral Large 4` and `GLM 5.3`) are configured in the harness and still need keys/credits uploaded before being enabled in production. `DEFAULT_ENGINE` stays unset until named after human scoring.
- **Syllabus / external-model privacy check:** Resolved as an internal course-project prototype (`evidence-log/security-audit.md`); institutional data-processing clearance remains a precondition for any real IE-wide rollout.
- **Professor academic-pass assumptions email:** Drafted in `private/email-professor-assumptions.draft.md` (not yet sent).
- **Undo / rollback procedure:** Documented in [`specs/tech-stack.md`](specs/tech-stack.md) (*How to undo a bad change*) covering Git revert PRs, Railway redeploy rollback, Alembic `downgrade()`, engine `enabled` toggles, and `pg_dump` before destructive migrations.

---

## Quick Checks (Offline, No Model Calls)

```bash
# Phase 1 prototype tests (SQLite)
cd prototype/tfgpt && python -m pytest -q

# Same suite against PostgreSQL 17 with real Alembic migrations
cd prototype/tfgpt && TEST_DATABASE_URL="postgresql://postgres:dev@localhost:5432/tfgpt_test" python -m pytest -q

# Advisor spike harness offline tests
cd prototype/advisor-spike && python -m pytest -q tests/test_spike.py
```

Full local run, document-pack upload, evaluation CLI, and Railway deploy commands live in [`prototype/tfgpt/README.md`](prototype/tfgpt/README.md).

---

## Repository Structure

```text
rpai_gp/
├── AGENTS.md                          Coding-agent scope, rules, and check commands
├── README.md                          Entry point, submission links, and Phase Evidence Pack
├── SECURITY.md                        Security policy and vulnerability reporting
├── .github/
│   ├── dependabot.yml                 Automated dependency updates (pip, npm, Docker, Actions)
│   └── workflows/
│       ├── ci.yml                     Offline pytest (SQLite + Postgres 17 + spike) & Node checks
│       ├── security.yml               Full-history gitleaks, hygiene guard, Bandit, pip-audit, npm audit
│       └── codeql.yml                 GitHub CodeQL SAST (Python & JavaScript)
├── agents/
│   └── persona-agent.md               Synthetic Persona Agent instructions (rehearsal only, never evidence)
├── downloads/                         Verbatim course helpers & final-project-guide.md (do not edit)
├── evidence-log/                      Living Venture Evidence Log (opportunity, assumptions, goals,
│                                      JTBD, personas, market, ERRC, experiments, spikes, security-audit,
│                                      decision-record, ai-usage-log; user-feedback & pricing-and-metrics pending)
├── specs/
│   ├── mission.md                     Product constitution: purpose, promise, core flow, non-goals
│   ├── tech-stack.md                  Architecture, model harness, run rules, undo rules, ADRs
│   ├── roadmap.md                     Phases, feature split, and Current behaviour
│   ├── 2026-11-25-check-once/         Sub-feature 1: requirements.md, plan.md, validation.md
│   ├── 2026-11-25-check-again/        Sub-feature 2: requirements.md, plan.md, validation.md
│   └── 2026-11-25-ask-the-documents/  Sub-feature 3: requirements.md, plan.md, validation.md
├── prototype/
│   ├── tfgpt/                         Phase 1 build: shared/, web/, advisor/, harness/, eval/, tests/
│   ├── advisor-spike/                 Protocol v2 multi-engine spike harness, tests, public counts
│   ├── briefs/                        Build briefs and reports for all three Phase 1 sub-features
│   ├── prototype-v0.pdf               Historical Wizard-of-Oz kit
│   └── prototype-v0-backup.png        Historical Wizard-of-Oz backup screenshot
├── group-project-1-presentation/      Group Project I slides (HTML) and script (13 Oct 2026 record)
├── tfgpt-landing/                     Fake-door landing page and signup API (Railway)
├── tfgpt-pilot/                       Wizard-of-Oz pilot app (Railway)
├── venture-skeleton-v0.pptx           v0 Venture Skeleton (Session 5)
└── venture-skeleton-v0.1.pptx         v0.1 Venture Skeleton (Session 8 / Group Project I)
```
