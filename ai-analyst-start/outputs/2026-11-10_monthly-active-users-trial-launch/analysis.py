"""Is engagement growing, and what happened around the trial launch? Run from the repo root."""
from pathlib import Path

import pandas as pd

from helpers import charts
from helpers.checks import date_boundaries, join_fan_out, matured_only, parts_sum_to_total

RUN = Path("outputs/2026-11-10_monthly-active-users-trial-launch")
(RUN / "data").mkdir(parents=True, exist_ok=True)
AS_OF = pd.Timestamp("2026-09-24")
LAUNCH = pd.Timestamp("2026-08-01")

act = pd.read_csv("data/user_activity_metrics.csv", parse_dates=["date"])
users = pd.read_csv("data/users.csv", parse_dates=["signup_date"])
trials = pd.read_csv("data/trials.csv", parse_dates=["started_at", "ends_at", "outcome_at"])
subs = pd.read_csv("data/subscriptions.csv", parse_dates=["start_date", "end_date"])

# --- checks
print("CHECK", date_boundaries(act, "date")["summary"])
print("CHECK", date_boundaries(users, "signup_date")["summary"])
fan = join_fan_out(trials, users, on="user_id")
print("CHECK", fan["summary"])

# --- monthly active users: mau is a rolling figure, so take the last day of each month
act["month"] = act["date"].dt.to_period("M")
m = act.groupby("month").agg(
    mau=("mau", "last"), last_day=("date", "max"), dau_avg=("dau", "mean")
)
m["days_in_data"] = act.groupby("month")["date"].count()
m["complete"] = m["last_day"] == m.index.to_timestamp(how="end").normalize()
m["dau_to_mau"] = m["dau_avg"] / m["mau"]
m["mom_change"] = m["mau"].diff()
m["mom_pct"] = m["mau"].pct_change() * 100
m["yoy_pct"] = m["mau"].pct_change(12) * 100
m.reset_index().to_csv(RUN / "data/mau_monthly.csv", index=False)
closed = m[m["complete"]]
print("CHECK closed months:", len(closed), "last closed:", closed.index[-1], "open:", list(m.index[~m["complete"]]))

aug26, aug25, aug24 = closed.loc["2026-08", "mau"], closed.loc["2025-08", "mau"], closed.loc["2024-08", "mau"]
print(f"HEADLINE MAU end Aug 2026 {aug26:,} vs end Aug 2025 {aug25:,}: {(aug26/aug25-1)*100:.1f}% relative (YoY); "
      f"end Aug 2025 vs end Aug 2024 {aug24:,}: {(aug25/aug24-1)*100:.1f}% relative")
jan24 = closed.iloc[0]["mau"]
print(f"HEADLINE first closed month {closed.index[0]} {jan24:,} -> Aug 2026 {aug26:,}: {(aug26/jan24-1)*100:.0f}% relative")

# --- September 2025 anomaly: growth with and without the step
step = closed.loc["2025-09", "mom_change"]
pre = closed.loc["2024-02":"2025-08", "mom_change"].mean()
post = closed.loc["2025-10":"2026-07", "mom_change"].mean()
print(f"ANOMALY Sep 2025 MAU change {step:,.0f} vs avg monthly change before {pre:,.0f} and after (Oct25-Jul26) {post:,.0f}")
print(f"ANOMALY YoY Aug 2026 vs Aug 2025 is mostly the step: Sep 2025 step excess over trend = {step-pre:,.0f} of the {aug26-aug25:,} gain")
print(f"ANOMALY DAU/MAU ratio avg before Sep 2025 {closed.loc['2025-01':'2025-08','dau_to_mau'].mean():.3f}, "
      f"Oct25-Jul26 {closed.loc['2025-10':'2026-07','dau_to_mau'].mean():.3f}, Aug 2026 {closed.loc['2026-08','dau_to_mau']:.3f}")

# --- trial launch: monthly change vs the pre-launch baseline (post-spike months, same era)
base = closed.loc["2025-10":"2026-07", "mom_change"]
print(f"LAUNCH MAU change Aug 2026 {closed.loc['2026-08','mom_change']:,.0f} vs Oct25-Jul26 avg {base.mean():,.0f} "
      f"(range {base.min():,.0f} to {base.max():,.0f}); Jul 2026 {closed.loc['2026-07','mom_change']:,.0f}")
sep = m.loc["2026-09"]
print(f"LAUNCH Sep 2026 (open, to 24th) MAU {sep['mau']:,} change vs end Aug {sep['mau']-aug26:,} over {int(sep['days_in_data'])} days "
      f"(avg change in {int(sep['days_in_data'])}-day slices pre-launch not comparable; treat as open)")
daily = act.set_index("date")["mau"]
print("LAUNCH daily MAU growth per day: 2026-06-01..07-31 "
      f"{(daily['2026-07-31']-daily['2026-06-01'])/60:,.1f}; 2026-08-01..08-31 {(daily['2026-08-31']-daily['2026-07-31'])/31:,.1f}; "
      f"2026-09-01..09-24 {(daily['2026-09-24']-daily['2026-08-31'])/24:,.1f}")

