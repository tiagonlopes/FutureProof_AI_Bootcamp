# user_activity_metrics

Grain (a guess from the data, confirm it): no id column found. 998 rows.

Grain (inferred): one row per calendar day, no gaps, no duplicate dates.

## Columns

| Name | Type | Null rate | Distinct |
| --- | --- | --- | --- |
| date | datetime64[ns] | 0.00% | 998 |
| dau | int64 | 0.00% | 842 |
| wau | int64 | 0.00% | 950 |
| mau | int64 | 0.00% | 985 |

## Date ranges

- `date`: 2024-01-01T00:00:00 to 2026-09-24T00:00:00

## Low-cardinality values

- None

## Meaning

- `date`: the day the metrics describe; daily, continuous from 2024-01-01 to 2026-09-24 (inferred).
- `dau`: users active that day (inferred).
- `wau`: users active in the trailing 7 days up to and including that date (inferred, since wau >= dau on every row).
- `mau`: users active in the trailing window ending that date (inferred as trailing 30 days; mau >= wau on every row). It is a rolling number on every day, not a calendar-month count. For a monthly figure use the value on the last day of the month, or say which convention is used. September 2026 is open (ends 2026-09-24).
- No user-level rows, so activity cannot be split by plan, trial or signup cohort from this table.
- Quirk: September 2025 jump in mau (see quirks.md).
- Verdict: Proceed, with the caveat that mau is a rolling window.
