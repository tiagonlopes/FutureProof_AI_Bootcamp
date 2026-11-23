# AI Analyst

An AI data analyst that runs inside Claude Code and answers business questions about Beam's data. Beam is a media app where users browse, listen to and read content on free, monthly and annual plans, with 14-day trials. You ask a question in plain words; the analyst frames it, profiles the tables, queries the database, checks its own work and hands back a written brief.

## How It Works

Run `/analyst <question>` and the analyst works through five steps:

1. **Frame** - Pins the question, the decision it informs and the audience. If no decision is named, it asks and stops.
2. **Profile** - Describes each table from the live database and writes it into `knowledge/beam/`.
3. **Analyse** - Saves the SQL it runs in `queries.sql`, then computes every number in one rerunnable `analysis.py`, each with its comparison.
4. **Validate** - Peer reviews its own work: mechanics first, then reasoning. Verdict: Ship it, Think on it or Fix first.
5. **Deliver** - Writes a brief with the answer first and a Checks section saying what was and was not verified.

Each step is also its own skill (`/frame`, `/profile`, `/analyse`, `/validate`, `/deliver`) and works alone. Skills share nothing except the files in the run folder and `knowledge/beam/`.

## Setup

### Prerequisites

- Python 3.10 or 3.11
- [Poetry](https://python-poetry.org/docs/#installation)
- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
- Read access to the course Postgres database, and the MCP Toolbox binary for Postgres (see Database connection)

### Installation

1. **Install Poetry** (if not already installed):

   **Windows (PowerShell)**:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
   ```

   **macOS/Linux**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

   After installation, restart your terminal. If `poetry` command is not found:
   - **Windows**: Add `%APPDATA%\Python\Scripts` to your system PATH
   - **macOS/Linux**: Add `export PATH="$HOME/.local/bin:$PATH"` to your `~/.bashrc` or `~/.zshrc`

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Connect the database** (next section).

4. **Start Claude Code**:
   ```bash
   claude
   ```
   Run `claude` from the repo root so it picks up the project's skills and instructions. Approve the `course-db` MCP server when prompted.

### Database connection

Profile and Analyse read from the live database, not from the CSV exports. They reach it through an MCP server called `course-db`, defined in `.mcp.json`. It runs the MCP Toolbox for Databases (`toolbox --prebuilt postgres --stdio`) and takes its connection details from environment variables.

1. Copy `.env.example` to `.env` and fill in the five values from your course materials:
   ```
   POSTGRES_HOST=
   POSTGRES_PORT=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_DATABASE=
   ```
   `.env` is git-ignored. Never commit credentials.
2. In `.mcp.json`, replace `/path/to/toolbox` in `command` with the path of your Toolbox binary.
3. Export the variables in the shell you start Claude Code from, so `.mcp.json` can substitute them:
   ```bash
   set -a; source .env; set +a
   claude
   ```
4. Check it works: in Claude Code run `/mcp` and confirm `course-db` is connected.

The database has these tables:

| Schema | Table | What it is |
|---|---|---|
| public | `users`, `subscriptions`, `payments`, `trials`, `sessions` | Source tables. Use these for anything that must be exact. `sessions` is very large: aggregate only. |
| marts | `user_activity_metrics`, `user_revenue_summary` | Derived copies. Reconcile against the source before relying on them. |
| ml | `churn_snapshot`, `trial_snapshot` | Versioned training tables with a `snapshot_date`. Not for volumes. |

Rules the skills follow with the connection: every statement is a read-only SELECT, one statement per call, aggregates only (no raw rows are printed), and dates are written out because the data ends on 2026-09-24, which is treated as today.

## How the agent is put together

There is no framework and no Python program controlling the model. The agent is a Claude Code project:

- **An entry-point skill:** `.claude/skills/analyst/SKILL.md` lists the steps in order, and `/analyst <question>` runs them.
- **Routing lines:** `AGENTS.md` says which skill handles which kind of request, and holds the conventions (run with `poetry run python`, no raw rows in the conversation, never modify `data/`, no em dashes in anything written for a reader, today is 2026-09-24).
- **One skill per step:** `frame`, `profile`, `analyse`, `validate`, `deliver` under `.claude/skills/`.
- **A knowledge folder:** `knowledge/beam/` holds one YAML note per table (fields, measures, derived dimensions and golden queries that have been run), `quirks.md` for known data quirks, and `corrections.md`, which the agent reads before every run and appends a dated line to when you correct it.
- **Helpers:** `helpers/checks.py` (fan-out, parts-sum-to-total, date-boundary and matured-trial checks), `helpers/charts.py` (one house style, titles that state the takeaway) and `helpers/profile.py`. The arithmetic runs in code, never in the model's head.
- **One output folder per question:** `outputs/<date>_<slug>/` with the brief, charts and the scripts that produced the numbers, so anyone can rerun it.

## What a run produces

```
outputs/<YYYY-MM-DD>_<slug>/
├── frame.md        question, decision, audience, what would change the decision
├── queries.sql     every SQL block, one per result table
├── data/           verbatim query results (small aggregates)
├── analysis.py     reads data/, computes every number, runs checks, draws charts
├── charts/         PNG charts
├── review.md       Validate's verdict and at most three findings
└── brief.md        the answer, recommendations, analysis and Checks
```

Run folders are named with the date the run happens. Rerun a script from the repo root with `poetry run python outputs/<run>/analysis.py`. It reads only its own `data/` folder and does not connect to the database; to refresh the numbers, rerun the blocks in `queries.sql` through `course-db` and save the results.

Runs so far:

- `2026-11-10_march-price-increase-retention`, `2026-11-10_monthly-active-users-trial-launch`, `2026-11-10_trial-conversion-weekly`: earlier runs built on the CSV exports.
- `2026-11-23_march-price-increase-retention`: did the March 2026 price rise hurt retention, and for whom.
- `2026-11-23_trial-day-one-binge-conversion`: do day-one bingers who go quiet convert worse than steady trial users.

## Project Structure

```
ai-analyst/
├── AGENTS.md             # Project instructions and routing
├── .mcp.json             # course-db MCP server (Postgres)
├── .env.example          # Connection variables to copy into .env
├── data/                 # Beam's exported tables (CSV); never modified
├── knowledge/beam/       # Table notes (YAML), quirks.md, corrections.md
├── helpers/              # Checks, charts and profiling helpers
├── outputs/              # One folder per question
├── .claude/skills/       # analyst, frame, profile, analyse, validate, deliver
└── pyproject.toml        # Dependencies
```

## Data

The CSV exports in `data/` are a snapshot kept for reference; the skills query the database instead.

- `users.csv`: one row per user
- `subscriptions.csv`: one row per subscription
- `payments.csv`: payments from 2025-01-01
- `trials.csv`: one row per trial
- `user_activity_metrics.csv`: daily active user counts (dau, wau, mau)

Session-level data is in the database (`public.sessions`) but not in the CSVs.

Known quirks (read `knowledge/beam/quirks.md` before trusting a number): the monthly price rose from $10 to $12 in March 2026; trials last 14 days and recent ones have no outcome yet; free plans never end; end dates can be in the future; September 2025 shows a signup spike; subscription status labels changed in August 2026, so read churn from `end_date`.

---

*Future Proof Data Science - Teaching data scientists to optimize workflows with AI*
