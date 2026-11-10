# Review: Did the March 2026 price increase hurt retention, and for whom?

**Date:** 2026-11-10
**Reviewed:** outputs/2026-11-10_march-price-increase-retention/analysis.py
**Verdict:** Think on it

## The question
Did the March 2026 monthly price rise ($10 to $12) raise churn on the monthly plan, and for which customers? The head of growth decides whether to roll back part of the increase for some customers.

## Mechanics
| Check | Result |
|---|---|
| Joins | `join_fan_out` on subscriptions and users by user_id kept 30,747 of 30,747 rows. user_id is unique in subscriptions, so no fan-out. Payments are only joined to subscriptions for the price check, which uses shares, not sums. |
| Grain | One row per subscription and one per user. The churn panel is one row per subscriber per closed month, and the rate is counted at that grain. |
| Denominators | Active at the start of the month = started before it and no end date, or end date on or after it. Free, annual and scheduled starts are excluded. Future end dates count as active. Recounted separately from end dates by month: matches the monthly counts. |
| Date boundaries | September 2026 is open and excluded. March 2026 is dropped from both windows: its churn (26.2 per 1,000) matches the pre level, because March renewals were the first at $12 and cancellations land in April. Including it gives index 221 instead of 244. |
| Filters | 8,924 of 9,376 monthly rows kept (452 scheduled starts removed). Status was not used because it relabels from "expired" to "canceled" in August 2026; end_date was used. |
| Parts and totals | `parts_sum_to_total` matched for country, device, tenure and cohort (1,553 cancellations each). |
| Comparison and units | Rates per 1,000 per month. Index = post / pre x 100. Relative and absolute change are labelled. |

## Reasoning
- Right question: yes. The script measures monthly churn before and after, split by segment, against a break-even set by the price change. The frame's revenue test is covered only through a steady-state rule.
- Outside the frame: every monthly subscriber was repriced, so there is no untreated monthly group. The annual plan was not repriced and is the only available control. The pre baseline is itself higher than early 2025 (23.7 against 8.0 per 1,000), after the September 2025 spike.
- So-what: the step lands in April, the first month after the first $12 renewals, and the annual plan does not move (5.5 before, 5.3 after, index 97) while the monthly plan more than doubles (index 244). That supports the price as the cause. The result sits far above the 120 break-even, so the decision does not turn on small errors.

## Findings
1. **No control group in the first version of the script** (Small change): all monthly subscribers were repriced, so a before and after on the monthly plan alone cannot separate the price from anything else that changed. The annual plan was not repriced and its churn did not move. Added to the script; see below.
2. **The pre baseline is unstable** (Caveat only): monthly churn was 8.0 per 1,000 in January to August 2025 and 23.7 in October 2025 to February 2026. The index of 244 is against the higher, later baseline. Against early 2025 the rise is much larger. The increase is real under either baseline, but its exact size depends on the baseline chosen.
3. **Segment results do not discriminate** (Caveat only): every segment's index is between 218 and 289 and every one is beyond the break-even, so the rollback flag is true for all of them. Differences between segments were not tested against each other. Levels differ more than ratios do: lowest churn in iOS and the US, highest in Web, India, and subscribers under 3 months.

## Changes made to analysis.py
- Added the annual plan as a control (finding 1). Output: annual churn per 1,000 pre 5.5, post 5.3, index 97 against 244 for the monthly plan. No headline number changed.
- Earlier, before this review: the post window was moved from March to August to April to August, because March shows no step. This changed the monthly index from 221 to 244.

## Not checked
- Whether the p-values are overstated: person-months are not independent, since one subscriber appears in several months.
- Dollar impact of a rollback. The script uses a steady-state rule (lifetime revenue is price over churn), which ignores discounting and a new customer mix.
- Whether the September 2025 spike, or a change in billing or product around then, explains the higher pre baseline.
- Whether the status change from "expired" to "canceled" in August 2026 means anything for the business.
- Trials: the monthly plan is not split into trial conversions and other starts.
