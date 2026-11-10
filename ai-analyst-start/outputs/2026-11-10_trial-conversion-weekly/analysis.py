"""How is the 14-day trial converting since launch, and is it changing week over week?

Conversion = share of matured trials (ends_at on or before 2026-09-24) that ended in a paid subscription.
Run from the repo root: poetry run python outputs/<run>/analysis.py
"""

import math
from pathlib import Path

import pandas as pd

from helpers import charts, checks

RUN = Path("outputs/2026-11-10_trial-conversion-weekly")
(RUN / "data").mkdir(parents=True, exist_ok=True)
TODAY = pd.Timestamp("2026-09-24 23:59:59")  # the data ends on 2026-09-24

trials = pd.read_csv("data/trials.csv", parse_dates=["started_at", "ends_at", "outcome_at"])
subs = pd.read_csv("data/subscriptions.csv", parse_dates=["start_date", "end_date"])
users = pd.read_csv("data/users.csv")

# Checks on the inputs
print(checks.join_fan_out(trials, subs, on="user_id")["summary"])
print(checks.join_fan_out(trials, users, on="user_id")["summary"])
print(checks.date_boundaries(trials, "started_at", freq="W")["summary"])
print(f"Trial length in days: {sorted((trials.ends_at - trials.started_at).dt.days.unique())}")

# Conversion means a paid subscription starts. Confirm the outcome column agrees with the subscriptions table.
j = trials.merge(subs[["user_id", "plan", "start_date"]], on="user_id", how="left")
paid = j.plan.isin(["monthly", "annual"])
conv = j.outcome == "converted"
print(f"Outcome 'converted' and a paid subscription agree on {(conv == paid).mean():.1%} of all trials "
      f"({int((conv & ~paid).sum())} converted without a paid plan, {int((~conv & paid).sum())} paid without 'converted').")
print(f"Paid subscriptions start on the trial end date for {(j[paid].start_date == j[paid].ends_at).mean():.1%} of converted trials.")

# The trap: an open trial has an empty outcome. Show what each way of counting would say.
m = checks.matured_only(trials, "ends_at", as_of=TODAY)
print(m["summary"])
matured = m["kept"].copy()
matured["converted"] = matured.outcome == "converted"
trials["converted"] = trials.outcome == "converted"
print(f"Matured trials with an empty outcome: {int(matured.outcome.isna().sum())} (should be 0).")
open_trials = trials[trials.ends_at > TODAY]
print(f"Open trials: {len(open_trials):,}; of these {int(open_trials.outcome.notna().sum()):,} already show 'canceled' "
      f"(cancellations are recorded early; conversions only at day 14). 'converted' among them: "
      f"{int((open_trials.outcome == 'converted').sum())}.")

trials["week"] = trials.started_at.dt.to_period("W-SUN")
matured["week"] = matured.started_at.dt.to_period("W-SUN")


