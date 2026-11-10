# Frame: Is engagement growing, and what happened around the trial launch?

**Date:** 2026-11-10
**Data runs to:** 2026-09-24

## Question
Are monthly active users up over the last two years, and what happened around the trial launch?

## Decision
Whether to keep funding the trial programme or move that budget to retention offers. The head of growth makes it.

## Audience
Head of growth

## What would change the decision
- If monthly active users are growing and the trial launch coincides with a lasting lift in actives or in conversion to paid plans: keep funding the trial programme.
- If growth is flat or comes from a one-off spike, and the trial launch shows no lasting lift: move the budget to retention offers.
- No threshold for "enough lift" was stated.

## Definitions
- Engagement: measured as monthly active users, as the question implies. Confirm against the activity table.
- Monthly active users: open, to be fixed from the activity table's own definition during profiling.
- Growing: compare the latest complete month with the same month a year earlier and show the trend across the window.
- Trial launch: 2026-08-01, per the quirks note.

## Time window
Two years up to 2026-09-24. September 2026 is an open month and is flagged, not compared as complete.

## Tables likely involved
- user_activity_metrics
- trials
- subscriptions
- users

## Known quirks that may matter
- September 2025 shows a signup and active spike of about five times a normal month, which distorts any year-over-year comparison.
- Trials launched on 2026-08-01 and mature after 14 days, so recent trials have no outcome yet and are not failures.
- Subscriptions with a start date after the analysis date are scheduled starts and are excluded from counts of what has happened.
- Free plans never end, so they are excluded from churn or retention measures.
- The monthly plan price rose in March 2026, which affects payments but not activity counts.
- Dates are timestamps; compare on dates.

## Open items
- Definition of monthly active users, to be taken from the activity table.
- No threshold stated for what counts as a meaningful lift.
- user_activity_metrics has no knowledge note yet and needs profiling.
