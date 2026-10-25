"""
EV Market Intelligence — Sales & Market Trends
=================================================
Dedicated analytics page for annual and category-level sales trends.
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import annual_sales_trend, yoy_growth, category_sales, manufacturer_market_share
from src.charts import (
    chart_annual_sales_trend, chart_category_sales_bar, chart_yoy_growth,
    chart_stacked_area_by_category, chart_manufacturer_share_bar, _empty_chart
)
from src.ui_components import (
    inject_global_css, page_header, data_source_badge, section_header,
    kpi_card, empty_state, filter_status_bar, format_number,
    build_sidebar_filters, show_warnings
)

st.set_page_config(page_title="Sales Trends · EV Market", page_icon="📈", layout="wide")
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

df = apply_filters(
    df_full,
    years=filters.get("years"),
    manufacturers=filters.get("manufacturers"),
    categories=filters.get("categories"),
    battery_types=filters.get("battery_types"),
    countries=filters.get("countries"),
)

page_header("Sales & Market Trends", "Annual trends, growth rates, and category-level sales breakdown.", "📈")
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {
    "Years": f"{filters['years'][0]}–{filters['years'][1]}" if filters.get("years") else None,
})

if len(df) == 0:
    empty_state()
    st.stop()

# ─── KPI row ─────────────────────────────────────────────────────────────────
section_header("Sales Summary")
trend = annual_sales_trend(df)
k1, k2, k3, k4 = st.columns(4)

with k1:
    total_s = df["annual_sales_units"].sum() if "annual_sales_units" in df.columns else len(df)
    kpi_card("Total Sales / Records", format_number(total_s), "Filtered dataset")
with k2:
    yrs = df["model_year"].nunique() if "model_year" in df.columns else 0
    kpi_card("Years Covered", str(yrs), "Distinct model years")
with k3:
    if len(trend) >= 2:
        growth_df = yoy_growth(df).dropna(subset=["yoy_growth_pct"])
        if not growth_df.empty:
            last_growth = growth_df.iloc[-1]["yoy_growth_pct"]
            kpi_card("Latest YoY Growth",
                     f"{last_growth:+.1f}%",
                     f"Year {int(growth_df.iloc[-1]['model_year'])}")
        else:
            kpi_card("Latest YoY Growth", "N/A", "Need ≥2 years")
    else:
        kpi_card("Latest YoY Growth", "N/A", "Need ≥2 years")
with k4:
    top_cat = df.groupby("category").size().idxmax() if "category" in df.columns else "N/A"
    kpi_card("Leading Category", top_cat, "By record count")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Trend charts ─────────────────────────────────────────────────────────────
section_header("Annual Sales Trend")
col1, col2 = st.columns([3, 2])
with col1:
    split_by = st.selectbox("Split by", ["None", "category", "manufacturer"], key="trend_split")
    color_by = None if split_by == "None" else split_by
    st.plotly_chart(chart_annual_sales_trend(df, color_by=color_by), use_container_width=True,
                    config={"displayModeBar": False})
with col2:
    st.plotly_chart(chart_yoy_growth(df), use_container_width=True, config={"displayModeBar": False})

# ─── Stacked area ──────────────────────────────────────────────────────────
section_header("Category Composition Over Time", "How vehicle category mix has evolved year by year")
st.plotly_chart(chart_stacked_area_by_category(df), use_container_width=True,
                config={"displayModeBar": False})

# ─── Category comparison ──────────────────────────────────────────────────────
section_header("Category Sales Breakdown")
col3, col4 = st.columns([2, 3])
with col3:
    st.plotly_chart(chart_category_sales_bar(df), use_container_width=True,
                    config={"displayModeBar": False})
with col4:
    section_header("Manufacturer Rankings", "Sales or record count")
    share = manufacturer_market_share(df)
    if not share.empty:
        st.dataframe(
            share.rename(columns={"manufacturer": "Manufacturer", "sales": "Sales/Records", "share_pct": "Share (%)"}),
            use_container_width=True, hide_index=True
        )

# ─── Growth table ────────────────────────────────────────────────────────────
section_header("Year-over-Year Detail Table")
trend_full = yoy_growth(df)
if not trend_full.empty:
    trend_full["model_year"] = trend_full["model_year"].astype(int)
    trend_full["yoy_growth_pct"] = trend_full["yoy_growth_pct"].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "—"
    )
    trend_full["sales"] = trend_full["sales"].apply(lambda x: f"{x:,.0f}")
    st.dataframe(
        trend_full.rename(columns={
            "model_year": "Year", "sales": "Sales / Records", "yoy_growth_pct": "YoY Growth"
        }),
        use_container_width=True, hide_index=True
    )
    with st.expander("ℹ️ Growth calculation notes"):
        st.markdown("""
        - YoY growth = (current year − prior year) / prior year × 100.
        - Requires consecutive years with non-zero prior-year values.
        - Blank (—) for the first year or where prior year is zero.
        - Growth reflects record counts or sales units in the **demonstration dataset**, not verified market data.
        """)
else:
    st.info("Need at least 2 years of data to compute growth rates.")
