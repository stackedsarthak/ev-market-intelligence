"""
EV Market Intelligence — Customer Insights
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.data_loader import load_bundled_data
from src.preprocessing import preprocess, apply_filters
from src.metrics import avg_customer_rating, rating_by_manufacturer, rating_by_category
from src.charts import chart_customer_rating
from src.ui_components import (inject_global_css, page_header, data_source_badge, section_header,
                                kpi_card, empty_state, filter_status_bar, build_sidebar_filters,
                                show_warnings)

st.set_page_config(page_title="Customer Insights · EV Market", page_icon="⭐", layout="wide")
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

page_header("Customer Insights", "Satisfaction ratings, model comparisons, and review analysis.", "⭐")
data_source_badge(is_uploaded)
show_warnings(data_warnings)
filter_status_bar(df, df_full, {})

if len(df) == 0:
    empty_state()
    st.stop()

has_ratings = "customer_rating" in df.columns and df["customer_rating"].notna().any()

if not has_ratings:
    st.markdown("""
    <div style="background:#121A2B;border:1px dashed #253554;border-radius:10px;padding:40px;text-align:center;">
        <div style="font-size:36px;margin-bottom:12px">⭐</div>
        <div style="color:#F5F7FB;font-size:15px;font-weight:600;margin-bottom:8px">Customer Rating Data Not Available</div>
        <div style="color:#A8B3C7;font-size:12px;">
            The current dataset does not contain <code>customer_rating</code> values.<br>
            Upload a dataset with a <code>customer_rating</code> column (values 1–5) to enable this page.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── KPIs ────────────────────────────────────────────────────────────────────
section_header("Rating Overview")
k1, k2, k3, k4 = st.columns(4)
with k1:
    avg_r = avg_customer_rating(df)
    kpi_card("Avg Customer Rating", f"{avg_r:.2f} / 5.0" if avg_r else "N/A",
             f"{df['customer_rating'].notna().sum():,} rated vehicles")
with k2:
    kpi_card("Rated Vehicles", f"{df['customer_rating'].notna().sum():,}", f"of {len(df):,} total")
with k3:
    top_mfr_rated = rating_by_manufacturer(df, min_count=5)
    if not top_mfr_rated.empty:
        kpi_card("Top Rated Maker", top_mfr_rated.iloc[0]["manufacturer"],
                 f"{top_mfr_rated.iloc[0]['avg_rating']:.2f}/5.0")
    else:
        kpi_card("Top Rated Maker", "N/A", "Need 5+ ratings")
with k4:
    top_cat_rated = rating_by_category(df, min_count=5)
    if not top_cat_rated.empty:
        kpi_card("Top Rated Category", top_cat_rated.iloc[0]["category"],
                 f"{top_cat_rated.iloc[0]['avg_rating']:.2f}/5.0")
    else:
        kpi_card("Top Rated Category", "N/A", "Need 5+ ratings")

st.markdown("<br>", unsafe_allow_html=True)

# ─── By Manufacturer ──────────────────────────────────────────────────────────
section_header("Ratings by Manufacturer", "Minimum 5 rated vehicles required per manufacturer")
col1, col2 = st.columns([3, 2])
with col1:
    st.plotly_chart(chart_customer_rating(df, group_by="manufacturer"),
                    use_container_width=True, config={"displayModeBar": False})
with col2:
    mfr_rated = rating_by_manufacturer(df, min_count=5)
    if not mfr_rated.empty:
        st.dataframe(mfr_rated.rename(columns={"manufacturer": "Manufacturer",
                                                "avg_rating": "Avg Rating",
                                                "rating_count": "Rated Vehicles"}),
                     use_container_width=True, hide_index=True)

# ─── By Category ─────────────────────────────────────────────────────────────
section_header("Ratings by Category")
col3, col4 = st.columns([3, 2])
with col3:
    st.plotly_chart(chart_customer_rating(df, group_by="category"),
                    use_container_width=True, config={"displayModeBar": False})
with col4:
    cat_rated = rating_by_category(df, min_count=5)
    if not cat_rated.empty:
        st.dataframe(cat_rated.rename(columns={"category": "Category",
                                                "avg_rating": "Avg Rating",
                                                "rating_count": "Rated Vehicles"}),
                     use_container_width=True, hide_index=True)

