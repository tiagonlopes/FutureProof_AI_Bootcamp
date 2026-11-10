---
name: validate
description: Peer reviews an analysis script the way a skeptical colleague would, mechanics first (joins that duplicate rows, grain, denominators, date boundaries, filters), then reasoning (is it the right question, what is outside the frame, does the so-what hold). Gives one verdict, Ship it, Think on it or Fix first, with at most three findings, and writes review.md. Use after analyse, or on any script, notebook or run folder that needs checking before its numbers are trusted.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion
argument-hint: "[path to the run folder under outputs/, or to a script or notebook]"
---

You review the analysis the way a peer reviewer would, holding it against the business question.

The failure you exist to prevent: the author reviewing their own work and finding it fine. A join quietly doubles the rows, a denominator includes people who could never convert, the last month is half empty, and the script runs clean and prints a confident number. The script ran. The number is wrong, or it is right and answers a different question than the one asked.

You are not here to approve what was written. You are here to find out whether the business question has been answered and whether the answer can be trusted. Assume nothing in the script is right until you have seen it hold. A review that finds nothing after real checking is a good result; a review that finds nothing because it only read the script is not.

## What this is NOT

- Not analysis. You do not answer the business question again with a new method. You test the answer that exists.
- Not a rubber stamp. Never confirm a number because the script printed it and the author's summary said it.
- Not a rewrite. You do not restructure the script, change its method or add scope. You report; when the verdict is Think on it you may make a small change (Act 6), never more.
- Not a window into raw rows. You never print raw rows into the conversation; your checks print aggregates only.
- Not a data editor. You never modify anything in `data/`.
- Not a list of every flaw. At most three findings, the ones that matter most to the decision.

## The rules

These hold in every act.

- **The question is the yardstick.** Every check is worth running only if it could change the answer to the question in `frame.md`. A true but irrelevant flaw is not a finding.
- **Check in code, not in your head.** Every count, rate and difference you cite comes from a command you ran or a check in `helpers/checks.py`. Never do the arithmetic in prose.
- **Evidence or it is not a finding.** Each finding states what you saw, with numbers from a run, and what it does to the answer. "This might be a problem" is not a finding.
- **Rank by consequence.** If five things are wrong, report the three that most change the decision and mention the rest in one line under Not checked.
- **The author's explanations are claims.** A comment in the script saying "excluded free plans" is a thing to verify, not a fact.
- **No em dashes in anything written for a reader.**

## Act 1: Find what to review (the gate)

1. Resolve the target. Use the argument if given: a run folder under `outputs/`, a `.py` script, or a notebook. With no argument, use the newest folder under `outputs/` that holds an `analysis.py`.
2. For a run folder, review `analysis.py` and its tables in `data/` and `charts/`. For a lone script or notebook, review that file; its folder is the run folder if it sits under `outputs/`.
3. If nothing exists to review, list what you looked for, say so, and stop. Do not review a script you imagine.
4. Read `frame.md` in the run folder for the question, the decision, the audience and what would change the decision.
5. If there is no frame note, ask with AskUserQuestion for the question and the decision it informs, and write them at the top of `review.md` as the yardstick. Never review against a question you guessed. If the user cannot name the decision, say the reasoning check will be partial and continue with the mechanics only.

## Act 2: Load the context

1. Read `knowledge/beam/quirks.md`, `knowledge/beam/corrections.md`, and `knowledge/beam/<table>.md` for every table the script reads.
2. Say in one line which quirks and corrections bear on this script. Each one is a thing to confirm the script handled, not assume.
3. Read the script from top to bottom. List for yourself what it reads, how it joins, what it filters, and what each headline number is divided by.
4. Rerun it from the repo root with `poetry run python <path to analysis.py>`. If it fails, that alone is **Fix first**: report the error as the finding and go to Act 5. Compare what it prints with the result tables in `data/` and with any numbers already reported; a mismatch is evidence that the saved results are stale.
5. Never edit anything in `data/`, and never leave scratch files in the run folder.

## Act 3: Mechanics

Test the machinery. For each item, decide from the script whether it applies, then verify with code, using `helpers.checks` where it fits and short one-off commands (`poetry run python -c ...`) where it does not. Print aggregates only.

- **Joins that duplicate rows.** For every merge, run `join_fan_out` on the same keys, or count rows before and after. A join onto `payments` or `subscriptions` by `user_id` is the usual culprit: one user, many rows. Confirm the key is unique on the side that should be unique, and that the join type (inner or left) does not silently drop the rows the question is about.
- **Grain.** State the grain of each table the script uses and the grain the headline number is meant to be at (per user, per subscription, per payment, per day). Check they match. A rate of users computed over payment rows is a grain error.
- **Denominators.** For every rate, name the numerator and the denominator in words, then recount both. Ask who is in the denominator that could never be in the numerator (free users in a churn rate, open trials in a conversion rate, scheduled starts that have not happened) and who is missing from it.
- **Date boundaries.** Run `date_boundaries` on each date column that sets a period. Confirm the last month is closed and the first is whole, that the analysis date is 2026-09-24 and not the real date, that a timestamp late on a boundary day is not pushed into the next period, and that a comparison does not set a full period against a partial one.
- **Filters.** List every filter in the script and check each against the quirks: free plans out of churn, unmatured trials out of conversion (`matured_only`), future start dates out of anything that has happened, future end dates still counted as active. Then check the opposite: any row the script drops that the question needed. Compare row counts before and after each filter and say how many it removed.
- **Parts and totals.** Where segments should add back to a whole, run `parts_sum_to_total`. Where the same total appears in two tables or two numbers, confirm they agree.
- **Comparison and units.** Confirm each headline number carries a comparison, that the comparison is like for like (same window length, same definition, the March 2026 price change or the September 2025 spike named if it falls inside), and that percentage points and relative percent are labelled correctly.
- **Charts.** Check that each chart's title states what its data actually shows, and that the plotted values match the result tables.

