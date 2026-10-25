"""
EV Market Intelligence — Sustainability & Research
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import co2_savings_summary
from src.charts import (chart_co2_savings, chart_annual_sales_trend, chart_yoy_growth,
                         chart_category_sales_bar, chart_country_bar, chart_safety_distribution)
from src.ui_components import (inject_global_css, page_header, data_source_badge, section_header,
                                kpi_card, empty_state, filter_status_bar, build_sidebar_filters,
                                show_warnings, format_number)

st.set_page_config(page_title="Sustainability · EV Market", page_icon="🌱", layout="wide")
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

page_header("Sustainability & Research", "Environmental indicators, technology trends, and research notes.", "🌱")
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {})

if len(df) == 0:
    empty_state()
    st.stop()

# ─── CO2 Savings ──────────────────────────────────────────────────────────────
section_header("Estimated CO₂ Savings", "Based on simplified assumptions — labeled as estimates")
st.warning("**These are estimates only.** Real lifecycle CO₂ depends on manufacturing emissions, "
           "electricity grid carbon intensity, battery production, vehicle use, and end-of-life. "
           "EVs do not have zero lifecycle emissions.")

co2 = co2_savings_summary(df)
if co2:
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Total Est. CO₂ Saved", format_number(co2.get("total_co2_saved_tons", 0), 1, suffix=" t"),
                 "tons/yr (estimate)")
    with k2:
        kpi_card("Avg per Vehicle", f"{co2.get('avg_co2_saved_per_vehicle', 0):.2f} t/yr",
                 "Estimated tons CO₂")
    with k3:
        kpi_card("Vehicles with Data", f"{co2.get('vehicle_count', 0):,}", "Records with CO₂ estimate")
    with k4:
        kpi_card("Max Est. Savings", f"{co2.get('max_co2_saved', 0):.2f} t/yr", "Per single vehicle")

    with st.expander("🔎 CO₂ Estimation Assumptions"):
        st.markdown("""
        | Assumption | Value |
        |---|---|
        | Annual distance | 15,000 km |
        | Baseline ICE emissions | 150 g CO₂/km |
        | Electricity emission factor | 0.5 kg CO₂/kWh (global average) |

        **Limitations:** Manufacturing/battery production not included. Grid mix varies by country.
        Real-world range differs from test values.
        """)

    st.plotly_chart(chart_co2_savings(df), use_container_width=True, config={"displayModeBar": False})
else:
    st.info("CO₂ savings column (co2_saved_tons_per_year) not available in this dataset.")

# ─── Battery Sustainability ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Battery Technology Sustainability")
col1, col2 = st.columns(2)
with col1:
    if "battery_type" in df.columns and "battery_degradation_pct_5yr" in df.columns:
        deg = (df.groupby("battery_type")["battery_degradation_pct_5yr"]
               .mean().reset_index()
               .rename(columns={"battery_degradation_pct_5yr": "avg_deg"}))
        fig_deg = px.bar(deg, x="battery_type", y="avg_deg",
                         title="Avg Battery Degradation at 5yr (%) by Type",
                         labels={"avg_deg": "Avg Degradation (%)", "battery_type": "Battery Type"},
                         color_discrete_sequence=["#FFB347"])
        fig_deg.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                               font_color="#A8B3C7", height=320)
        st.plotly_chart(fig_deg, use_container_width=True, config={"displayModeBar": False})
        st.caption("Lower degradation = longer battery lifespan = better sustainability.")
with col2:
    if "battery_type" in df.columns and "battery_cycle_life" in df.columns:
        cyc = (df.dropna(subset=["battery_cycle_life"])
               .groupby("battery_type")["battery_cycle_life"]
               .mean().reset_index()
               .rename(columns={"battery_cycle_life": "avg_cycles"}))
        if not cyc.empty:
            fig_cyc = px.bar(cyc, x="battery_type", y="avg_cycles",
                             title="Avg Battery Cycle Life by Type",
                             labels={"avg_cycles": "Avg Cycles", "battery_type": "Battery Type"},
                             color_discrete_sequence=["#3DDE91"])
            fig_cyc.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                                   font_color="#A8B3C7", height=320)
            st.plotly_chart(fig_cyc, use_container_width=True, config={"displayModeBar": False})
            st.caption("Higher cycle life = more charge cycles before significant degradation.")

# ─── Market Growth ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("EV Market Growth Trends")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(chart_annual_sales_trend(df), use_container_width=True,
                    config={"displayModeBar": False})
with col4:
    st.plotly_chart(chart_yoy_growth(df), use_container_width=True,
                    config={"displayModeBar": False})

# ─── Category Distribution ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Vehicle Category Distribution")
col5, col6 = st.columns([2, 1])
with col5:
    st.plotly_chart(chart_category_sales_bar(df), use_container_width=True,
                    config={"displayModeBar": False})
with col6:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("Commercial EVs (buses, trucks) have higher per-vehicle CO₂ impact due to high annual mileage.")
    st.info("Two-wheelers and micro city cars have the lowest absolute energy consumption per vehicle.")

# ─── Manufacturing Country ────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Manufacturing Country Distribution")
st.plotly_chart(chart_country_bar(df), use_container_width=True, config={"displayModeBar": False})

# ─── Autonomous & Safety ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Autonomous Level & Safety Distribution")
col7, col8 = st.columns(2)
with col7:
    if "autonomous_level" in df.columns:
        auto_counts = df["autonomous_level"].value_counts().sort_index().reset_index()
        auto_counts.columns = ["level", "count"]
        fig_auto = px.bar(auto_counts, x="level", y="count",
                          title="Autonomous Driving Level Distribution (SAE L0–L5)",
                          labels={"level": "SAE Level", "count": "Vehicles"},
                          color_discrete_sequence=["#9B59B6"])
        fig_auto.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                                font_color="#A8B3C7", height=320)
        st.plotly_chart(fig_auto, use_container_width=True, config={"displayModeBar": False})
with col8:
    st.plotly_chart(chart_safety_distribution(df), use_container_width=True,
                    config={"displayModeBar": False})

# ─── Research Notes ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📚 Research Notes & Dataset Limitations", expanded=False):
    st.markdown("""
    ## Research Notes

    ### Dataset
    - This dataset is **synthetic demonstration data** generated with a fixed seed (SEED=42).
    - Manufacturer and model names are fictional. Values are statistically plausible but **not** real.
    - Do not use for purchasing, engineering, or policy decisions.

    ### CO₂ Estimation Methodology
    - CO₂ savings estimated against a baseline ICE vehicle (150 g CO₂/km).
    - Electricity emissions factor: 0.5 kg CO₂/kWh (global average — varies by country).
    - Manufacturing, battery production, and end-of-life emissions **not included**.

    ### Important Caveats
    - **EVs do not have zero lifecycle emissions.** Battery production is energy-intensive.
    - Grid electricity CO₂ ranges from ~20 g/kWh (renewables) to ~900 g/kWh (coal).
    - Real-world range is affected by temperature, speed, load, and HVAC use.
    - Test standards (WLTP, EPA, NEDC) produce different range ratings for the same vehicle.

    ### Reproducibility
    - Dataset generated with Python NumPy/Pandas, seed=42.
    - Run `python src/generate_dataset.py` to regenerate.
    """)
