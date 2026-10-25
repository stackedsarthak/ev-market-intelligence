"""
EV Market Intelligence — Data Explorer
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import load_bundled_data, REQUIRED_COLUMNS, load_uploaded_data
from src.preprocessing import preprocess, apply_filters, get_quality_report
from src.ui_components import (inject_global_css, page_header, data_source_badge, section_header,
                                kpi_card, filter_status_bar, build_sidebar_filters, show_warnings)

st.set_page_config(page_title="Data Explorer · EV Market", page_icon="🔬", layout="wide")
inject_global_css()

@st.cache_data(show_spinner=False)
def get_clean_data():
    raw = load_bundled_data()
    return preprocess(raw)

def get_active_data():
    if "uploaded_df" in st.session_state and st.session_state["uploaded_df"] is not None:
        return st.session_state["uploaded_df"], st.session_state.get("upload_warnings", []), True
    df, warnings = get_clean_data()
    return df, warnings, False

df_full, data_warnings, is_uploaded = get_active_data()
filters = build_sidebar_filters(df_full)
df = apply_filters(df_full, years=filters.get("years"), manufacturers=filters.get("manufacturers"),
                   categories=filters.get("categories"), battery_types=filters.get("battery_types"),
                   countries=filters.get("countries"))

page_header("Data Explorer", "Inspect, search, filter, and download the EV dataset.", "🔬")
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {})

# ─── Dataset Summary ─────────────────────────────────────────────────────────
section_header("Dataset Summary")
report = get_quality_report(df_full)
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Total Rows", f"{report['total_rows']:,}", "Full dataset")
with k2:
    kpi_card("Columns", str(report["total_columns"]), "Features")
with k3:
    kpi_card("Duplicate Rows", str(report["duplicate_rows"]), "In full dataset")
with k4:
    total_missing = sum(report["missing_by_column"].values())
    kpi_card("Missing Values", f"{total_missing:,}", "Across all columns")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Column Overview ──────────────────────────────────────────────────────────
section_header("Column Overview")
col1, col2 = st.columns(2)
with col1:
    missing_dict = {k: v for k, v in report["missing_by_column"].items() if v > 0}
    if missing_dict:
        missing_df = pd.DataFrame([
            {"Column": col, "Missing": cnt,
             "Missing (%)": f"{report['missing_pct_by_column'][col]:.1f}%"}
            for col, cnt in sorted(missing_dict.items(), key=lambda x: -x[1])
        ])
        st.markdown("**Missing Values by Column**")
        st.dataframe(missing_df, use_container_width=True, hide_index=True)
    else:
        st.success("No missing values in the full dataset.")
with col2:
    dtype_df = pd.DataFrame([
        {"Column": col, "Type": str(dtype)}
        for col, dtype in report["dtypes"].items()
    ])
    st.markdown("**Data Types**")
    st.dataframe(dtype_df, use_container_width=True, hide_index=True, height=300)

# ─── Descriptive Statistics ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Descriptive Statistics")
num_cols = df_full.select_dtypes(include=np.number).columns.tolist()
if num_cols:
    desc = df_full[num_cols].describe().round(2).T
    st.dataframe(desc, use_container_width=True, height=420)
else:
    st.info("No numeric columns found.")

# ─── Data Table ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Data Table", "Browse, search, and paginate the filtered dataset")

all_cols = df.columns.tolist()
selected_cols = st.multiselect("Show columns", options=all_cols, default=all_cols, key="data_cols")
if not selected_cols:
    selected_cols = all_cols

search = st.text_input("Search manufacturer or model name", "", key="data_search",
                        placeholder="e.g. VoltAura, TerraMotors...")

display_df = df[selected_cols].copy()
if search.strip():
    mask = pd.Series([False] * len(display_df), index=display_df.index)
    if "manufacturer" in selected_cols:
        mask = mask | display_df["manufacturer"].astype(str).str.contains(search, case=False, na=False)
    if "model_name" in selected_cols:
        mask = mask | display_df["model_name"].astype(str).str.contains(search, case=False, na=False)
    display_df = display_df[mask]

ROWS_PER_PAGE = 50
total_rows = len(display_df)
total_pages = max(1, (total_rows + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)
page_num = st.number_input(f"Page (1–{total_pages})", min_value=1, max_value=total_pages,
                            value=1, step=1, key="page_num")
start = (page_num - 1) * ROWS_PER_PAGE
end = min(start + ROWS_PER_PAGE, total_rows)

st.markdown(f"Showing rows **{start+1}–{end}** of **{total_rows:,}** (after search/filter)")
st.dataframe(display_df.iloc[start:end], use_container_width=True, hide_index=True, height=400)

# ─── Downloads ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Downloads")
col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    st.download_button("↓ Download Filtered Data (CSV)", df.to_csv(index=False),
                        "ev_data_filtered.csv", "text/csv", use_container_width=True)
    st.caption(f"Contains {len(df):,} filtered rows")

with col_d2:
    st.download_button("↓ Download Full Dataset (CSV)", df_full.to_csv(index=False),
                        "ev_data_full_cleaned.csv", "text/csv", use_container_width=True)
    st.caption(f"Contains {len(df_full):,} total rows")

with col_d3:
    dict_path = os.path.join(os.path.dirname(__file__), "..", "data", "data_dictionary.md")
    if os.path.exists(dict_path):
        with open(dict_path, "r", encoding="utf-8") as f:
            dict_content = f.read()
        st.download_button("↓ Download Data Dictionary (MD)", dict_content,
                            "ev_data_dictionary.md", "text/markdown", use_container_width=True)
        st.caption("Schema documentation")

# ─── Upload ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Upload Your Dataset", "Replace the demo data with your own EV dataset")

st.markdown("**Minimum required columns:**")
req_cols_display = ", ".join([f"`{c}`" for c in REQUIRED_COLUMNS])
st.markdown(req_cols_display)

up_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx", "xls"],
                            key="explorer_upload")
if up_file:
    up_df, up_msg = load_uploaded_data(up_file)
    if up_df is not None:
        clean_up, up_warnings = preprocess(up_df)
        st.session_state["uploaded_df"] = clean_up
        st.session_state["upload_warnings"] = up_warnings
        st.success(up_msg)
        if st.button("Apply Uploaded Dataset"):
            st.rerun()
    else:
        st.error(up_msg)
