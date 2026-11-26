# Pricing, Product-Market Fit & Metrics

**Version:** 1.0, 2026-11-26  
**Purpose:** Evidence record backing the mandatory Economics slide for Group Presentation II (`downloads/final-project-guide.md`, §§1, 3, 5; Sessions 26–27). Every figure is explicitly labelled **Measured**, **Target**, **Estimate**, or **Hypothesis**.

---

## 1. Unit Cost & Delivery Price Floor

Source: [`prototype/cost-benchmark.md`](../prototype/cost-benchmark.md). Development spend (~\$47.30 in spike/judge/smoke API calls + coding-agent time) is tracked separately and excluded from the delivery price floor.

| Cost layer (1,000 final-year students, AWS `eu-south-2` Multi-AZ) | Sonnet 5.5 *(current C2)* | Narrowed + Cached Sonnet 5.5 *(target)* | Opus 5.5 *(high-cost ceiling)* | Label |
|---|---:|---:|---:|---|
| **AI running cost / check** *(with 1.25× retry margin)* | \$0.49 | ~\$0.26 | \$0.68 | Measured (spike) / Estimate (narrowed) |
| **AI running cost / student / academic year** *(4 checks + 4 re-checks + 15 asks + 8 Haiku compactions, incl. 1.25× retry)* | \$2.63 | ~\$1.44 | \$3.99 | Estimate from measured spike rates |
| **Operations + Hosting / student / academic year** *(AWS `eu-south-2` Multi-AZ \$2,544/yr + 40 h academic pack maintenance \$1,300/yr ÷ 1,000 students)* | \$3.84 | \$3.84 | \$3.84 | Estimate (`eu-south-2` list rates) |
| **Full delivery cost / student / academic year (Delivery Price Floor)** | **\$6.47** (~€6.00) | **~\$5.28** (~€4.90) | **\$7.83** (~€7.25) | **Estimate** |
| **Full delivery cost / check or re-check task** *(8,000 tasks/yr)* | **\$0.81** | **~\$0.66** | **\$0.98** | **Estimate** |

---

## 2. Pricing Strategy & Packaging (`HYPOTHESIS` — Untested With Buyer)

*No university administrator or student has reacted to a price yet. Every pricing decision below is an explicit **Hypothesis**, not validated willingness to pay.*

