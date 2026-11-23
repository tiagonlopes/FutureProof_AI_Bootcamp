# Review: Did the March 2026 price increase hurt retention, and for whom?

**Date:** 2026-11-23
**Reviewed:** outputs/2026-11-23_march-price-increase-retention/analysis.py
**Verdict:** Think on it

## The question
Did the March 2026 price increase hurt retention, and for whom? The head of growth decides whether to roll back part of the increase for some customers.

## Mechanics
| Check | Result |
|---|---|
| Joins | Subscriptions to users on user_id: 9,376 monthly subscriptions, 9,376 distinct subscriptions and 9,376 distinct users, so no fan-out. |
| Grain | Subscriber-months on the monthly plan; each rate is churned subscriptions over subscriptions active at month start. |
| Denominators | Free plans excluded; only subscriptions started before the month start; scheduled future end dates (154) are not counted as churn; 452 future starts never enter months up to Aug 2026. |
| Date boundaries | Months Oct 2025 to Aug 2026 are closed; Sep 2026 is excluded as open. |
| Filters | Plan filter and start/end rules match the subscriptions note golden query. |
| Parts and totals | Country, device and tenure parts sum exactly to the total for subscriber-months and churn, before and after. |
| Comparison and units | Pre (Oct 2025 to Mar 2026) against post (Apr to Aug 2026), reported in percentage points and relative percent. The September 2025 spike sits before the pre window; a cohort check was run. |

## Reasoning
- Right question: yes for "did churn rise and where". "Hurt" in revenue terms is only approximated.
- Outside the frame: no control group on the monthly plan, since every monthly subscriber got the $2 rise. The annual plan (flat, 0.52% to 0.53%) is the only comparison, and it differs in kind. Other changes in April to August (for example the trial launch on 2026-08-01) cannot be separated out. Segments differ by who they are, not by how much they were charged, so "for whom" shows who left, not who is price sensitive.
- So-what: monthly churn went from 2.42% to 5.79% (+3.37 percentage points, +140% relative); post months range 4.84% to 6.57%, never inside the pre range of 2.16% to 2.64%. The September 2025 cohort rose from 3.94% to 8.79% and everyone else from 2.03% to 5.28%, so the rise is not that cohort alone. The conclusion holds; the revenue trade-off per segment is the weak part.

## Findings
1. **Revenue trade-off is one month only** (Caveat only): the lost revenue per segment assumes extra leavers cost one month at $12, and ignores how many future months they would have paid. Lifetime value could flip the "uplift beats loss" result for segments that look close, such as under 6 months.
2. **No monthly-plan control** (Caveat only): the rise cannot be separated from other April to August changes, so the effect is an association with timing, supported by the flat annual plan.
3. **Segment results overlap** (Caveat only): country, device and tenure are cut one at a time; the combined segments were not tested.

## Changes made to analysis.py
Added the September 2025 cohort check (queries.sql block, data file and printed lines). No headline number changed.

## Not checked
- Combined segments, such as tenure by country.
- Reasons for cancelling and any price-related support signals.
- Whether March churn was flat because of renewal timing; not tested.
- Statistical significance tests; the gap is large against the observed ranges but no test was run.
