---
name: course-ai-interaction-logger
description: "Preview and, only after explicit user approval, create or update the Rapid Prototyping with AI course AI Usage Log. Use when a student asks to log, summarise, record, append, rebuild, or update meaningful AI interactions. Every user-facing response and generated log uses Markdown table format. Preserves student judgement and human verification, uses the syllabus to label stages when available, appends safely by default, and overwrites only with explicit permission."
---

# Course AI Interaction Logger

## Purpose

Maintain concise, audit-ready evidence of how Artificial Intelligence supported the student's work across the full Rapid Prototyping with AI course

The log must make two things visible at the same time:

- What the AI materially contributed
- What the student decided, checked, changed, rejected, or remained responsible for

Do not turn the log into a transcript or a list of every prompt

## Course grounding

When the course repository or syllabus is available, use this authority order:

1. Professor's latest approved instruction
2. Relevant `syllabus_roadmap.md` session or session range
3. Approved task or exercise brief
4. Repository instructions such as `AGENTS.md`
5. The visible conversation, supplied transcripts, files, and project artifacts

The canonical course destination is normally:

`evidence-log/ai-usage-log.md`

Use another path when the student explicitly supplies one

The course treats AI as a working method while keeping students responsible for judgement, evidence, validation, security, and final decisions. Preserve that distinction in every row

## Required table

Use exactly these six columns in this order:

`Date | Tool & version | Stage/ Step | Use | Output used | Student's decisions`

Markdown header:

```markdown
| Date | Tool & version | Stage/ Step | Use | Output used | Student's decisions |
|---|---|---|---|---|---|
```

Do not add extra columns unless the professor explicitly changes the schema

## Mandatory approval gate

Always show the proposed AI interactions to the user before creating or changing a file

1. Draft the supported rows
2. Display the complete proposed interaction table in the screen, console, or chat where the skill is running
3. Stop and request explicit approval to write those exact rows
4. If the user requests changes, revise the rows and display the complete table again
5. Create, append, overwrite, or rebuild the file only after the user explicitly approves the currently displayed table

A request to log, update, append, rebuild, or overwrite starts the preview workflow. It does not approve a file change before the preview

Approval must refer clearly to the latest displayed table. Do not treat silence, a prior approval, or approval of different rows as approval

The approval request must also be a Markdown table. Use this shape after the interaction table:

```markdown
| Status | Required action |
|---|---|
| Awaiting approval | Approve this table to write it, or request changes |
```

Do not include prose, headings, bullets, or code fences outside the rendered tables in any user-facing response

## What counts as a loggable interaction

Log meaningful AI use that materially contributed to course work, including when AI:

- Structured or challenged an opportunity, assumption, goal, experiment, decision, or reflection
- Helped prepare, critique, or synthesise user research while preserving real-user evidence
- Compared alternatives, concepts, tools, models, architectures, or implementation paths
- Helped define workflows, specifications, acceptance criteria, risks, controls, data handling, or architecture decisions
- Generated, modified, explained, debugged, or reviewed prototype code or configuration that the student actually used
- Helped design or run evaluations, test cases, adversarial checks, accessibility checks, user tests, or evidence reviews
- Helped interpret failures and decide what to change, remove, keep, retest, pivot, or stop
- Supported preparation of phase-gate evidence or the final venture recommendation

Do not log routine or low-value interactions such as:

- Spelling fixes or trivial rewording with no substantive effect
- Navigation questions or simple tool commands
- Repeated prompts that did not change the work
- Exploratory outputs the student ignored and that did not affect a decision
- Every individual debugging turn when several turns belong to one meaningful debugging episode

Prefer one row for one meaningful episode or decision point

## Scope and evidence source

When the student asks to log a particular session or range of sessions:

1. Use only interactions visible in the current conversation, supplied transcripts, supplied files, or project history the current environment can actually access
2. Do not invent missing interactions from the syllabus
3. Use the syllabus only to identify the correct stage, step, learning purpose, or artifact ownership
4. If important source material is missing, identify what is missing and request it in a two-column Markdown status table
5. If the student gives a short recap of an off-platform AI interaction, log it as student-reported rather than pretending the interaction was directly observed

