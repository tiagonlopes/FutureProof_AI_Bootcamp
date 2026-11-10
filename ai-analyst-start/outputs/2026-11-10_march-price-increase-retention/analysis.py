"""Did the March 2026 monthly price rise ($10 to $12) raise churn, and for whom?

Churn = cancellations in a month / monthly subscribers active at the start of it.
Run from the repo root: poetry run python outputs/<run>/analysis.py
"""

import math
from pathlib import Path

import pandas as pd

from helpers import charts, checks

RUN = Path("outputs/2026-11-10_march-price-increase-retention")
(RUN / "data").mkdir(parents=True, exist_ok=True)
TODAY = pd.Timestamp("2026-09-24")
OLD_PRICE, NEW_PRICE = 10, 12
BREAK_EVEN = NEW_PRICE / OLD_PRICE  # steady state: lifetime revenue = price / churn

subs = pd.read_csv("data/subscriptions.csv", parse_dates=["start_date", "end_date"])
users = pd.read_csv("data/users.csv", parse_dates=["signup_date"])
pay = pd.read_csv("data/payments.csv", parse_dates=["payment_date"])

# Checks on the inputs
print(checks.join_fan_out(subs, users, on="user_id")["summary"])
monthly = subs[(subs.plan == "monthly") & (subs.start_date <= TODAY)].copy()
print(f"Monthly plan rows used: {len(monthly):,} of {(subs.plan == 'monthly').sum():,} "
      f"(scheduled starts after {TODAY.date()} excluded).")
print(checks.date_boundaries(monthly, "start_date")["summary"])
monthly = monthly.merge(users[["user_id", "country", "device_type"]], on="user_id", how="left")

# Did the new price reach existing subscribers? Share of monthly payments at $12 by month.
mp = pay.merge(subs[["subscription_id", "plan", "start_date"]], on="subscription_id")
mp = mp[mp.plan == "monthly"]
mp["month"] = mp.payment_date.dt.to_period("M")
price_share = mp.assign(new=mp.amount_usd == NEW_PRICE).groupby("month").new.mean()
before_mar = price_share[price_share.index < pd.Period("2026-03")].max()
after_mar = price_share[price_share.index >= pd.Period("2026-03")].min()
existing = mp[(mp.payment_date >= "2026-03-01") & (mp.start_date < "2026-03-01")]
print(f"Share of monthly payments at ${NEW_PRICE}: at most {before_mar:.0%} before March 2026, "
      f"at least {after_mar:.0%} from March. Among subscribers who started before March, "
      f"{(existing.amount_usd == NEW_PRICE).mean():.0%} of March-on payments were at ${NEW_PRICE}.")

# Person-month panel: one row per monthly subscriber active at the start of a closed month.
months = pd.period_range("2025-01", "2026-08", freq="M")  # Sept 2026 is still open
rows = []
for m in months:
    start, end = m.start_time, m.end_time
    act = monthly[(monthly.start_date < start) & (monthly.end_date.isna() | (monthly.end_date >= start))].copy()
    act["month"] = m
    act["churned"] = (act.end_date >= start) & (act.end_date <= end)
    months_in = (start - act.start_date).dt.days / 30.44
    act["tenure"] = pd.cut(months_in, [-1, 3, 12, 1e9], labels=["under 3 months", "3 to 12 months", "over 12 months"])
    act["cohort"] = act.start_date.dt.to_period("M").eq(pd.Period("2025-09")).map(
        {True: "Sept 2025 signups", False: "other signups"})
    rows.append(act[["month", "churned", "country", "device_type", "tenure", "cohort"]])
panel = pd.concat(rows, ignore_index=True)

PRE = (pd.Period("2025-10"), pd.Period("2026-02"))
# March 2026 is a transition month: its renewals were the first at $12, and the cancellations
# that follow land in April. It is left out of both windows and shown as a sensitivity below.
POST = (pd.Period("2026-04"), pd.Period("2026-08"))
EARLY = (pd.Period("2025-01"), pd.Period("2025-08"))


def window(df, w):
    return df[(df.month >= w[0]) & (df.month <= w[1])]


def rate(df):
    return 1000 * df.churned.sum() / len(df)


