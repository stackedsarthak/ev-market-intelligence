"""
EV Market Intelligence — Rule-Based Insight Generation
========================================================
Generates concise, data-backed insights from the filtered DataFrame.
All insights are traceable to the underlying data.
No external APIs required.
"""

import pandas as pd
import numpy as np
from typing import Optional
from src.metrics import (
    manufacturer_market_share, category_sales, annual_sales_trend,
    yoy_growth, avg_range_by_category, rating_by_manufacturer,
    battery_tech_distribution
)

MIN_RATING_COUNT = 10   # Minimum ratings for a manufacturer insight
MIN_GROWTH_YEARS = 3    # Minimum years needed for a growth insight
MIN_CATEGORY_COUNT = 10 # Minimum records for category insight


def _fmt_num(val, decimals=1) -> str:
    """Format a number for display."""
    if pd.isna(val):
        return "N/A"
    if abs(val) >= 1_000_000:
        return f"{val/1_000_000:.{decimals}f}M"
    if abs(val) >= 1_000:
        return f"{val/1_000:.{decimals}f}K"
    return f"{val:.{decimals}f}"


def insight_top_manufacturer(df: pd.DataFrame) -> Optional[str]:
    """Which manufacturer leads by sales or record count."""
    share = manufacturer_market_share(df)
    if share.empty:
        return None
    top = share.iloc[0]
    metric_label = "sales units" if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any() else "vehicle records"
    return (
        f"**{top['manufacturer']}** leads the current dataset with "
        f"**{_fmt_num(top['sales'])}** {metric_label}, representing "
        f"**{top['share_pct']:.1f}%** of the filtered market."
    )


def insight_top_category(df: pd.DataFrame) -> Optional[str]:
    """Which vehicle category leads."""
    cat = category_sales(df)
    if cat.empty:
        return None
    top = cat.iloc[0]
    return (
        f"**{top['category']}** is the most represented vehicle category, "
        f"accounting for **{top['share_pct']:.1f}%** of the filtered dataset."
    )


def insight_battery_tech(df: pd.DataFrame) -> Optional[str]:
    """Largest battery technology segment."""
    batt = battery_tech_distribution(df)
    if batt.empty or "battery_type" not in batt.columns:
        return None
    top = batt.iloc[0]
    return (
        f"**{top['battery_type']}** is the dominant battery chemistry in this dataset, "
        f"found in **{top['share_pct']:.1f}%** of vehicles ({int(top['count'])} records)."
    )


def insight_best_range_category(df: pd.DataFrame) -> Optional[str]:
    """Category with highest average range (min sample size check)."""
    if "range_km" not in df.columns:
        return None
    
    agg = avg_range_by_category(df)
    # Filter to categories with enough data
    agg = agg[agg["count"] >= MIN_CATEGORY_COUNT]
    if agg.empty:
        return None
    
    top = agg.iloc[0]
    return (
        f"**{top['category']}** vehicles have the highest average driving range "
        f"at **{top['avg_range_km']:.0f} km** (based on {int(top['count'])} records). "
        f"Note: range depends on battery size, weight, and driving conditions."
    )


def insight_best_rated_manufacturer(df: pd.DataFrame) -> Optional[str]:
    """Best-rated manufacturer (with minimum sample size)."""
    rated = rating_by_manufacturer(df, min_count=MIN_RATING_COUNT)
    if rated.empty:
        return None
    top = rated.iloc[0]
    return (
        f"**{top['manufacturer']}** has the highest average customer rating "
        f"of **{top['avg_rating']:.1f}/5.0** "
        f"(based on {int(top['rating_count'])} rated vehicles). "
        f"Ratings reflect the demonstration dataset only."
    )


def insight_yoy_growth(df: pd.DataFrame) -> Optional[str]:
    """Year-over-year sales growth — only when sufficient history exists."""
    trend = yoy_growth(df)
    if len(trend) < MIN_GROWTH_YEARS:
        return None
    
    # Get last completed year and previous year
    trend = trend.dropna(subset=["yoy_growth_pct"]).tail(2)
    if len(trend) < 2:
        return None
    
    latest = trend.iloc[-1]
    year = int(latest["model_year"])
    growth_pct = latest["yoy_growth_pct"]
    
    if abs(growth_pct) < 0.1:
        direction = "flat"
        desc = f"essentially flat ({growth_pct:+.1f}%)"
    elif growth_pct > 0:
        direction = "growth"
        desc = f"up **{growth_pct:.1f}%**"
    else:
        direction = "decline"
        desc = f"down **{abs(growth_pct):.1f}%**"
    
    return (
        f"Dataset records for **{year}** show {desc} compared to the prior year. "
        f"This reflects record counts in the demonstration dataset, not verified market statistics."
    )


def insight_price_range_correlation(df: pd.DataFrame) -> Optional[str]:
    """Whether higher-priced vehicles tend to have more range."""
    if "price_usd" not in df.columns or "range_km" not in df.columns:
        return None
    
    sub = df[["price_usd", "range_km"]].dropna()
    if len(sub) < 50:
        return None
    
    corr = sub["price_usd"].corr(sub["range_km"])
    if pd.isna(corr):
        return None
    
    if corr > 0.5:
        strength = "strong positive"
        desc = "higher-priced vehicles tend to offer significantly more range"
    elif corr > 0.2:
        strength = "moderate positive"
        desc = "higher-priced vehicles tend to offer somewhat more range"
    elif corr < -0.2:
        strength = "negative"
        desc = "price and range do not follow a clear positive trend in this dataset"
    else:
        strength = "weak"
        desc = "price and range are weakly correlated in this dataset"
    
    return (
        f"There is a **{strength} correlation** (r = {corr:.2f}) between price and driving range — "
        f"{desc}."
    )


def generate_all_insights(df: pd.DataFrame) -> list[str]:
    """
    Generate all available insights from the filtered dataset.
    Returns a list of markdown strings. Empty list if no insights possible.
    """
    if df is None or len(df) == 0:
        return ["ℹ️ No data available for insight generation with the current filters."]
    
    insight_fns = [
        insight_top_manufacturer,
        insight_top_category,
        insight_battery_tech,
        insight_best_range_category,
        insight_best_rated_manufacturer,
        insight_yoy_growth,
        insight_price_range_correlation,
    ]
    
    insights = []
    for fn in insight_fns:
        try:
            result = fn(df)
            if result:
                insights.append(result)
        except Exception:
            pass  # Skip failed insights silently
    
    if not insights:
        insights.append("ℹ️ Insufficient data to generate insights with the current filters. Try expanding the filter range.")
    
    return insights