def ztest_p(c1, n1, c2, n2):
    """Two-sided two-proportion z test p value."""
    p = (c1 + c2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return float("nan") if se == 0 else math.erfc(abs(c2 / n2 - c1 / n1) / se / math.sqrt(2))


overall = matured.converted.mean()
n_all, c_all = len(matured), int(matured.converted.sum())

weekly = matured.groupby("week").agg(trials=("converted", "size"), converted=("converted", "sum"))
weekly["conversion"] = weekly.converted / weekly.trials
weekly["vs_overall_pp"] = (weekly.conversion - overall) * 100
weekly["change_vs_prior_week_pp"] = weekly.conversion.diff() * 100
all_weeks = trials.groupby("week").agg(started=("converted", "size"), converted_all=("converted", "sum"))
all_weeks["naive_conversion"] = all_weeks.converted_all / all_weeks.started
weekly = all_weeks.join(weekly, how="left").rename(columns={"trials": "matured_trials"})
weekly["share_matured"] = weekly.matured_trials / weekly.started
weekly.index = weekly.index.astype(str)
weekly.to_csv(RUN / "data" / "weekly_conversion.csv", index_label="week")

# Is it changing? Earlier half against later half of matured trials, by start date.
mid = matured.started_at.sort_values().iloc[len(matured) // 2]
first, second = matured[matured.started_at < mid], matured[matured.started_at >= mid]
trend = {
    "overall_conversion": overall, "matured_trials": n_all,
    "first_half_conversion": first.converted.mean(), "first_half_trials": len(first),
    "second_half_conversion": second.converted.mean(), "second_half_trials": len(second),
    "change_pp": (second.converted.mean() - first.converted.mean()) * 100,
    "p_value": ztest_p(int(first.converted.sum()), len(first), int(second.converted.sum()), len(second)),
}
# Sensitivity: drop the partial launch week (2026-08-01 and 08-02 only, the days right after launch).
core = matured[matured.started_at >= "2026-08-03"]
mid2 = core.started_at.sort_values().iloc[len(core) // 2]
f2, s2 = core[core.started_at < mid2], core[core.started_at >= mid2]
trend["change_pp_without_launch_weekend"] = (s2.converted.mean() - f2.converted.mean()) * 100
trend["p_value_without_launch_weekend"] = ztest_p(int(f2.converted.sum()), len(f2), int(s2.converted.sum()), len(s2))
pd.DataFrame([trend]).to_csv(RUN / "data" / "trend_first_vs_second_half.csv", index=False)

# Segments
matured = matured.merge(users[["user_id", "country", "device_type"]], on="user_id", how="left")
matured = matured.merge(subs[["user_id", "plan"]], on="user_id", how="left")
seg_rows = []
for dim in ["country", "device_type"]:
    g = matured.groupby(dim).agg(trials=("converted", "size"), converted=("converted", "sum"))
    print(f"{dim}:", checks.parts_sum_to_total(g.trials, n_all)["summary"])
    for val, r in g.iterrows():
        seg_rows.append({"dimension": dim, "segment": val, "trials": int(r.trials), "converted": int(r.converted),
                         "conversion": r.converted / r.trials, "vs_overall_pp": (r.converted / r.trials - overall) * 100})
seg = pd.DataFrame(seg_rows)
seg.to_csv(RUN / "data" / "segment_conversion.csv", index=False)

# What converters buy, and when cancellations happen
plan_mix = matured[matured.converted].plan.value_counts()
plan_mix.to_csv(RUN / "data" / "plan_of_converters.csv", header=["trials"])
# Matured trials only: open trials show only their early cancellations, which would skew the timing.
canc = matured[matured.outcome == "canceled"].copy()
canc["days_to_cancel"] = (canc.outcome_at - canc.started_at).dt.days
timing = canc.days_to_cancel.value_counts().sort_index().rename("cancellations")
timing.to_csv(RUN / "data" / "days_to_cancel.csv", header=True, index_label="days_since_start")
print(f"Cancellations by day since start: median {canc.days_to_cancel.median():.0f}, "
      f"earliest day {int(canc.days_to_cancel.min())}, share on days 0 to 6 {(canc.days_to_cancel <= 6).mean():.0%}, on days 7 to 13 {(canc.days_to_cancel >= 7).mean():.0%}.")

# Charts
x = list(weekly.index)
fig = charts.line(
    [w[5:10] for w in x],
    {"Matured trials": (weekly.conversion * 100).round(1).tolist(),
     "All trials (wrong)": (weekly.naive_conversion * 100).round(1).tolist()},
    "Counting open trials makes conversion look like it collapsed; matured trials are flat",
    highlight="Matured trials", ylabel="Trials ending in a paid plan (%)",
    source="Weeks start on the date shown (Monday; first week starts 08-01). Matured = ends_at on or before 2026-09-24")
charts.save(fig, RUN / "charts" / "weekly_conversion.png")

t = timing.reindex(range(0, 14), fill_value=0)
fig = charts.bar([str(d) for d in t.index], t.tolist(),
                 "Cancellations are spread evenly from day 4 to day 13; none happen in days 0 to 3",
                 highlight=None, ylabel="Cancellations",
                 source="Days from trial start to cancellation, matured canceled trials")
charts.save(fig, RUN / "charts" / "days_to_cancel.png")

# Headline
print(f"\nMatured trials: {n_all:,}; converted {c_all:,} = {overall:.1%}. Comparison: the naive rate over all "
      f"{len(trials):,} trials is {trials.converted.mean():.1%} (counts {len(trials) - n_all:,} open trials as failures).")
print(f"Earlier half {trend['first_half_conversion']:.1%} (n={trend['first_half_trials']:,}) vs later half "
      f"{trend['second_half_conversion']:.1%} (n={trend['second_half_trials']:,}): change {trend['change_pp']:+.1f} percentage points, p={trend['p_value']:.2f}.")
print(f"Without the launch weekend: change {trend['change_pp_without_launch_weekend']:+.1f} percentage points, "
      f"p={trend['p_value_without_launch_weekend']:.2f}.")
print(f"Plan chosen by converters: {plan_mix.to_dict()}")
print(weekly[["started", "matured_trials", "share_matured", "naive_conversion", "conversion",
              "vs_overall_pp", "change_vs_prior_week_pp"]].round(3).to_string())
print(seg.round(3).to_string(index=False))
