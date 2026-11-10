# Frame: Did the March 2026 price increase hurt retention, and for whom?

**Date:** 2026-11-10
**Data runs to:** 2026-09-24

## Question
Did the March 2026 monthly price increase from $10 to $12 hurt retention, and for which customers?

## Decision
Whether to roll back part of the increase for some customers. The head of growth decides.

## Audience
Head of growth

## What would change the decision
- If, for a segment, the revenue lost from extra cancellations outweighs the extra revenue from the higher price: roll the increase back for that segment.
- If, for a segment, the extra revenue outweighs the revenue lost, or churn did not move beyond normal variation: keep the increase for that segment.

## Definitions
- Retention: monthly churn of paying subscribers, the share of active paid monthly subscribers who cancel in a month, compared before and after March 2026.
- Hurt: churn rises and the lost revenue is larger than the revenue from the $2 uplift. Normal month-to-month variation is not yet defined (open).
- For whom: segments available in the data, such as country and device type (open: others may be tested).

## Time window
Before and after March 2026, up to 2026-09-24. Payment history starts 2025-01-01.

## Tables likely involved
- subscriptions
- payments
- users

## Known quirks that may matter
- Monthly plan price changed from $10 to $12 in March 2026, which is the event under study.
- Free plans never end and must be left out of churn.
- end_date can be in the future for scheduled cancellations, which are still active.
- Some start dates are after today; scheduled starts are excluded.
- September 2025 signup spike distorts the active base and any comparison that includes it.
- Dates are timestamps; compare on dates.

## Open items
- Normal month-to-month churn variation is not defined.
- Whether the annual plan is in scope (assumed no: the price change was on the monthly plan).
