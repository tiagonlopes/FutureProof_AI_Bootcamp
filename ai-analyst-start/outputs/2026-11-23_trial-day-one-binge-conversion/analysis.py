"""Do trial users who binge on day one and then go quiet convert worse than steady users?

Inputs: data/*.csv are verbatim results of the blocks in queries.sql, run through the
course-db MCP tool (execute_sql). This script does not read the repo-level data/ and does
not connect to the database. Run: poetry run python <this file>.
Window: trials started 2026-08-01 to 2026-09-09 (all matured, none open). Session counts
are capped at 8 (3-day table) and 12 (week table), so '8' means 8 or more.
Working definitions (open in the frame):
  binge  = 8+ sessions on day 1 ; quiet = 0 to 2 sessions on days 2 and 3 ;
  steady = 1 to 5 sessions on day 1 and 3+ on days 2 and 3 ;
  low-start = 0 to 3 sessions on day 1 and 0 to 2 on days 2 and 3 (quiet without a binge).
"""
from pathlib import Path
import math
import pandas as pd
from helpers import charts, checks

RUN = Path(__file__).parent
d = RUN / "data"
t3 = pd.read_csv(d / "three_day.csv")
wk = pd.read_csv(d / "week_survivors.csv")
ct = pd.read_csv(d / "cancel_timing.csv")

print("Cancellation timing:", f"first cancellation on day {ct[ct.outcome=='canceled'].days_to_outcome.min()}")
print(checks.parts_sum_to_total([t3.trials.sum()], 1516)["summary"], "(trials in window from the count query)")
overall = t3.converted.sum() / t3.trials.sum()
print(f"All matured trials: {t3.trials.sum():,}, conversion {overall:.1%}")


def wilson(k, n, z=1.96):
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def grp(df, mask, a, b):
    g = df[mask(df)]
    n, k = int(g.trials.sum()), int(g.converted.sum())
    lo, hi = wilson(k, n)
    return {"group": a, "trials": n, "converted": k, "rate": k / n, "ci_low": lo, "ci_high": hi}


def table(df, early, late, tag, binge_min=8, quiet_max=2):
    groups = [
        grp(df, lambda x: (x[early] >= binge_min) & (x[late] <= quiet_max), "Binge then quiet", tag),
        grp(df, lambda x: (x[early] >= binge_min) & (x[late] > quiet_max), "Binge and keep going", tag),
        grp(df, lambda x: x[early].between(1, 5) & (x[late] >= 3), "Steady", tag),
        grp(df, lambda x: (x[early] <= 3) & (x[late] <= quiet_max), "Low start, quiet", tag),
    ]
    out = pd.DataFrame(groups)
    out["window"] = tag
    return out


r3 = table(t3, "d0", "d12", "first 3 days")
# Week window: quiet = 0 to 6 sessions across days 2 to 7 (scaled to the longer window); steady = 7+
rw = table(wk, "d0", "d16", "first 7 days, trials open on day 7", quiet_max=6)
g = wk[wk.d0.between(1, 5) & (wk.d16 >= 7)]
rw.loc[rw.group == "Steady", ["trials", "converted"]] = [int(g.trials.sum()), int(g.converted.sum())]
rw["rate"] = rw.converted / rw.trials
rw[["ci_low", "ci_high"]] = [wilson(k, n) for k, n in zip(rw.converted, rw.trials)]
res = pd.concat([r3, rw])
res.round(4).to_csv(d / "group_results.csv", index=False)
print(res.round(3).to_string(index=False))

for w, df in res.groupby("window", sort=False):
    bq = df[df.group == "Binge then quiet"].iloc[0]
    for other in ("Steady", "Binge and keep going", "Low start, quiet"):
        o = df[df.group == other].iloc[0]
        print(f"[{w}] Binge then quiet {bq.rate:.1%} vs {other} {o.rate:.1%}: {100*(bq.rate-o.rate):+.1f} percentage points, {bq.rate/o.rate-1:+.0%} relative")
    print(f"[{w}] Binge-then-quiet CI {bq.ci_low:.1%} to {bq.ci_high:.1%}; Steady CI {df[df.group=='Steady'].iloc[0].ci_low:.1%} to {df[df.group=='Steady'].iloc[0].ci_high:.1%}")

# Sensitivity: day-one bucket by follow-up bucket, 3-day window
t3["d1_band"] = pd.cut(t3.d0, [-1, 0, 3, 7, 8], labels=["0", "1-3", "4-7", "8+"])
t3["follow_band"] = pd.cut(t3.d12, [-1, 2, 5, 8], labels=["0-2", "3-5", "6+"])
sens = t3.groupby(["d1_band", "follow_band"], observed=True)[["trials", "converted"]].sum()
sens["rate"] = sens.converted / sens.trials
sens.round(4).to_csv(d / "day1_by_follow_up.csv")
print(sens.round(3).to_string())
print(checks.parts_sum_to_total([sens.trials.sum()], t3.trials.sum())["summary"])

fig = charts.bar(list(r3.group), list(r3.rate * 100),
                 "Binge-then-quiet trials convert about a third as often as steady ones",
                 highlight="Binge then quiet", ylabel="% of trials converted",
                 source="trials, sessions; 1,516 matured trials, first 3 days")
charts.save(fig, RUN / "charts" / "conversion_by_pattern.png")