# --- signups and trials by month
users["month"] = users["signup_date"].dt.to_period("M")
signups = users.groupby("month").size().rename("signups")
trials["month"] = trials["started_at"].dt.to_period("M")
tstart = trials.groupby("month").size().rename("trials_started")
sig = pd.concat([signups, tstart], axis=1).fillna(0).astype(int)
sig = sig.loc[sig.index <= pd.Period("2026-09")]
sig["mau_end"] = m["mau"]
sig.reset_index().to_csv(RUN / "data/signups_trials_monthly.csv", index=False)
pre_sig = sig.loc["2026-01":"2026-07", "signups"]
nt = sig["signups"] - sig["trials_started"]
print(f"SIGNUPS non-trial Aug 2026 {nt.loc['2026-08']:,} vs Jan-Jul 2026 avg {nt.loc['2026-01':'2026-07'].mean():,.0f}")
print(f"SIGNUPS Aug 2026 {sig.loc['2026-08','signups']:,} vs Jan-Jul 2026 avg {pre_sig.mean():,.0f}; "
      f"Jul 2026 {sig.loc['2026-07','signups']:,}; Sep 2026 (open, to 24th) {sig.loc['2026-09','signups']:,}")
print(f"TRIALS started Aug 2026 {sig.loc['2026-08','trials_started']:,}, Sep 2026 (to 24th) {sig.loc['2026-09','trials_started']:,}")
tu = trials.merge(users[["user_id", "signup_date"]], on="user_id")
new_signup = (tu["signup_date"].dt.normalize() >= tu["started_at"].dt.normalize() - pd.Timedelta(days=1)).mean()
print(f"TRIALS share whose user signed up on/within a day before trial start: {new_signup:.0%}")

# --- weekly signups split: did non-trial signups move at the launch too?
users["has_trial"] = users["user_id"].isin(trials["user_id"])
wsig = users[users["signup_date"] >= "2026-05-04"].groupby(
    [users["signup_date"].dt.to_period("W").dt.start_time, "has_trial"]).size().unstack(fill_value=0)
wsig.columns = ["non_trial_signups", "trial_signups"]
wsig.reset_index().to_csv(RUN / "data/weekly_signups_split.csv", index=False)
full = wsig.loc[wsig.index <= "2026-09-14"]  # complete weeks only (week of 09-21 is partial)
print(f"WEEKLY non-trial signups per full week: May-Jul 2026 avg {full.loc[:'2026-07-20','non_trial_signups'].mean():.0f}; "
      f"Aug 3-Sep 14 avg {full.loc['2026-08-03':,'non_trial_signups'].mean():.0f}; trial signups Aug 3-Sep 14 avg {full.loc['2026-08-03':,'trial_signups'].mean():.0f}")
print(f"CHECK every closed month had a positive MAU change since {closed.index[1]}: {bool((closed['mom_change'].dropna() > 0).all())}")

# --- trial outcomes: matured only
mat = matured_only(trials, "ends_at", as_of=AS_OF)
print("CHECK", mat["summary"])
t = mat["kept"].copy()
t_out = t["outcome"].value_counts()
print("CHECK matured trials with empty outcome:", int(t["outcome"].isna().sum()))
tot = len(t)
conv = (t["outcome"] == "converted").sum()
print(f"TRIALS matured {tot:,}; converted {conv:,} = {conv/tot*100:.1f}%; canceled {(t['outcome']=='canceled').sum():,} = {(t['outcome']=='canceled').sum()/tot*100:.1f}%. "
      "No comparison available: trials did not exist before 2026-08-01.")
pc = parts_sum_to_total(t_out.values, tot)
print("CHECK", pc["summary"])
t["week"] = t["started_at"].dt.to_period("W").dt.start_time
wk = t.groupby("week").agg(trials=("trial_id", "size"), converted=("outcome", lambda s: (s == "converted").sum()))
wk["conv_rate_pct"] = wk["converted"] / wk["trials"] * 100
wk.reset_index().to_csv(RUN / "data/trial_conversion_weekly.csv", index=False)

# --- paid subs from trials vs paid subs starting otherwise (where did new paid users come from)
subs_ok = subs[subs["start_date"] <= AS_OF].copy()
subs_ok["month"] = subs_ok["start_date"].dt.to_period("M")
subs_ok["from_trial"] = subs_ok["user_id"].isin(trials["user_id"])
paid = subs_ok[subs_ok["plan"] != "free"]
pm = paid.groupby(["month", "from_trial"]).size().unstack(fill_value=0)
pm.columns = ["not_from_trial", "from_trial"] if list(pm.columns) == [False, True] else pm.columns
pm = pm.loc["2026-01":"2026-09"]
pm.reset_index().to_csv(RUN / "data/paid_starts_monthly.csv", index=False)
print("PAID starts by month (not from trial / from trial):")
print(pm.to_string())
print("CHECK", join_fan_out(subs, users, on="user_id")["summary"])

# --- charts
x = [str(p) for p in closed.index]
fig = charts.line(x, {"MAU (month-end)": closed["mau"].tolist()},
                  "Monthly actives have grown every month, with one step up in September 2025",
                  highlight="MAU (month-end)", ylabel="Monthly active users",
                  source="Source: user_activity_metrics, mau on last day of each closed month")
ax = fig.axes[0]
ax.set_xticks(range(0, len(x), 3))
ax.set_xticklabels(x[::3], rotation=45)
charts.save(fig, RUN / "charts/mau_trend.png")

rec = closed.loc["2025-10":"2026-09", "mom_change"]
rec_x = [str(p) for p in rec.index]
fig = charts.bar(rec_x, rec.tolist(),
                 "August 2026, the trial launch month, added far more actives than any month before it",
                 highlight="2026-08", ylabel="Change in MAU over the month",
                 source="Source: user_activity_metrics; closed months only, September 2026 is open")
fig.axes[0].tick_params(axis="x", rotation=45)
charts.save(fig, RUN / "charts/mau_monthly_change.png")
print("DONE")
