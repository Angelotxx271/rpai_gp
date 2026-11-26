> **Use:** final-project guide for Group Presentation II, Sessions 28 and 29, on 1 and 3 December 2026. Read it with the final-project slides

# Group Presentation II: final-project guide

Submit two deliverables: your repository with the remote build and supporting evidence, and your live presentation with demonstration and questions

This assessment weighs 25 % of the course grade. Within it, repository and build weigh 45 % and live presentation and mastery weigh 55 %

Build **one critical feature** from your roadmap, split into **about three sub-features** (two or three, as in Session 20). Each sub-feature runs end to end and is useful to a user on its own; none is a technical layer such as "the database" or "the front end"

This is a rapid prototyping course. We grade evidence, judgment and a working product, not engineering volume

**Validation against ground truth is required.** Without a reference set of known correct answers, your feature has nothing to be validated against, and a demo alone proves nothing. See Section 6, "Validation against ground truth"

## 1. The presentation: answer first

There is no fixed time split. You decide how to use your slot, and you must be ready to pivot when the professor asks a question. Questions can come at any point, and they take priority over your plan

Organise the pitch with two best practices from consulting:

### Tell it as one storyline: Situation, Problem, Solution, Impact

| Step | Question it answers | In your pitch |
|---|---|---|
| Situation | Who is the user, and in what context? | One line on the target user and their Job |
| Problem | What pain did real users confirm? | The struggle, and the evidence behind it |
| Solution | What did you build, and does it work? | Live demo of your feature, end to end, plus its score against ground truth and one safe failure |
| Impact | What changes for the user? | Quantify the gain, then recommend: iterate, pivot, stop or invest |

Source: BCG storyline framework

### Answer first: the pyramid principle

| Level | What it holds | When you say it |
|---|---|---|
| Answer | Your recommendation and its impact: what you built, for whom, and what it changes | Your first sentence |
| Key arguments | Two or three reasons to believe it: users need it, it scores well against ground truth, evidence shaped it | Right after the answer |
| Evidence | Demo, ground-truth results, tests, user feedback, specifications and reviewed commits | During the demo, or when a question asks for proof |

Source: Barbara Minto, The Pyramid Principle

Put together: say the impact first, walk the storyline briefly, demo the Solution, and only then go into details. Do not tour everything you built, and do not repeat the first presentation

### Your economics slide: required

Include one slide on the economics of your product, taught in Sessions 26-27:

- Cost: your cost per successful task, and what it includes (running cost only, or full delivery with human review and hosting)
- Price: how you set the price, what you charge for, how you package it, your price floor and your proposed price
- Fit: your strongest evidence that people want the product, and the next test that would strengthen it
- Metrics: one main metric and three guardrails, each with its target and data source

We do not grade how low your cost is or how high your price is. We assess whether your reasoning is clear, backed by evidence, and honest about what you have not tested. A price nobody has reacted to is a hypothesis: say so

Every member contributes, by presenting or by answering questions

Prepare to explain and demonstrate the whole feature and each sub-feature. Show representative proof live, and let the professor's questions pick any other part. If a question takes you elsewhere, follow it, answer it, then return to the impact

## 2. Live demo checklist

- Open the deployed build before your slot starts
- Use the safe test data you prepared and checked the day before
- Run the user task end to end before you open any file
- Show the feature's score against your ground-truth set, and one item it got wrong if any
- Show one failure path: a refusal, a validation error or a case sent to a person
- Then open a linked requirement, its named validation case and the recorded result
- Show one change you reviewed and how you checked it did not break earlier sub-features
- Keep a local or recorded backup of the same flow immediately accessible. If the live build fails, switch to it and say so
- Never show real personal data, tokens or keys on screen

## 3. Hand-in checklist, by 30 November 2026, 23:59 Madrid time

- Tag the submission commit `final` and push it
- The deployed build runs the `final` commit; show which commit it runs, for example with a version label
- Supply working links to the repository, `final` tag, remote build, presentation and backup, and check access from a fresh session that is not signed in as you
- `specs/tech-stack.md` explains how to run the build and how to undo a bad change
- `README.md` is the entry point and links to the evidence the presentation relies on
- The ground-truth set, how it was built, and the latest scored run on the `final` commit are in the repository
- `prototype/cost-benchmark.md` and `evidence-log/pricing-and-metrics.md` back your economics slide
- The local or recorded backup demonstration is ready
- No secrets or unapproved personal data in the repository or its history

A presentation outage is different from an absent remote deployment. A backup keeps the presentation going; it does not replace remote deployment. Disclose every simulated, manual or mocked step

## 4. Questions to prepare

The professor samples from these. Every member should be able to answer any of them

**Venture and evidence**

