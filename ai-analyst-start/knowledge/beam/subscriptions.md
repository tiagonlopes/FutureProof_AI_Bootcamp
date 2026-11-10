# subscriptions

Grain (a guess from the data, confirm it): one row per subscription_id. 30,747 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| subscription_id | int64 | 0.00% | 30,747 |
| user_id | int64 | 0.00% | 30,747 |
| plan | object | 0.00% | 3 |
| start_date | datetime64[ns] | 0.00% | 9,584 |
| end_date | datetime64[ns] | 87.90% | 1,789 |
| status | object | 0.00% | 3 |

## Date ranges

- `start_date`: 2022-01-11T00:00:00 to 2026-10-04T17:15:33
- `end_date`: 2022-03-07T00:00:00 to 2026-11-11T18:47:46

## Low-cardinality values

- `plan`: free (18,234), monthly (9,376), annual (3,137)
- `status`: active (27,028), expired (2,929), canceled (790)

## Meaning

Grain (inferred): one row per user; user_id is unique here, so each user has at most one subscription row.

- `subscription_id`: key of the subscription (inferred).
- `user_id`: owner of the subscription; joins to `users` one to one (inferred, join checked unique).
- `plan`: free, monthly or annual. Free never ends (quirk: free plans never end).
- `start_date`: when the subscription began. Some are after 2026-09-24: scheduled starts (quirk: future start dates).
- `end_date`: when it ended; empty for 87.9% of rows because those are active (inferred). Present for every canceled and expired row. Future values are scheduled cancellations (quirk: future end dates).
- `status`: active, expired or canceled (inferred: expired is an ended term, canceled is a user cancellation).
- Verdict: Proceed, with the future start and end dates handled.

