"""
EV Market Intelligence — UI Components
=========================================
Reusable Streamlit UI widgets: KPI cards, sidebar, empty states, warnings.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional


# ─── Color palette (matching design system) ────────────────────────────────
_CYAN = "#00D4FF"
_GREEN = "#3DDE91"
_AMBER = "#FFB347"
_CORAL = "#FF6B6B"
_BG = "#121A2B"
_SURFACE = "#182338"
_BORDER = "#253554"
_TEXT = "#F5F7FB"
_TEXT_DIM = "#A8B3C7"


def inject_global_css():
    """Inject global CSS for consistent styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0D1525 !important;
        border-right: 1px solid #253554;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* KPI card */
    .kpi-card {
        background: #121A2B;
        border: 1px solid #253554;
        border-radius: 10px;
        padding: 16px 18px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #00D4FF; }
    
    .kpi-label {
        color: #A8B3C7;
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .kpi-value {
        color: #F5F7FB;
        font-size: 26px;
        font-weight: 700;
        line-height: 1.1;
        margin: 4px 0;
    }
    .kpi-sub {
        color: #A8B3C7;
        font-size: 11px;
        margin-top: 2px;
    }
    .kpi-delta-pos { color: #3DDE91; font-size: 12px; }
    .kpi-delta-neg { color: #FF6B6B; font-size: 12px; }
    
    /* Section header */
    .section-header {
        border-left: 3px solid #00D4FF;
        padding-left: 10px;
        margin-bottom: 1rem;
    }
    .section-header h3 {
        color: #F5F7FB;
        font-size: 15px;
        font-weight: 600;
        margin: 0;
    }
    .section-header p {
        color: #A8B3C7;
        font-size: 12px;
        margin: 2px 0 0 0;
    }
    
    /* Data badge */
    .data-badge {
        display: inline-block;
        background: rgba(255, 179, 71, 0.12);
        border: 1px solid rgba(255, 179, 71, 0.4);
        color: #FFB347;
        border-radius: 5px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 500;
        margin-bottom: 12px;
    }
    
    /* Insight card */
    .insight-card {
        background: #121A2B;
        border: 1px solid #253554;
        border-left: 3px solid #3DDE91;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .insight-card p { color: #F5F7FB; font-size: 13px; margin: 0; }
    
    /* Filter info bar */
    .filter-bar {
        background: #0D1525;
        border: 1px solid #253554;
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 11px;
        color: #A8B3C7;
        margin-bottom: 12px;
    }
    
    /* Empty state */
    .empty-state {
        background: #121A2B;
        border: 1px dashed #253554;
        border-radius: 10px;
        padding: 40px 20px;
        text-align: center;
        color: #A8B3C7;
        font-size: 13px;
    }
    
    /* Streamlit dataframe */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    
    /* Metric overrides */
    [data-testid="stMetricValue"] { color: #F5F7FB !important; }
    [data-testid="stMetricLabel"] { color: #A8B3C7 !important; }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #182338 !important;
        border-radius: 6px !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        color: #A8B3C7;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #00D4FF !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0B1020; }
    ::-webkit-scrollbar-thumb { background: #253554; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #00D4FF; }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a consistent page header."""
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f'<p style="color: {_TEXT_DIM}; font-size: 13px; margin-top: -8px;">{subtitle}</p>',
                    unsafe_allow_html=True)
    st.markdown("---")


def data_source_badge(is_uploaded: bool = False):
    """Show data source label."""
    if is_uploaded:
        st.markdown('<span class="data-badge">📂 User-uploaded dataset</span>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<span class="data-badge">⚗️ Synthetic demonstration data — not verified real-world statistics</span>',
            unsafe_allow_html=True
        )


def kpi_card(label: str, value: str, sub: str = "", delta: Optional[float] = None):
    """Render a KPI card with optional delta indicator."""
    delta_html = ""
    if delta is not None:
        direction = "▲" if delta >= 0 else "▼"
        cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        delta_html = f'<div class="{cls}">{direction} {abs(delta):.1f}%</div>'
    
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, description: str = ""):
    """Render a section header with a left accent bar."""
    desc_html = f'<p>{description}</p>' if description else ""
    st.markdown(f"""
    <div class="section-header">
        <h3>{title}</h3>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def insight_card(text: str, index: int = 0):
    """Render a single insight card."""
    icons = ["🏆", "📊", "🔋", "🚗", "⭐", "📈", "🌱", "💡"]
    icon = icons[index % len(icons)]
    st.markdown(f"""
    <div class="insight-card">
        <p>{icon} &nbsp;{text}</p>
    </div>
    """, unsafe_allow_html=True)


def empty_state(message: str = "No data matches the current filters.",
                hint: str = "Try expanding or resetting your filters."):
    """Render an empty state message."""
    st.markdown(f"""
    <div class="empty-state">
        <div style="font-size: 32px; margin-bottom: 10px;">🔍</div>
        <div style="font-weight: 600; font-size: 14px; color: #F5F7FB; margin-bottom: 6px;">{message}</div>
        <div style="font-size: 12px;">{hint}</div>
    </div>
    """, unsafe_allow_html=True)


def filter_status_bar(df_filtered: pd.DataFrame, df_total: pd.DataFrame, filters: dict):
    """Show a compact filter status bar."""
    total = len(df_total)
    filtered = len(df_filtered)
    pct = (filtered / max(total, 1)) * 100
    
    active = [f"**{k}**: {v}" for k, v in filters.items() if v]
    filter_str = "  |  ".join(active) if active else "No active filters"
    
    st.markdown(
        f'<div class="filter-bar">📋 Showing <strong>{filtered:,}</strong> of {total:,} records ({pct:.1f}%)  ·  {filter_str}</div>',
        unsafe_allow_html=True
    )


def format_number(val, decimals: int = 1, prefix: str = "", suffix: str = "") -> str:
    """Format a number for display in KPI cards."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    if abs(val) >= 1_000_000:
        return f"{prefix}{val/1_000_000:.{decimals}f}M{suffix}"
    if abs(val) >= 1_000:
        return f"{prefix}{val/1_000:.{decimals}f}K{suffix}"
    return f"{prefix}{val:.{decimals}f}{suffix}"


def sidebar_logo():
    """Render the sidebar logo and branding."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 16px 0 8px 0;">
        <div style="font-size: 32px; margin-bottom: 4px;">⚡</div>
        <div style="color: #00D4FF; font-size: 16px; font-weight: 700; letter-spacing: 0.05em;">
            EV MARKET
        </div>
        <div style="color: #F5F7FB; font-size: 13px; font-weight: 600;">
            INTELLIGENCE
        </div>
        <div style="color: #A8B3C7; font-size: 10px; margin-top: 4px; font-style: italic;">
            Understand the Market. Accelerate the Future.
        </div>
    </div>
    <hr style="border-color: #253554; margin: 8px 0 16px 0;">
    """, unsafe_allow_html=True)


def build_sidebar_filters(df: pd.DataFrame) -> dict:
    """
    Build sidebar filter widgets and return filter dict.
    Returns dict with keys: years, manufacturers, categories, battery_types, countries.
    """
    sidebar_logo()
    st.sidebar.markdown("### 🎛️ Filters")
    
    filters = {}
    
    # Year range
    if "model_year" in df.columns:
        years_available = sorted(df["model_year"].dropna().unique().astype(int))
        if len(years_available) >= 2:
            year_range = st.sidebar.slider(
                "Model Year Range",
                min_value=int(min(years_available)),
                max_value=int(max(years_available)),
                value=(int(min(years_available)), int(max(years_available))),
                key="sidebar_year_range",
            )
            filters["years"] = year_range
        else:
            filters["years"] = None
    else:
        filters["years"] = None
    
    # Manufacturer multiselect
    if "manufacturer" in df.columns:
        all_mfrs = sorted(df["manufacturer"].dropna().unique().tolist())
        selected_mfrs = st.sidebar.multiselect(
            "Manufacturer",
            options=all_mfrs,
            default=[],
            key="sidebar_manufacturers",
        )
        filters["manufacturers"] = selected_mfrs if selected_mfrs else None
    else:
        filters["manufacturers"] = None
    
    # Vehicle category multiselect
    if "category" in df.columns:
        all_cats = sorted(df["category"].dropna().unique().tolist())
        selected_cats = st.sidebar.multiselect(
            "Vehicle Category",
            options=all_cats,
            default=[],
            key="sidebar_categories",
        )
        filters["categories"] = selected_cats if selected_cats else None
    else:
        filters["categories"] = None
    
    # Battery type multiselect
    if "battery_type" in df.columns:
        all_batt = sorted(df["battery_type"].dropna().unique().tolist())
        selected_batt = st.sidebar.multiselect(
            "Battery Technology",
            options=all_batt,
            default=[],
            key="sidebar_battery_types",
        )
        filters["battery_types"] = selected_batt if selected_batt else None
    else:
        filters["battery_types"] = None
    
    # Manufacturing country
    if "manufacturing_country" in df.columns:
        all_countries = sorted(df["manufacturing_country"].dropna().unique().tolist())
        selected_countries = st.sidebar.multiselect(
            "Manufacturing Country",
            options=all_countries,
            default=[],
            key="sidebar_countries",
        )
        filters["countries"] = selected_countries if selected_countries else None
    else:
        filters["countries"] = None
    
    # Reset button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True, key="sidebar_reset"):
        # Clear session state for filter keys
        for key in ["sidebar_year_range", "sidebar_manufacturers", "sidebar_categories",
                    "sidebar_battery_types", "sidebar_countries"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    return filters


def show_warnings(warnings: list[str]):
    """Display preprocessing warnings."""
    if warnings:
        with st.expander(f"⚠️ Data Quality Notices ({len(warnings)})", expanded=False):
            for w in warnings:
                st.warning(w)
