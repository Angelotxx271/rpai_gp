# Advisor spike, protocol v2, amendment 1

Proposed by AI on 2026-11-24 and 2026-11-25, accepted by Angelotxx271 on 2026-11-25, before any run: "use qwen3.6", "effort for opus put it in medium", "start everything in order", and Mistral Large 4 and GLM 5.3 as the Mistral engines. Its SHA-256 sits next to the protocol's in `evidence-log/spikes.md`, and `spike.py verify` (which `run` calls first) checks it.

Nothing here changes the routes, the prompts, the answer key or the decision rules of protocol v2. It fixes the engines and their settings, and writes down how the harness reads the rules where protocol v2 leaves them open.

## 1. A fifth engine: Claude Sonnet 5.5

Asked for by the owner on 2026-11-24. It is reported like the other engines; it is not the stand-in engine. 5 engines x 3 routes x 4 versions x 3 repeats = 180 runs.

Sonnet 5.5 is also the judge. The judge is blind to the engine but may prefer reviews written the way it writes, so judge-vs-people agreement is reported per engine, and the human counts stay the headline.

## 2. Claude runs through the Anthropic API, not the Claude Code CLI

Asked for by the owner on 2026-11-24. The API gives exact token counts and cost per run.

- **Claude Opus 5.5:** effort **medium**, set by the owner on 2026-11-25 (also the API default). Adaptive thinking is on; on this model it can't be turned off
- **Claude Sonnet 5.5:** the API defaults: adaptive thinking, effort high
- No temperature or sampling settings (the API no longer accepts them). Answers can be up to 32,000 tokens
- Prompt caching is on for the arms. It changes the cost, not what the model reads
- No automatic fallback to another model. A refused run fails visibly, is not scored, and is reported
- The CLI route stays in the harness as `opus-cli`, off

## 3. The local engine is Qwen 3.6

`qwen3.6:35b-a3b` (Q4_K_M, a mixture of experts with about 3B active parameters) on Ollama 0.40.18, on an RTX 5070 with 12 GB and 64 GB of system memory. Context window 98,304 tokens, answers up to 32,768 tokens, flash attention, 8-bit KV cache, thinking on (the model's default).

Why: `qwen3.8:27b` is newer but is a dense 27B model that doesn't fit in 12 GB. Measured on 2026-11-25 with the same 42k-token prompt built from public repo files: Qwen 3.6 read it at 1,172 tokens/s and wrote at 67 tokens/s (125 s for 6,000 tokens); Qwen 3.8 read it at 727 tokens/s and wrote at 11 tokens/s (633 s). At that speed the 36 local runs would take more than a day on Qwen 3.8, against a few hours on Qwen 3.6. Both spent the 6,000 test tokens thinking before answering, hence the 32k answer limit.

The harness refuses any prompt that might not fit the context window instead of letting Ollama cut it.

## 4. The Mistral engines are pinned

Both on Mistral's API, IDs confirmed on 2026-11-25 from `GET /v1/models`:

- **Mistral:** `mistral-large-4` (Mistral Large 4.0; `mistral-large-latest` and `mistral-large-4-0` are aliases of it today, so the pinned name keeps the runs on one model)
- **GLM 5.3:** `zai-glm-5-3` (Z.ai's GLM 5.3)

Mistral's public pricing page doesn't give a per-model price, so their cost per run is filled in from the Mistral console after the runs. Token counts are logged either way.

## 5. Runs that aren't scored

A turn that stops for any reason other than a normal end (the length limit, a refusal, the context window), or comes back empty, counts as a failed run. Failed runs are rerun, never scored, and their count is reported. Turn 2 receives turn 1's answer text only, for every engine, so all engines get the same conversation. A saved run made with another model ID or another prompt is never reused or mixed into a cell. Only cells with all 3 repeats scored are read by the decision rules. Every run records the harness commit it ran on, and `run` refuses to start with uncommitted harness changes.

## 6. How the harness reads the decision rules

protocol v2 leaves these open; accepted as follows:

- **The stand-in for falsifier 4** is C2 on Claude Opus 5.5 for every route, the engine falsifier 3 is read on
- **C = K + E per round**, with K the points caught by at least 2 of 3 repeats and E the mean count of correct extra flags over the 3 repeats. W is the mean of wrong flags
- **The noise rule** ("a difference of 1 counts as the same") widens the C tolerance from 1 to 2 when either cell's K varies by more than 1 across its repeats. The W tolerance stays at 1
- **The flags half** holds for a route at 2 of 3 rounds with the same flags. It does not hold once 2 of 3 can no longer be reached
- **Judge against people:** "1 point in 5" counts each key point in each run scored by both people. The judge is compared with what both people matched, since disagreements between them count as not matched. The rate is also shown per engine
- **Human sheets:** a list counts as scored only when the scorer marks its "done" row. A list only one person scored is left out until both have

## 7. What is public and what stays private

Public (`prototype/advisor-spike/`, `evidence-log/spikes.md`): the harness, its tests, the engine settings, this amendment, and the results as counts: per cell, pooled, the decision rules, and a per-run log of tokens, seconds, cost and counts with no text.

Private (git-excluded, available to the professor on request, as spikes.md already says): the proposal versions, the context packs, the topic sentence, the answer key, the raw reviews, the judge's verdicts and the scorers' sheets. The reviews quote the proposal, and the proposal is unsubmitted thesis work that must not appear in a public repository.

## 8. Spending limit

`run --budget <dollars>` stops starting new runs once the money spent reaches the limit. Estimated before run 1 with `estimate`: about $11 for Opus and $5 for Sonnet on 36 runs each, plus the GLM and Mistral calls and roughly $15 to $20 for judging 180 runs with Sonnet. Local runs cost nothing.
