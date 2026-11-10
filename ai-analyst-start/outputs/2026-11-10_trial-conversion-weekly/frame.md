# Frame: How is the 14-day trial converting since launch, and is it changing week over week?

**Date:** 2026-11-10
**Data runs to:** 2026-09-24

## Question
How is the 14-day trial converting since launch, and is the conversion rate changing from week to week?

## Decision
Whether to keep the trial at 14 days or change its length. The head of growth decides.

## Audience
Head of growth

## What would change the decision
- Not stated. No target rate or threshold was given, so any threshold is open.

## Definitions
- Converting: a trial that ends with a paid subscription (monthly or annual) starting. Confirmed by the user.
- Week: calendar week by the date the trial started (open: week boundary chosen in the analysis and stated there).
- Since launch: trials started from the launch on 2026-08-01 to 2026-09-24.

## Time window
2026-08-01 (trial launch) to 2026-09-24.

## Tables likely involved
- trials
- subscriptions
- users

## Known quirks that may matter
- Trials last 14 days and mature late: recent trials have an empty outcome and are still open, not failed.
- Future start dates: some subscriptions start after today and are scheduled starts from trials that have not matured.
- Timestamps everywhere: compare on dates.

## Open items
- No threshold for changing the trial length is stated.
- Only one trial length (14 days) exists in the data, so a different length cannot be compared directly.
