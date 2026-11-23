# Frame: Do trial users who binge on day one and then go quiet convert worse than steady users?

**Date:** 2026-11-23
**Data runs to:** 2026-09-24

## Question
Do trial users who binge on day one and then go quiet convert worse than steady users?

## Decision
Whether the onboarding emails should push trial users to spread their first week out. The head of growth decides.

## Audience
Head of growth

## What would change the decision
- If day-one bingers who go quiet convert clearly worse than steady users, and the gap holds after comparing like with like: pushing users to spread their first week out is worth trying.
- If they convert about the same or better: do not change the emails on this ground.
- The size of gap that counts as clearly worse is not stated.

## Definitions
- Binge on day one: open. Working meaning is an unusually large share of first-week activity falling on the first day of the trial.
- Go quiet: open. Working meaning is little or no activity on the remaining days of the first week.
- Steady users: open. Working meaning is activity spread across several days of the first week.
- Convert: the trial ended as a paid plan (the outcome value is to be confirmed from the data). Open trials are not counted.
- First week: the first 7 days from the trial start.

## Time window
Trials that have matured by 2026-09-24 (started on or before 2026-09-09), launched 2026-08-01 onward.

## Tables likely involved
- trials
- sessions
- users

## Known quirks that may matter
- Trials launched on 2026-08-01 and last 14 days; recent trials have no outcome yet and must not count as failures.
- The trials table has no documented outcome values; they must be read from the data.
- Trials link to subscriptions only by user and timing.
- A user can have more than one trial.
- Dates are timestamps; compare on dates.
- sessions is very large and is queried in aggregates only.
- corrections.md holds no entries.

## Open items
- Definitions of binge, quiet and steady are working definitions, not agreed ones.
- No threshold for what gap would justify changing the emails.
- Binge and conversion may both reflect how interested a user already was, so a gap is not proof that spreading out would help.