- What is your riskiest assumption today, and how strong is its evidence?
- Which real-user evidence changed your build? Show the entry
- What is your strongest alternative, and why would a user switch?
- Which Eliminate, Reduce, Raise and Create move survived contact with users?
- What did your Persona Agent suggest that real users contradicted?

**Specification and build**

- Why this critical feature, and why split it into these sub-features?
- Show one scenario and the case that proves it
- What does your root `AGENTS.md` allow and forbid?
- Show a change you reviewed and explain how you verified it; use an authentic example rather than manufacturing an agent mistake
- Why this build path and tech stack? What did you trade off?

**Agent use and orchestration**

- Which work did you give to a lead agent, and which to subagents or cheaper models? Why?
- Where did you keep one agent instead of delegating, and why?
- Which agent-stack parts did you use (`AGENTS.md`, skills, MCP servers, subagents, hooks), and which did you leave out on purpose?
- How did you verify what a subagent returned?

**Validation against ground truth**

- What is your ground truth, how many items does it hold, and who confirmed the correct answers?
- What does your feature score against it, and what was the score before your last change?
- Show one item the feature got wrong. What did you change, and did the rerun pass?
- Why is this set representative of real use, and what does it not cover?

**Evaluation and quality**

- Which case failed first, and what did you change?
- How do you know the last change did not break an earlier sub-feature?
- Your AI step varies between runs. How many repeats, and what passed?
- Explain a piece of generated code you kept

**Security**

- How do you show there are no secrets in the code or the history?
- Where does user data go, and which permissions does the product use?
- Which actions need a person's approval, and why those?
- What happens when an input contains instructions?

**Value and decision**

- Which signals show value, and at what sample size?
- What would make you stop?
- What did you remove or decide not to automate?

## 5. Where the evidence lives

Keep the four living artifacts: Evidence Log, Specification and Decisions, Prototype and Evaluation Repository, and Phase Evidence Pack

| Home | Contents or links |
|---|---|
| `README.md` | Entry point; links to repository, `final` tag, remote build, presentation, backup and the evidence your presentation uses (your Phase Evidence Pack) |
| `evidence-log/opportunity.md`, `goals.md`, `recruitment.md`, `assumptions.md`, `experiment-card.md` | Venture logic, Product Goal, current Sprint Goal, participant access, risks, thresholds, results and decisions |
| `evidence-log/jtbd.md`, `personas/`, `ERRC.md` | Job, evidence-bounded Personas and retained drafts, strategic choices and open proof |
| `evidence-log/user-feedback.md` | Both testing rounds: who took part, what you saw, what you changed and whether the retest supported it |
| `evidence-log/ai-usage-log.md` | Meaningful AI use and how a person checked it |
| `evidence-log/pricing-and-metrics.md` | Pricing choices, price floor, product-market fit evidence, and your main metric and guardrails, each marked measured, target or hypothesis |
| `specs/mission.md`, `tech-stack.md`, `roadmap.md` | Constitution, build path, tools, run and undo instructions, phases and Current behaviour |
| One dated folder per sub-feature under `specs/` | Each has `requirements.md`, `plan.md` and `validation.md`, with scenarios, named cases and executed results |
| Root `AGENTS.md`, `briefs/`, Git history | Coding-agent rules and limits, task-group briefs, test-first work, human review and commits |
| `prototype/` | Implementation, tests, safe data, environment definition and backup |
| `prototype/cost-benchmark.md` | Run log with real token usage, cost per attempt and per successful task for each route, monthly projection and chosen cost levers |
| Ground-truth set and scored runs (inside `prototype/` or linked from `validation.md`) | Reference inputs with known correct outputs, how they were built and checked, and each scored run with its commit |
| `downloads/` | Downloaded helper prompts, separate from team-authored evidence |

Market tables, value curves, research sources and feedback can stay in any readable format linked from the Evidence Log. Use the paths that suit your build; link them from `README.md`

## 6. Full evidence checklist

### Venture and strategy

- Connect the target user, Job and evidence-bounded Personas to the current solution
- Keep the Product Goal, current Sprint Goal and riskiest assumptions coherent
- Explain the strongest alternative, switching logic and decision-relevant market findings
- Show how Eliminate, Reduce, Raise and Create choices support the value proposition
- Keep Experiment Card thresholds and decision rules set before results, then record results and next actions
- Keep contradictions visible, and show which evidence changed the final solution
- State the current decision and next test

### Specification and agent discipline

- Keep the constitution current: mission, tech stack and roadmap
- State included behaviour and exclusions in each sub-feature's `requirements.md`
- Link every scenario to a named validation case
- Review plans and confirm task-group briefs before the agent builds
- Keep scope, commands, allowed actions and limits in root `AGENTS.md`
- Show test-first work, human review of changes and traceable commits
- Update `roadmap.md` Current behaviour from passed scenarios
- Give a fresh agent enough repository context to act without your chat history

