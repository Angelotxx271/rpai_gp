# Scoring guide for the advisor spike

For the scorer (adriFCM) and the second checker (kristgiuff05), as named in `evidence-log/decision-record.md`. The rules come from protocol v2 in `evidence-log/spikes.md`. Your counts are the headline: the AI judge's counts are only a first pass that you check.

## What you get

Angelotxx271 sends you, privately and never through this repo, a folder with four pairs of files, one pair per version of the proposal:

- `sheet-v1.md` (and v2, v3, final): the key points at the top, then the anonymous reviews, numbered L01, L02 and so on. You can't tell which AI or which route wrote a review, and you shouldn't try to. Each review has two turns
- `sheet-v1.csv`: one row per key point, one column per review, and a last row called `done`

## How to score one review

1. Read both turns of the review
2. For each key point at the top of the sheet, decide whether the review raises **the same problem in the same passage**. A flag on the same passage about a different problem is not a match. A general remark ("improve clarity", "proofread") is not a match for a specific point. **When in doubt, it is not a match**
3. In the CSV, in that review's column:
   - **Match:** write where the review raises it (`T1 3` for turn 1, point 3; several places separated by spaces), or just `x`
   - **No match:** leave the cell empty
4. When you have decided every key point for that review, put `x` in its `done` row. A review without `x` in `done` is left out, so a review you didn't get to never counts as "no matches"

Excel is fine: it may save with `;` instead of `,`, and that's handled. Keep the file names as they are.

## Which reviews

Both of you score **the same reviews, in order from L01**, because only reviews you have both scored count. The order is already random, so the first ones are a fair sample of every engine and route. Agree with Angelotxx271 how far to go. A suggested minimum is L01 to L10 in each of V1, V2 and V3, which is 30 reviews and takes a few hours. The `final` sheet (the approved version) is optional.

## Rules

- **Score alone.** Don't compare answers with each other before you hand them in. Where you two disagree, it counts as not matched
- **Never paste a sheet or a review into any AI tool.** The sheets hold the key points written from the supervisor's comments and quotes from an unsubmitted thesis
- Don't share the sheets, and don't ask which AI wrote which review. Angelotxx271 keeps the key (`map.json`) until scoring is over
- Return your filled CSVs to Angelotxx271 privately by **Friday 27 November 2026**

## What happens next

Angelotxx271 puts each person's CSVs in their own folder and runs `spike.py agree` on the two folders. It combines your two scores (a disagreement counts as not matched), then compares them with the judge, per engine too. If you and the judge disagree on more than 1 point in 5, only the reviews you scored are reported (`report --source human`). The counts, never the reviews, then go into spikes.md.
