# Persona: The Few-Minutes Advisor

**Status:** Selected stakeholder Persona (Stakeholder persona: TFG advisor). Grounded in two real advisors (interview-evidence.md entries 05 and 06): its behaviour claims are REPORTED, and its decision claims are not yet tested with real users

**Source draft:** drafts/persona-hypothesis-06.md (content unchanged; see selection.md)

**Persona type:** Stakeholder persona: the IE TFG advisor (also called supervisor or mentor in this repo), not the student target user. This is a deliberate adaptation of the Persona Builder, decided by the author: the Job to Be Done below is the students' job and the context the advisor works inside, and the advisor's own desired progress and forces sit in the decision-relevant profile

## Shared Job to Be Done

When final-year IE students work on their TFG through two-month gaps between deliverable meetings without knowing whether they're on track, finding out at a meeting that the last two months of work were faulty prompts them to seek a way to go into each meeting already knowing their work meets what's required, so they can move on to the next phase

## Behavioural archetype

A full-time professor supervising about ten TFGs, whose students report slow, brief email replies and little guidance, and who says he would like to help more but his schedule doesn't allow it

## Decision-relevant profile

- **Relevant context:** Full-time professor supervising about 10 TFGs, with maybe a few minutes per student and no time for long conversations or one-to-one meetings
- **Most relevant current behaviour:** As some of his students report it, the first reply to their first email took almost two weeks. When they email him a draft or a change, the answer takes more than a week, sometimes longer, and comes back as a short email or comment rather than detailed guidance. After about a month the cycle is the same, with one short meeting so far and almost no guidance
- **Consequence for his students (the author's account):** They wait, stuck, and can't yet tell whether their work is on track. Whether they are also drifting is UNKNOWN
- **Current approach or alternative:** Email exchanges with short written comments; one short meeting so far
- **Decision-relevant constraints:** Time, by his own account: he has limited time and would like to help more, but his schedule doesn't allow it. His load is about 10 TFGs as a full-time professor. Whether anything besides time plays a part is UNKNOWN
- **Advisor's own desired progress (stated, not behaviour):** Help his students more, and be able to check how they are doing without having to interact with them. Seeing their AI use is the author's idea, not his stated wish (HYPOTHESIS)
- **Forces on the advisor:** Push: limited time for the number of students he has (REPORTED, his own account). Pull: checking how his students are doing without meetings (REPORTED, stated opinion). Habit: guiding by short emails and comments (REPORTED by his students over about a month; whether it is habit or only time is UNKNOWN). Anxiety: UNKNOWN
- **Product or research decision affected:** Cover the advisor in the tool: add a supervisor view where the advisor can see, in a different view and at the same time, what the student is doing, and check the platform's AI usage logs, tested with advisors and with students before it is built. prototype-v0 left a supervisor view out of scope on purpose, because it tested substitution only. This adds it to the product scope and revisits the S03 choice of scope drift over supervisor visibility as the front door
- **Tension kept visible:** The author expects the IE requirement to submit an AI declaration and log to limit concealment, because students will have to disclose their AI use anyway. The concealment insight (opportunity.md, a team hypothesis) points the other way: if students care most about making work look not-AI, an AI log their advisor can see may push their real AI work back to their own AI, which would hurt the riskiest assumption. How the required log is produced and checked is UNKNOWN

## Evidence boundary

| Claim | Evidence status | Basis |
|---|---|---|
| Has limited time and would like to help his students more, but his schedule doesn't allow it | REPORTED, his own words | The advisor told a team member (interview-evidence.md entry 05) |
| Supervises about 10 TFGs as a full-time professor, with maybe a few minutes per student and no time for long conversations or one-to-one meetings | REPORTED | Told to a team member by the advisor and some of his students, sources not separated (entry 05) |
| Would like to check how his students are doing without having to interact with them | REPORTED, stated opinion, not behaviour | The team member's account, confirmed by him as the advisor's stated opinion (entry 05) |
| Would want to see his students' AI use | HYPOTHESIS | The author's idea, not something the advisor is recorded as saying |
| Almost two weeks from his students' first email to his first reply | REPORTED, by some of his students | Entry 05 |
| Replies to drafts or changes take more than a week, sometimes longer, and come back as a short email or comment; after about a month the cycle is the same, with one short meeting so far and almost no guidance | REPORTED, by some of his students | Entry 05 |
| His students wait, stuck, and can't yet tell whether their work is on track | REPORTED, the author's account | The team member's summary of his students' situation; their own words are not recorded (entry 05) |
| The cause of that uncertainty is that they have no experience writing a paper | HYPOTHESIS | The author's interpretation |
| His students are also drifting off scope | UNKNOWN | Too early to see |
| Another student reports that mentor emails take a few days | REPORTED, first-hand | ai-persona-03 (a teammate's own experience) |
| A student who couldn't find a TFG document stopped searching and waited to ask her mentor at the next meeting | REPORTED | interview-evidence.md entry 04; students fall back on the advisor as the check |
| How much guidance students get depends on the advisor's available time, not on a missing tool | HYPOTHESIS | The author's interpretation across two advisors (entries 05 and 06). Participant 01's entry credits a good relationship with his supervisor, not capacity, so it may be a competing explanation (entry 01) |
| Contrast case: a researcher-supervisor with 2 TFGs and very little teaching | REPORTED | A team member's account; per the team member, the advisor said the same when the team reached out (entry 06) |
| Contrast case: he gives long conversations and a lot of help, and communication has been flawless so far | OBSERVED, first-hand, not a neutral source | A team member who works with him directly (entry 06) |
| IE requires students to disclose their AI use (the tool, how it was used, and the prompts on request) and keep usage records | SUPPORTED | IE's Student Guidelines for Appropriate Use of AI, July 2025 (market-sources.md #8, #78). The author also reports a declaration of when and where AI was used, plus a log, in the guidelines on Blackboard |
| A supervisor view would save this advisor time | HYPOTHESIS | The author's proposal |
| An AI log the advisor can see would remove any worry about concealment | HYPOTHESIS | The author's reasoning; there is no recorded statement from the advisor about concealment |
| Students would still do their TFG work in the tool if their advisor can see an AI log | UNKNOWN | Conflicts with the concealment insight (opportunity.md) and the riskiest assumption (assumptions.md) |

## Validation gaps

- **Most important:** whether a supervisor view changes the advisor's behaviour at all. If time, not the lack of a tool, is the bottleneck, students may still get little guidance and still drift off topic
- Whether students keep doing their TFG work in the tool once their advisor can see an AI log, and how the AI log IE already requires is produced and checked
- All evidence on this advisor is relayed by one team member, who also proposed the supervisor view, and how many of his students were spoken to is not recorded. Ask the advisor and a few of his students directly, in neutral wording, what he would want to see and how often
- Whether the pattern goes beyond one advisor: two advisor inputs so far (interview-evidence.md entries 05 and 06), one matching this persona and one its opposite. How many advisors carry about 10 TFGs as full-time professors, and how many of their students reach a meeting off scope
- Whether this advisor's students are drifting or only stalled, since the Job to Be Done assumes drift
- Whether each programme's final-project syllabus adds its own AI rule: one BBA syllabus bans AI by default (market-sources.md #12)
