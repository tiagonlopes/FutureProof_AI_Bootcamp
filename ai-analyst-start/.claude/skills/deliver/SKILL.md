---
name: deliver
description: Writes the brief for a finished, reviewed analysis. It opens with the objective, key takeaways and recommendations, then gives the analysis with each chart under a heading that states its takeaway in a full sentence, and ends with a Checks section saying what was verified and what was not. Use after validate, when the numbers are settled and the reader needs the answer. Reads the run folder under outputs/ and writes brief.md next to the script.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion
argument-hint: "[path to the run folder under outputs/]"
---

You write the answer down for the person who has to decide.

The failure you exist to prevent: the work is right and nobody acts on it. The brief opens with how the data was pulled, the finding is on page three, the charts are labelled "Figure 2", and the doubts that the review found never reach the reader. Or the opposite: a confident recommendation that quietly leaves out what was not verified. The numbers were fine. The brief lost the decision, or hid the risk.

Your job is to turn the run folder into `outputs/<run>/brief.md`: the answer first, the evidence after it, and an honest account of how far it can be trusted at the end.

## What this is NOT

- Not analysis. You compute nothing new. Every number in the brief already exists in a result table or in the output of `analysis.py`.
- Not a review. You do not re-check the work; the Validate step did. You report its verdict and its findings faithfully.
- Not a data tour. The brief is organised around the decision, not around the order in which the script ran.
- Not a window into raw rows. You never print raw rows into the conversation or the brief; result tables are aggregates.
- Not a data editor. You never modify anything in `data/`, and you do not edit `analysis.py`.
- Not a softener. You do not drop a finding because it is awkward, or round a caveat down to nothing.

## The rules

These hold in every act.

- **The answer comes first.** Objective, then Key Takeaways, then Recommendations. A reader who stops after the first screen still has the decision.
- **Every number traces back.** Each number in the brief comes from `analysis.py` and a result table in the run folder, and the brief says which table and which filter.
- **A number alone is not a finding.** Each headline number appears with its comparison, or says "no comparison available". Percentage points and relative percent are named every time.
- **Every chart has a sentence for a heading.** A full sentence that states what the chart proves, with a verb. Not "Conversion by plan".
- **The review is part of the brief.** Findings from `review.md` that were not fixed appear in Checks as not verified or as caveats. Never leave one out.
- **No em dashes.** No jargon the audience would not use.

## Act 1: Find what to deliver (the gate)

1. Find the run folder. Use the argument if given. Otherwise use the newest folder under `outputs/` that holds an `analysis.py`.
2. Check the run folder holds `frame.md`, `analysis.py`, at least one table in `data/`, and `review.md`. List what is missing.
3. If `frame.md` is missing, ask with AskUserQuestion for the question, the decision and the audience, and write nothing until you have them. Never invent a decision.
4. If `review.md` is missing, stop and say the work has not been validated: read `.claude/skills/validate/SKILL.md` and follow it first, or ask the user to run `/validate`. Do not write a brief on unreviewed work.
5. Read the verdict in `review.md`:
   - **Fix first**: stop. Do not write a brief. Report the findings from `review.md` and say the script must be fixed and reviewed again.
   - **Think on it** or **Ship it**: continue.
6. If `analysis.py` or any result table is newer than `review.md`, the review may not cover the current numbers. Say so and ask whether to continue; if the user continues, record it under Checks.

## Act 2: Gather what the brief is made from

1. Read `frame.md` for the question, the decision, the audience, what would change the decision, the definitions, and the time window.
2. Read `review.md` for the verdict, the findings with their tags, the changes made to the script, and what was not checked.
3. Read `knowledge/beam/quirks.md` and `knowledge/beam/corrections.md`, so the brief names every quirk the analysis touched in terms the reader understands.
4. Read the numbers from the run folder, not from memory. Print the result tables in `outputs/<run>/data/` as aggregates with `poetry run python -c ...`, and read the headline numbers and check summaries from a rerun of `poetry run python outputs/<run>/analysis.py`. If the rerun does not match the saved tables, stop and say the results are stale.
5. List the charts in `outputs/<run>/charts/`. For each, find the result table behind it and decide what it proves.
6. Never do arithmetic in prose. If you need a number that is not in a table (a difference, a share), ask for it to be added to `analysis.py` through a rerun of Analyse, or leave it out. Do not compute it yourself.

## Act 3: Decide what the brief says

Before writing, settle these in your own head. They set the whole brief.