# ─── Distribution ─────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Rating Distribution")
rating_data = df[["customer_rating"]].dropna()
if len(rating_data) > 0:
    fig_hist = px.histogram(rating_data, x="customer_rating", nbins=20,
                            title="Distribution of Customer Ratings",
                            labels={"customer_rating": "Rating (1–5)", "count": "Count"},
                            color_discrete_sequence=["#00D4FF"])
    fig_hist.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                            font_color="#A8B3C7", height=320)
    st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

# ─── Rating vs Range ──────────────────────────────────────────────────────────
if "range_km" in df.columns:
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Rating vs Driving Range")
    sub = df.dropna(subset=["customer_rating", "range_km"])
    if len(sub) > 20:
        corr = sub["customer_rating"].corr(sub["range_km"])
        color_col = "category" if "category" in sub.columns else None
        plot_sub = sub.sample(2000, random_state=42) if len(sub) > 2000 else sub
        fig_rr = px.scatter(plot_sub, x="range_km", y="customer_rating", color=color_col,
                            title=f"Customer Rating vs Driving Range (r={corr:.2f})",
                            labels={"range_km": "Driving Range (km)", "customer_rating": "Customer Rating"},
                            opacity=0.6,
                            color_discrete_sequence=["#00D4FF","#3DDE91","#FFB347","#FF6B6B","#9B59B6",
                                                      "#F39C12","#1ABC9C","#E74C3C","#3498DB","#2ECC71",
                                                      "#E67E22","#8E44AD","#16A085","#D35400","#2980B9"])
        fig_rr.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                              font_color="#A8B3C7", height=380)
        st.plotly_chart(fig_rr, use_container_width=True, config={"displayModeBar": False})
        st.caption(f"Pearson r={corr:.2f}. Correlation does not imply causation.")

# ─── Rating vs Price ──────────────────────────────────────────────────────────
if "price_usd" in df.columns:
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("Rating vs Price")
    sub2 = df.dropna(subset=["customer_rating", "price_usd"])
    if len(sub2) > 20:
        corr2 = sub2["customer_rating"].corr(sub2["price_usd"])
        color_col2 = "category" if "category" in sub2.columns else None
        plot_sub2 = sub2.sample(2000, random_state=42) if len(sub2) > 2000 else sub2
        fig_rp = px.scatter(plot_sub2, x="price_usd", y="customer_rating", color=color_col2,
                            title=f"Customer Rating vs Price (r={corr2:.2f})",
                            labels={"price_usd": "Price (USD)", "customer_rating": "Customer Rating"},
                            opacity=0.6,
                            color_discrete_sequence=["#00D4FF","#3DDE91","#FFB347","#FF6B6B","#9B59B6",
                                                      "#F39C12","#1ABC9C","#E74C3C","#3498DB","#2ECC71",
                                                      "#E67E22","#8E44AD","#16A085","#D35400","#2980B9"])
        fig_rp.update_layout(paper_bgcolor="#121A2B", plot_bgcolor="#182338",
                              font_color="#A8B3C7", height=380)
        st.plotly_chart(fig_rp, use_container_width=True, config={"displayModeBar": False})

# ─── Model-level ratings ──────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("Top Rated Vehicle Models")
model_cols = [c for c in ["manufacturer", "model_name", "category",
                           "customer_rating", "range_km", "price_usd"] if c in df.columns]
model_df = (df[model_cols]
            .dropna(subset=["customer_rating"])
            .sort_values("customer_rating", ascending=False)
            .head(30))
st.dataframe(model_df, use_container_width=True, hide_index=True, height=350)
col_dl, _ = st.columns([1, 3])
with col_dl:
    st.download_button("Download Rated Models CSV", model_df.to_csv(index=False),
                        "ev_rated_models.csv", "text/csv")

st.markdown("---")
st.caption("Ratings reflect the demonstration dataset only. Rating scale: 1.0 (lowest) – 5.0 (highest). "
           "Small samples may not represent real-world customer sentiment.")
