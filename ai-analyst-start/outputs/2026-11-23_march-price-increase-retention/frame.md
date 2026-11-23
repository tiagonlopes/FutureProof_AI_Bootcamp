# Frame: Did the March 2026 price increase hurt retention, and for whom?

**Date:** 2026-11-23
**Data runs to:** 2026-09-24

## Question
Did the March 2026 price increase hurt retention, and for whom?

## Decision
Whether to roll back part of the increase for some customers. The head of growth decides.

## Audience
Head of growth

## What would change the decision
- If retention got worse after the increase for an identifiable group of customers: a partial rollback for that group is worth considering.
- If retention did not move beyond normal variation, or moved only in groups too small to matter: keep the increase as it is.
- The size of drop, or the revenue trade-off, that counts as "worth rolling back" is not stated.

## Definitions
- Retention: open. Working meaning is the share of paying subscribers who stay from one month to the next, compared before and after March 2026.
- Hurt: open. Normal month-to-month variation is not yet defined.
- For whom: open. Segments available in the data (plan, country, tenure, device and others) will be tested; none is chosen in advance.
- Price increase: the monthly plan price rose from $10 to $12 in March 2026 (from quirks). Whether any other plan was affected is open.

## Time window
Months before and after March 2026, up to 2026-09-24. Payment history starts 2025-01-01.

## Tables likely involved
- subscriptions
- payments
- users

## Known quirks that may matter
- The monthly plan price rose from $10 to $12 in March 2026, which is the event under study.
- Free plans never end and must be left out of churn and retention.
- end_date can be in the future for scheduled cancellations; those subscriptions are still active.
- Some start dates are after the analysis date (scheduled starts) and are excluded.
- Ended subscriptions switched label from expired to canceled from August 2026; churn is read from end_date, never status.
- The September 2025 signup spike distorts the active base in any comparison that includes it.
- Dates are timestamps; compare on dates.
- corrections.md holds no entries.

## Open items
- No threshold stated for what counts as a retention drop worth acting on.
- Retention, hurt and the segments to test are open definitions.
- Whether the annual plan is in scope.
- Normal month-to-month churn variation is not defined.
