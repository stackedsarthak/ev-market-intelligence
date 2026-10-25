"""
EV Market Intelligence — Executive Overview
============================================
Main entry point and executive dashboard.
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import load_bundled_data, load_uploaded_data, get_data_source_label
from src.preprocessing import preprocess, apply_filters
from src.metrics import (
    total_sales, unique_manufacturers, unique_models,
    avg_range, avg_battery_capacity, avg_customer_rating,
    leading_manufacturer, top_category
)
from src.insights import generate_all_insights
from src.charts import (
    chart_annual_sales_trend, chart_category_sales_bar,
    chart_manufacturer_share_bar, chart_battery_donut,
    chart_range_by_category_bar, chart_customer_rating
)
from src.ui_components import (
    inject_global_css, page_header, data_source_badge,
    kpi_card, section_header, insight_card, empty_state,
    filter_status_bar, format_number, build_sidebar_filters,
    show_warnings
)

# ─── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="EV Market Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "EV Market Intelligence Dashboard — Synthetic demonstration data.",
    }
)

inject_global_css()


# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_clean_data():
    """Load and preprocess the bundled dataset."""
    raw = load_bundled_data()
    clean, warnings = preprocess(raw)
    return clean, warnings


def get_active_data():
    """Return the currently active dataset (uploaded or bundled)."""
    if "uploaded_df" in st.session_state and st.session_state["uploaded_df"] is not None:
        return st.session_state["uploaded_df"], st.session_state.get("upload_warnings", []), True
    df, warnings = get_clean_data()
    return df, warnings, False


# ─── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Loading dataset..."):
    df_full, data_warnings, is_uploaded = get_active_data()


# ─── Sidebar ──────────────────────────────────────────────────────────────────
filters = build_sidebar_filters(df_full)

# Upload section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Upload Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Replace demonstration data (CSV/Excel)",
    type=["csv", "xlsx", "xls"],
    help="Upload a CSV or Excel file matching the required schema.",
    key="file_uploader",
)

if uploaded_file is not None:
    upload_df, upload_msg = load_uploaded_data(uploaded_file)
    if upload_df is not None:
        clean_upload, upload_warnings = preprocess(upload_df)
        st.session_state["uploaded_df"] = clean_upload
        st.session_state["upload_warnings"] = upload_warnings
        st.sidebar.success(upload_msg)
    else:
        st.sidebar.error(upload_msg)

if is_uploaded and st.sidebar.button("🗑 Clear Uploaded Data", key="clear_upload"):
    st.session_state.pop("uploaded_df", None)
    st.session_state.pop("upload_warnings", None)
    st.rerun()


# ─── Apply filters ────────────────────────────────────────────────────────────
df = apply_filters(
    df_full,
    years=filters.get("years"),
    manufacturers=filters.get("manufacturers"),
    categories=filters.get("categories"),
    battery_types=filters.get("battery_types"),
    countries=filters.get("countries"),
)


# ─── Page content ─────────────────────────────────────────────────────────────
page_header(
    "Executive Overview",
    "Market-level KPIs, key trends, and executive insights from the EV dataset.",
    "⚡"
)

data_source_badge(is_uploaded)
show_warnings(data_warnings)

# Filter status
active_filters = {k: v for k, v in filters.items() if v}
filter_status_bar(df, df_full, {
    "Years": f"{filters['years'][0]}–{filters['years'][1]}" if filters.get("years") else None,
    "Manufacturers": f"{len(filters['manufacturers'])} selected" if filters.get("manufacturers") else None,
    "Categories": f"{len(filters['categories'])} selected" if filters.get("categories") else None,
    "Battery": f"{len(filters['battery_types'])} selected" if filters.get("battery_types") else None,
    "Countries": f"{len(filters['countries'])} selected" if filters.get("countries") else None,
})

# Empty state
if len(df) == 0:
    empty_state(
        "No records match the current filters.",
        "Try expanding the year range, removing manufacturer/category filters, or clicking 'Reset All Filters' in the sidebar."
    )
    st.stop()

# ─── KPI Row ──────────────────────────────────────────────────────────────────
section_header("Key Performance Indicators", "Calculated from currently filtered dataset")

kpi_cols = st.columns(4)

with kpi_cols[0]:
    total_s = total_sales(df)
    if total_s is not None:
        kpi_card("Total Sales Units", format_number(total_s, 1), "Sum of annual_sales_units (filtered)")
    else:
        kpi_card("Vehicle Records", f"{len(df):,}", "Records in filtered dataset")

with kpi_cols[1]:
    kpi_card("Manufacturers", str(unique_manufacturers(df)),
             "Unique manufacturers")

with kpi_cols[2]:
    kpi_card("Vehicle Models", str(unique_models(df)),
             "Unique model names")

with kpi_cols[3]:
    avg_r = avg_range(df)
    kpi_card("Avg Driving Range",
             f"{avg_r:.0f} km" if avg_r else "N/A",
             "Average across filtered records")

kpi_cols2 = st.columns(4)

with kpi_cols2[0]:
    avg_b = avg_battery_capacity(df)
    kpi_card("Avg Battery Capacity",
             f"{avg_b:.1f} kWh" if avg_b else "N/A",
             "Average across filtered records")

with kpi_cols2[1]:
    avg_r2 = avg_customer_rating(df)
    if avg_r2:
        rated_count = df["customer_rating"].notna().sum() if "customer_rating" in df.columns else 0
        kpi_card("Avg Customer Rating",
                 f"{avg_r2:.2f} / 5.0",
                 f"Based on {rated_count:,} rated vehicles")
    else:
        kpi_card("Avg Customer Rating", "N/A", "customer_rating not available")

with kpi_cols2[2]:
    lead_mfr = leading_manufacturer(df)
    kpi_card("Leading Manufacturer",
             lead_mfr or "N/A",
             "By sales units or record count")

with kpi_cols2[3]:
    top_cat = top_category(df)
    kpi_card("Top Category",
             top_cat or "N/A",
             "By sales units or record count")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts Row 1 ────────────────────────────────────────────────────────────
section_header("Market Trends", "Annual sales trajectory and category breakdown")

chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    trend_split = st.selectbox(
        "Color trend by",
        ["None", "category", "manufacturer"],
        key="trend_color_by",
        label_visibility="collapsed",
    )
    color_by = None if trend_split == "None" else trend_split
    st.plotly_chart(chart_annual_sales_trend(df, color_by=color_by),
                    use_container_width=True, config={"displayModeBar": False})

with chart_col2:
    st.plotly_chart(chart_category_sales_bar(df),
                    use_container_width=True, config={"displayModeBar": False})

# ─── Charts Row 2 ────────────────────────────────────────────────────────────
section_header("Market Share & Technology", "Manufacturer rankings and battery chemistry distribution")

chart_col3, chart_col4 = st.columns([3, 2])

with chart_col3:
    st.plotly_chart(chart_manufacturer_share_bar(df, top_n=12),
                    use_container_width=True, config={"displayModeBar": False})

with chart_col4:
    st.plotly_chart(chart_battery_donut(df),
                    use_container_width=True, config={"displayModeBar": False})

# ─── Charts Row 3 ────────────────────────────────────────────────────────────
section_header("Performance & Satisfaction", "Range by category and customer ratings overview")

chart_col5, chart_col6 = st.columns(2)

with chart_col5:
    st.plotly_chart(chart_range_by_category_bar(df),
                    use_container_width=True, config={"displayModeBar": False})

with chart_col6:
    rating_group = st.selectbox(
        "Rate by",
        ["manufacturer", "category"],
        key="rating_group",
        label_visibility="collapsed",
    )
    st.plotly_chart(chart_customer_rating(df, group_by=rating_group),
                    use_container_width=True, config={"displayModeBar": False})

# ─── Executive Insights ───────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header(
    "Executive Insights",
    "Rule-based insights computed from the current filtered dataset. All claims are traceable to the underlying data."
)

insights = generate_all_insights(df)
for i, insight in enumerate(insights):
    insight_card(insight, index=i)

# Methodology note
with st.expander("ℹ️ About these insights"):
    st.markdown("""
    - Insights are generated deterministically from the filtered dataset using rule-based logic.
    - Growth insights require at least 3 years of data.
    - Rating insights require a minimum of 10 rated vehicles per group.
    - No external AI or API is used.
    - All values reflect the **demonstration dataset** — not verified real-world market statistics.
    """)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color: #A8B3C7; font-size: 11px;">'
    '⚡ EV Market Intelligence · Synthetic demonstration data · '
    'Built with Streamlit, Pandas, Plotly'
    '</p>',
    unsafe_allow_html=True
)
