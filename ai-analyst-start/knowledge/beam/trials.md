# trials

Grain (a guess from the data, confirm it): one row per trial_id. 2,073 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| trial_id | int64 | 0.00% | 2,073 |
| user_id | int64 | 0.00% | 2,073 |
| started_at | datetime64[ns] | 0.00% | 2,071 |
| ends_at | datetime64[ns] | 0.00% | 2,071 |
| outcome | object | 20.16% | 2 |
| outcome_at | datetime64[ns] | 20.16% | 1,655 |

## Date ranges

- `started_at`: 2026-08-01T00:29:17 to 2026-09-24T22:59:05
- `ends_at`: 2026-08-15T00:29:17 to 2026-10-08T22:59:05
- `outcome_at`: 2026-08-06T05:37:23 to 2026-09-24T23:55:08

## Low-cardinality values

- `outcome`: converted (828), canceled (827)

## Meaning

Grain (inferred): one row per trial, and one trial per user (user_id is unique).

- `trial_id`: key of the trial.
- `user_id`: the user who started it; joins to `subscriptions` and `users` one to one (inferred).
- `started_at`: when the trial began; the first is 2026-08-01, the launch (quirk: trials mature late).
- `ends_at`: always 14 days after `started_at` (inferred from the data: every trial is 14 days).
- `outcome`: `converted` or `canceled`; empty for 20.2% because the trial is still open (quirk: trials mature late). Empty rows are not failures.
- `outcome_at`: when the outcome was recorded. Canceled outcomes are recorded before `ends_at`, so they appear early; converted outcomes appear at `ends_at` (inferred). For this reason an open trial is not a canceled one, and a rate over trials with an outcome so far overstates cancellations in recent weeks.
- A converted trial has a paid subscription starting at `ends_at` (inferred); a canceled one has a free subscription (inferred).
- Verdict: Caution. Use only trials whose `ends_at` is on or before the analysis date.

