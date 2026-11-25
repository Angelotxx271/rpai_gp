# Advisor spike results (public: counts only)

Matches from: judge judge-sonnet, a first pass: the human scores are the headline. Generated 2026-11-25T09:38. Engines: glm, mistral, opus, sonnet. Harness commit: 8b8c8cfbbf75. A point counts as caught in a cell when a majority of repeats caught it. Failed runs not scored: 7. Notes on runs left out: 0.

| Engine | Cond | Version | Repeats | Caught / raised (majority) | K per repeat | G caught | Early (mean) | Carry (mean) | Flags (mean) | Correct extra | Wrong | Taste | Tokens in/out (mean) | s (mean) | $ (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| glm | C0 | v1 | 3 | 3 / 10 | 3, 3, 5 | 2 / 4 | 2.7 | 0.0 | 40.0 | 4.3 | 0.7 | 28.7 | 4324 / 28777 | 130 | n/a |
| glm | C0 | v2 | 3 | 0 / 5 | 2, 1, 0 | 0 / 0 | 1.0 | 0.0 | 39.3 | 6.0 | 0.7 | 30.7 | 5346 / 26080 | 162 | n/a |
| glm | C0 | v3 | 3 | 1 / 3 | 1, 2, 1 | 0 / 0 | 0.0 | 0.0 | 34.7 | 2.3 | 2.7 | 28.0 | 5110 / 19467 | 112 | n/a |
| glm | C0 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 1.0 | 35.3 | 3.0 | 1.3 | 30.0 | 5016 / 22079 | 179 | n/a |
| glm | C1 | v1 | 3 | 2 / 10 | 2, 3, 3 | 1 / 4 | 0.3 | 0.0 | 12.0 | 3.0 | 2.3 | 4.0 | 26829 / 69620 | 312 | n/a |
| glm | C1 | v2 | 3 | 1 / 5 | 2, 1, 0 | 0 / 0 | 1.0 | 0.0 | 15.7 | 4.7 | 0.3 | 8.3 | 28140 / 79414 | 434 | n/a |
| glm | C1 | v3 | 3 | 0 / 3 | 0, 0, 0 | 0 / 0 | 0.0 | 0.0 | 11.7 | 6.0 | 0.7 | 5.0 | 27406 / 60107 | 291 | n/a |
| glm | C1 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.0 | 15.7 | 8.7 | 0.7 | 6.3 | 27722 / 72181 | 326 | n/a |
| glm | C2 | v1 | 3 | 4 / 10 | 3, 3, 4 | 2 / 4 | 0.7 | 0.0 | 11.3 | 1.7 | 0.7 | 5.7 | 64867 / 69858 | 299 | n/a |
| glm | C2 | v2 | 3 | 2 / 5 | 2, 2, 0 | 0 / 0 | 0.7 | 0.0 | 15.3 | 5.3 | 0.0 | 7.0 | 66133 / 69736 | 313 | n/a |
| glm | C2 | v3 | 3 | 0 / 3 | 0, 0, 1 | 0 / 0 | 0.0 | 0.0 | 18.3 | 6.0 | 0.7 | 11.3 | 66070 / 79236 | 433 | n/a |
| glm | C2 | final | 1 (incomplete) | 0 / 0 | 0 | 0 / 0 | 0.0 | 0.0 | 17.0 | 7.0 | 1.0 | 9.0 | 65736 / 76761 | 453 | n/a |
| mistral | C0 | v1 | 3 | 4 / 10 | 6, 2, 4 | 2 / 4 | 1.3 | 0.0 | 34.3 | 1.3 | 4.0 | 23.7 | 4302 / 17107 | 185 | n/a |
| mistral | C0 | v2 | 3 | 1 / 5 | 3, 1, 0 | 0 / 0 | 1.3 | 0.0 | 39.3 | 2.7 | 3.3 | 30.7 | 5460 / 15659 | 225 | n/a |
| mistral | C0 | v3 | 3 | 1 / 3 | 1, 1, 1 | 0 / 0 | 0.0 | 0.7 | 25.3 | 1.3 | 4.3 | 18.0 | 5036 / 13574 | 189 | n/a |
| mistral | C0 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.7 | 25.3 | 3.0 | 4.0 | 17.7 | 5307 / 15196 | 226 | n/a |
| mistral | C1 | v1 | 3 | 1 / 10 | 2, 1, 1 | 1 / 4 | 0.0 | 0.0 | 13.0 | 4.3 | 3.0 | 4.0 | 26553 / 30914 | 322 | n/a |
| mistral | C1 | v2 | 3 | 0 / 5 | 0, 0, 0 | 0 / 0 | 0.0 | 0.3 | 17.7 | 3.7 | 3.7 | 10.0 | 27818 / 28556 | 290 | n/a |
| mistral | C1 | v3 | 3 | 0 / 3 | 0, 0, 1 | 0 / 0 | 0.0 | 0.0 | 20.3 | 5.3 | 4.0 | 10.7 | 28045 / 28127 | 333 | n/a |
| mistral | C1 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.0 | 19.0 | 7.3 | 2.7 | 9.0 | 27985 / 30137 | 299 | n/a |
| mistral | C2 | v1 | 3 | 1 / 10 | 1, 3, 1 | 1 / 4 | 0.0 | 0.0 | 11.0 | 3.7 | 2.0 | 3.3 | 64338 / 32958 | 512 | n/a |
| mistral | C2 | v2 | 3 | 0 / 5 | 0, 0, 0 | 0 / 0 | 0.0 | 0.0 | 14.3 | 4.7 | 3.0 | 6.7 | 65579 / 29430 | 565 | n/a |
| mistral | C2 | v3 | 1 (incomplete) | 0 / 3 | 0 | 0 / 0 | 0.0 | 0.0 | 16.0 | 7.0 | 0.0 | 9.0 | 65238 / 23513 | 442 | n/a |
| opus | C0 | v1 | 3 | 2 / 10 | 2, 2, 3 | 2 / 4 | 2.0 | 0.0 | 37.0 | 8.0 | 0.0 | 24.3 | 5930 / 7004 | 74 | 0.157 |
| opus | C0 | v2 | 3 | 2 / 5 | 1, 2, 1 | 0 / 0 | 2.0 | 0.0 | 43.0 | 6.3 | 1.3 | 31.7 | 7810 / 7655 | 77 | 0.170 |
| opus | C0 | v3 | 3 | 1 / 3 | 1, 1, 1 | 0 / 0 | 0.0 | 0.0 | 32.7 | 5.0 | 0.3 | 26.3 | 7375 / 7881 | 81 | 0.174 |
| opus | C0 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 1.0 | 31.7 | 8.7 | 2.3 | 19.7 | 7933 / 7760 | 80 | 0.174 |
| opus | C1 | v1 | 3 | 4 / 10 | 4, 4, 4 | 3 / 4 | 1.0 | 0.0 | 28.7 | 5.7 | 1.7 | 16.7 | 42260 / 19708 | 170 | 0.449 |
| opus | C1 | v2 | 3 | 0 / 5 | 0, 0, 1 | 0 / 0 | 1.0 | 0.0 | 28.0 | 5.3 | 1.3 | 20.0 | 43543 / 21656 | 187 | 0.489 |
| opus | C1 | v3 | 3 | 2 / 3 | 1, 2, 2 | 0 / 0 | 0.0 | 0.0 | 27.7 | 10.3 | 1.0 | 14.7 | 43192 / 20181 | 177 | 0.459 |
| opus | C1 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.3 | 30.0 | 11.7 | 1.7 | 16.3 | 43647 / 21982 | 192 | 0.497 |
| opus | C2 | v1 | 3 | 3 / 10 | 3, 3, 4 | 2 / 4 | 1.0 | 0.0 | 25.7 | 7.0 | 1.3 | 13.0 | 101717 / 21429 | 187 | 0.542 |
| opus | C2 | v2 | 3 | 2 / 5 | 3, 2, 1 | 0 / 0 | 2.0 | 0.0 | 29.0 | 9.3 | 0.3 | 15.3 | 103254 / 22279 | 194 | 0.561 |
| opus | C2 | v3 | 3 | 2 / 3 | 1, 2, 3 | 0 / 0 | 0.0 | 0.0 | 26.7 | 9.3 | 1.7 | 13.3 | 103044 / 19037 | 170 | 0.496 |
| opus | C2 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.3 | 29.3 | 14.0 | 0.0 | 15.0 | 103036 / 22828 | 199 | 0.572 |
| sonnet | C0 | v1 | 3 | 3 / 10 | 3, 3, 3 | 2 / 4 | 2.7 | 0.0 | 39.0 | 6.0 | 0.3 | 25.7 | 6029 / 8196 | 69 | 0.091 |
| sonnet | C0 | v2 | 3 | 2 / 5 | 2, 2, 2 | 0 / 0 | 2.0 | 0.0 | 40.0 | 5.7 | 0.7 | 29.0 | 7525 / 9460 | 76 | 0.103 |
| sonnet | C0 | v3 | 3 | 3 / 3 | 3, 2, 3 | 0 / 0 | 0.0 | 0.0 | 35.0 | 7.7 | 1.0 | 23.7 | 7516 / 9405 | 76 | 0.103 |
| sonnet | C0 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.7 | 36.0 | 8.0 | 1.3 | 26.0 | 7162 / 9265 | 76 | 0.100 |
| sonnet | C1 | v1 | 3 | 3 / 10 | 3, 3, 3 | 2 / 4 | 1.0 | 0.0 | 20.0 | 5.0 | 1.3 | 9.7 | 41138 / 27426 | 182 | 0.299 |
| sonnet | C1 | v2 | 3 | 1 / 5 | 1, 1, 1 | 0 / 0 | 1.0 | 0.0 | 21.7 | 6.0 | 0.7 | 12.3 | 42610 / 27597 | 182 | 0.301 |
| sonnet | C1 | v3 | 3 | 1 / 3 | 1, 1, 1 | 0 / 0 | 0.0 | 0.0 | 22.7 | 8.3 | 0.7 | 12.7 | 42714 / 26326 | 178 | 0.290 |
| sonnet | C1 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.7 | 24.0 | 10.7 | 0.0 | 12.7 | 42578 / 29986 | 204 | 0.326 |
| sonnet | C2 | v1 | 3 | 3 / 10 | 4, 3, 2 | 2 / 4 | 0.0 | 0.0 | 23.3 | 6.0 | 0.7 | 14.0 | 101097 / 31062 | 208 | 0.366 |
| sonnet | C2 | v2 | 3 | 0 / 5 | 0, 1, 0 | 0 / 0 | 1.0 | 0.0 | 23.0 | 8.7 | 0.3 | 12.7 | 102383 / 34368 | 230 | 0.399 |
| sonnet | C2 | v3 | 3 | 1 / 3 | 1, 1, 1 | 0 / 0 | 0.0 | 0.0 | 24.7 | 7.7 | 0.7 | 15.3 | 102343 / 36874 | 249 | 0.425 |
| sonnet | C2 | final | 3 | 0 / 0 | 0, 0, 0 | 0 / 0 | 0.0 | 0.0 | 23.7 | 8.0 | 1.0 | 14.7 | 102397 / 33381 | 226 | 0.390 |

## Pooled over V1 to V3 (falsifier 3 reads the miss rate)

Complete cells only (3 scored repeats); a row with fewer than three rounds shows fewer points.

| Engine | Cond | Caught | Missed | Miss rate | G caught |
|---|---|---|---|---|---|
| glm | C0 | 4 / 18 | 14 | 78% | 2 / 4 |
| glm | C1 | 3 / 18 | 15 | 83% | 1 / 4 |
| glm | C2 | 6 / 18 | 12 | 67% | 2 / 4 |
| mistral | C0 | 6 / 18 | 12 | 67% | 2 / 4 |
| mistral | C1 | 1 / 18 | 17 | 94% | 1 / 4 |
| mistral | C2 | 1 / 15 | 14 | 93% | 1 / 4 |
| opus | C0 | 5 / 18 | 13 | 72% | 2 / 4 |
| opus | C1 | 6 / 18 | 12 | 67% | 3 / 4 |
| opus | C2 | 7 / 18 | 11 | 61% | 2 / 4 |
| sonnet | C0 | 8 / 18 | 10 | 56% | 2 / 4 |
| sonnet | C1 | 5 / 18 | 13 | 72% | 2 / 4 |
| sonnet | C2 | 4 / 18 | 14 | 78% | 2 / 4 |

## Decision rules (protocol v2), provisional

Stand-in = C2 on opus. C = K (majority) + E (mean), W = mean wrong flags. A noisy cell (K varies by more than 1 across repeats) widens the C tolerance from 1 to 2. Only cells with all 3 repeats scored are read.

Cells not read yet, scored repeats in brackets: glm/C2/final (1), mistral/C2/v3 (1)

- **Falsifier 3:** C2 on opus caught 7 of 18, miss rate 61%: **holds** (above 40%): narrow the check

| Engine | Route | v1 C/W vs stand-in | v2 | v3 | Same flags in | Flags half |
|---|---|---|---|---|---|---|
| glm | C0 | 7.33/0.67 vs 10.00/1.33 differs (noisy) | 6.00/0.67 vs 11.33/0.33 differs (noisy) | 3.33/2.67 vs 11.33/1.67 differs (noisy) | 0 of 3 | does not hold |
| glm | C1 | 5.00/2.33 vs 10.00/1.33 differs | 5.67/0.33 vs 11.33/0.33 differs (noisy) | 6.00/0.67 vs 11.33/1.67 differs (noisy) | 0 of 3 | does not hold |
| mistral | C0 | 5.33/4.00 vs 10.00/1.33 differs (noisy) | 3.67/3.33 vs 11.33/0.33 differs (noisy) | 2.33/4.33 vs 11.33/1.67 differs (noisy) | 0 of 3 | does not hold |
| mistral | C1 | 5.33/3.00 vs 10.00/1.33 differs | 3.67/3.67 vs 11.33/0.33 differs (noisy) | 5.33/4.00 vs 11.33/1.67 differs (noisy) | 0 of 3 | does not hold |
| opus | C0 | 10.00/0.00 vs 10.00/1.33 same | 8.33/1.33 vs 11.33/0.33 differs (noisy) | 6.00/0.33 vs 11.33/1.67 differs (noisy) | 1 of 3 | does not hold |
| opus | C1 | 9.67/1.67 vs 10.00/1.33 same | 5.33/1.33 vs 11.33/0.33 differs (noisy) | 12.33/1.00 vs 11.33/1.67 same (noisy) | 2 of 3 | holds |
| sonnet | C0 | 9.00/0.33 vs 10.00/1.33 same | 7.67/0.67 vs 11.33/0.33 differs (noisy) | 10.67/1.00 vs 11.33/1.67 same (noisy) | 2 of 3 | holds |
| sonnet | C1 | 8.00/1.33 vs 10.00/1.33 differs | 7.00/0.67 vs 11.33/0.33 differs (noisy) | 9.33/0.67 vs 11.33/1.67 same (noisy) | 1 of 3 | does not hold |

Per-run tokens, time, cost and counts: runs-public.csv (137 runs, 7 failed and not saved). The proposal text, the answer key and the reviews stay private.