### Agent use and orchestration

- Explain how you split the work across agents: one lead agent, subagents for bounded tasks, or a single agent where delegation did not pay off
- Match models to roles: capable models for direction and review, faster or cheaper models (cloud or local) for bounded tasks
- Name the pattern you used where relevant: routing, orchestrator and workers, or draft, review and revise
- Verify every delegated result with tests or your own review; a separate agent run is not independent evidence
- Optional: compare engines on the same feature, starting commit and tests (see Section 7)

We do not grade a cost figure or a price level. We grade whether your agent setup was a deliberate, proportionate choice you can explain, and whether your cost, pricing and metrics reasoning is evidenced and honest about its limits

### Security: required

Make this explicit in the repository and be ready to show it

- No secrets in code or Git history: keys, tokens and `.env` files stay out, ignored by Git, with a recorded check of the history
- Bounded permissions: the product and its agents get only the access they need
- Treat emails, documents, web pages and tool output as data, never as instructions
- A person approves consequential actions; show where
- No real personal data in the repository; use safe test data

### Production principles: recommended, not graded one by one

These are good-practice habits to ask your coding agents ("clankers") for. You do not need to present or evidence each one. Expect your agent to deliver them, and check the result

| Principle | What to expect from your agent |
|---|---|
| 1. Single source of truth | One home for settings and agent rules |
| 2. Small commits | Small, reviewable changes you can undo |
| 3. No secrets in code | Required; see Security above |
| 4. Separation of concerns | Small, clear modules so one change touches one place |
| 5. Explicit contracts | Each stage's input and output named, agent replies too |
| 6. Fail fast | Clear errors early instead of silent wrong output |
| 7. Environment discipline | One environment file with pinned versions |
| 8. Don't repeat yourself | Shared logic once the flow works |
| 9. Determinism and repeat tests | Rule steps exact; AI steps repeated in tests |
| 10. Traceability | Prompt, model, input and output logged for important runs |

### Validation against ground truth: required

Ground truth is a fixed set of realistic inputs whose correct outputs you know before you run the feature. It is what your feature is validated against. The golden reference does this with one reference quarter: 44 documents with known amounts, rerun after every parser change, 0 wrong amounts

- Build a reference set of safe, realistic inputs, each with its expected correct output, confirmed by a person or a trusted source, never by the AI you are testing
- Size it to your product: enough items to cover normal, edge and failure cases for each sub-feature
- Choose one clear score, such as exact matches, wrong values or correct decisions out of the total, and set the threshold before you run it
- Run the feature against the set, record the score with the commit it ran on, and keep the failures
- Rerun after every relevant change; a drop in score is a regression
- Repeat runs where an AI step varies, and report how many passed
- State what the set does not cover

Link the set and its scored runs from each sub-feature's `validation.md`

### Evaluation and failures

- Use safe, repeatable test data
- Cover normal, edge and failure cases; include a prompt-injection case where the product reads untrusted text
- Distinguish planned, unrun, passed and failed checks
- Record failures, corrections and reruns; do not manufacture an agent mistake
- Show regression evidence after relevant changes
- Repeat trials when outputs vary and report how many passed
- State coverage gaps and known failures honestly

### User testing and iteration

- Run two prototype-testing rounds, including one with at least three real people
- Record participant fit, sample size, task, method, threshold, observations and limitations
- Count classmates as target users only when they match the profile; otherwise call them pilot users
- Keep synthetic Persona work as rehearsal; synthetic users do not validate anything
- Trace evidence to a decision, specification change, implementation and retest
- Keep negative results visible

### Deployment

- The remote build runs the `final` commit
- `tech-stack.md` explains how to run it and how to undo a bad change
- Keep a same-flow backup for the presentation

Apply controls to your actual product. A deterministic product can meet the standard. Multiple agents, skills, hooks, MCP servers and plugin packaging are optional; use them only when they solve a real need

## 7. Rubric and stronger work

These weights are percentages of Group Presentation II and total 100 %