- **Who pays (Buyer):** **IE University (institutional B2B license)**, not individual students — consistent with `evidence-log/ERRC.md` (Falsifier 2) and `evidence-log/market-research.md`. Students already pay for general AI (Claude/ChatGPT) or stick to free tiers and strongly resist a second personal subscription, whereas IE already pays for campus-wide AI tooling (`market-sources.md` #1, #3, #181) and owns the official TFG guidelines.
- **What we charge for & how we package it:** **Annual per-student institutional seat license** billed per programme or across all final-year bachelor students (minimum 1 programme cohort / 100 seats; campus tier at 1,000+ seats). Includes:
  - Preloaded, maintained programme guideline packs (syllabus, template, rubrics, milestone dates).
  - Up to **15 full checks/re-checks per student per academic year** + unlimited cited stage questions (enforced by daily & annual fair-use caps so a single power user cannot break unit margins).
  - Optional **Bring-Your-Own-Compute / IE GPU Cluster** deployment mode if IE prefers to run vetted open-weights models on its own infrastructure once quality clears the miss-rate bar.
- **Delivery price floor:** **€6.00 / student / academic year** (Sonnet 5.5 + AWS `eu-south-2` Multi-AZ + ops at 1,000 students; **€7.25** ceiling on Opus 5.5; **€4.90** target once narrowed).
- **Proposed institutional price (`HYPOTHESIS`):** **€18 / final-year student / academic year** (campus-wide 1,000-student license = **€18,000 / year**; pilot single-programme 100-student pack = **€2,500 / year** due to higher per-student fixed hosting overhead).
  - **Expected gross margin at 1,000 students:** **67% on Sonnet 5.5** (`(€18 - €6.00) / €18`), **60% on Opus 5.5**, and **73% on narrowed Sonnet** — aligned with Bessemer's 50–60% AI software gross margin benchmark (Sessions 26–27) with buffer for token spikes and support.
  - **Value anchor vs. buyer alternative:** Saves supervisor re-review time across repeated low-level formatting/scope rounds (advisor persona `ai-persona-04`: supervisors spend minutes per student across heavy cohorts) and avoids costly student rework between deliverable meetings, for roughly **0.07% of one year's IE undergraduate tuition**.
- **What would falsify this pricing:** IE refuses to fund or maintain TFGPT (Falsifier 2), or demands a price below €8/student/year while requiring Opus-tier cloud models without narrowing.

---

## 3. Product-Market Fit Evidence & Next Test

### Strongest evidence today (honest evidence strength)

| Signal / Test | Result | Evidence label & limit | Source |
|---|---|---|---|
| **Wizard-of-Oz simulated chat (Round 1)** | **6 of 10** final-year IE students completed all 3 TFG tasks without opening their own AI (met pre-set 6/10 bar → `CONTINUE`); 2 more paired TFGPT alongside their own AI (`8/10` finished in TFGPT) | **Measured (`MEDIUM`)** — single 20-min simulated session, not repeated real-deliverable use; no-verdict UI not yet tested | `evidence-log/experiment-card.md` |
| **Fake-door landing page signups** | **19 signups:** 11 said *alongside* their own AI, 2 *instead*, 6 *probably not* | **Reported signal (`LOW`)** — stated intention from same class group, no pre-set bar; shifted our positioning from "instead" to **coexist** | `evidence-log/recruitment.md`, `evidence-log/assumptions.md` |
| **Real student & advisor interviews** | Late drift & rework reported across CS cohort (`Participant 01`); scattered guidelines observed first-hand (`ai-persona-03`); time-starved advisor confirmed bottleneck (`Advisor A`, contrasted with `Advisor B`) | **Reported / Observed (`LOW–MEDIUM`)** — small sample (`n=6` entries) | `evidence-log/interview-evidence.md` |
| **Field comparison + Advisor spike v2** | Field comparison caught 9/9 advisor points on one proposal (`n=2`); Protocol v2 judge first pass shows Opus C2 catches 7/18 (61% miss rate — triggers narrowing if humans agree) | **Feasibility only (`LOW` as demand)** — human blind scoring by `adriFCM` & `kristgiuff05` pending (due 2026-11-27) | `evidence-log/spikes.md` |

### Next test that would strengthen fit
1. **Two real-user prototype testing rounds (`evidence-log/user-feedback.md`, Phase 1 `coexist` test):** Give ≥3 real final-year BDBA students (scaling toward 10) the live Phase 1 Railway build on their actual proposals while keeping their own AI open. Measure whether ≥60% finish a check in TFGPT and revise at least one flagged passage, change the product from Round 1 findings, and retest in Round 2.
2. **Institutional buyer check (Falsifier 2 ladder, `private/advisor-spike/f2-ie-commitment.draft.md`):** After human spike counts land, test willingness to endorse/pilot with supervisor + BDBA Capstone Director (currently parked pending academic-pass email to the professor).

---

## 4. Metrics: One Main Metric & Three Guardrails

| Role | Metric | Exact definition | Target | Data source | Status |
|---|---|---|---|---|---|
| **Main Metric** | **Actionable Check Rate ("Coexist Value")** | `%` of tested final-year students who run a proposal check in TFGPT (with their own AI free to use) **and** resolve ≥1 cited flag on re-check (or edit their draft due to a flag) | **≥ 60%** (`≥ 6 / 10` per `specs/roadmap.md`) | `advisor.flags` (`status = 'solved'` on re-check) + `evidence-log/user-feedback.md` session logs | **Target** *(unmeasured on live Phase 1 build)* |
| **Guardrail 1 · Quality & Safety** | **Grounding Integrity & Advisor Miss Rate** | (a) `0%` unverified quotes/sections displayed; (b) `0` prompt-injection approvals (`c14`, `q10`); (c) `≤ 40%` miss rate on advisor ground truth (`ERRC.md` Falsifier 3) & `≤ 1` wrong flag / synthetic check | **0%** unverified shown · **0** injections obeyed · **≤ 40%** miss rate | `advisor.messages` (`hidden`), `tfgpt_eval run` JSON results, advisor-spike human sheets | **(a–b) Verified offline (77+ tests) & live smoke (0 hidden); (c) Provisional 61% Opus C2 first pass — human counts & narrowing pending** |
| **Guardrail 2 · Unit Economics** | **AI Running Cost per Check & Budget Cap Compliance** | Mean AI running cost per completed check/re-check + count of daily budget breaches (`DAILY_BUDGET_USD=\$15`, `10 checks/student/day`) | **≤ \$0.50/check** now (**≤ \$0.25/check** post-narrowing) · **0** cap breaches | `harness.runs` (`cost_usd`, `tokens_in`, `tokens_out`, `fallback_used`) + `python -m tfgpt_eval online` | **Measured on spike (\$0.395 Sonnet / \$0.543 Opus C2) & smoke (\$0.061 synthetic); target for live cohort** |
| **Guardrail 3 · User Trust & UX** | **Flag Dismissal Rate & Check Latency** | `%` of shown flags dismissed by students as `"Not relevant"` + p95 check completion time (with live SSE progress) | **≤ 25%** dismissed · **p95 ≤ 180 s** | `advisor.flags` (`status = 'dismissed'`), `harness.runs` (`seconds`), `tfgpt_eval online` | **Latency measured on spike (188–228 s) & live smoke (65 s); dismissal rate target (unmeasured until user tests)** |
