# Advisor spike harness

Runs the advisor comparison in `evidence-log/spikes.md` (protocol v2 and `protocol-v2-amendment-1.md`): the same frozen prompts, three routes (C0 own AI as usual, C1 own AI with everything pasted, C2 the TFGPT stand-in), four versions of one proposal, three repeats, on five engines. A blind judge then matches each review's flags to the answer key, and two people check the judge.

The code is public; the material it reads is not. The proposal versions, the context packs, the topic sentence, the answer key, the raw reviews and the API keys stay in `private/advisor-spike/` (git-excluded). Only counts come out, into `results/`.

## Engines

Pick them with `--engine`: a name, a group, or `all` (every engine that is on).

| Name | Model | Where | Settings |
|---|---|---|---|
| `opus` | Claude Opus 5.5 | Anthropic API | effort medium, adaptive thinking |
| `sonnet` | Claude Sonnet 5.5 | Anthropic API | API defaults (effort high) |
| `glm` | GLM 5.3 (`zai-glm-5-3`) | Mistral API | provider defaults |
| `mistral` | Mistral Large 4 (`mistral-large-4`) | Mistral API | provider defaults |
| `qwen-local` | Qwen 3.6 35B-A3B, Q4_K_M | Ollama on an RTX 5070 (12 GB) | 96k context, thinking on |
| off unless named | `qwen38-local`, `local-openai`, `opus-cli`, `haiku` | | |

Groups: `protocol-v2`, `claude`, `mistral-api`, `local`, `api`, `everything`. The judge is `judge-sonnet` (Claude Sonnet 5.5) and never runs as an arm.

## Run

From the repo root, with the spike's own Python (`private\advisor-spike\.venv`, built from `requirements.txt`):

```powershell
$py = "private\advisor-spike\.venv\Scripts\python.exe"
& $py -I -m pytest prototype\advisor-spike\tests -q                       # offline tests, no model calls
& $py -I prototype\advisor-spike\spike.py verify                          # key, protocol, amendment and prompts against spikes.md
& $py -I prototype\advisor-spike\spike.py check --engine everything       # one tiny call each, no thesis text
& $py -I prototype\advisor-spike\spike.py run --engine api --budget 40    # the cloud engines
& $py -I prototype\advisor-spike\spike.py run --engine local              # the local engine, a few hours
& $py -I prototype\advisor-spike\spike.py judge --engine api              # blind first pass
& $py -I prototype\advisor-spike\spike.py report --engine api             # results/results-public.md and runs-public.csv
```

`run` stops before sending anything if a committed hash differs or the harness has uncommitted changes. It skips finished runs, so an interrupted run resumes where it stopped, and reruns runs that failed (for example when an API's credits ran out). After all engines: `sheets` writes the blind sheets for the two scorers (how they score: [SCORING.md](SCORING.md)), `agree` reads their filled sheets back, then `report --source human` if the judge and the people differ on more than 1 point in 5.

## Safeguards

- A truncated, refused or empty answer fails the run instead of being scored; a prompt that might not fit the local context window is refused instead of cut
- A saved run made with another model or prompt is never reused; every run records its model, prompt hash and harness commit
- Keys are read from the private `.secrets.env` and never printed; Claude always goes to `api.anthropic.com`, whatever `ANTHROPIC_BASE_URL` says
- The public outputs are checked for key-point IDs and carry no review text
- `--budget` stops new runs once the spend reaches the limit

## Files

| Path | What |
|---|---|
| `spike.py` | The harness; `--help` lists every command |
| `engines.json` | Engines, groups, settings and prices ($ per million tokens; null = not yet known) |
| `protocol-v2-amendment-1.md` | The engines, their settings and how the decision rules are read, accepted before run 1 |
| `SCORING.md` | How the scorer and the second checker fill in the blind sheets |
| `tests/test_spike.py` | Offline tests with fake providers and a synthetic answer key |
| `results/` | Public counts: `results-public.md` and `runs-public.csv` (tokens, seconds, cost and counts per run) |
| `requirements.txt` | Pinned Python packages |
