# Review: Do trial users who binge on day one and then go quiet convert worse than steady users?

**Date:** 2026-11-23
**Reviewed:** outputs/2026-11-23_trial-day-one-binge-conversion/analysis.py
**Verdict:** Think on it

## The question
Do day-one bingers who go quiet convert worse than steady trial users? The head of growth decides whether onboarding emails should push trial users to spread their first week out.

## Mechanics
| Check | Result |
|---|---|
| Joins | Trials left-joined to sessions on user_id then aggregated back to one row per trial inside the query. 1,516 trials, 1,516 distinct users, so no fan-out and no repeat trials per user. |
| Grain | One row per trial; rates are converted trials over matured trials. |
| Denominators | Only trials started before 2026-09-10; none open in this window (0 of 1,516). Count matches the 1,516 matured trials in the trial snapshot note. |
| Date boundaries | Last included start is 2026-09-09; ends 14 days later, before the data end of 2026-09-24. Trials from 2026-09-10 on excluded (some are open and cancellations arrive early, which would bias the rate down). |
| Filters | Window of 3 days closes before the first cancellation (day 4), so quiet is not caused by cancelling. The 7-day table keeps only trials still open on day 7. |
| Parts and totals | The four groups are partial by design; the day-one by follow-up grid sums to the 1,516 total (parts_sum_to_total). |
| Comparison and units | Rates compared in percentage points and relative percent with 95% Wilson intervals; overall conversion 53.2% is the benchmark. |

## Reasoning
- Right question: yes for the association. Binge, quiet and steady are working definitions from the frame, not agreed ones.
- Outside the frame: activity and conversion both reflect interest, so the gap does not show that spreading use out would raise conversion. The 3-day window is shorter than the week the decision names. Session counts are capped, and the cut-offs (8 or more, 2 or fewer) were chosen by the analyst.
- So-what: the gap is large and well outside the noise (25.2% against 75.4%, intervals 18.0% to 34.2% and 72.0% to 78.5%). But low-start, quiet users convert worse (14.2%), so quietness explains more than the binge. Within a quiet follow-up, a day-one binge (25.2%) is not worse than a light start (19.2%).

## Findings
1. **Association, not cause** (Caveat only): the data cannot show whether nudging users to spread out would raise conversion; it only shows that those who stay active convert more.
2. **Definitions and window are ours** (Caveat only): thresholds were picked by the analyst, and the 7-day check rests on 50 binge-then-quiet trials (10.0%, interval 4.3% to 21.4%), conditioned on surviving to day 7.
3. **Binge is not the driver** (Caveat only): the worst group is quiet users with a light start, so the email goal is better framed as keeping users active after day one than as limiting day one.

## Changes made to analysis.py
None after review (two cosmetic lines removed during writing; numbers unchanged).

## Not checked
- Segments by country, device or plan.
- Effect of the trial itself or of existing email nudges.
- Other thresholds for binge and quiet.