Do not claim completeness beyond the evidence available

## Session and stage labelling

Use `Stage/ Step` to make the row traceable to the course sequence

When a session number and syllabus are available, prefer:

`SNN · [short syllabus-aligned activity or step]`

Examples of shape only:

- `S03 · Interview guide`
- `S10 · Workflow map`
- `S21 · Evaluation Suite`

Do not copy these labels when they do not match the actual session

For work spanning sessions, use the session where the material decision or output occurred. If one interaction genuinely spans a range, use `S07-S08 · [step]`

If the session is known but the specific step is not, use `SNN · Course project work` rather than inventing a false label

## Column rules

### Date

Use `YYYY-MM-DD`

Use the actual interaction date when available. If only a session date is known, use that date. Never fabricate a date

### Tool & version

Record the exact AI tool and model/version when known, for example `ChatGPT · GPT-5.6 Sol`

If the tool is known but the model/version is not, use `[Tool] · version not recorded`

If neither is known, use `Not recorded`

Never invent a model version

### Stage/ Step

Use the syllabus-aligned session and short activity label when available

Keep it concise and traceable

### Use

State what the AI was used for and why it mattered

Prefer specific functions such as:

- `Challenged assumption wording and surfaced overlap before prioritisation`
- `Compared two implementation approaches against speed, control, and privacy`
- `Debugged failing parser and proposed targeted test cases`

Do not write vague entries such as `Helped with project` or `Used AI for research`

### Output used

Record only what actually influenced the student's work

Good forms include:

- A revised structure the student adopted
- A shortlist or comparison used for a decision
- Code, tests, prompts, or configuration incorporated into the prototype
- A critique that caused the student to change their own work
- `No direct output adopted; critique informed revision` when the interaction mattered without copied output

Do not claim an output was used merely because AI generated it

### Student's decisions

Make student control visible

State what the student accepted, rejected, changed, verified, tested, or decided after considering the AI output

Where relevant, include human verification or a known limitation in this cell because the six-column course schema has no separate verification column

Good patterns include:

- `Kept the narrower segment after comparing evidence; rejected the broader framing`
- `Accepted the code only after tests passed; changed error handling manually`
- `Used the critique to revise the metric; kept the original threshold`
- `Rejected the recommendation because it relied on a weak proxy`

Do not imply that the AI made the final judgement

## Attribution discipline

Describe AI contribution with restrained verbs such as:

- drafted
- structured
- compared
- proposed
- identified
- summarised
- challenged
- explained
- generated
- debugged
- checked

Reserve final-decision language for the student

Do not write that the AI approved, validated, confirmed, decided, selected, accepted, rejected, or proved a course conclusion unless the sentence clearly describes a mechanical test result rather than a human judgement

## Granularity

Aim for concise, useful evidence rather than a process diary

As a default:

- A normal session often needs about 3 to 6 rows
- A light session may need only 1 to 2 rows
- A dense build or evaluation session may need more

Do not force a target row count. Cluster repeated prompts into one row when they serve one meaningful activity or decision

A good row should let a professor understand what AI did and what the student retained responsibility for without reopening the original chat

## Multi-session requests

For a range such as `log Sessions 7 to 10`:

1. Review the available interactions across the requested range
2. Group them by session and meaningful activity
3. Avoid duplicate rows for the same output or decision
4. Preserve chronological order
5. Use one row per meaningful AI-assisted episode, not one row per message
6. Note any requested session for which no supported interaction evidence is available

Do not fabricate filler rows so every session appears populated

## File behaviour

### No path supplied

If the course project filesystem is available, use `evidence-log/ai-usage-log.md`

If the file does not exist, create it after approval with:

```markdown
| Date | Tool & version | Stage/ Step | Use | Output used | Student's decisions |
|---|---|---|---|---|---|
```

Then add the new rows

If the file already exists, append the approved rows by default without rewriting historical rows

