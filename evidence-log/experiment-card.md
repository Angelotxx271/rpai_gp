# Experiment Card

## Hypothesis
Final-year IE students, about to do a real TFG task with their own AI available, will do that task with the copilot instead of their own AI.

## Method
Wizard of Oz. Give final-year IE students a simple chat loaded with their topic and the IE TFG guidelines, ask them to check whether their project idea fits their topic and to ask about structure, format and dates, with the answers produced behind the curtain, and observe whether they do that work in the chat instead of switching to their own AI.

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
