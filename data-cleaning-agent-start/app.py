"""Streamlit interface for the Data Cleaning Agent."""

import traceback
from datetime import datetime

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from data_cleaning_agent import LightweightDataCleaningAgent
from comparison import show_comparison

load_dotenv()

st.title("🧹 Data Cleaning Agent")

# Upload file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# Persist results across Streamlit reruns (button clicks trigger a rerun)
st.session_state.setdefault("result", None)
st.session_state.setdefault("error_log", [])
st.session_state.setdefault("show_code", False)
st.session_state.setdefault("show_errors", False)
st.session_state.setdefault("clean_started", False)


def log_error(context: str, details: str):
    """Append an error entry to the session error log."""
    st.session_state.error_log.append(
        f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {context}\n{details}"
    )


if uploaded_file:
    try:
        df_raw = pd.read_csv(uploaded_file)
    except Exception:
        log_error("Failed to read uploaded CSV", traceback.format_exc())
        st.error("Could not read the CSV file. Open the error log below for details.")
        df_raw = None

    # Clean button
    if df_raw is not None and st.button("Clean Data"):
        st.session_state.result = None
        st.session_state.clean_started = True
        try:
            with st.spinner("Cleaning..."):
                llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
                agent = LightweightDataCleaningAgent(model=llm, log=True)
                agent.invoke_agent(data_raw=df_raw)
                agent_error = (agent.response or {}).get("data_cleaner_error")
                if agent_error:
                    log_error("Agent could not fix the generated code", str(agent_error))
                st.session_state.result = {
                    "df_raw": df_raw,
                    "df_cleaned": agent.get_data_cleaned(),
                    "code": agent.get_data_cleaner_function(),
                    "failed": bool(agent_error),
                }
        except Exception:
            log_error("Unexpected error while running the agent", traceback.format_exc())
            st.error("Something went wrong during cleaning. Open the error log below for details.")

result = st.session_state.result
if result:
    df_raw, df_cleaned = result["df_raw"], result["df_cleaned"]
    if result["failed"]:
        st.warning("Finished with errors. Check the error log below.")
    else:
        st.success("Done!")

    st.subheader("Cleaned Data")
    st.write(f"Shape: {df_cleaned.shape[0]} rows × {df_cleaned.shape[1]} columns")
    st.dataframe(df_cleaned.head())

    try:
        show_comparison(df_raw, df_cleaned)
    except Exception:
        log_error("Failed to render comparison", traceback.format_exc())
        st.error("Could not render the comparison. Open the error log below for details.")

    # Download cleaned data
    st.download_button(
        "Download Cleaned Data",
        data=df_cleaned.to_csv(index=False),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )

    # Generated code (toggle button) + .py download
    if st.button("Hide Generated Code" if st.session_state.show_code else "Show Generated Code"):
        st.session_state.show_code = not st.session_state.show_code
        st.rerun()
    if st.session_state.show_code:
        code = result["code"]
        if code:
            st.code(code, language="python")
            st.download_button(
                "Download Code (.py)",
                data=code,
                file_name="data_cleaner.py",
                mime="text/x-python",
            )
        else:
            st.info("No code was generated.")

# Error log (toggle button) - shown once cleaning has started, or if any error exists (e.g. load error)
if st.session_state.clean_started or st.session_state.error_log:
    st.divider()
    n_errors = len(st.session_state.error_log)
    label = f"Error Log ({n_errors})"
    if st.button(f"Hide {label}" if st.session_state.show_errors else f"Show {label}"):
        st.session_state.show_errors = not st.session_state.show_errors
        st.rerun()
    if st.session_state.show_errors:
        if n_errors:
            st.code("\n\n".join(st.session_state.error_log), language="text")
            if st.button("Clear Error Log"):
                st.session_state.error_log = []
                st.rerun()
        else:
            st.info("No errors recorded.")
