# Market evidence: TFGPT

**Status:** Draft for Group Project I. AI research agents did the desk research on 2026-10-11, and a second agent re-opened every source to check each claim. Sourced numbers cite a row in [market-sources.md](market-sources.md) (#n); bounds marked ASSUME are the author's. Behaviour evidence comes from the team's own tests and conversations and carries its status. The author chose the strongest alternative, the factors, the Fermi filters and the so-what; the value-curve scores, the tenth factor's scores and TFGPT's target line were proposed by AI from the evidence and ERRC.md, and await the team's review

Desk research shapes the hypothesis; real users test it. Market sources show what exists, not what IE students do

---

## 1. Fermi estimate: how many IE students could TFGPT serve each year?

| Step | Label | Base | Range | Running total (base) | Basis |
|---|---|---|---|---|---|
| IE bachelor graduates per year (each completes a final project) | KNOWN | 1,351 | 1,334 to 1,950 | 1,351 | Ministry SIIU 2024-25 (#146); IE's own count for the class of 2025 is 1,334 (#144). Upper bound ASSUME: 2,139 entrants in 2024 and over 2,500 in 2025 (#142, #149) at the 78% entry-to-graduation ratio seen for 2025 (#150) |
| Use AI at all | PROXY | 90% | fixed | 1,216 | Spanish bachelor students, 2026 (#38) |
| Use AI to produce academic work | PROXY | 46% | 37% to 46% | 559 | Spain, 2026: 37% of all students, 46% at private universities (#165). The private subgroup is small, about 15% of 800 respondents (#39) |
| AI is allowed in their final project | ASSUME | 80% | 50% to 100% | 447 | IE lets each syllabus set its AI rule (#7). Within BBA alone one final-project syllabus bans GenAI by default (#12) and another encourages it (#13); feedback is an allowed use by default (#76) |
| Do the check task in TFGPT instead of their own AI | OBSERVED in one session, used here as a PROXY | 60% | 30% to 80% (ASSUME) | 268 | Wizard-of-Oz: 6 of 10 classmates completed three given tasks in a simulated chat without opening their own AI, exactly the threshold (experiment-card.md). One 20-minute session with n=10, so sustained switching is a HYPOTHESIS and the range is wide |
| **Result** | DERIVED | | | **about 270 students a year** | Low about 65 (1,334 x 90% x 37% x 50% x 30%); high about 650 (1,950 x 90% x 46% x 100% x 80%) |

**Tightest filters:** using AI to produce academic work (46%), and switching (60%, the least certain input)

**Caveat:** IE is not representative of Spain. 83% of the class of 2025 was foreign (#145), against 7.2% of Spanish bachelor students (#157), so the Spanish survey proxies may not transfer; the direction of the bias is unknown

**Wider frame:** Spain had 215,365 bachelor graduates in 2024-25 (#146), so IE is about 0.6% of them. Private universities produced 21.1% of the 2023-24 graduates (#155) and hold 22.9% of 2024-25 enrolment (#156). Each new university means loading its own guidelines, so growth beyond IE has a real per-university cost

**Not estimated:** money, because willingness to pay is untested.
- **Free options exist:** free tiers of ChatGPT and Claude (#18, #24), and a Spain-wide free year of Google AI Plus for students (#27)
- **Payment figures are thin:** 30% of AI-using Harvard students pay for a premium plan (#44, #177), and 44% in a US survey (#45, weak, mixed respondents). None is from Spain or IE
- **The team's own evidence points both ways:** a team member reports that many technical students in his school pay for Claude, while interview-evidence 02 says most non-Computer Science students use free or the cheapest plans. The split by degree has not been checked (jtbd.md). Money paid for Claude is also spend on the incumbent alternative

---

## 2. Four-category alternatives map

| Category | Alternatives | What exists (market evidence) | What our target users do (behaviour evidence) | Compare on | Gap | So what |
|---|---|---|---|---|---|---|
| **Direct competitors** (same user, same job) | Grammarly AI Grader; Thesify; Mattie (RSM pilot); instructor- or publisher-configured checkers (FeedbackFruits, Paperpal Preflight) | Grammarly checks a draft against a rubric the student uploads and estimates a grade, free for one use a day and unlimited on Pro (#53, #189). Grammarly Authorship records the writing process and labels AI-assisted text (#55). Thesify gives thesis feedback on its own rubrics, EUR 14.95 per review (#49, #51). Mattie, a funded pilot at Erasmus RSM, gives thesis feedback and remembers decisions across drafts (#47, #48). Institution-specific checks were found only where the instructor or publisher configures them (#59, #67); students can upload a rubric themselves (#53, #75). Writing tools (Jenni, ThesisAI, Tesify) write the text for the student (#56, #60, #138) | UNKNOWN. No participant or interviewee mentioned any of these | Feature, price, trust, switching | None found in a search that checks a student's work against their own university's guidelines, keeps context between deliverables and stays feedback-only. Mattie shows universities may build this themselves | Differentiate on IE-programme guidelines, kept context and check-only. A university-built tool like Mattie means IE could be a buyer or a competitor |
| **Indirect substitutes** (same progress, different route) | General AI on the student's own account: ChatGPT, Claude, Gemini. IE-provided AI: ChatGPT Edu and IE's own platform (IE AI Engine at nebulaone.ie.edu) | IE announced ChatGPT Edu and AI training for all students in Feb 2025 (#1, #2, #3); its 2024-25 report lists ChatGPT licences for all students (#181), and in Oct 2025 it piloted ChatGPT Edu with 500 students (#4). IE AI Engine exists behind IE login (#5). Claude Free has projects and memory, Pro is about USD 20 a month (#24); ChatGPT Projects can hold class materials (#20); Spanish students can get a free year of Google AI Plus (#27). Of Spanish students who use AI, 89% use chat assistants (#166). Google added course-material notebooks for students in Aug 2026 (#28); OpenAI's equivalent ships through ChatGPT Edu (#23, #188) | OBSERVED (Wizard-of-Oz): 3 of 10 opened their own AI. Two used it alongside the chat (participant 4 kept ChatGPT open; participant 7 generated ideas in Claude and checked them in the chat), and one (participant 10) did all three tasks in Claude and only pasted his answers back (experiment-card.md). REPORTED by a team member about classmates in his technical school: they use ChatGPT and Claude on their own accounts and many pay for Claude; ChatGPT Edu was released but quietly disappeared in favour of IE AI Engine, which almost no one uses because its models are outdated and not trusted. That report conflicts with #4, #181 and #188 and is not verified beyond his account. REPORTED, second-hand, unnamed, count not recorded: students stay with the AI they know and worry that university tools run outdated models (interview-evidence.md 02; jtbd.md) | Outcome, effort, cost, habit | A student can set their own AI up for the check (#20, #75), but must load the guidelines and the draft; how well it checks against TFG guidelines is untested. One student's stated condition for switching implies she re-prompts Claude today (interview-evidence.md 03, a conditional intention, not reported behaviour) | The strongest alternative (section 3), which TFGPT lives alongside rather than replaces (section 7) |
| **Manual workarounds** (student assembles it) | Guidelines and rubrics on Blackboard / Campus Online; friends; Google; emailing the supervisor; IE Library final-project sessions | IE hosts final-project rubrics on Campus Online (#106). Format and citation rules differ by degree (#104). IE Library runs short sessions on tools for the final project (#107). Students help each other when the tutor is absent (#123) | OBSERVED (Wizard-of-Oz): 4 of 10 checked something with an official source or a person, namely Blackboard (participants 1, 5, 9), friends (1, 5), Google (3) and a message to the supervisor (3); participant 8 re-read her own proposal. REPORTED: a student could not find a guideline document and waited for her mentor (interview-evidence.md 04); a student checks workshop materials, then emails the mentor and waits a few days (ai-persona-03) | Time, error risk, effort, ownership | Guidelines are scattered and differ per programme. Some students double-checked fit, format or dates with an official source or a person; whether this reflects distrust of a tool is a HYPOTHESIS | Cite the guideline section behind every answer, so students can verify it, as some already do |
| **Doing nothing** (delay or accept the pain) | Wait for the supervisor's reply or the next meeting; accept rework | At IE, missing the delivery deadline gives a zero (#92); retakes are capped at 8/10 in BBA and IR (#95, #103); the supervisor can refuse permission to present in the first call (#16, #82). Spanish TFG graduates report uneven tutor replies, with some taking a week (#117), being told in the last week that the work was not acceptable (#119), and delays after feeling abandoned (#121) | REPORTED, second-hand: found out at the meeting and redid the work (interview-evidence.md 01). REPORTED: waited for the mentor (04). REPORTED, relayed by one team member, one advisor's students, count not recorded: about two weeks for a first reply (05). Contrasts: a researcher-supervisor with 2 TFGs reports no delays (06, not a neutral source); mentor emails take a few days (ai-persona-03) | Urgency, pain cost, risk tolerance | The cost of late discovery is explicit at IE, but how often it happens is unknown, and reply time depends on the supervisor | The trigger is the deliverable and the permission gate: time the checks before each deliverable and before the supervisor decides |

---

## 3. Strongest current alternative

**The general AI the student already has on their own account (ChatGPT, or a paid Claude), plus their own judgement, with the supervisor meeting as the only authoritative check.** Chosen by the author on 2026-10-11

- **Why the author chose it:**
  - It is free or already paid for, it is allowed for feedback by IE's AI guidelines (#76), it runs top models, and it is a habit
  - Per the team member, IE-provided AI does not displace it: ChatGPT Edu disappeared and almost no one uses IE AI Engine (unverified, see section 2)
- **Where it is weak:**
  - It only checks against the student's guidelines if the student loads them and the draft
  - It knows nothing about the student's programme out of the box
  - It has no standing with the supervisor or IE. In the Wizard-of-Oz test some participants re-checked the simulated chat's answers with Blackboard, a friend or the supervisor (1, 3, 5, 9), which suggests AI-chat answers get verified
- **Evidence:** in the Wizard-of-Oz test, 3 of 10 used their own AI and 4 of 10 checked with an official source or a person; the habit is supported by the team member's report and interview-evidence 02 (second-hand); 89% of Spanish students who use AI use chat assistants (#166). The manual route is a close second

---

## 4. Factors for the value curve (chosen by the author) and current scores

| Factor | What the student receives or gives up | Where it comes from |
|---|---|---|
| Knows my programme's TFG guidelines without being told | Correct answers without loading documents | Guidelines differ per programme (#104) |
| Keeps my TFG context between sessions | No re-briefing | assumptions.md Area 2; interview-evidence.md 03 (implied by a conditional intention) |
| Checks scope and method fit before the meeting | Drift caught early | jtbd.md; FHNW bachelor-thesis study (#125); Wizard-of-Oz participant 6 |
| Starts the check without being asked (added 2026-10-12 by the ERRC Create move) | Drift caught without having to remember to ask | ERRC.md (Create); ai-persona-03 (HYPOTHESIS) |
| Model quality | Answers as good as top general AI | jtbd.md Anxiety; the team member's report on IE AI Engine |
| Speed of an answer | No waiting | interview-evidence.md 05; #117 |
| Authority | Confidence the supervisor will agree | Wizard-of-Oz verification episodes; supervisor permission gate (#16, #82) |
| Fits IE's AI rules | Feedback, not ghostwriting; a disclosure record | IE guidelines (#8, #78); writing tools (#60, #138) |
| Cost to the student | Money | #18, #24, #27, #51 |
| Effort to start | Setup and loading the guidelines | #20, #75 |

### Value curve: current alternatives and TFGPT's target

![Value curve with TFGPT's target line](value-curve.svg)

**Status:** scores proposed by AI from the cited evidence on 2026-10-11 and checked against their sources by a second agent; they await the team's review. They are judgements on a 0 to 5 scale, not measurements. Conventions: each cell scores what the alternative offers when the student uses it as intended; for cost and effort a higher score means more cost or more effort, as price is plotted on a strategy canvas; the two alternatives without AI score 5 on "Fits IE's AI rules" because those rules do not apply to them. The dashed line is TFGPT's target from ERRC.md, a HYPOTHESIS proposed by AI and accepted by the author on 2026-10-12 (table below)

| Factor | General AI, own account (ChatGPT / Claude) | Supervisor | Blackboard plus friends | Thesis feedback tools (Thesify / Grammarly) |
|---|---|---|---|---|
| Knows my programme's TFG guidelines without being told | 1: only if the student uploads them (#20, #75); the rubrics are hosted on Campus Online (#106), access path not checked | 5: judges the work against the programme's minimum standards and can refuse permission to present (#16, #82); the authority participant 3 chose for her format question (experiment-card.md); some rules are set by each supervisor (#13) | 3: the guidelines are on Campus Online (#106), and Wizard-of-Oz participants 1, 5 and 9 got format or date answers from Blackboard; classmates gave participant 3 conflicting format advice | 1: their own rubrics or one the student uploads, nothing IE-specific (#49, #53) |
| Keeps my TFG context between sessions | 3: Claude projects and memory, ChatGPT Projects, if the student sets them up (#20, #24); Free-tier limits apply (#18); one student's condition for switching implies she re-prompts and re-adds context in Claude today (interview-evidence 03, a conditional intention) | 3: ASSUME he follows the project across meetings, not evidenced; with about 10 TFGs he has a few minutes per student and gives short replies (interview-evidence 05); the 2-TFG contrast case reports long conversations (06, not a neutral source) | 1: ASSUME: documents are static and friends know only what they are told | 1: one upload per review (#49, #51); Mattie keeps context across drafts but only at RSM (#47) |
| Checks scope and method fit before the meeting | 3: possible with the rubric loaded (#75); participant 10 did the fit check in Claude and participants 4 and 7 used their own AI alongside the chat (experiment-card.md); how well it checks is untested (section 8) | 3: the authoritative scope check, but only when he meets or replies: students found out at the meeting (interview-evidence 01), replies were slow (05); the calendar is his to set (#96) | 2: a friend checked participant 1's fit verdict; participant 3 searched Google for hers (experiment-card.md); peers help when the tutor is absent (#123); documents check nothing | 3: rubric-based feedback on an uploaded draft (#49, #53), generic and with untested quality, the same mechanism as general AI with a rubric (#75) |
| Starts the check without being asked | 1: scheduled tasks exist in ChatGPT Plus (#18); none found used for a guideline check, though this was not searched for specifically; otherwise it waits to be asked | 0: checks only when the student brings work to a meeting or an email (interview-evidence 01, 05) | 0: documents check nothing; friends answer only when asked (Wizard-of-Oz participants 1, 5) | 0: feedback only on a draft the student uploads (#49, #53) |
| Model quality (for people: quality of the answer) | 5: the reference point for this factor; students stay with the AI they know as the best they know (interview-evidence 02, second-hand); the team member describes IE-provided AI as outdated (unverified) | 4: varies by supervisor, so a midpoint: brief comments and almost no guidance with about 10 students (05, relayed by students); long conversations and a lot of help in the 2-TFG case (06, not neutral); better-guided work with a good relationship (01) | 2: one episode of conflicting advice from classmates (participant 3); no conflict was recorded for participants 1, 5 and 9, who used Blackboard or a friend | 3: model-based, with no independent accuracy data found; a grade estimate is not a grade (#189) |
| Speed of an answer | 5: no wait by nature (assumed); participants 10, 4 and 7 opened their own AI at minutes 1, 2 and 4 (experiment-card.md) | 2: about two weeks for a first reply and more than a week for drafts (interview-evidence 05); a few days (ai-persona-03); some reply the same day (#117) | 3: Blackboard is immediate once found (participants 1, 5, 9); friends were consulted mid-session (participant 1 at minute 6, participant 5 at minute 11), with reply times not recorded | 4: automated, so presumably fast; turnaround not stated (#53) |
| Authority | 1: no standing with the supervisor or IE: the supervisor decides (#16, #82) and IE makes the student own and disclose AI output (#8, #78). The Wizard-of-Oz re-checks (participants 1, 3, 5, 9) were of the simulated chat, not of their own AI | 5: decides permission to present (#16, #82) | 3: official documents carry weight, friends less; participants 1 and 9 confirmed on Blackboard, participant 5 got her answer there and then checked with a friend | 1: the Grammarly estimate is explicitly not a grade (#189); nothing found gives Thesify standing |
| Fits IE's AI rules | 3: allowed for feedback (#76); disclosure and usage records are required (#8, #78), and how a student keeps them with ChatGPT or Claude is not established; it can also write the text | 5: no AI involved | 5: no AI involved | 3: feedback-only positioning, though Thesify also markets a Coauthor that drafts (#50); Grammarly Authorship records the writing process but shows no link to IE's rules (#55); writing tools are left out of this line (#60, #138) |
| Cost to the student (higher = more) | 2: a range from 0 on a free plan to about 2 on Claude Pro at about USD 20 a month (#18, #24); many technical students pay (team member's report), most others use free or the cheapest plans (interview-evidence 02, second-hand); a free year of Google AI Plus (#27) | 0: part of tuition | 0: free | 2: Grammarly free for one use a day (#189); Thesify EUR 14.95 per review (#51) |
| Effort to start (higher = more) | 3: load the guidelines and the draft and prompt for the check (#20, #75), though using it is already a habit | 2: an email and finding the right moment; the student has to make contact (#96) | 3: finding the right document: one interviewee gave up (interview-evidence 04) and one persona episode found it only through a friend (ai-persona-03); how common this is is untested | 3: an upload, and for Thesify a paid review, each time (#49, #51, #53) |

### TFGPT target line (from ERRC.md; HYPOTHESIS, proposed by AI and accepted by the author on 2026-10-12)

| Factor | TFGPT target | Basis |
|---|---|---|
| Knows my programme's TFG guidelines without being told | 5 | Raise: preloaded guidelines, rubric and dates |
| Keeps my TFG context between sessions | 5 | Raise: keeps the student's topic and work, so no re-briefing |
| Checks scope and method fit before the meeting | 5 | Raise and Create: checks the work against the programme's requirements with the guideline section cited; the hypothesis is wrong if TFGPT misses more than 40% of what a supervisor would otherwise flag as not ideal |
| Starts the check without being asked | 5 | Create |
| Model quality | 5 | Assumed: it runs on a top general model (not chosen yet); the hypothesis is wrong if a general LLM gives the same flags for the same effort |
| Speed of an answer | 5 | Assumed: automated |
| Authority | 2 | Cites the guideline section behind every flag (HYPOTHESIS); the supervisor still decides |
| Fits IE's AI rules | 4 | Eliminate and Reduce: flags and suggested fixes only, no drafting and no grade; disclosure still applies (#8, #78) |
| Cost to the student (higher = more) | 0 | Only if IE pays: the hypothesis is wrong if IE doesn't commit to the full maintenance and adoption; willingness to pay is untested |
| Effort to start (higher = more) | 1 | Raise: no uploading and no re-briefing |

**Reading the curve**
- **No alternative scores high on programme knowledge, authority and speed together.** The supervisor scores 5, 5 and 2. The student's own AI is fast and strong but knows the programme only if the student loads it, and has no standing. Blackboard plus friends sits at 3 on all three, held back by findability
- **Every current line stays at 3 or below on "keeps my context" and "checks scope before the meeting", and at 1 or below on "starts the check without being asked".** That is the dip TFGPT aims at: instead of the student's own AI for the check, alongside it for everything else
- **Authority stays with the supervisor.** This fits "live alongside" and "checks, not grades"; TFGPT may borrow some authority by citing the guideline section behind every answer (HYPOTHESIS)
- **TFGPT's target (dashed):** it diverges from the student's own AI on programme knowledge, context, the scope check, starting the check and effort, matches it on model quality and speed, scores a little higher on authority (2 against 1, by citing sources), on fitting IE's AI rules (4 against 3) and on cost (0 against 2, only if IE pays), and leaves the authoritative check with the supervisor. Grading and drafting, which ERRC eliminates and reduces, are not factors on this curve

---

## 5. Claim, evidence, source, strength, contradiction, implication

| Claim | Evidence | Source | Strength | Contradiction or gap | Implication for TFGPT |
|---|---|---|---|---|---|
| Almost every student already uses AI | 90% of Spanish bachelor students; 95% in the UK | #38, #32 | Strong | TFG-specific use is not measured, and IE is not representative of Spain (#157) | Compete on the job, not on "AI or not" |
| Students rely on their own general AI rather than IE-provided AI | A team member reports ChatGPT Edu disappeared in favour of IE AI Engine, which almost no one uses, and that technical students pay for Claude | Team member's report | REPORTED, one school | IE's own sources say licences for all students (#181) and a 500-student pilot in Oct 2025 (#4) | The strongest alternative is the student's own AI; the Edu status needs checking |
| Some students do not use or trust IE AI Engine | The platform exists behind IE login | #5; team member's report | Medium (exists); REPORTED, one school (use) | Only one school's view | A "university tool" label can carry distrust: TFGPT needs top models and has to earn trust, which complicates IE branding (assumptions.md Area 3) |
| IE requires AI disclosure, including prompts on request, and AI rules differ per syllabus | Official IE guidelines, July 2025; within BBA one syllabus bans GenAI by default, another encourages it | #7, #8, #12, #13, #78 | Strong | The final-project regulation does not mention AI; current per-programme rules are unknown | An IE-rule-specific AI-use record could differentiate (HYPOTHESIS: Grammarly Authorship already records writing process, #55); TFGPT must respect per-programme AI rules |
| No product found that checks a student's work against their own university's guidelines with kept context | The pieces exist separately | #47 to #67 | Medium (none found in a search) | Mattie shows universities building it; Google added course-material notebooks for students (#28) | The window is open but closing: IE-specific knowledge and speed matter |
| Meeting cadence differs by programme | BBA: 4 mandatory sessions in one syllabus, supervisor-set calendar in another; BIE: 4 or 5 mandatory sessions; IR: about monthly; Communication: about ten sessions; the regulation sets no fixed cadence | #14, #96, #15, #97, #105, #89 | Medium (syllabi from 2022 to 2025) | Other programmes differ from the "two-month gap" in opportunity.md, which rests on one Computer Science graduate; no Computer Science or SciTech cadence was found | Qualify the two-month gap by programme and check the SciTech cadence |
| In one study, guidance on goals and methods was associated with thesis grade, while students' ratings of availability and meetings were not | One Swiss business school's survey, n=189, association only | #125, #126 | Medium; HYPOTHESIS for IE | The team's own evidence shows students waiting for replies (interview-evidence.md 04, 05; ai-persona-03) | Make scope and method checks central, and keep answer speed as a live competing factor until cadence and waiting are tested |
| Late discovery is costly at IE | Zero for a missed deadline, retakes capped at 8/10, supervisor permission gate | #16, #82, #92, #95, #103 | Strong | How often it happens is unknown | The pain has a hard price; time checks before each deliverable |
| AI used to evaluate learning outcomes, including steering learning, is high-risk under the EU AI Act | Annex III 3(b), obligations from 2 Dec 2027 | #194, #195, #196 | Medium (dates via secondary sources) | A tool that checks work and says what does not fit could arguably steer learning | The team intends checks, not grades; whether that stays outside Annex III 3(b) is UNKNOWN and needs legal advice |
| Students' willingness to pay is unknown | Harvard: 30% of AI users pay; a US survey: 44% (weak) | #44, #177, #45 | Weak | Free tiers and offers exist (#18, #24, #27); none of the figures is from Spain or IE | A student-paid model at IE alone looks weak; the buyer may be IE or other universities (HYPOTHESIS) |

---

## 6. Opportunity stress test

- **Entry:** barriers are low. A university teacher built a scope-feedback agent quickly (#74), inference costs have fallen sharply (#198), and Google added course-material notebooks for students (#28). The real barrier is IE-specific guideline knowledge and trust, not technology
- **Substitution:** a general AI with an uploaded rubric may be good enough for many (#20, #75). In the Wizard-of-Oz test, participant 10 did all three tasks in Claude, and participants 4 and 7 used their own AI alongside the chat
- **Dependencies:** access to current per-programme guidelines (behind Campus Online, #106); per-syllabus AI rules (#7, #12, #13); model APIs; the EU AI Act line (#194)
- **Major shifts:** general AI gaining course context (#28; #23 through ChatGPT Edu); some institutions moving from AI detection to process transparency (#190, #191, #192, weak); students unsure of AI rules (#174)

**Top 3 findings most likely to change the decision**
1. The strongest alternative is the student's own general AI, free or already paid for, allowed by IE for feedback, and gaining course context, so TFGPT lives alongside it and has to win on IE-programme specificity and scope checks (section 7 later scopes this: instead of it for the check, alongside it for everything else)
2. Disclosure is mandatory at IE, so an IE-rule-specific AI-use record could set TFGPT apart (HYPOTHESIS). It carries a tension: a log the advisor can see may push real AI work back to students' own AI (ai-persona-04.md; opportunity.md)
3. Cadence differs by programme, and in one study guidance on goals and methods mattered more than students' rating of availability, so early scope and method checks per programme look central (HYPOTHESIS; one participant spent most of her session on a scope question)

---

## 7. So what: what this changes in TFGPT

**Decision (the author, 2026-10-11): live alongside general AI instead of trying to replace it.** The author's premise is that students have ChatGPT and Claude, will keep access to them and will keep using them, so that alternative is irreplaceable; it is not strictly a competitor, because students can also use it for our purpose. In the author's view TFGPT can still thrive because it tackles one specific part of the problem: checking the work against the student's programme guidelines and scope between meetings

- **Evidence behind it:**
  - **OBSERVED, Wizard-of-Oz:**
    - participant 7 generated ideas in Claude and brought them to the chat to check them
    - participant 4 kept ChatGPT open alongside
    - participant 10 did everything in Claude: the negative case, where the general AI did the whole job
    - 6 of 10 did the check tasks without their own AI (experiment-card.md)
  - **REPORTED by a team member:** classmates use their own ChatGPT and Claude accounts, while almost no one uses IE-provided AI
  - **SUPPORTED:** 89% of Spanish students who use AI use chat assistants (#166), and IE's guidelines allow AI for feedback (#76)
- **How it fits the test result:** the Wizard-of-Oz threshold was met, so the committed decision is CONTINUE, building a working slice. Living alongside general AI is a positioning choice inside that decision, not the card's missed-threshold "complement" branch
- **What changes:** the promise becomes "the check, already loaded with the student's programme guidelines and kept between sessions, which a student's own AI only does if the student sets it up", not "a better AI". How well general AI does that check is untested (section 8)
- **What must agree with it (reconciled 2026-10-12):** instead of their AI of choice for the check, alongside it for everything else. ERRC.md states it as falsifier 1, and assumptions.md records the scope. The earlier wording follows:
  - The riskiest assumption (assumptions.md), the Sprint Goal (goals.md) and the experiment card say "instead of their AI of choice"
  - The press release's evidence box now says "instead of their own AI (for the check; they keep their own AI for everything else)", and its subheadline "instead of re-explaining them to a general AI each time", which already reads as instead for the check
  - The Wizard-of-Oz result supports "instead" for the check tasks only. assumptions.md and goals.md now note the scope next to their unchanged sentences

**What ERRC did with the further implications (ERRC.md, 2026-10-11, revised 2026-10-12):**
1. An IE-rule-specific AI-use record (#8, #78): not taken into the grid; kept as an open option
2. Scope and method checks with the guideline section cited: adopted (Eliminate: flags with the source behind each one; Raise and Create)
3. Checks, not grades: adopted (Eliminate); the EU AI Act position still needs legal advice
4. Qualifying the "two-month gap" by programme: done in opportunity.md (v02), press-release.md and the jtbd.md validation gaps
5. IE or other universities as the buyer: partly reflected in the falsifiable hypothesis, which is wrong if IE doesn't commit to the full maintenance and adoption of the tool; who pays is still untested

## 8. Gaps to take to real users

- Give a few students a check task in their own AI with the guidelines uploaded and compare it with TFGPT: does their own AI do the check well enough?
- Whether ChatGPT Edu is really gone at IE (IE's own sources say it was rolled out), and whether anyone uses IE AI Engine
- The meeting cadence in SciTech and Computer Science programmes
- Whether AI is allowed in each student's final-project syllabus
- Willingness to pay, and who would pay
- Whether students check their work against the guidelines by hand (checklists, rubric self-checks)

## 9. Inputs for the ERRC run (done: see ERRC.md)

The ERRC helper (downloads/ai-prompt-ERRC.md) starts with three market-baseline questions; this file answers them:

1. **Alternatives in the four categories:** section 2
2. **Strongest current alternative:** section 3, the student's own general AI plus their own judgement, with the supervisor as the only authoritative check
3. **Factors and trade-offs:** section 4, with the current value curve, the tenth factor and TFGPT's target line proposed for the team to review

Carry into ERRC:
- **The decision:** live alongside general AI (section 7)
- **Candidate moves, not decisions:** the five implications listed under section 7
- **Tensions to keep visible:**
  - "instead of their AI" against "alongside" (reconciled on 2026-10-12: instead for the check, alongside for everything else)
  - an AI log the advisor can see, against students' concealment (ai-persona-04)
  - the EU AI Act position (legal advice needed)
  - whether ChatGPT Edu is still live at IE
  - meeting cadence by programme

The helper also reads opportunity.md, jtbd.md, goals.md and assumptions.md, the personas (ai-persona-01 to 04) and the Wizard-of-Oz results in experiment-card.md. It writes evidence-log/ERRC.md and a proposed evidence-log/opportunity-v02.md (accepted by the team as opportunity.md on 2026-10-12)