1. **The answer.** In one sentence, what does the data say about the question? It must be one the numbers support, and it must be stated against what it is compared with.
2. **Where it falls against the decision line.** Take the line from "What would change the decision" in the frame. Say which side the result lands on, and how close to the line it is. If the frame says "not stated", say that the data supports a direction but no threshold was set.
3. **What to do.** One to three recommendations, each a concrete action with an owner where the frame names one, and each traceable to a takeaway. A recommendation the takeaways do not support does not go in.
4. **How far to trust it.** Use the review verdict. **Ship it** means the answer stands. **Think on it** means it stands with the caveats and findings from `review.md` stated beside it, in the body where they bear on a claim and in Checks. Do not turn a caveat into a certainty.

## Act 4: Write the brief

Write `outputs/<run>/brief.md` in exactly this order.

```markdown
# <Title that states the answer, not the topic>

**Date:** <YYYY-MM-DD, from `date +%F`>
**For:** <audience from the frame>
**Data runs to:** 2026-09-24
**Run folder:** <outputs/<run>/>

## Objective
<The question and the decision it informs, who makes it, and what would change it. Two to four sentences, in the audience's words.>

## Key Takeaways
- <Takeaway: a full sentence with the number and its comparison>
- <Three to five bullets in all, ordered by importance to the decision>

## Recommendations
1. <A concrete action, and the takeaway it follows from>
2. <...>

## Analysis
### <Full sentence stating what this chart proves>
![<short description>](charts/<name>.png)
<Two to four sentences: what the chart shows, the comparison, and the source table and filter. Name any quirk that applies.>

### <Next chart's takeaway as a full sentence>
...

## Checks
**Review verdict:** <Ship it | Think on it>

**Verified**
- <What was checked, what it showed, and the check that ran it>

**Changed after review**
- <Any change made to analysis.py by the review, with the number before and after, or "None">

**Not verified**
- <Each finding from review.md that was not fixed, as the reviewer wrote it, and each item under Not checked>
- <Open periods, unmatured trials, untested assumptions>

**Source**
- <Script path, and the result tables each number comes from>
```

Rules for each part:

- **Title.** It states the answer ("Annual plans retain better than monthly after the price change"), not the topic ("Retention analysis").
- **Objective.** Written for the audience in the frame. It comes from the frame, not from what the script ended up doing.
- **Key Takeaways.** Three to five. Each is a full sentence with its number and its comparison, for example: "Trial conversion is 46% for annual starts against 39% for monthly, 7 percentage points higher." Each must appear in the Analysis section with its evidence.
- **Recommendations.** Fewer is better. Each names an action, not an observation. If the data does not support a recommendation, say what extra evidence would, instead of recommending anyway.
- **Analysis.** One subsection per chart that matters, ordered to follow the argument, not the script. A chart that does not support a takeaway is left out. The heading is a full sentence stating the takeaway; the body gives the comparison, the source table in `data/` and the filter that produced it. Segment results come with the whole they add up to. If a quirk applies (the March 2026 price change, the September 2025 spike, unmatured trials), say so where it touches the number, in plain words.
- **Checks.** Always present, always last. Verified and Not verified both appear, even if one is short. Not verified carries every unfixed finding from `review.md`, labelled as such. It is not a place to bury the doubt: if a caveat changes how much a takeaway can be trusted, say that in the Analysis section too.
- **Length.** One to two pages of reading. Cut anything the decision does not need.

## Act 5: Check the brief against the work

Before you finish, read the brief once as the audience would, cold.

1. Does the first screen give the objective, the takeaways and the recommendations?
2. Does every number in it appear in a result table or in the script's output? Spot check each headline number against `outputs/<run>/data/`.
3. Does every takeaway carry a comparison, with percentage points or relative percent named?
4. Is every chart heading a full sentence with a verb, and does the chart show what the sentence says?
5. Does every finding from `review.md` appear somewhere in the brief?
6. Are there any em dashes, raw rows, or numbers computed in prose?

Fix what fails. If a number cannot be traced, remove it.

## Deliver

The brief is the deliverable. On the CLI, show only:

- The review verdict.
- The Key Takeaways, copied verbatim from the brief.
- The path of the run folder.

Keep it under fifteen lines. Do not paste the whole brief into the CLI. If you stopped at the gate, show what was missing or the Fix first findings, and say that no brief was written.

## Principles

- **Decision first.** The reader opens the brief to decide something. Give them the answer before the evidence.
- **Headings carry the argument.** A reader who only reads the headings should come away with the story.
- **Never a naked number.** Every number carries a comparison, or says none is available, and names its unit of change.
- **Everything traces.** Table, filter and script behind every number, so anyone can rerun it and get the same brief.
- **Code computed it, you wrote it.** The brief reports numbers; it does not produce them.
- **Carry the doubts forward.** What the review found and what nobody checked belong in the brief, in plain words. A brief that sounds surer than the work was is the real failure.
- **No review, no brief.** Unvalidated work is not delivered, and Fix first is never delivered.
- **Say what you did not check.** A gap you name is safer than one a reader finds later.
