# payments

Grain (a guess from the data, confirm it): one row per payment_id. 100,914 rows.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| payment_id | int64 | 0.00% | 100,914 |
| subscription_id | int64 | 0.00% | 11,122 |
| payment_date | datetime64[ns] | 0.00% | 13,232 |
| amount_usd | float64 | 0.00% | 3 |
| method | object | 0.00% | 4 |

## Date ranges

- `payment_date`: 2025-01-01T00:00:00 to 2026-09-24T23:51:30

## Low-cardinality values

- `amount_usd`: 10.0 (59,064), 12.0 (37,384), 100.0 (4,466)
- `method`: card (50,237), paypal (20,272), apple_pay (15,298), google_pay (15,107)

## Meaning

Grain (inferred): one row per payment.

- `payment_id`: key.
- `subscription_id`: the subscription paid; joins many payments to one subscription, so it fans out if joined from subscriptions (inferred).
- `payment_date`: when the payment was made; starts 2025-01-01, so earlier history is missing.
- `amount_usd`: 10 and 12 are monthly plan payments, 100 are annual (inferred). 12 appears only from March 2026 (quirk: monthly price change).
- `method`: payment method (card, paypal, apple_pay, google_pay).
- Verdict: Proceed, from 2025-01 only.

