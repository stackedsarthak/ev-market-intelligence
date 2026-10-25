"""
EV Market Intelligence — Battery & Vehicle Performance
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import avg_range_by_category, avg_range_by_battery_type, battery_tech_distribution
from src.charts import (chart_battery_donut, chart_battery_capacity_vs_range, chart_range_boxplot,
                        chart_range_by_category_bar, chart_efficiency_by_category, _empty_chart)
from src.ui_components import (inject_global_css, page_header, data_source_badge, section_header,
                                kpi_card, empty_state, filter_status_bar, format_number,
                                build_sidebar_filters, show_warnings)

COLORS = {'cyan': '#00D4FF', 'green': '#3DDE91', 'amber': '#FFB347', 'panel': '#121A2B', 'border': '#253554', 'text_dim': '#A8B3C7'}

st.set_page_config(page_title='Battery Performance · EV Market', page_icon='🔋', layout='wide')
inject_global_css()

@st.cache_data(show_spinner=False)
def get_clean_data():
    raw = load_bundled_data()
    return preprocess(raw)

def get_active_data():
    if 'uploaded_df' in st.session_state and st.session_state['uploaded_df'] is not None:
        return st.session_state['uploaded_df'], st.session_state.get('upload_warnings', []), True
    df, warnings = get_clean_data()
    return df, warnings, False

df_full, data_warnings, is_uploaded = get_active_data()
filters = build_sidebar_filters(df_full)
df = apply_filters(df_full, years=filters.get('years'), manufacturers=filters.get('manufacturers'), categories=filters.get('categories'), battery_types=filters.get('battery_types'), countries=filters.get('countries'))

page_header('Battery & Vehicle Performance', 'Battery chemistry, driving range, charging, and engineering specifications.', '🔋')
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {})

if len(df) == 0:
    empty_state()
    st.stop()

# KPIs
section_header('Performance Summary')
k1, k2, k3, k4 = st.columns(4)
with k1:
    avg_bat = df['battery_capacity_kwh'].mean() if 'battery_capacity_kwh' in df.columns else None
    kpi_card('Avg Battery Capacity', f'{avg_bat:.1f} kWh' if avg_bat else 'N/A', 'Mean across records')
with k2:
    avg_r = df['range_km'].mean() if 'range_km' in df.columns else None
    kpi_card('Avg Driving Range', f'{avg_r:.0f} km' if avg_r else 'N/A', 'Mean across records')
with k3:
    avg_e = df['efficiency_wh_per_km'].mean() if 'efficiency_wh_per_km' in df.columns else None
    kpi_card('Avg Efficiency', f'{avg_e:.0f} Wh/km' if avg_e else 'N/A', 'Lower = more efficient')
with k4:
    avg_p = df['motor_power_kw'].mean() if 'motor_power_kw' in df.columns else None
    kpi_card('Avg Motor Power', f'{avg_p:.0f} kW' if avg_p else 'N/A', 'Mean motor power')

st.markdown('<br>', unsafe_allow_html=True)

# Battery Chemistry
section_header('Battery Chemistry Analysis')
col1, col2 = st.columns([2, 3])
with col1:
    st.plotly_chart(chart_battery_donut(df), use_container_width=True, config={'displayModeBar': False})
with col2:
    batt_range = avg_range_by_battery_type(df)
    if not batt_range.empty:
        st.markdown('**Average Range & Capacity by Battery Technology**')
        display = batt_range.copy()
        display['avg_range_km'] = display['avg_range_km'].round(1)
        if 'avg_battery_kwh' in display.columns:
            display['avg_battery_kwh'] = display['avg_battery_kwh'].round(1)
        st.dataframe(display.rename(columns={'battery_type': 'Battery Type', 'avg_range_km': 'Avg Range (km)', 'avg_battery_kwh': 'Avg Capacity (kWh)', 'count': 'Records'}), use_container_width=True, hide_index=True)
    st.info('Note: Battery chemistry is one factor in range. Vehicle weight, aerodynamics, battery size, temperature, and test standards also matter significantly.')

# Capacity vs Range Scatter
st.markdown('<br>', unsafe_allow_html=True)
section_header('Battery Capacity vs Driving Range', 'Relationship between energy stored and range achieved')
st.plotly_chart(chart_battery_capacity_vs_range(df), use_container_width=True, config={'displayModeBar': False})

# Range Distribution
section_header('Range Distribution')
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(chart_range_boxplot(df), use_container_width=True, config={'displayModeBar': False})
with col4:
    st.plotly_chart(chart_range_by_category_bar(df), use_container_width=True, config={'displayModeBar': False})

# Charging Analysis
if 'max_dc_charging_kw' in df.columns:
    st.markdown('<br>', unsafe_allow_html=True)
    section_header('Charging Analysis')
    col5, col6 = st.columns(2)
    with col5:
        if 'category' in df.columns:
            charge_cat = df.groupby('category')['max_dc_charging_kw'].mean().reset_index()
            charge_cat.columns = ['category', 'avg_dc_kw']
            charge_cat = charge_cat.sort_values('avg_dc_kw')
            fig_c = px.bar(charge_cat, y='category', x='avg_dc_kw', orientation='h',
                           title='Avg Max DC Charging Speed by Category',
                           labels={'avg_dc_kw': 'Avg DC Speed (kW)', 'category': ''},
                           color_discrete_sequence=['#00D4FF'])
            fig_c.update_layout(paper_bgcolor='#121A2B', plot_bgcolor='#182338',
                                font_color='#A8B3C7', height=400)
            st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})
    with col6:
        if 'battery_type' in df.columns and 'charging_dc_fast_time_min' in df.columns:
            charge_batt = df.groupby('battery_type')['charging_dc_fast_time_min'].mean().reset_index()
            charge_batt.columns = ['battery_type', 'avg_dc_time_min']
            fig_t = px.bar(charge_batt, x='battery_type', y='avg_dc_time_min',
                           title='Avg DC Fast Charge Time (80%) by Battery Type',
                           labels={'avg_dc_time_min': 'Avg DC Time (min)', 'battery_type': 'Battery Type'},
                           color_discrete_sequence=['#3DDE91'])
            fig_t.update_layout(paper_bgcolor='#121A2B', plot_bgcolor='#182338',
                                font_color='#A8B3C7', height=400)
            st.plotly_chart(fig_t, use_container_width=True, config={'displayModeBar': False})

# Efficiency
st.markdown('<br>', unsafe_allow_html=True)
section_header('Energy Efficiency by Category')
st.plotly_chart(chart_efficiency_by_category(df), use_container_width=True, config={'displayModeBar': False})

# Vehicle Spec Table
st.markdown('<br>', unsafe_allow_html=True)
section_header('Vehicle Specifications Table')
spec_cols = [c for c in ['manufacturer', 'model_name', 'category', 'model_year', 'battery_type',
                          'battery_capacity_kwh', 'range_km', 'motor_power_kw', 'top_speed_kmph',
                          'price_usd', 'customer_rating'] if c in df.columns]
spec_df = df[spec_cols].copy()
for col in ['battery_capacity_kwh', 'range_km', 'motor_power_kw', 'top_speed_kmph']:
    if col in spec_df.columns:
        spec_df[col] = spec_df[col].round(1)
if 'price_usd' in spec_df.columns:
    spec_df['price_usd'] = spec_df['price_usd'].round(0)

st.dataframe(spec_df, use_container_width=True, hide_index=True, height=350)
col_dl, _ = st.columns([1, 3])
with col_dl:
    csv = spec_df.to_csv(index=False)
    st.download_button('Download Spec Table (CSV)', csv, 'ev_specs_filtered.csv', 'text/csv')

with st.expander('ℹ️ Battery & Performance Notes'):
    st.markdown("""
    - **Battery chemistry alone does not determine range.** Vehicle size, weight, aerodynamics, ambient temperature, driving speed, and acceleration patterns all affect real-world range.
    - **Efficiency (Wh/km):** Lower values mean more energy-efficient operation.
    - **DC fast charging time** assumes 0–80% charge from an empty battery.
    - **Range figures** in this dataset are idealized estimates based on battery capacity and a simulated efficiency value — not real manufacturer WLTP or EPA ratings.
    - All data is synthetic demonstration data.
    """)
