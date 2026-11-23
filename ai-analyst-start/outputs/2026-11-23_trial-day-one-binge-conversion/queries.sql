-- name: cancel_timing
-- Days from trial start to outcome for matured trials (started before 2026-09-10); shows cancellations only begin on day 4.
SELECT outcome, (outcome_at::date - started_at::date) AS days_to_outcome, COUNT(*) AS trials FROM trials WHERE started_at < DATE '2026-09-10' AND outcome IS NOT NULL GROUP BY 1,2 ORDER BY 1,2;

-- name: trial_count_check
-- Matured trials, distinct users and open trials in the window.
SELECT COUNT(*) AS trials, COUNT(DISTINCT user_id) AS users, COUNT(*) FILTER (WHERE outcome IS NULL) AS open FROM trials WHERE started_at < DATE '2026-09-10';

-- name: three_day
-- Per-trial sessions on day 1 (d0) and days 2 and 3 (d12), capped at 8, with trials and conversions per cell. Window closes before the first cancellation (day 4).
WITH s AS (SELECT t.trial_id, t.outcome,
  COUNT(*) FILTER (WHERE x.session_date::date - t.started_at::date = 0) AS d0,
  COUNT(*) FILTER (WHERE x.session_date::date - t.started_at::date IN (1,2)) AS d12
 FROM trials t LEFT JOIN sessions x ON x.user_id = t.user_id AND x.session_date >= t.started_at::date AND x.session_date < t.started_at::date + 3
 WHERE t.started_at < DATE '2026-09-10' GROUP BY 1,2)
SELECT LEAST(d0,8) AS d0, LEAST(d12,8) AS d12, COUNT(*) AS trials, COUNT(*) FILTER (WHERE outcome='converted') AS converted FROM s GROUP BY 1,2 ORDER BY 1,2;

-- name: week_survivors
-- Same on day 1 (d0) versus days 2 to 7 (d16, capped at 12), only trials still open on day 7 (outcome on day 7 or later), so early cancellers do not look quiet by construction.
WITH s AS (SELECT t.trial_id, t.outcome,
  COUNT(*) FILTER (WHERE x.session_date::date - t.started_at::date = 0) AS d0,
  COUNT(*) FILTER (WHERE x.session_date::date - t.started_at::date BETWEEN 1 AND 6) AS d16
 FROM trials t LEFT JOIN sessions x ON x.user_id = t.user_id AND x.session_date >= t.started_at::date AND x.session_date < t.started_at::date + 7
 WHERE t.started_at < DATE '2026-09-10' AND (t.outcome_at::date - t.started_at::date) >= 7 GROUP BY 1,2)
SELECT LEAST(d0,8) AS d0, LEAST(d16,12) AS d16, COUNT(*) AS trials, COUNT(*) FILTER (WHERE outcome='converted') AS converted FROM s GROUP BY 1,2 ORDER BY 1,2;
