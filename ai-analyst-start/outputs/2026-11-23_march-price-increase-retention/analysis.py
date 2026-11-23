"""Did the March 2026 monthly price rise hurt retention, and for whom?

Inputs: data/*.csv are verbatim results of the blocks in queries.sql, run through
the course-db MCP tool (execute_sql). This script does not read data/ at the repo
root and does not connect to the database. Run: poetry run python <this file>.
Pre = Oct 2025 to Mar 2026 (March churn is measured before the first $12 renewals bite);
post = Apr to Aug 2026. Sep 2026 is open and excluded. Sep 2025 spike is outside the pre window.
"""
from pathlib import Path
import pandas as pd
from helpers import charts, checks

RUN = Path(__file__).parent
d = RUN / "data"
plan = pd.read_csv(d / "monthly_churn_by_plan.csv", parse_dates=["month_start"])
price = pd.read_csv(d / "monthly_price_paid.csv")
seg = pd.read_csv(d / "segment_pre_post.csv")

print("Price paid on monthly plan:", price.groupby("amount_usd")["month"].agg(["min", "max"]).to_dict("index"))

plan["rate"] = plan.churned / plan.paid_at_month_start
w = plan.pivot(index="month_start", columns="plan", values="rate")
w.to_csv(d / "monthly_churn_rates.csv")
pre = plan[(plan.month_start >= "2025-10-01") & (plan.month_start <= "2026-03-01")]
post = plan[plan.month_start >= "2026-04-01"]
for p in ("monthly", "annual"):
    a = pre[pre.plan == p]; b = post[post.plan == p]
    ra, rb = a.churned.sum() / a.paid_at_month_start.sum(), b.churned.sum() / b.paid_at_month_start.sum()
    print(f"{p}: monthly churn {ra:.2%} pre vs {rb:.2%} post = {100*(rb-ra):+.2f} percentage points, {rb/ra-1:+.0%} relative")
m = pre[pre.plan == "monthly"].eval("churned/paid_at_month_start")
print(f"Pre-period monthly range {m.min():.2%} to {m.max():.2%}; post range "
      f"{post[post.plan=='monthly'].eval('churned/paid_at_month_start').min():.2%} to "
      f"{post[post.plan=='monthly'].eval('churned/paid_at_month_start').max():.2%}")

seg["post"] = seg.post.astype(str).str.lower() == "true"
pv = seg.pivot_table(index=["dim", "seg"], columns="post", values=["sub_months", "churned"]).reset_index()
pv.columns = ["dim", "seg", "churn_pre", "churn_post", "sm_pre", "sm_post"]
pv["rate_pre"] = pv.churn_pre / pv.sm_pre
pv["rate_post"] = pv.churn_post / pv.sm_post
pv["pp_change"] = 100 * (pv.rate_post - pv.rate_pre)
pv["rel_change"] = pv.rate_post / pv.rate_pre - 1
pv["multiple"] = pv.rate_post / pv.rate_pre
# Simple revenue view per month at the post-period base: $2 uplift on those who stay vs $12 on extra leavers
pv["monthly_base"] = pv.sm_post / 5
pv["extra_leavers_pm"] = (pv.rate_post - pv.rate_pre) * pv.monthly_base
pv["uplift_usd_pm"] = 2 * (pv.monthly_base * (1 - pv.rate_post))
pv["lost_usd_pm"] = 12 * pv.extra_leavers_pm
pv.round(4).to_csv(d / "segment_results.csv", index=False)
print(pv[["dim", "seg", "rate_pre", "rate_post", "pp_change", "multiple", "uplift_usd_pm", "lost_usd_pm"]].round(3).to_string(index=False))

for dim in ("country", "device", "tenure"):
    s = pv[pv.dim == dim]
    for col in ("sm_pre", "sm_post", "churn_pre", "churn_post"):
        tot = pv[pv.dim == "all"][col].iloc[0]
        print(dim, col, checks.parts_sum_to_total(s[col], tot)["summary"])
print(checks.date_boundaries(plan.assign(d=plan.month_start), "d")["summary"],
      "Sep 2026 excluded as open; scheduled future end_dates counted only when end_date is inside the month.")

ten = pv[pv.dim == "tenure"].set_index("seg").loc[["under 6 months", "6 to 12 months", "12 to 24 months", "over 24 months"]]
fig = charts.bar(list(ten.index), list(ten.pp_change.round(1)),
                 "Churn rose most for subscribers under 12 months, and least for 12 to 24 months",
                 highlight=["under 6 months", "6 to 12 months"], ylabel="percentage-point rise in monthly churn", source="subscriptions, users; monthly plan, Oct-Mar vs Apr-Aug")
charts.save(fig, RUN / "charts" / "churn_rise_by_tenure.png")
fig = charts.line([x.strftime("%Y-%m") for x in w.index[-14:]], {"Monthly plan": list(w.monthly[-14:] * 100), "Annual plan": list(w.annual[-14:] * 100)},
                  "Monthly-plan churn doubled from April 2026 while annual stayed flat", highlight="Monthly plan", ylabel="% churned in month", source="subscriptions")
charts.save(fig, RUN / "charts" / "monthly_churn.png")

# Cohort check: is the rise just the September 2025 spike cohort ageing?
co = pd.read_csv(d / "sep2025_cohort_check.csv")
co["post"] = co.post.astype(str).str.lower() == "true"
co["rate"] = co.churned / co.sub_months
for c, g in co.groupby("cohort"):
    a, b = g[~g.post].rate.iloc[0], g[g.post].rate.iloc[0]
    print(f"Cohort {c}: churn {a:.2%} pre vs {b:.2%} post = {100*(b-a):+.2f} percentage points")
print(checks.parts_sum_to_total(co[co.post].sub_months, seg[(seg.dim == "all") & seg.post].sub_months.iloc[0])["summary"])
