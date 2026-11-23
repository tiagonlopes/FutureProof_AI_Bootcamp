"""Streamlit UI component: before/after comparison of raw vs cleaned data.

This module renders directly with ``st.*`` calls, so it is UI code, not pure data logic.
"""

import pandas as pd
import streamlit as st


def show_comparison(before: pd.DataFrame, after: pd.DataFrame) -> None:
    """Render a visual before/after comparison of the raw and cleaned data."""
    st.subheader("Before vs After")

    # Headline metrics (delta shown relative to the original)
    metrics = [
        ("Rows", len(before), len(after)),
        ("Columns", before.shape[1], after.shape[1]),
        ("Missing values", int(before.isna().sum().sum()), int(after.isna().sum().sum())),
        ("Duplicate rows", int(before.duplicated().sum()), int(after.duplicated().sum())),
    ]
    for col, (label, b, a) in zip(st.columns(len(metrics)), metrics):
        # inverse: fewer missing/duplicates is good (green)
        color = "inverse" if label in ("Missing values", "Duplicate rows") else "off"
        col.metric(label, a, delta=a - b, delta_color=color)

    # Per-column summary
    all_cols = list(dict.fromkeys([*before.columns, *after.columns]))
    rows = []
    for c in all_cols:
        in_b, in_a = c in before.columns, c in after.columns
        rows.append({
            "Column": c,
            "Status": "kept" if in_b and in_a else ("removed" if in_b else "added"),
            "Type before": str(before[c].dtype) if in_b else "—",
            "Type after": str(after[c].dtype) if in_a else "—",
            "Missing before": int(before[c].isna().sum()) if in_b else None,
            "Missing after": int(after[c].isna().sum()) if in_a else None,
            "Unique before": int(before[c].nunique()) if in_b else None,
            "Unique after": int(after[c].nunique()) if in_a else None,
        })
    summary = pd.DataFrame(rows)

    # Missing values per column chart
    st.markdown("**Missing values per column**")
    chart = summary.set_index("Column")[["Missing before", "Missing after"]].fillna(0)
    if chart.to_numpy().sum() > 0:
        st.bar_chart(chart)
    else:
        st.caption("No missing values before or after cleaning.")

    # Changed data types
    changed = summary[(summary["Status"] == "kept") & (summary["Type before"] != summary["Type after"])]
    if not changed.empty:
        st.markdown("**Data type changes**")
        st.dataframe(changed[["Column", "Type before", "Type after"]], hide_index=True)

    with st.expander("Full column-by-column comparison"):
        st.dataframe(summary, hide_index=True)

    # Side-by-side samples
    left, right = st.columns(2)
    left.markdown("**Original (first 5 rows)**")
    left.dataframe(before.head())
    right.markdown("**Cleaned (first 5 rows)**")
    right.dataframe(after.head())
