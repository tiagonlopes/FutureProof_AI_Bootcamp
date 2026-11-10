# Review: Is engagement growing, and what happened around the trial launch?

**Date:** 2026-11-10
**Reviewed:** outputs/2026-11-10_monthly-active-users-trial-launch/analysis.py
**Verdict:** Think on it

## The question
Are monthly active users up over two years, and what happened around the trial launch? The head of growth decides whether to keep funding the trial programme or move the budget to retention offers.

## Mechanics
| Check | Result |
|---|---|
| Joins | `join_fan_out` on trials to users kept 2,073 of 2,073 rows, and on subscriptions to users kept 30,747 of 30,747. No fan-out. |
| Grain | Activity table is one row per day with no gaps (997 one-day steps). Trials, users and subscriptions are one row per user. Monthly figures are taken at month grain from the daily rows. |
| Denominators | Trial conversion is converted over matured trials (1,516), none with an empty outcome. Open trials (557) are excluded. |
| Date boundaries | `date_boundaries` shows September 2026 is partial (to the 24th). It is excluded from every closed-month comparison and labelled open. |
| Filters | Scheduled starts after 2026-09-24 removed from paid-start counts. Free plans are not used in any churn measure. |
| Parts and totals | Converted plus canceled sum to 1,516 matured trials, 0.00% apart. |
| Comparison and units | MAU is a rolling figure, so the last day of each month is used. Year over year is relative percent. The September 2025 spike is named and quantified. |

## Reasoning
- Right question: partly. MAU growth and the launch-month change are answered. Whether the trial programme is worth funding needs conversion value and retention of converted users, which the data cannot yet show.
- Outside the frame: non-trial signups also rose at the launch week, so the launch month cannot be credited to trials alone. The activity table has no user level, so actives cannot be split by trial status.
- So-what: the growth is real and steady, and the launch month stands out. The decision turns on a threshold nobody stated, so the result cannot be placed against a line.

## Findings
1. **Lift cannot be attributed to the trial** (Caveat only): average non-trial signups per full week rose from 155 (May to July 2026) to 260 (Aug 3 to Sep 14), alongside 261 trial signups a week. Something else changed at the launch, or trials draw in free signups. Either way the August MAU gain of 1,748 is not purely the trial.
2. **Year-over-year growth is inflated by the September 2025 spike** (Caveat only): of the 9,654 gain from Aug 2025 to Aug 2026, about 2,928 is the spike's excess over trend. Underlying monthly gains were about 518 before the spike and 446 after it.
3. **Unexplained July 2026 paid-start spike** (Caveat only): paid starts not tied to trials were 649 in July against 247 to 286 in earlier months, then 90 in August. It sits just before the launch and is not explained by the data.

## Changes made to analysis.py
Added a weekly signup split (trial and non-trial) and a check that every closed month's MAU change is positive. No headline number changed.

## Not checked
- Whether converted trial users stay: the oldest conversion is about six weeks old.
- Value of trial conversions against the trial programme cost, which is not in the data.
- Cause of the September 2025 spike and of the July 2026 paid-start spike.
- Any marketing change at the launch.
