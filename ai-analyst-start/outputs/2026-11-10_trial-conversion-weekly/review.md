# Review: How is the 14-day trial converting since launch, and is it changing week over week?

**Date:** 2026-11-10
**Reviewed:** outputs/2026-11-10_trial-conversion-weekly/analysis.py
**Verdict:** Think on it

## The question
How the 14-day trial converts since launch and whether it changes week to week. The head of growth decides whether to keep the trial at 14 days or change its length.

## Mechanics
| Check | Result |
|---|---|
| Joins | `join_fan_out` for trials with users kept 2,073 of 2,073 rows. Trials with subscriptions kept 1,655 of 2,073 because it is an inner join and open trials have no subscription yet; no row grew. The script uses left joins, so no trial was dropped. |
| Grain | One row per trial and one trial per user. Rates are per trial. |
| Denominators | Recounted outside the script: 1,553 trials have ended by 2026-09-24, 828 converted, 53.3%; none of the 1,553 has an empty outcome. The 520 open trials are left out of the denominator. Counting them as failures would give 39.9%, which is the trap and is shown in the script. |
| Date boundaries | Matured trials are those started by 2026-09-10 (14 days before the end of the data). The week of 2026-09-07 has 160 of 260 trials matured; the two weeks after have none. The first week holds only 2026-08-01 and 08-02. |
| Filters | Conversion was checked both ways: `outcome` = converted and a paid subscription agree on all 2,073 trials, and every paid subscription starts on the trial end date. No subscription starts before its trial. |
| Parts and totals | `parts_sum_to_total` matched for country and device type (1,553 each). |
| Comparison and units | Each weekly rate is set against the overall rate in percentage points. The earlier-half against later-half change is in percentage points with a p-value. |

## Reasoning
- Right question: partly. The first half (how it converts, whether it changes) is answered. The decision is about trial length, and the data holds one length only.
- Outside the frame: no trial of another length exists in the data. Cancellations and their timing are the only length-related evidence. Also outside: how many cancelled trials would have converted with more or less time.
- So-what: conversion is flat at about 53% for every week that has matured. A drop in the latest weeks is an artefact of open trials, not a decline. The decision cannot be settled from this data alone, and no threshold was stated in the frame.

## Findings
1. **The data cannot compare trial lengths** (Caveat only): all 2,073 trials are 14 days. The result says conversion is stable at 14 days, not that 14 is the right length. The cancellation timing (none before day 4, then roughly even through day 13) does not point to a better length either.
2. **The most recent weeks are not known yet** (Caveat only): trials started 2026-09-11 or later (520 trials, 25% of all) have not reached day 14. The newest result covers trials started up to 2026-09-10; the week of 2026-09-07 is based on 160 of its 260 trials.
3. **The launch weekend drives the small apparent decline** (Small change, already in the script): the first two days of trials (88 trials) convert at 60.2%. The earlier half against later half shows -1.6 percentage points (p=0.52); without those two days it shows +0.1 percentage points (p=0.98). The sensitivity is in the script and the brief reports both.

## Changes made to analysis.py
None after the review. Finding 3 was already handled in the script before the review (a second test without the launch weekend), and cancellation timing already uses matured trials only.

## Not checked
- Whether Web (48.1%) against iOS (57.1%) and the US (56.7%) against EU (50.0%) differences are beyond chance; segments were not tested against each other.
- Why the launch weekend converts higher (novelty, promotion, or a different mix of users).
- Revenue per converted trial: converters split into 590 monthly and 238 annual plans, but their value was not compared.
- Whether cancellation on a given day depends on a reminder or billing prompt.