| Criterion | Weight | Ready | Revise | Rework |
|---|---|---|---|---|
| Venture continuity and traceability | 5 % | Current venture and strategy agree with linked evidence and decisions | A material link is stale or incomplete | Claims conflict or earlier contradictions are ignored |
| Spec-driven build | 8 % | Current constitution, linked scenarios and cases, reviewed briefs, test-first work, commits and Current behaviour | A material scenario, review or specification link is missing | Build has no usable specification or review trail |
| End-to-end feature | 7 % | One useful critical feature; each sub-feature works end to end on safe data, with safe failure behaviour | A sub-feature is incomplete or a needed step is simulated and disclosed | No useful working flow, or simulation presented as implementation |
| Remote deployment | 3 % | Remote build matches `final`; run and undo documented | Build unstable, mismatched or poorly documented | Local only or remote deployment absent |
| Validation against ground truth | 7 % | Reference set with known correct outputs; feature scored against it with a pre-set threshold, version-linked, rerun after changes; failures and fixes recorded | Set too small or unclear, threshold missing, or scores not rerun after changes | No ground truth, so nothing to validate against, or unsupported verification claims |
| User testing and iteration | 8 % | Two rounds, one with at least three real people; participant fit recorded; evidence-to-change-to-retest loop | A round, fit, threshold or retest is weak | No usable testing evidence, or synthetic output presented as customer validation |
| Security and safety | 4 % | No secrets in code or history, bounded permissions, untrusted input handled, human approval where it matters | A material control lacks evidence | Exposed secrets, unapproved personal data or an unsafe consequential action |
| Agent use and decision | 3 % | Deliberate lead-agent and subagent use, explained and verified; evidence justifies the next decision | Agent setup or next decision weakly explained | No rationale for agent use and no evidence-to-decision link |
| Live presentation and mastery | 55 % | Answer-first storyline, end-to-end demo, reasoning, ownership, evidence use, adaptation and honest limits across the team | Descriptive explanation, weak evidence navigation or uneven understanding | Members cannot explain material decisions or the working flow |

Judge submitted evidence under its relevant criterion and live understanding under mastery. A repeated deduction needs a distinct observable reason; do not deduct twice for the same missing artifact

Own your answers. If you can only relay what your AI told you, you are a meat proxy (https://meatproxy.me/): you add latency, not judgment

The existing grading rule remains: Ready earns up to 8.0; grades 9 and 10 go to teams that outperform the others

Examples of stronger work beyond baseline compliance:

- Measure improvement against a relevant baseline, with comparable conditions and a stated sample size
- Justify a simplification and retest its effect
- Trace a user finding through specification, implementation and evaluation
- Show robust performance on an appropriate additional case
- Demonstrate cross-topic understanding across the team
- State clear limitations and make a credible next investment decision

Comparing cloud, delegated or local engines is optional. Keep the feature, starting commit and tests the same, and report resource differences. Extra technology, paid access or better hardware earns no distinction by itself

## 8. More questions across the course

The professor samples understanding; the presentation need not cover the whole question bank

- What connects the Product Goal, current Sprint Goal and riskiest assumption?
- Which Persona claim remains a hypothesis, and how would you test it?
- Which experiment threshold was set before the result, and what decision followed?
- Which market finding changed your decision rather than merely describing the market?
- How do your strategic choices change cost and buyer value?
- Why does each sub-feature run end to end rather than being a technical layer?
- Show a reviewed plan, task-group brief, failing test, passing change and reviewed commit
- Which agent-stack components did you use or omit, and why?
- How would you undo a change, and where does Current behaviour show the accepted result?
- What do normal, edge and failure cases reveal about the same feature?
- What changed between your two testing rounds, and did the retest support the change?
- What can your participant sample establish, and what remains uncertain?
- What would make you iterate, pivot, stop or invest further, and who owns the next test?

## 9. Rehearsal

- Rehearse the opening and the end-to-end demo until they are reliable
- Rehearse being interrupted: answer the question, then return to the customer outcome
- Have each member practise questions outside their own area
- Practise jumping from a claim to its proof and back
- Rehearse the switch to the backup
- Reset safe data so repeated demonstrations stay reliable
- Test repository and deployment access without your own signed-in session
- Say what is observed, reported, assumed, simulated, unrun or unresolved

## 10. Golden-reference boundary

The golden reference demonstrates method, not a student volume or architecture benchmark

- The golden critical feature (Phase 1) is split into two sub-features, `gmail-quarter-download` and `quarter-expense-list`, and explicitly defers a third
- `review-assist` in the feature-splitting lesson is an optional teaching example, not a completed third golden sub-feature
- In the November download specification, S4 maps to V2: preserve a linked receipt as text and list its link for manual action without following it
- `specs/2026-11-02-gmail-quarter-download/validation.md` records V1 to V5 as unrun, with pending results and coverage gaps
- The historical 44-document regression belongs to the operational `gmail-expense-extractor/VALIDATION.md`; it is not a newly executed November feature result

## 11. Method references

Course objectives and assessment come from the professor's instructions and the final-project slides. These sources support the methods, without setting assessment rules:

- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), checked 9 November 2026
- Barbara Minto, The Pyramid Principle
- BCG storyline framework: Situation, Problem, Solution, Impact
- [Meat Proxy](https://meatproxy.me/)
