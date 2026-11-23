---
name: analyse
description: Answers a framed business question about Beam's data by querying the database directly through course-db, then computing every headline number in one script that can be rerun, where every headline number carries its comparison. Use after a question has been framed, when it is time to compute the answer. Reads the frame note in the run folder under outputs/ and writes the queries, script, result tables and charts next to it.
user-invocable: true
allowed-tools: Read Bash Write Edit Glob AskUserQuestion mcp__course-db__list_tables mcp__course-db__execute_sql
argument-hint: "[path to the run folder under outputs/]"
---

You answer the framed question with queries and code that can be rerun.

The failure you exist to prevent: a confident number with no baseline, or a number that came out of a chain of arithmetic written in prose that nobody can check. "Trial conversion is 50%" tells a reader nothing until it says 50% against what. And a number computed in the conversation cannot be rerun, reviewed or corrected. The answer might even be right. Nobody can tell.

So the model reasons and the code computes. You decide what to compute and what to compare it with. The database does the aggregation through saved queries, and a script in the run folder does every rate, check and chart from those results.

The source is the live database, reached only through the `course-db` MCP tools. Do not read the CSVs in `data/`.

## What this is NOT

- Not the brief. You report numbers on the CLI; the Deliver step writes the brief.
- Not the review. You run the checks your plan needs; the Validate step reviews the work.
- Not a notebook. The output is a query file and one script that runs top to bottom.
- Not a window into raw rows. You never select raw rows into the conversation; every query returns aggregates, and the script prints aggregates only.
- Not a data editor. Every statement you send is a read-only SELECT. You never modify the database or anything in `data/`.

## The rules

These hold in every act.

- **A number alone is not a finding.** Every headline number carries a comparison: a prior period, a segment, or a benchmark.
- **If no comparison exists, say "no comparison available".** Never invent a baseline to fill the gap.
- **Segment before you average** when the frame or a quirk suggests groups behave differently. An average over groups that move in opposite directions hides both.
- **Percentage points and relative percent are different numbers.** A rate going from 40% to 44% is up 4 percentage points and up 10% relative. Name which one you mean, every time.
- **Never trust a period that has not closed.** A month still in progress, or a trial still inside its 14 days, is not a result yet.
- **Aggregate in the query.** Counts, sums, averages and distinct counts are computed by `execute_sql`, grouped by a period or a dimension. `sessions` in particular is very large: filter on `session_date` first and never select its rows.
- **Today is 2026-09-24.** The data ends there. Never use `CURRENT_DATE` or `NOW()` in a query; write the date.

## Act 1: Find the question (the gate)

1. Find the run folder. Use the argument if given. Otherwise use the newest folder under `outputs/` that holds a `frame.md`.
2. Read `frame.md` for the question, the decision it informs, the audience, and what would change the decision.
3. If there is no frame note, ask with AskUserQuestion for the question and the decision it informs. Then write `outputs/<YYYY-MM-DD>_<slug>/frame.md` yourself before anything else, with the same fields the Frame step writes: question, decision, audience, what would change the decision, and the tables likely involved. Get the date with `date +%F`; never guess it.
4. Never proceed on a guessed question. You may confirm a question you infer; you may not assume one.

## Act 2: Load the context

1. Read `knowledge/beam/quirks.md`, `knowledge/beam/corrections.md`, and `knowledge/beam/<table>.yaml` for each table involved.
2. Call `mcp__course-db__list_tables` to see which tables exist in the database, across schemas, and use it to pick the right source. Prefer the base tables in `public` for anything that must be exact. Treat the `marts` and `ml` tables as derived copies: read their notes for what they omit, and reconcile them against the source before you rely on them.
3. If a table involved has no note, run the profile skill on it first: read `.claude/skills/profile/SKILL.md` and follow it, then come back here. Where a note has a golden query that fits, start from it.
4. Say in one line which quirks apply to this question, and which corrections, if any.

## Act 3: Plan

Write three to six bullets describing the computation. The plan must say:

- What each headline number is and the comparison it will carry (prior period, segment or benchmark), or that none exists.
- Which tables each query reads, with the schema, and the join path.
- How each applicable quirk is handled. For example: matured trials only; free plans excluded from churn; scheduled starts after today excluded; the September 2025 anomaly named if it enters a comparison.
- Which segments you will split by and why.
- Which checks the script will run.

Show the plan before running anything.

## Act 4: Query, then compute

1. Write the queries to `outputs/<run>/queries.sql`, one named block per result table, each a single aggregate SELECT. Add a comment above each saying what it returns.
2. Run each with `mcp__course-db__execute_sql`, one statement per call. If a query errors, read the message, fix it in `queries.sql` and resend. Do not drop a check because it failed once.
3. Before you trust a join, run a fan-out check as a query: the row count before and after the join, or a count of distinct keys against rows.
4. Save each result as `outputs/<run>/data/<name>.csv`, a verbatim copy of the query result with the column names as returned. The results are aggregates, so they are small. Say in the script's header comment that these files come from `queries.sql`, and which tool ran it.
5. Write one script at `outputs/<run>/analysis.py`:
   - Read the result tables from `outputs/<run>/data/`. It does not read `data/` and does not connect to the database.
   - Compute every rate, difference and comparison here, not in prose. Use `helpers.checks` for at least the checks the plan needs: `date_boundaries` for partial periods at the edges, `matured_only` for windows that have not closed, `join_fan_out` before trusting any join, `parts_sum_to_total` when segments should add back to a total. Print each check's `summary`.
   - Make charts only through `helpers.charts`: `bar` or `line`, then `save` into `outputs/<run>/charts/<name>.png`. Every title states the takeaway the chart proves, not a label.
   - Print the headline numbers, each with its comparison, and the check summaries. Print aggregates only.
6. Run it from the repo root with `poetry run python outputs/<run>/analysis.py`. If it fails, fix it and rerun until it runs clean. If a check fails, decide whether it changes the answer and fix the query or the script, or report it. If the data cannot answer the question, say so plainly and stop.

## Act 5: Report

On the CLI, report:

- Each headline number with its comparison, stated as percentage points or relative percent, saying which.
- What was segmented and why.
- Which tables were queried and which quirks were handled.
- Which checks ran and what each said.
- What was not checked.
- The path of the run folder.

Keep it under twenty lines. No brief here; the Deliver step writes the brief.

## Principles

- **The question is the gate.** No frame note, no analysis. Ask; never guess.
- **The database is the source.** Every number traces to a query on `course-db`. None comes from a CSV export or from memory.
- **The model reasons, the code computes.** Every number comes out of a saved query or `analysis.py`. None comes from prose arithmetic.
- **Aggregates only.** Query for counts, sums and averages, never for rows, and never write to the database.
- **Always compare.** A number without its comparison is not a finding. When there is no comparison, say so.
- **Quirks first.** Read what is known about the tables before computing anything, and say how each applicable quirk was handled.
- **Closed periods only.** An open month or an unmatured trial is not a result.
- **Name the unit of change.** Percentage points or relative percent, never left for the reader to guess.
- **Rerunnable or it did not happen.** Anyone can rerun `queries.sql` through `course-db`, run the script on the saved results, and get the same tables, charts and numbers.
- **Say what you did not check.** A gap you name is safer than one a reader finds later.
