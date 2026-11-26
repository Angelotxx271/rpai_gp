# Cost Benchmark

**Version:** 1.0, 2026-11-26 *(expanded from v0.1 drafted in PR #38 `dev/angel-cost-benchmark`)*  
**Status:** Measured for the advisor spike (173 runs) and Phase 1 smoke run; full Phase 1 `tfgpt_eval` run and human-scored quality headline pending (due 2026-11-27).  
**Purpose:** Evidence record for Sessions 26–27 and `downloads/final-project-guide.md` (§§1, 3, 5) separating **development cost**, **AI running cost**, and **operations/hosting = full delivery cost per successful task**, including a production **AWS Spain (`eu-south-2`)** scaling plan for 100 / 1,000 / 2,000 students.

---

## 1. Sources & Token Pricing Used

- **Measured advisor-spike log:** `prototype/advisor-spike/results/runs-public.csv` — harness commit `8b8c8cf`, **173 scored arm runs** across 5 engines × 3 routes (`C0`, `C1`, `C2`) × 4 proposal versions × 3 repeats (7 runs failed when Mistral API credits ran out and are excluded from scored totals).
- **Measured Phase 1 product smoke run:** `prototype/tfgpt/eval/results/2026-11-25-sonnet-smoke.json` (1 synthetic case `c01` on Claude Sonnet 5.5, commit `eea990e`).
- **Model API pricing (USD per 1M tokens):**

| Model / Route | Provider | Uncached input | Cache read | Cache write | Output | Source & date |
|---|---|---|---|---|---|---|
| `claude-opus-5-5` | Anthropic API | \$4.00 | \$0.20 | \$5.00 | \$20.00 | `prototype/tfgpt/harness/engines.json` & API-recorded per-run costs (2026-11-25) |
| `claude-sonnet-5-5` | Anthropic API | \$2.00 | \$0.10 | \$2.50 | \$10.00 | `prototype/tfgpt/harness/engines.json` & API-recorded per-run costs (2026-11-25) |
| `claude-haiku-5-5` *(compaction only)* | Anthropic API | \$0.10 | \$0.005 | \$0.125 | \$0.50 | `prototype/tfgpt/harness/engines.json` (cache ratios assumed at Sonnet ratios; not offered for checks) |
| `zai-glm-5-3` | Mistral API | \$1.40 | \$0.14 | \$1.40 | \$4.40 | Mistral pricing page (`docs.mistral.ai/inference/pricing`), read 2026-11-25 |
| `mistral-large-4` | Mistral API | \$0.70 | \$0.07 | \$0.70 | \$2.10 | Mistral pricing page, read 2026-11-25 *(preview rate; list reported at \$1.36/\$4.18 — re-verify before lock-in)* |
| `qwen3.6:35b-a3b` (local) | Ollama on RTX 5070 | \$0 (tokens) | — | — | \$0 (tokens) | Owned desktop GPU (Segovia, Spain); electricity & hardware estimated in Section 4 |

---

## 2. Three Costs Separated (Course Framework, Sessions 26–27)

| Cost category | What it includes | Measured / Estimated figure | Used in delivery price floor? |
|---|---|---|---|
| **1. Development (building) cost** | One-time spike runs (173 arm runs = **\$34.09**), blind judge first pass (**\$10.76** for 137 scored / **\$13.13** incl. reruns per `spikes.md`), Phase 1 smoke run (**\$0.06**), plus coding-agent tooling & team time | **~\$47.30** in direct LLM API spend (measured) + student tooling/time | **No** (tracked separately; never mixed into unit price floor) |
| **2. AI running cost** | Model API calls per completed user task, including retries/fallbacks, cache writes/reads, stage questions, and automatic Haiku thread compaction | **\$0.075 – \$0.543 / C2 check** (measured on spike prompts); **\$0.061** on synthetic case `c01` | **Yes** |
| **3. Operations & hosting cost** | Cloud hosting (Railway Hobby today; AWS `eu-south-2` at scale), database backups, monitoring, and annual human guideline-pack updates | **\$15–\$20/mo** (Railway Hobby pilot) or **\$210/mo** (AWS `eu-south-2` Multi-AZ for 1,000 students) + ~\$120/mo amortized academic/ops maintenance | **Yes** (`Full Delivery = Running + Operations`) |

---

## 3. Measured Run Log Summary (Advisor Spike, `runs-public.csv`, n = 173)

All figures below are **measured** from `runs-public.csv` (two turns combined per run: initial check + `"Anything else that doesn't fit the guidelines?"`). Claude costs are the exact API-recorded per-run amounts; GLM and Mistral costs are **computed** from recorded token counts using `(tokens_in - cache_read) * input + cache_read * cache_read_price + tokens_out * output`.

| Engine | Route | Runs | Mean total in | Mean cache read | Mean cache write | Mean output | Mean seconds | Mean \$/run | Median \$/run | Cell total \$ |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Opus 5.5 | C0 (own AI) | 12 | 7,262 | 3,942 | 3,312 | 7,575 | 78.0 s | \$0.1689 | \$0.1683 | \$2.03 |
| Opus 5.5 | C1 (pasted) | 12 | 43,160 | 33,354 | 9,798 | 20,882 | 181.5 s | \$0.4733 | \$0.4623 | \$5.68 |
| **Opus 5.5** | **C2 (TFGPT)** | **12** | **102,763** | **83,069** | **19,686** | **21,393** | **187.7 s** | **\$0.5429** | **\$0.5178** | **\$6.52** |
| Sonnet 5.5 | C0 (own AI) | 12 | 7,058 | 3,942 | 3,108 | 9,082 | 74.3 s | \$0.0990 | \$0.0944 | \$1.19 |
| Sonnet 5.5 | C1 (pasted) | 12 | 42,260 | 33,354 | 8,898 | 27,834 | 186.2 s | \$0.3039 | \$0.2988 | \$3.65 |
| **Sonnet 5.5** | **C2 (TFGPT)** | **12** | **102,055** | **83,069** | **18,978** | **33,921** | **228.2 s** | **\$0.3950** | **\$0.3876** | **\$4.74** |
| GLM 5.3 | C0 (own AI) | 12 | 4,949 | 2,667 | 0 | 24,101 | 145.7 s | \$0.1096 | \$0.1067 | \$1.32 |
| GLM 5.3 | C1 (pasted) | 12 | 27,525 | 21,493 | 0 | 70,330 | 340.7 s | \$0.3209 | \$0.3244 | \$3.85 |
| **GLM 5.3** | **C2 (TFGPT)** | **10** | **65,695** | **59,814** | **0** | **73,325** | **359.1 s** | **\$0.3392** | **\$0.3455** | **\$3.39** |
| Mistral Large 4 | C0 (own AI) | 12 | 5,026 | 2,347 | 0 | 15,384 | 206.3 s | \$0.0343 | \$0.0343 | \$0.41 |
| Mistral Large 4 | C1 (pasted) | 12 | 27,600 | 23,040 | 0 | 29,434 | 311.0 s | \$0.0666 | \$0.0667 | \$0.80 |
| **Mistral Large 4** | **C2 (TFGPT)** | **7** | **64,998** | **53,833** | **0** | **30,097** | **524.5 s** | **\$0.0748** | **\$0.0717** | **\$0.52** |
| Qwen 3.6 local | C0 (own AI) | 12 | 5,295 | 0 | 0 | 6,545 | 98.4 s | \$0.0000* | \$0.0000* | \$0.00* |
| Qwen 3.6 local | C1 (pasted) | 12 | 28,269 | 0 | 0 | 12,921 | 187.9 s | \$0.0000* | \$0.0000* | \$0.00* |
| **Qwen 3.6 local** | **C2 (TFGPT)** | **12** | **67,731** | **0** | **0** | **12,748** | **208.9 s** | **\$0.0000*** | **\$0.0000*** | **\$0.00*** |

*\*Token API bill is \$0; local electricity + hardware amortization in Segovia is estimated in Section 4.*

**Engine totals (spike arms):** Opus **\$14.22** (36 runs), Sonnet **\$9.57** (36 runs), GLM 5.3 **\$8.56** (34 runs), Mistral Large 4 **\$1.74** (31 runs), Qwen local **\$0 API** (36 runs) → **\$34.09 total across 173 runs**. Refilling the 7 budget-cut Mistral/GLM runs (Mistral C2 r3 ×2, final ×3; GLM C2 final ×2) costs **~\$1.05** (`\$5` top-up covers refill plus margin).

**Phase 1 product smoke run (measured, 2026-11-25):** Synthetic case `c01` on Sonnet 5.5 (`prototype/tfgpt/eval/results/2026-11-25-sonnet-smoke.json`): **3/3 planted issues caught, 0 wrong flags, 34.6 s, \$0.0612**. *(Lower than the \$0.395 spike C2 mean because the synthetic pack is ~130 lines vs. the ~22k-word real BDBA pack.)*

---

## 4. Local GPU Benchmark: RTX 5070 in Segovia, Spain (`qwen3.6:35b-a3b`)

- **Hardware:** Desktop NVIDIA GeForce **RTX 5070 (12 GB GDDR7, 250 W TDP/TBP)** running Ollama (`num_ctx=98304`, `num_predict=32768`). Including host CPU, RAM, motherboard, and PSU efficiency overhead (~100 W), estimated wall power draw during active inference is **~350 W (0.35 kW)** (GPU-only lower bound: 250 W / 0.25 kW).
- **Electricity rate (Segovia, Spain — mainland 2.0TD PVPC tariff, 2025–2026):** Full effective residential consumer price including regulated tolls and taxes averages **€0.17–€0.24/kWh** across time-of-use bands (`P1` peak / `P2` flat / `P3` off-peak); using **€0.20/kWh (≈ \$0.22/kWh at 1.08 USD/EUR)** as the midpoint estimate.
- **Measured C2 local run duration:** **208.9 seconds** (`3.48 min` = `0.0580 hours`).

| Local cost component | Formula / Assumption | Per C2 check (estimate) | All 36 spike runs (~1.67 h) |
|---|---|---|---|
| Electricity (GPU only, 250 W) | `0.25 kW × 0.0580 h × €0.20/kWh` | €0.0029 (≈ **\$0.0031**) | €0.08 (≈ \$0.09) |
| **Electricity (full PC wall draw, 350 W)** | `0.35 kW × 0.0580 h × €0.20/kWh` | **€0.0041 (≈ \$0.0045)** *(range \$0.003–\$0.005)* | **€0.12 (≈ \$0.13)** |
| Hardware amortization (illustrative) | RTX 5070 ~\$650 ÷ 3,000 active inference hours = \$0.217/h × `0.0580 h` | **~\$0.0126** | ~\$0.36 |
| **Total effective local cost (wall + GPU)** | Electricity + amortized GPU (excludes hosting/ops) | **~\$0.017 / check** | **~\$0.49** |

**Pareto-frontier conclusion:** Local Qwen is ~23× cheaper than Sonnet C2 (\$0.017 vs. \$0.395), **but** caught only **2/18 points (89% miss rate)** with **3.3 wrong flags/review** on the judge first pass — far below our quality bar. Local inference stays **development/benchmark only**, never in the student production chain.

---

## 5. Cost per Successful Task vs. Quality (Provisional — Judge First Pass)

*Headline quality counts await blind human scoring by `adriFCM` and `kristgiuff05` (due 2026-11-27). Do not lock the default engine until human counts land.*

| Engine (C2 stand-in) | Mean AI \$/attempt | With 1.25× retry/fallback margin | Pooled caught (first pass) | Miss rate | Wrong flags/review | Status |
|---|---:|---:|---:|---:|---:|---|
| **Opus 5.5** | \$0.543 | \$0.679 | 7 / 18 | 61% | 1.1 | Highest catch so far; highest cost |
| **Sonnet 5.5** | \$0.395 | \$0.494 | 4 / 18 | 78% | 0.6 | Lowest wrong-flag rate; weaker on unnarrowed C2 |
| **GLM 5.3** | \$0.339 | \$0.424 | 6 / 18 | 67% | 0.4 | Strongest cost-vs-catch mid-tier; credits need refill |
| **Mistral Large 4** | \$0.075 | \$0.094 | 1 / 15 | 93% | 2.5 | Cheapest cloud; too weak on unnarrowed C2 |
| **Qwen 3.6 local** | ~\$0.017* | ~\$0.021* | 2 / 18 | 89% | 3.3 | Dev/benchmark only |

### Other Phase 1 Task Costs (Estimated from Current Prompts & Pricing)

| Task | Model | Estimated tokens (in / cache read / out) | Estimated AI \$/task | Basis |
|---|---|---|---:|---|
| **Check once** (real BDBA pack) | Sonnet 5.5 / Opus 5.5 | ~102k in (~83k cached) / 21k–34k out | **\$0.395 / \$0.543** | Measured (spike C2) |
| **Check again (re-check)** | Sonnet 5.5 / Opus 5.5 | ~55k in (~45k cached) / ~6k out *(1 turn)* | **~\$0.085 / ~\$0.165** | Estimate (single-turn JSON re-check with cached pack) |
| **Ask the documents** | Sonnet 5.5 / Opus 5.5 | ~52k in (~50k cached) / ~300 out | **~\$0.012 / ~\$0.024** | Estimate (cached pack + ~150-word cited answer) |
| **Auto thread compaction** | **Haiku 5.5** | ~1,500 uncached in / ~400 out | **~\$0.00035** | Estimate (runs automatically after 5 quiet min via `advisor` worker + Anthropic API; no separate deploy needed) |

---

## 6. Hosting & Infrastructure Comparison: Railway vs. AWS Spain (`eu-south-2`)

### Current Prototype Hosting (Railway — Live Today)
- **Plan:** Railway Hobby (**\$5/mo** base + metered usage).
- **Topology:** 3 FastAPI services (`web`, `advisor`, `harness`) + 1 Railway PostgreSQL instance.
- **Estimated monthly bill (pilot, ≤100 students):** **\$15–\$20/month** (Railway Pro at 1,000 students: ~\$50–\$70/month).

### Production AWS Architecture in Spain (`eu-south-2`, Zaragoza — EU Data Residency)

Matching TFGPT's exact 3-service + PostgreSQL architecture on **AWS `eu-south-2`** (ECS Fargate ARM/Graviton + Amazon RDS PostgreSQL + Application Load Balancer + CloudWatch/Secrets Manager/S3 automated snapshots):

| AWS `eu-south-2` Service | 100 students *(Pilot, Single-AZ)* | **1,000 students *(IE Cohort, Multi-AZ HA)*** | 2,000 students *(Multi-School HA)* | Notes (`eu-south-2` On-Demand list est.) |
|---|---:|---:|---:|---|
| **ECS Fargate (ARM Graviton)** (`web`, `advisor`, `harness`) | 3× `0.25 vCPU / 0.5 GB` ≈ **\$26/mo** | 6× `0.5 vCPU / 1 GB` (2 tasks/svc) ≈ **\$105/mo** | 6× `1 vCPU / 2 GB` ≈ **\$210/mo** | ARM Graviton ~20% cheaper than x86 (~\$0.036/vCPU-h, ~\$0.004/GB-h in `eu-south-2`) |
| **Amazon RDS PostgreSQL** | `db.t4g.micro` Single-AZ + 20 GB gp3 ≈ **\$19/mo** | `db.t4g.small` **Multi-AZ** + 50 GB gp3 + backups ≈ **\$68/mo** | `db.t4g.medium` **Multi-AZ** + 100 GB gp3 ≈ **\$132/mo** | `db.t4g.small` ~\$0.038/h Single-AZ (~2× Multi-AZ) + ~\$0.13/GB-mo gp3 |
| **Application Load Balancer + Egress** | 1 ALB + minimal LCU/egress ≈ **\$20/mo** | 1 ALB + moderate LCU + ~30 GB egress ≈ **\$25/mo** | 1 ALB + ~60 GB egress ≈ **\$32/mo** | Public HTTPS ingress only to `web`; `advisor` & `harness` stay in private subnets |
| **CloudWatch Logs, Secrets Manager & S3 Backups** | 4 secrets + logs + backups ≈ **\$8/mo** | 6 secrets + logs + automated DB dumps ≈ **\$14/mo** | 6 secrets + retention ≈ **\$22/mo** | Keeps keys out of code; S3 snapshot retention for rollback |
| **Total AWS Infrastructure / month** | **~\$73/mo** *(vs. \$15–\$20 Railway)* | **~\$212/mo** *(~\$140 Single-AZ)* | **~\$396/mo** | Can drop ~25–35% with 1-year Compute Savings Plans + RDS Reserved Instances |

---

## 7. Full Delivery Cost Projection for 1,000 Students (AWS `eu-south-2`)

### Usage Assumptions (Explicitly Marked `ESTIMATE` — to be calibrated from live Phase 1 logs)
- **Active cohort:** **1,000 final-year students** across IE's TFG year (**6 active months/year**: proposal, interim, pre-final, final).
- **Per student per academic year (expected usage):**
  - **4 initial checks** (1 per major deliverable/draft) + **4 re-checks** + **15 stage questions** + **8 Haiku compactions** = **8 full check/re-check tasks + 15 asks** per student per year.
- **Cohort totals (1,000 students / academic year):**
  - **4,000 initial checks** + **4,000 re-checks** + **15,000 stage questions** + **8,000 compactions** across 6 active months (average ~1,333 check/re-check tasks/month; peak deliverable month ~3,000 tasks).
- **Operations / Human maintenance allowance (allocated):** ~\$212/mo AWS × 12 months (**\$2,544/yr**) + ~40 hrs/yr academic/ops pack maintenance at €30/hr (**~\$1,300/yr**) = **\$3,844/yr** (**\$3.84 / student / year**, or **\$0.48 per check/re-check task** across 8,000 tasks).

| Route (1,000 students / academic year) | AI running cost / student / yr *(4 checks + 4 re-checks + 15 asks + 8 compactions)* | AWS `eu-south-2` + Ops / student / yr | **Full delivery cost / student / yr** | **Total annual cost (1,000 students)** | **Full delivery \$ per check/re-check task** |
|---|---:|---:|---:|---:|---:|
| **Opus 5.5** *(current unnarrowed C2)* | \$3.19 *(incl. 1.25× retry: \$3.99)* | \$3.84 | **\$7.03** *(retry: \$7.83)* | **\$7,034** *(retry: \$7,832)* | **\$0.88** *(retry: \$0.98)* |
| **Sonnet 5.5** *(current unnarrowed C2)* | \$2.10 *(incl. 1.25× retry: \$2.63)* | \$3.84 | **\$5.94** *(retry: \$6.47)* | **\$5,944** *(retry: \$6,469)* | **\$0.74** *(retry: \$0.81)* |
| **GLM 5.3** *(Mistral API, unnarrowed C2)* | \$1.76 *(incl. 1.25× retry: \$2.20)* | \$3.84 | **\$5.60** *(retry: \$6.04)* | **\$5,604** *(retry: \$6,044)* | **\$0.70** *(retry: \$0.76)* |
| **Target: Narrowed + Cached Sonnet 5.5** *(−45% output tokens, 1-turn check)* | **~\$1.15** *(incl. 1.25× retry: \$1.44)* | \$3.84 | **~\$4.99** *(retry: \$5.28)* | **~\$4,994** *(retry: \$5,282)* | **~\$0.62** *(retry: \$0.66)* |
| **IE Self-Hosted GPU Cluster** *(open-weights model once quality clears bar)* | ~\$0.15 *(power/cluster marginal est.)* | \$3.84 | **~\$3.99** | **~\$3,994** | **~\$0.50** |

**Key takeaway:** At 1,000 students on AWS Spain (`eu-south-2`), **total annual full delivery cost is only ~\$5,000–\$7,800/year (\$5–\$8 per student per academic year)**. Even on Opus 5.5 with Multi-AZ AWS hosting and a 25% retry margin, a single student's entire TFG year costs less than **\$8** — which is why institutional B2B licensing easily clears healthy margins (see `evidence-log/pricing-and-metrics.md`).

---

## 8. Chosen Cost Levers (Course Framework, Slide 264)

| Lever | How TFGPT implements it | Measured / Expected impact |
|---|---|---|
| **1. Rules first** | Quote matching, section verification, flag-ledger state (`open`/`solved`/`dismissed`), caps, and CSV/JSON scoring are deterministic Python code, never LLM calls | Eliminates extra judge/verifier LLM calls on every student check |
| **2. Right model per job** | **Claude Haiku 5.5** (\$0.10/\$0.50 per 1M) runs automatic thread compaction (`COMPACT_ENGINE=haiku`), while stronger models handle checking and stage answers | ~40× cheaper compaction (~\$0.00035/fold vs. ~\$0.015 on Opus) |
| **3. Cache what repeats** | Document pack (~51k tokens on Claude) is marked for Anthropic prompt caching (`cache: true` in `harness`) so turn 2, re-checks, and consecutive questions hit cache at 90%–95% discount (\$0.10/1M vs. \$2.00/1M on Sonnet) | Measured in `runs-public.csv`: ~81% of C2 input tokens were cache reads (83,069 / 102,763) |
| **4. Send less** | Rolling summary + last 12 messages (`TAIL=12`) instead of full conversation history; uploads purged after 30 min; narrowing the check prompt after Friday's human counts cuts over-flagging (currently 24–29 flags/review on approved text) | Expected −40% to −50% output tokens once narrowed (re-verify quality on `tfgpt_eval` after any prompt trim) |
| **5. Enforced limits** | Hard caps in `harness`: `CHECKS_PER_STUDENT_DAY=10`, `TOKENS_PER_STUDENT_DAY=1,500,000`, `DAILY_BUDGET_USD=15` (all Railway/AWS env vars), plus per-provider circuit breakers | Prevents runaway spend or Jevons-paradox loops |
| **6. Batch / async queue** | Postgres `FOR UPDATE SKIP LOCKED` job queue decouples multi-minute checks from HTTP requests and keeps worker container sizing small | Avoids over-provisioning web servers; enables optional batch API tier (−50%) for future Phase 3 scheduled checks |

---

## 9. Assumptions, Caveats & What Is Still Unmeasured

- **Provisional quality link:** Cost-per-caught-point is provisional until blind human scoring (`adriFCM`, `kristgiuff05`, due 2026-11-27) and the full `tfgpt_eval` run (`--repeats 3 --held-out --questions --rechecks`) complete.
- **Provider price drift:** `mistral-large-4` (\$0.70/\$2.10) was listed as a half-price preview; re-verify prices before locking `engines.json`.
- **Re-check & Ask token counts:** Currently estimated from prompt sizes and the synthetic smoke run; replace with measured means once `tfgpt_eval` runs on the full set and live user testing accumulates in `harness.runs`.
- **AWS `eu-south-2` rates:** Based on standard public `eu-south-2` On-Demand list rates (Nov 2026); actual enterprise IE AWS discounts (EDP / academic credits) would lower hosting costs further.
