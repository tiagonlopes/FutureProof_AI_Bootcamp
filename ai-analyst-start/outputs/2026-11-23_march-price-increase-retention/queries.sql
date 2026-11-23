-- name: monthly_churn_by_plan
-- Paid subscriptions active at each month start and those that ended in the month, by plan, Jan 2025 to Aug 2026.
WITH months AS (SELECT generate_series(DATE '2025-01-01', DATE '2026-08-01', INTERVAL '1 month')::date AS month_start)
SELECT m.month_start, s.plan,
  COUNT(*) AS paid_at_month_start,
  COUNT(*) FILTER (WHERE s.end_date < m.month_start + INTERVAL '1 month') AS churned
FROM months m JOIN subscriptions s ON s.plan IN ('monthly','annual') AND s.start_date < m.month_start AND (s.end_date IS NULL OR s.end_date >= m.month_start)
GROUP BY 1,2 ORDER BY 1,2;

-- name: monthly_price_paid
-- Monthly-plan payment amounts per month, to confirm what the increase was.
SELECT DATE_TRUNC('month', p.payment_date)::date AS month, s.plan, p.amount_usd, COUNT(*) AS payments
FROM payments p JOIN subscriptions s ON s.subscription_id = p.subscription_id
WHERE s.plan='monthly' AND p.payment_date >= DATE '2026-01-01'
GROUP BY 1,2,3 ORDER BY 1,3;

-- name: segment_pre_post
-- Monthly-plan subscriber-months and churn by segment; pre = Oct 2025 to Mar 2026, post = Apr to Aug 2026 (Sep 2026 is open and excluded).
WITH months AS (SELECT generate_series(DATE '2025-10-01', DATE '2026-08-01', INTERVAL '1 month')::date AS month_start),
base AS (
 SELECT m.month_start, u.country, u.device_type,
  CASE WHEN m.month_start - s.start_date < INTERVAL '6 months' THEN 'under 6 months'
       WHEN m.month_start - s.start_date < INTERVAL '12 months' THEN '6 to 12 months'
       WHEN m.month_start - s.start_date < INTERVAL '24 months' THEN '12 to 24 months'
       ELSE 'over 24 months' END AS tenure_band,
  (s.end_date < m.month_start + INTERVAL '1 month')::int AS churned
 FROM months m JOIN subscriptions s ON s.plan='monthly' AND s.start_date < m.month_start AND (s.end_date IS NULL OR s.end_date >= m.month_start)
 JOIN users u ON u.user_id = s.user_id)
SELECT 'country' AS dim, country AS seg, (month_start >= DATE '2026-04-01') AS post, COUNT(*) AS sub_months, SUM(churned) AS churned FROM base GROUP BY 1,2,3
UNION ALL SELECT 'device', device_type, (month_start >= DATE '2026-04-01'), COUNT(*), SUM(churned) FROM base GROUP BY 1,2,3
UNION ALL SELECT 'tenure', tenure_band, (month_start >= DATE '2026-04-01'), COUNT(*), SUM(churned) FROM base GROUP BY 1,2,3
UNION ALL SELECT 'all', 'all', (month_start >= DATE '2026-04-01'), COUNT(*), SUM(churned) FROM base GROUP BY 1,2,3
ORDER BY 1,2,3;

-- name: sep2025_cohort_check
-- Monthly-plan subscriber-months and churn for the September 2025 signup-spike cohort versus everyone else, pre and post.
WITH months AS (SELECT generate_series(DATE '2025-10-01', DATE '2026-08-01', INTERVAL '1 month')::date AS month_start)
SELECT CASE WHEN s.start_date >= DATE '2025-09-01' AND s.start_date < DATE '2025-10-01' THEN 'sep2025_cohort' ELSE 'other' END AS cohort,
 (m.month_start >= DATE '2026-04-01') AS post, COUNT(*) AS sub_months,
 COUNT(*) FILTER (WHERE s.end_date < m.month_start + INTERVAL '1 month') AS churned
FROM months m JOIN subscriptions s ON s.plan='monthly' AND s.start_date < m.month_start AND (s.end_date IS NULL OR s.end_date >= m.month_start)
GROUP BY 1,2 ORDER BY 1,2;
