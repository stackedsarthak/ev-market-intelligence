"""
EV Market Intelligence — Manufacturer Intelligence
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import manufacturer_market_share, manufacturer_comparison, rating_by_manufacturer, category_sales
from src.charts import chart_manufacturer_share_bar, chart_manufacturer_heatmap, chart_customer_rating, chart_stacked_area_by_category, chart_battery_donut
from src.ui_components import inject_global_css, page_header, data_source_badge, section_header, kpi_card, empty_state, filter_status_bar, format_number, build_sidebar_filters, show_warnings

st.set_page_config(page_title='Manufacturer Intelligence · EV Market', page_icon='🏭', layout='wide')
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

page_header('Manufacturer Intelligence', 'Competitive analysis, rankings, and cross-manufacturer comparison.', 'factory')
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {'Years': f"{filters['years'][0]}–{filters['years'][1]}" if filters.get('years') else None})

if len(df) == 0:
    empty_state()
    st.stop()

# KPIs
section_header('Summary')
k1, k2, k3, k4 = st.columns(4)
share = manufacturer_market_share(df)
comp = manufacturer_comparison(df)
with k1:
    kpi_card('Manufacturers', str(df['manufacturer'].nunique() if 'manufacturer' in df.columns else 0), 'In filtered dataset')
with k2:
    if not share.empty:
        top_mfr = share.iloc[0]
        kpi_card('Market Leader', top_mfr['manufacturer'], f"{top_mfr['share_pct']:.1f}% share")
    else:
        kpi_card('Market Leader', 'N/A', '')
with k3:
    if 'avg_range_km' in comp.columns:
        best_range = comp.sort_values('avg_range_km', ascending=False).iloc[0]
        kpi_card('Best Avg Range', f"{best_range['avg_range_km']:.0f} km", best_range['manufacturer'])
    else:
        kpi_card('Best Avg Range', 'N/A', '')
with k4:
    rated = rating_by_manufacturer(df, min_count=5)
    if not rated.empty:
        kpi_card('Top Rated', rated.iloc[0]['manufacturer'], f"{rated.iloc[0]['avg_rating']:.2f}/5.0")
    else:
        kpi_card('Top Rated', 'N/A', 'Need 5+ rated vehicles')

st.markdown('<br>', unsafe_allow_html=True)

# Market Share
section_header('Market Share Rankings', 'Relative to currently filtered dataset')
st.plotly_chart(chart_manufacturer_share_bar(df), use_container_width=True, config={'displayModeBar': False})

# Comparison Table
section_header('Manufacturer Comparison Table')
if not comp.empty:
    # Rename columns nicely
    display_cols = {'manufacturer': 'Manufacturer', 'model_name': 'Models', 'avg_range_km': 'Avg Range (km)',
                    'avg_battery_kwh': 'Avg Battery (kWh)', 'avg_price_usd': 'Avg Price (USD)',
                    'avg_rating': 'Avg Rating', 'vehicle_count': 'Records', 'total_sales': 'Total Sales'}
    display_df = comp.rename(columns={k: v for k, v in display_cols.items() if k in comp.columns})
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info('Manufacturer comparison requires manufacturer and metric columns.')

# Multi-manufacturer comparison tool
st.markdown('<br>', unsafe_allow_html=True)
section_header('Compare Manufacturers', 'Select 2 or more to compare side by side')
all_mfrs = sorted(df['manufacturer'].dropna().unique().tolist()) if 'manufacturer' in df.columns else []
selected_mfrs = st.multiselect('Select Manufacturers', options=all_mfrs, default=[], key='mfr_compare')
if len(selected_mfrs) >= 2:
    df_sel = df[df['manufacturer'].isin(selected_mfrs)]
    comp_sel = manufacturer_comparison(df_sel)
    if not comp_sel.empty:
        display_cols = {'manufacturer': 'Manufacturer', 'model_name': 'Models', 'avg_range_km': 'Avg Range (km)',
                        'avg_battery_kwh': 'Avg Battery (kWh)', 'avg_price_usd': 'Avg Price (USD)',
                        'avg_rating': 'Avg Rating', 'vehicle_count': 'Records'}
        display_df = comp_sel.rename(columns={k: v for k, v in display_cols.items() if k in comp_sel.columns})
        st.dataframe(display_df, use_container_width=True, hide_index=True)
elif len(selected_mfrs) == 1:
    st.info('Select at least 2 manufacturers to compare.')
else:
    st.info('Select 2 or more manufacturers from the list above.')

# Heatmap
st.markdown('<br>', unsafe_allow_html=True)
section_header('Battery Technology Heatmap', 'Vehicle count by manufacturer × battery type')
st.plotly_chart(chart_manufacturer_heatmap(df), use_container_width=True, config={'displayModeBar': False})

# Ratings
section_header('Customer Ratings by Manufacturer')
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(chart_customer_rating(df, group_by='manufacturer'), use_container_width=True, config={'displayModeBar': False})
with col2:
    st.plotly_chart(chart_customer_rating(df, group_by='category'), use_container_width=True, config={'displayModeBar': False})

with st.expander('ℹ️ Market share methodology'):
    st.markdown("""
    - Market share is calculated **relative to the currently filtered dataset**, not global market data.
    - Sales metric uses `annual_sales_units` when available; falls back to vehicle record count.
    - Comparison metrics use simple averages — not sales-weighted averages.
    - Data is synthetic demonstration data, not real manufacturer statistics.
    """)
