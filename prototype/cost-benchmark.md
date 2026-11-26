# Cost benchmark

Version 0.1, 2026-11-25. Status: draft, written from the advisor spike's run records for revision and team review. It records what the comparisons cost and what one production check would cost at the prices read today. It is not a price for students

## Sources
- `prototype/advisor-spike/results/runs-public.csv` — harness commit `8b8c8cf`, 173 scored arm runs (7 budget-failures never completed and are not in it)
- `prototype/advisor-spike/results/results-public.md` and `evidence-log/spikes.md` (Results, protocol v2)
- The Mistral API price page (docs.mistral.ai/inference/pricing), read 2026-11-25, for `mistral-large-4` and `zai-glm-5-3`
- The Claude engines: the per-run costs the Anthropic API recorded in the run rows; not recomputed from list prices
- The local Qwen: marginal $0 per run on owned hardware; electricity not measured

## Prices used (per 1M tokens, USD, read 2026-11-25)

| Model | Input | Cached input | Output | Where from |
|---|---|---|---|---|
| `mistral-large-4` | $0.70 | $0.07 | $2.10 | Mistral price page |
| `zai-glm-5-3` | $1.40 | $0.14 | $4.40 | Mistral price page |
| `claude-opus-5-5` | — | — | — | recorded per-run costs only |
| `claude-sonnet-5-5` | — | — | — | recorded per-run costs only |
| Qwen 3.6 35B-A3B, local | $0 | — | $0 | own GPU (RTX 5070, 12 GB) |

One third-party page reports `mistral-large-4` as a half-price public preview since 2026-10-06, list $1.36/$4.18; the table uses the price page's current numbers. Re-read before the engine lock-in: prices move

## Per-run means, by engine and route

| Engine | Route | Runs | Tokens in/run | Tokens out/run | Seconds/run | $/run | Cell total |
|---|---|---|---|---|---|---|---|
| Opus 5.5 | C0 own AI as usual | 12 | 7,262 | 7,575 | 78 | $0.169 | $2.03 |
| Opus 5.5 | C1 everything pasted | 12 | 43,160 | 20,882 | 182 | $0.473 | $5.68 |
| Opus 5.5 | C2 stand-in | 12 | 102,763 | 21,393 | 188 | $0.543 | $6.52 |
| Sonnet 5.5 | C0 | 12 | 7,058 | 9,082 | 74 | $0.099 | $1.19 |
| Sonnet 5.5 | C1 | 12 | 42,260 | 27,834 | 186 | $0.304 | $3.65 |
| Sonnet 5.5 | C2 | 12 | 102,055 | 33,921 | 228 | $0.395 | $4.74 |
| GLM 5.3 | C0 | 12 | 4,949 | 24,101 | 146 | $0.110 | $1.32 |
| GLM 5.3 | C1 | 12 | 27,525 | 70,330 | 341 | $0.321 | $3.85 |
| GLM 5.3 | C2 | 10 | 65,695 | 73,325 | 359 | $0.339 | $3.39 |
| Mistral Large 4 | C0 | 12 | 5,026 | 15,384 | 206 | $0.034 | $0.41 |
| Mistral Large 4 | C1 | 12 | 27,600 | 29,434 | 311 | $0.067 | $0.80 |
| Mistral Large 4 | C2 | 7 | 64,998 | 30,097 | 524 | $0.075 | $0.52 |
| Qwen local | C0 | 12 | 5,295 | 6,545 | 98 | $0 | $0 |
| Qwen local | C1 | 12 | 28,269 | 12,921 | 188 | $0 | $0 |
| Qwen local | C2 | 12 | 67,731 | 12,748 | 209 | $0 | $0 |

Totals per engine: Opus **$14.22** (36 runs), Sonnet **$9.57** (36), GLM 5.3 **$8.56** (34), Mistral Large 4 **$1.74** (31), Qwen local **$0** (36) — **$34.09** for all 173 scored runs. The Claude total, $23.79 for 72 runs, matches the "$23.80" note in spikes.md. The blind first-pass judge (Sonnet 5.5) cost **$10.76** for 137 judgments, on top

## What one production check would cost (the C2 row)

| Engine | $/check, at spike prompts | With a 1.5× retry margin |
|---|---|---|
| Opus 5.5 | $0.543 | ≈ $0.81 |
| Sonnet 5.5 | $0.395 | ≈ $0.59 |
| GLM 5.3 | $0.339 | ≈ $0.51 |
| Mistral Large 4 | $0.075 | ≈ $0.11 |
| Qwen local | $0 | $0 (no cloud) |

A per-student daily cap of $1 holds on every cloud engine: two GLM checks, six Mistral, or one Opus with change. The cap and the price fields belong in the harness registry (`prototype/tfgpt/harness/engines.json`), so the `runs` table shows real money per student as it happens: `mistral-large-4 (0.70, 0.07, 2.10)`, `zai-glm-5-3 (1.40, 0.14, 4.40)` per 1M in/cached/out

## Cost against quality, so far

Judge first pass only; the scorer's and second checker's counts are the headline and were still to come when this was written (due 2026-11-27)

| Engine | $/C2 check | Pooled caught (first pass) | Miss rate | First-pass reading |
|---|---|---|---|---|
| Opus 5.5 | $0.543 | 7 of 18 | 61% | best catch of the stand-in route, highest price |
| Sonnet 5.5 | $0.395 | 4 of 18 | 78% | cheaper, weaker as stand-in |
| GLM 5.3 | $0.339 | 6 of 18 | 67% | mid on both |
| Mistral Large 4 | $0.075 | 1 of 15 scored | 93% | cheapest, caught almost nothing as stand-in |

Cost ranking is not quality ranking; no engine choice before the human counts

## Refill and the short cells

The Mistral-hosted spend for the whole spike was **$10.29** (GLM $8.56 + Mistral $1.74). Finishing the cells the budget cut short — Mistral C2 round 3 (×2) and final (×3), GLM C2 final (×2) — costs roughly **$1.05** at today's prices ($0.37 + $0.68). The 7 budget-failed runs never completed, so they are not priced. A $5 top-up covers the refill and a rerun with room left

## Assumptions and caveats

- tokens_in is read as the total prompt tokens and cache_read as the cached subset (how the Mistral API reports usage, and how the harness logs it); cost = (in − cached)×input + cached×cached-price + out×output. Without the cache split, the two Mistral-hosted engines would cost ≈ $11.74 instead of $10.29
- Token counts are each provider's tokenizer on the same text (the Claude engines log ~102k tokens where the others log ~66k on the same C2 pack); each provider bills its own counts
- Costs follow the spike's prompts: the full context pack per check. If Friday's counts narrow the check, tokens change and these numbers move; the registry's price fields make the recompute a script, not manual work
- All prices in USD, read 2026-11-25; the `mistral-large-4` preview discount may end without notice
