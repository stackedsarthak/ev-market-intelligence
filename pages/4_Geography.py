"""
EV Market Intelligence — Geography & Manufacturing
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import sales_by_country
from src.charts import chart_country_bar
from src.ui_components import (inject_global_css, page_header, data_source_badge, section_header,
                                kpi_card, empty_state, filter_status_bar, build_sidebar_filters, show_warnings)

# Manufacturer origin lookup (from dataset generation)
MANUFACTURER_ORIGIN = {
    'VoltAura': 'Germany', 'TerraMotors': 'USA', 'ZephyrEV': 'China',
    'NovaDrive': 'Japan', 'ArcLightning': 'South Korea', 'ClearPath': 'Germany',
    'HelixEV': 'USA', 'SolarSpeed': 'China', 'PinnacleAuto': 'Japan',
    'EcoWheels': 'India', 'KineticCharge': 'South Korea', 'PulseEV': 'France',
    'VelocityCore': 'USA', 'HorizonAuto': 'China', 'NexGen Motors': 'Germany',
}

st.set_page_config(page_title='Geography · EV Market', page_icon='🌍', layout='wide')
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

page_header('Geography & Manufacturing', 'Vehicle production distribution and manufacturing country analysis.', '🌍')
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {})

if len(df) == 0:
    empty_state()
    st.stop()

st.info('**Terminology Note:** "Manufacturing Country" = where the vehicle was assembled. "Manufacturer Origin" = the company headquarters country. These are different concepts.')

# Manufacturing Country Distribution
section_header('Manufacturing Country Distribution', 'Where vehicles in this dataset were produced')
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(chart_country_bar(df), use_container_width=True, config={'displayModeBar': False})
with col2:
    country_data = sales_by_country(df)
    if not country_data.empty:
        st.dataframe(country_data.rename(columns={'manufacturing_country': 'Country', 'count': 'Records/Sales', 'share_pct': 'Share (%)'}), use_container_width=True, hide_index=True)

# Manufacturer Origin
st.markdown('<br>', unsafe_allow_html=True)
section_header('Manufacturer Origin Countries', 'Headquarters country of each manufacturer (not manufacturing location)')
if 'manufacturer' in df.columns:
    mfr_df = pd.DataFrame([
        {'Manufacturer': mfr, 'Origin Country': origin}
        for mfr, origin in MANUFACTURER_ORIGIN.items()
        if mfr in df['manufacturer'].values
    ])
    if not mfr_df.empty:
        origin_counts = mfr_df.groupby('Origin Country').size().reset_index(name='Manufacturers')
        col3, col4 = st.columns(2)
        with col3:
            st.dataframe(mfr_df, use_container_width=True, hide_index=True)
        with col4:
            fig_origin = px.bar(origin_counts.sort_values('Manufacturers'), y='Origin Country', x='Manufacturers',
                                orientation='h', title='Manufacturers by Origin Country',
                                color_discrete_sequence=['#00D4FF'])
            fig_origin.update_layout(paper_bgcolor='#121A2B', plot_bgcolor='#182338', font_color='#A8B3C7', height=350)
            st.plotly_chart(fig_origin, use_container_width=True, config={'displayModeBar': False})

# Manufacturing cross-tab
if 'manufacturer' in df.columns and 'manufacturing_country' in df.columns:
    st.markdown('<br>', unsafe_allow_html=True)
    section_header('Manufacturer × Manufacturing Country', 'Where each manufacturer produces vehicles in this dataset')
    cross = pd.crosstab(df['manufacturer'], df['manufacturing_country'])
    fig_heat = go.Figure(go.Heatmap(
        z=cross.values, x=cross.columns.tolist(), y=cross.index.tolist(),
        colorscale=[[0, '#182338'], [0.5, '#00D4FF'], [1, '#3DDE91']],
        hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Count: %{z}<extra></extra>',
        text=cross.values, texttemplate='%{text}', textfont=dict(color='#F5F7FB', size=10),
    ))
    fig_heat.update_layout(paper_bgcolor='#121A2B', plot_bgcolor='#182338', font_color='#A8B3C7',
                           height=max(400, len(cross) * 28 + 80), title='Vehicle Records by Manufacturer × Manufacturing Country')
    st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

# Category by Country
if 'manufacturing_country' in df.columns and 'category' in df.columns:
    st.markdown('<br>', unsafe_allow_html=True)
    section_header('Vehicle Category by Manufacturing Country')
    cat_country = df.groupby(['manufacturing_country', 'category']).size().reset_index(name='count')
    top_countries = df['manufacturing_country'].value_counts().head(6).index.tolist()
    cat_country_top = cat_country[cat_country['manufacturing_country'].isin(top_countries)]
    if not cat_country_top.empty:
        fig_cc = px.bar(cat_country_top, x='manufacturing_country', y='count', color='category',
                        title='Category Distribution by Top Manufacturing Countries',
                        labels={'count': 'Records', 'manufacturing_country': 'Country'},
                        barmode='stack',
                        color_discrete_sequence=['#00D4FF','#3DDE91','#FFB347','#FF6B6B','#9B59B6',
                                                  '#F39C12','#1ABC9C','#E74C3C','#3498DB','#2ECC71',
                                                  '#E67E22','#8E44AD','#16A085','#D35400','#2980B9'])
        fig_cc.update_layout(paper_bgcolor='#121A2B', plot_bgcolor='#182338', font_color='#A8B3C7', height=420)
        st.plotly_chart(fig_cc, use_container_width=True, config={'displayModeBar': False})

# Market Region
if 'market_region' in df.columns:
    st.markdown('<br>', unsafe_allow_html=True)
    section_header('Market Region Distribution')
    region_counts = df['market_region'].value_counts().reset_index()
    region_counts.columns = ['market_region', 'count']
    fig_r = px.pie(region_counts, names='market_region', values='count',
                   title='Vehicles by Market Region',
                   color_discrete_sequence=['#00D4FF','#3DDE91','#FFB347','#FF6B6B','#9B59B6','#F39C12'])
    fig_r.update_traces(hole=0.4)
    fig_r.update_layout(paper_bgcolor='#121A2B', font_color='#A8B3C7', height=380)
    col5, _ = st.columns([2, 1])
    with col5:
        st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})

st.markdown('---')
st.caption('Manufacturing country reflects assembly location. Component sourcing, vehicle sales geography, and manufacturer headquarters may differ.')