If the filesystem is unavailable, return the complete approved Markdown table in the response so the student can save it

### Path supplied

Use the exact supplied `.md` path

If it does not exist, create it only after the student approves the displayed table

If it exists and the student asks to `update`, `log`, or `append`, preserve the existing content and append only the approved rows

If it exists and the student explicitly asks to `overwrite`, `replace`, or `rebuild` the file, treat that as overwrite permission only when the exact path is clear

If overwrite intent or path is ambiguous, request confirmation in a two-column Markdown status table before replacing anything

Never overwrite an existing file merely because a path was supplied

## Existing-log protection

Before appending or overwriting an existing log:

1. Read the existing file
2. Preserve the six-column schema unless the professor explicitly changed it
3. Check for duplicate or substantially overlapping rows
4. Preserve historical dates, tool names, and student decisions unless overwrite/rewrite was explicitly requested
5. Keep rows in chronological order when rebuilding

For append operations, do not silently edit old rows

For an explicitly authorised rebuild, preserve supported historical facts and remove only duplicates or wording problems that the student asked to correct

## Logging workflow

When invoked:

1. Identify the requested session, session range, date range, or current interaction scope
2. Identify the source material available to support the log
3. Determine the output path, defaulting to `evidence-log/ai-usage-log.md` when appropriate
4. Read the relevant syllabus section when available so `Stage/ Step` reflects the actual course sequence
5. Read the existing log when one exists
6. Extract only meaningful AI-assisted episodes
7. Draft rows using the six-column schema
8. Check attribution, evidence support, duplicates, dates, and tool/version accuracy
9. Display the complete proposed interaction table
10. Display the table-formatted approval request and stop without changing any file
11. After explicit approval of the displayed table, create or append to the file
12. Overwrite only when both the displayed rows and the overwrite operation were explicitly approved
13. Report the path and row count in a Markdown status table

If the user asks only to preview or draft the rows, display only the interaction table and do not write a file

## Quality audit

Before finalising, verify mechanically:

- Exactly six columns are present and in the required order
- Every row is supported by available interaction evidence or clearly identified student-reported context
- Every date is supported or explicitly unknown
- Tool/model information is exact when known and never invented
- `Stage/ Step` matches the syllabus or available course context
- `Use` explains the material AI role rather than a generic activity
- `Output used` describes what actually influenced the work
- `Student's decisions` shows human judgement, verification, change, rejection, or responsibility
- Routine interactions have been excluded
- Closely related prompts have been clustered rather than over-logged
- Existing rows are not overwritten during an append
- No destructive overwrite occurs without explicit permission
- No file is created or changed before the latest displayed interaction table is explicitly approved
- The written file contains the approved six-column Markdown table and no generated prose outside table format
- Every user-facing response contains only rendered Markdown tables
- Real-user evidence is not replaced by synthetic or AI-generated feedback
- The log does not imply that AI made consequential academic, product, privacy, security, legal, fiscal, or business decisions for the student

## Course-wide usefulness

Keep this skill applicable from course launch through the final venture decision

Do not hard-code one particular method, artifact, AI vendor, model family, or project stage

Use the live syllabus to adapt `Stage/ Step` as the course progresses from discovery and assumptions through specification, prototyping, evaluation, user testing, evidence-driven iteration, responsible AI, deployment readiness, and final recommendation

## Output style

Every user-facing output must use rendered Markdown table format, including previews, approval requests, missing-evidence requests, clarification requests, warnings, and completion reports

For a preview, show the six-column interaction table first. Then show the two-column approval table unless the user requested preview only

After an approved file write, use this format:

```markdown
| Result | Details |
|---|---|
| File | `evidence-log/ai-usage-log.md` |
| Change | Added 3 approved rows |
| Evidence gaps | None |
```

Adapt the values and path to the actual result. Include unavailable sessions in the `Evidence gaps` row

Do not output prose, headings, lists, block quotes, or code fences outside the rendered tables. Keep cell content in plain English suitable for first-year bachelor students