def ztest_p(c1, n1, c2, n2):
    """Two-sided two-proportion z test p value."""
    p = (c1 + c2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return float("nan")
    return math.erfc(abs(c2 / n2 - c1 / n1) / se / math.sqrt(2))


def compare(df):
    pre, post, early = window(df, PRE), window(df, POST), window(df, EARLY)
    r_pre, r_post = rate(pre), rate(post)
    return {
        "active_months_pre": len(pre), "active_months_post": len(post),
        "churn_per_1000_early_2025": rate(early) if len(early) else float("nan"),
        "churn_per_1000_pre": r_pre, "churn_per_1000_post": r_post,
        "change_per_1000": r_post - r_pre,
        "ratio_post_to_pre": r_post / r_pre if r_pre else float("nan"),
        "p_value": ztest_p(pre.churned.sum(), len(pre), post.churned.sum(), len(post)),
    }


# Monthly series
series = panel.groupby("month").agg(active=("churned", "size"), churned=("churned", "sum"))
series["churn_per_1000"] = 1000 * series.churned / series.active
series.to_csv(RUN / "data" / "monthly_churn_series.csv")

overall = compare(panel)
pd.DataFrame([overall]).to_csv(RUN / "data" / "overall_pre_post.csv", index=False)

seg_rows = []
for dim in ["country", "device_type", "tenure", "cohort"]:
    for val, g in panel.groupby(dim, observed=True):
        res = compare(g)
        res.update(dimension=dim, segment=str(val))
        seg_rows.append(res)
seg = pd.DataFrame(seg_rows)
seg["beyond_break_even"] = seg.ratio_post_to_pre > BREAK_EVEN
seg["distinguishable_from_noise"] = seg.p_value < 0.05
seg["rollback_candidate"] = seg.beyond_break_even & seg.distinguishable_from_noise
seg = seg[["dimension", "segment"] + [c for c in seg.columns if c not in ("dimension", "segment")]]
seg.to_csv(RUN / "data" / "segment_pre_post.csv", index=False)

# Cancellations beyond what the pre rate would have produced, in the post window
post = window(panel, POST)
expected = rate(window(panel, PRE)) / 1000 * len(post)
extra = post.churned.sum() - expected
pd.DataFrame([{"post_cancellations": int(post.churned.sum()), "expected_at_pre_rate": expected,
               "extra_cancellations": extra, "post_active_months": len(post)}]).to_csv(
    RUN / "data" / "extra_cancellations.csv", index=False)

# Checks on the output
for dim in ["country", "device_type", "tenure", "cohort"]:
    parts = [int(window(g, POST).churned.sum()) for _, g in panel.groupby(dim, observed=True)]
    print(f"{dim}:", checks.parts_sum_to_total(parts, int(post.churned.sum()))["summary"])
print(f"Panel covers {months[0]} to {months[-1]}; {pd.Period('2026-09')} is excluded because it is still open "
      f"(data ends {TODAY.date()}).")

# Charts
x = [str(m) for m in series.index]
fig = charts.line(x, {"Monthly churn per 1,000": series.churn_per_1000.round(1).tolist()},
                  "Monthly churn on the monthly plan rose after the March 2026 price increase",
                  highlight="Monthly churn per 1,000",
                  ylabel="Cancellations per 1,000 active subscribers",
                  source="Source: data/subscriptions.csv, monthly plan; Sept 2026 excluded (open)")
fig.axes[0].axvline(x.index("2026-03"), color="#999999", linestyle="--")
fig.axes[0].set_xticks(range(0, len(x), 2))
fig.axes[0].set_xticklabels(x[::2], rotation=45, ha="right")
charts.save(fig, RUN / "charts" / "monthly_churn.png")

plot = seg[seg.dimension.isin(["country", "tenure", "cohort"])].copy()
plot["label"] = plot.segment
plot = plot.sort_values("ratio_post_to_pre", ascending=False)
fig = charts.bar(plot.label.tolist(), (plot.ratio_post_to_pre * 100).tolist(),
                 "Every segment's churn more than doubled; roll-back pays above the dashed 120",
                 highlight=None, horizontal=True,
                 source="Index: pre-increase churn = 100. Pre = Oct 2025 to Feb 2026, post = Apr to Aug 2026 (Mar is transition)")
fig.axes[0].axvline(BREAK_EVEN * 100, color="#333333", linestyle="--")
charts.save(fig, RUN / "charts" / "churn_index_by_segment.png")

# Control group: the annual plan was not repriced, so its churn shows what happened without the increase.
annual = subs[(subs.plan == "annual") & (subs.start_date <= TODAY)]
ann_rows = []
for m in months:
    start, end = m.start_time, m.end_time
    act = annual[(annual.start_date < start) & (annual.end_date.isna() | (annual.end_date >= start))]
    ann_rows.append({"month": m, "active": len(act),
                     "churned": int(((act.end_date >= start) & (act.end_date <= end)).sum())})
ann = pd.DataFrame(ann_rows)
ann.to_csv(RUN / "data" / "annual_control_series.csv", index=False)


def ann_rate(w):
    a = ann[(ann.month >= w[0]) & (ann.month <= w[1])]
    return 1000 * a.churned.sum() / a.active.sum()


a_pre, a_post = ann_rate(PRE), ann_rate(POST)
pd.DataFrame([{"annual_pre_per_1000": a_pre, "annual_post_per_1000": a_post,
               "annual_ratio": a_post / a_pre, "monthly_ratio": overall["ratio_post_to_pre"]}]).to_csv(
    RUN / "data" / "annual_control.csv", index=False)
print(f"Control, annual plan churn per 1,000 per month: pre {a_pre:.1f}, post {a_post:.1f}, "
      f"index {a_post / a_pre * 100:.0f} (monthly plan index {overall['ratio_post_to_pre'] * 100:.0f}).")

# Headline
print(f"\nBreak-even index: {BREAK_EVEN * 100:.0f} (steady state: lifetime revenue = price / churn).")
print(f"Overall monthly churn per 1,000: pre {overall['churn_per_1000_pre']:.1f}, post {overall['churn_per_1000_post']:.1f}, "
      f"early 2025 {overall['churn_per_1000_early_2025']:.1f}; "
      f"relative change {overall['ratio_post_to_pre'] - 1:+.1%}; p={overall['p_value']:.3g}")
late = window(panel, (pd.Period("2026-03"), pd.Period("2026-08")))
print(f"Sensitivity, March included in post: churn per 1,000 {rate(late):.1f}, index {rate(late) / overall['churn_per_1000_pre'] * 100:.0f}.")
print(f"March 2026 alone: {rate(panel[panel.month == pd.Period('2026-03')]):.1f} per 1,000.")
print(f"Extra cancellations in Apr to Aug 2026 against the pre rate: {extra:,.0f} "
      f"of {int(post.churned.sum()):,}.")
print(seg[["dimension", "segment", "churn_per_1000_pre", "churn_per_1000_post", "ratio_post_to_pre",
           "p_value", "rollback_candidate"]].round(3).to_string(index=False))