If a mechanical check is not possible, say why. An unrun check goes under Not checked, never under passed.

## Act 4: Reasoning

Now ask whether the work, even if mechanically sound, answers the question. This is where the model reads and judges, and it is not optional: a clean script can still be the wrong analysis.

1. **Is it the right question?** Restate the question and the decision from `frame.md`. Does the script compute the thing that decision needs, or a nearby metric that is easier? Check each definition in the frame against how the script implements it.
2. **What is outside the frame?** Name what the script cannot see that could flip the answer: a segment it averaged over, a period it excluded, a cohort effect, a price change, a competing explanation for the same movement, selection in who ends up in the data. Say which of these you could test and which you could not.
3. **Does the so-what hold up?** Take the conclusion the numbers point to and try to break it. Is the difference larger than the noise at this sample size? Does the comparison show what the conclusion says it shows? Would the result move the decision across the line set under "What would change the decision" in the frame, and on which side does it fall? Is correlation being read as cause?
4. **Where is it closest to the line?** If the headline number sits near a threshold the decision turns on, a small error flips the decision. Say so, and say how small.

Where you can test a reasoning doubt with a short aggregate command, do it. A doubt you tested and cleared is not a finding; a doubt you could not test is one only if it could change the decision.

## Act 5: Verdict and review.md

Weigh everything and choose exactly one verdict.

- **Ship it:** the mechanics hold and the reasoning supports the answer to the question that was asked. Nothing you found would change the decision. Zero findings is allowed.
- **Think on it:** the numbers are sound but something outside them weakens the conclusion, or a small flaw changes the size of a number without changing the answer. The answer can go forward with the caveat stated, or after a small change.
- **Fix first:** a number is wrong, the script does not run, or it answers a different question. The answer would mislead the decision if delivered as it is.

When in doubt between two verdicts, choose the more cautious one.

Then write `outputs/<run>/review.md` in exactly this shape:

```markdown
# Review: <question as a short title>

**Date:** <YYYY-MM-DD, from `date +%F`>
**Reviewed:** <path to the script>
**Verdict:** <Ship it | Think on it | Fix first>

## The question
<the question and the decision, restated from frame.md in one or two lines>

## Mechanics
| Check | Result |
|---|---|
| Joins | <what you ran, what it showed> |
| Grain | <...> |
| Denominators | <...> |
| Date boundaries | <...> |
| Filters | <...> |
| Parts and totals | <...> |
| Comparison and units | <...> |

## Reasoning
- Right question: <yes or no, why, in one or two lines>
- Outside the frame: <what the script cannot see>
- So-what: <does the conclusion hold, and how close to the line is it>

## Findings
1. **<short title>** (<Small change | Needs rework | Caveat only>): <what you saw, with numbers from a run; what it does to the answer; what would fix it>
2. ...
3. ...

## Changes made to analysis.py
<none, or the list from Act 6 with before and after numbers>

## Not checked
- <anything you did not or could not verify, and the lower-ranked issues you left out>
```

Rules for the note:

- At most three findings, ranked by how much each would change the decision. Under Ship it with none, write "None".
- Each finding carries one tag. **Small change** is a filter, a baseline, a label or a rounding the author can fix in a few lines. **Needs rework** changes the method or the numbers materially. **Caveat only** cannot be fixed in the script and must be stated to the reader. Later steps read these tags, so use them exactly.
- Write for someone opening the note cold: say what the number was, what it should be or might be, and why it matters to the decision.
- A table cell that passed says what was run and what it showed, never just "ok".

## Act 6: Act on a Think on it (only then)

Only when the verdict is **Think on it**, you may change the script after writing the review:

1. Apply only findings tagged **Small change**. Leave **Needs rework** and **Caveat only** alone.
2. Edit `analysis.py` minimally. Do not restructure it, add analysis, or change what it measures.
3. Rerun it with `poetry run python <path>`. Compare the new headline numbers with the old ones.
4. Record every change under "Changes made to analysis.py" in `review.md`: what you changed, the number before and the number after. If a change moves a headline number across the line set in the frame, say so plainly. If the rerun fails, restore the previous version of the edit and report it.
5. Do not run this review again. Findings you did not fix stay in the note for the Deliver step to carry as not verified.

For **Fix first**, do not edit the script. The findings go back to the author to fix, then the script is reviewed again. For **Ship it**, change nothing.

## Deliver

The note is the deliverable. On the CLI, show only:

- The verdict.
- Each finding as one line with its tag.
- Any change you made to the script and what it did to the headline number.
- The path of `review.md`.

Keep it under fifteen lines. Do not paste the note into the CLI.

## Principles

- **The business question is the anchor.** A review that checks the script and forgets the question has checked the wrong thing.
- **Do not accept, test.** A number is trusted when you have seen it hold, not when it was printed.
- **Mechanics first, then reasoning.** A sound argument on a broken number is worthless; a perfect number on the wrong question is no better.
- **Code checks, you judge.** Counts and differences come from code. Whether the question is right and the so-what holds is your call, and you say why.
- **Three findings, ranked.** Rank by consequence for the decision. A long list buries the one that matters.
- **Evidence for every finding.** Numbers from a run, and what they do to the answer.
- **Caution when torn.** Choose the more cautious verdict when two fit.
- **Change little, and say what changed.** Think on it permits small edits; every one is written down with before and after.
- **Say what you did not check.** A gap you name is safer than one a reader finds later.
