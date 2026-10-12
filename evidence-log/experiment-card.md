# Experiment Card

## Hypothesis
Final-year IE students doing their TFG will do the task with the handed copilot instead of their AI of choice, in a 20-minute session on their TFG work.

## Method
Wizard of Oz. In a 20-minute session, give final-year IE students a simple chat loaded with their topic and the IE TFG guidelines, ask them to check whether their project idea fits their topic and to ask about structure, format and dates, with the answers produced behind the curtain, and observe whether they do that work in the chat instead of switching to their own AI.

## Metric
Students who complete the given TFG task in the copilot chat without opening their own AI, as a count out of the students tested.

## Threshold
The test clears the threshold if students completing the task in the copilot chat without opening their own AI is >= 6 out of 10 final-year students tested. Committed before the test.

## Evidence strength
MEDIUM, because the testers are 10 real final-year IE classmates doing their TFG, and the method observes a real TFG task in a simulated tool over one session, with some students not yet started so the task may not be their own work yet.

## Decision rule
If the threshold is met: CONTINUE by building a working slice of the chat with the IE guidelines loaded.
If the threshold is missed: CHANGE by reframing the copilot as a complement students use alongside their own AI, and rerun the test against that.
No ambiguous branch: the metric is a count out of 10.

## Results
| # | Degree | Started? | Tasks done in copilot (1 / 2 / 3) | Opened own AI? (y/n, minute) | Turns | Switched for... | Quote / note |
|---|---|---|---|---|---|---|---|
| 1 | BCSAI | Yes | 1 / 2 / 3 | n | 6 | Friend (min 6, T1); Blackboard (min 9, T2) | Accepted the dates as given; checked the fit verdict with a peer and the format against the official source. Trust seems to depend on the stakes of the answer, not on the tool |
| 2 | BBA | No (broad topic from list, narrow topic not chosen yet; proposal not due yet for her degree) | 1 / 2 / 3 | n | 3 | No exits | Short session. T1 asked what kind of topics could fit her broad area (ideas, not a fit check). T2 asked about the proposal's format, not the thesis sections. T3 asked when the proposal is due |
| 3 | BCSAI | Yes | 1 / 2 / — | n | 4 | Google (T1); message to her supervisor (T2) | Confirmed the fit of her idea on Google, and asked her supervisor whether the proposal goes in LaTeX or Word, because classmates had told her different things. Skipped T3: "already had a good notion of the dates". The copilot didn't settle either question for her, and peer noise on format sent her to the one authority she trusts |
| 4 | BDBA | Yes | 1 / 2 / 3 | y, min 2 | ~5 | ChatGPT open on a second screen from min 2, used alongside the copilot for the rest of the session | Opened ChatGPT right after his first question and kept both tools side by side, using ChatGPT to work out his answers to the copilot's clarifying questions on T2 and T3. He didn't leave the copilot; he paired it with his own AI. The first real case of "alongside, not instead" |
| 5 | BDBA | Yes |1 / 2 / 3 | n | 8 | T2 Blackboard, get answer (min 9); T2–T3 friend, verify (min 11); |Went to official sources and a friend before her own AI, wrote to friend: "I'm worried about the AI policy." Policy fear seems to shape *how* she will use AI, not *whether* |
| 6 | BAM | Yes | 1 / 2 / 3 | n | 8+ | none | T2 and T3: she already knew the dates and format. Spent ~8 minutes and 8+ messages on one question: whether her topic is too mathematical and not applied enough, and how to balance both in her thesis. The copilot became a sounding board for scope, the exact drift question the product is about |
| 7 | BCSAI | No | 1 / 2 / 3 | y, min 4| 9–10 | Claude (min 4, T1, get ideas) |	Worried the proposal is due soon and not well informed. Generated computer vision topic ideas in Claude, then brought them back to the copilot to validate (7 of his messages). For T2 and T3 he simply asked it to "tell me everything". Claude generated, the copilot checked: a clean split between the two tools| 
| 8 | BCSAI | Yes (proposal already written) | 1 / 2 / 3 | 	n | 1 | Her own proposal doc (T1, to re-read her draft)	| Asked: whether her topic is too simple. Opened her own written proposal to check it against that, then stopped: "she had everything done" so T2 and T3 were quick. With the proposal finished, the copilot's only value was a single reassurance check
| 9 | BCSAI | Yes (proposal started, written in LaTeX) | 1 / 2 / 3 | n | [4+] | Blackboard (T3, verify dates) | Used the copilot to understand his field first ("what does NLP entail?"), then to check whether his topic made sense based on that answer. T2 was about submission: LaTeX link or PDF?. Took the dates from the copilot, then reconfirmed them on Blackboard |
| 10 | BBA | No | — / — / — | y, min 1 | 1 | Claude (all tasks, from the start) | Read the copilot's opening message, then did all three tasks in his own AI using that message as the prompt. Came back only to paste his finished answers in. The copilot was a briefing and a drop box; the work happened in his own AI |
## Tally
**Real participants tested** from BCSAI, BBA, BAM and BDBA


**Completed all three tasks in the copilot without opening their own AI:** 6 / 10 


**Threshold:** ≥ 6 / 10 → met


**Decision (committed before the test):** CONTINUE. Build a working slice of the chat with the IE guidelines loaded.