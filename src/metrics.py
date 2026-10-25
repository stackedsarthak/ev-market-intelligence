"""
EV Market Intelligence — Metrics
==================================
Calculates KPIs, market share, growth rates, and rankings from a DataFrame.
All functions protect against division by zero and missing data.
"""

import pandas as pd
import numpy as np
from typing import Optional


def safe_div(numerator, denominator, default=0.0):
    """Safe division returning default when denominator is zero or NaN."""
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return default
    return numerator / denominator


# ─────────────────────────────────────────────────────────────────────────────
# KPI Calculations
# ─────────────────────────────────────────────────────────────────────────────

def total_sales(df: pd.DataFrame) -> Optional[float]:
    """Total annual_sales_units in the dataset."""
    if "annual_sales_units" not in df.columns:
        return None
    val = df["annual_sales_units"].sum(skipna=True)
    return float(val) if not pd.isna(val) else None


def total_vehicles(df: pd.DataFrame) -> int:
    """Total number of vehicle records."""
    return len(df)


def unique_manufacturers(df: pd.DataFrame) -> int:
    if "manufacturer" not in df.columns:
        return 0
    return df["manufacturer"].nunique()


def unique_models(df: pd.DataFrame) -> int:
    if "model_name" not in df.columns:
        return 0
    return df["model_name"].nunique()


def avg_range(df: pd.DataFrame) -> Optional[float]:
    if "range_km" not in df.columns or df["range_km"].isna().all():
        return None
    return float(df["range_km"].mean(skipna=True))


def avg_battery_capacity(df: pd.DataFrame) -> Optional[float]:
    if "battery_capacity_kwh" not in df.columns or df["battery_capacity_kwh"].isna().all():
        return None
    return float(df["battery_capacity_kwh"].mean(skipna=True))


def avg_customer_rating(df: pd.DataFrame) -> Optional[float]:
    if "customer_rating" not in df.columns or df["customer_rating"].isna().all():
        return None
    return float(df["customer_rating"].mean(skipna=True))


def leading_manufacturer(df: pd.DataFrame) -> Optional[str]:
    """Manufacturer with highest total sales or most vehicle records."""
    if "manufacturer" not in df.columns:
        return None
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        result = df.groupby("manufacturer")["annual_sales_units"].sum().idxmax()
    else:
        result = df["manufacturer"].value_counts().idxmax()
    return str(result) if result else None


def top_category(df: pd.DataFrame) -> Optional[str]:
    """Category with highest total sales or most records."""
    if "category" not in df.columns:
        return None
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        result = df.groupby("category")["annual_sales_units"].sum().idxmax()
    else:
        result = df["category"].value_counts().idxmax()
    return str(result) if result else None


# ─────────────────────────────────────────────────────────────────────────────
# Market Share
# ─────────────────────────────────────────────────────────────────────────────

def manufacturer_market_share(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute manufacturer market share within the filtered dataset.
    Uses annual_sales_units if available; falls back to record count.
    Returns DataFrame with columns: manufacturer, sales, share_pct.
    """
    if "manufacturer" not in df.columns:
        return pd.DataFrame(columns=["manufacturer", "sales", "share_pct"])
    
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        agg = df.groupby("manufacturer")["annual_sales_units"].sum().reset_index()
        agg.columns = ["manufacturer", "sales"]
    else:
        agg = df["manufacturer"].value_counts().reset_index()
        agg.columns = ["manufacturer", "sales"]
    
    total = agg["sales"].sum()
    agg["share_pct"] = (agg["sales"] / max(total, 1) * 100).round(2)
    return agg.sort_values("sales", ascending=False).reset_index(drop=True)


def category_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Category-level sales or record count."""
    if "category" not in df.columns:
        return pd.DataFrame(columns=["category", "sales", "share_pct"])
    
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        agg = df.groupby("category")["annual_sales_units"].sum().reset_index()
        agg.columns = ["category", "sales"]
    else:
        agg = df["category"].value_counts().reset_index()
        agg.columns = ["category", "sales"]
    
    total = agg["sales"].sum()
    agg["share_pct"] = (agg["sales"] / max(total, 1) * 100).round(2)
    return agg.sort_values("sales", ascending=False).reset_index(drop=True)


def annual_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Annual sales aggregated by model_year."""
    if "model_year" not in df.columns:
        return pd.DataFrame(columns=["model_year", "sales"])
    
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        agg = df.groupby("model_year")["annual_sales_units"].sum().reset_index()
        agg.columns = ["model_year", "sales"]
    else:
        agg = df.groupby("model_year").size().reset_index()
        agg.columns = ["model_year", "sales"]
    
    return agg.sort_values("model_year").reset_index(drop=True)


def yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year growth rate. Requires ≥ 2 years of data."""
    trend = annual_sales_trend(df)
    if len(trend) < 2:
        return pd.DataFrame(columns=["model_year", "sales", "yoy_growth_pct"])
    
    trend = trend.sort_values("model_year").reset_index(drop=True)
    trend["yoy_growth_pct"] = trend["sales"].pct_change() * 100
    # Handle division by zero (when previous year is 0)
    trend.loc[trend["yoy_growth_pct"] == float("inf"), "yoy_growth_pct"] = np.nan
    trend.loc[trend["yoy_growth_pct"] == float("-inf"), "yoy_growth_pct"] = np.nan
    return trend


def battery_tech_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Distribution of battery technologies."""
    if "battery_type" not in df.columns:
        return pd.DataFrame(columns=["battery_type", "count", "share_pct"])
    
    agg = df["battery_type"].value_counts().reset_index()
    agg.columns = ["battery_type", "count"]
    total = agg["count"].sum()
    agg["share_pct"] = (agg["count"] / max(total, 1) * 100).round(2)
    return agg


def avg_range_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Average driving range by vehicle category."""
    if "category" not in df.columns or "range_km" not in df.columns:
        return pd.DataFrame(columns=["category", "avg_range_km", "count"])
    
    agg = df.groupby("category").agg(
        avg_range_km=("range_km", "mean"),
        count=("range_km", "count")
    ).reset_index()
    return agg.sort_values("avg_range_km", ascending=False).reset_index(drop=True)


def avg_range_by_battery_type(df: pd.DataFrame) -> pd.DataFrame:
    """Average driving range by battery technology."""
    if "battery_type" not in df.columns or "range_km" not in df.columns:
        return pd.DataFrame(columns=["battery_type", "avg_range_km", "count"])
    
    agg = df.groupby("battery_type").agg(
        avg_range_km=("range_km", "mean"),
        avg_battery_kwh=("battery_capacity_kwh", "mean"),
        count=("range_km", "count")
    ).reset_index()
    return agg.sort_values("avg_range_km", ascending=False).reset_index(drop=True)


def manufacturer_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Manufacturer-level comparison table."""
    if "manufacturer" not in df.columns:
        return pd.DataFrame()
    
    agg_dict = {
        "model_name": ("model_name", "nunique"),
        "avg_range_km": ("range_km", "mean"),
        "avg_battery_kwh": ("battery_capacity_kwh", "mean"),
        "avg_price_usd": ("price_usd", "mean") if "price_usd" in df.columns else None,
        "avg_rating": ("customer_rating", "mean") if "customer_rating" in df.columns else None,
        "vehicle_count": ("vehicle_id", "count") if "vehicle_id" in df.columns else ("manufacturer", "count"),
    }
    
    # Build agg dict dynamically based on available columns
    safe_agg = {}
    for key, val in agg_dict.items():
        if val and val[0] in df.columns:
            safe_agg[key] = val
    
    if not safe_agg:
        return pd.DataFrame()
    
    agg = df.groupby("manufacturer").agg(**safe_agg).reset_index()
    
    # Add sales if available
    if "annual_sales_units" in df.columns:
        sales_agg = df.groupby("manufacturer")["annual_sales_units"].sum().reset_index()
        sales_agg.columns = ["manufacturer", "total_sales"]
        agg = agg.merge(sales_agg, on="manufacturer", how="left")
    
    # Round numeric columns
    for col in agg.select_dtypes(include=np.number).columns:
        agg[col] = agg[col].round(2)
    
    return agg.sort_values("vehicle_count" if "vehicle_count" in agg.columns else "manufacturer",
                            ascending=False).reset_index(drop=True)


def rating_by_manufacturer(df: pd.DataFrame, min_count: int = 5) -> pd.DataFrame:
    """Average customer rating by manufacturer, requiring min_count ratings."""
    if "customer_rating" not in df.columns or "manufacturer" not in df.columns:
        return pd.DataFrame(columns=["manufacturer", "avg_rating", "rating_count"])
    
    agg = df.groupby("manufacturer")["customer_rating"].agg(
        avg_rating="mean", rating_count="count"
    ).reset_index()
    # Only include manufacturers with sufficient ratings
    agg = agg[agg["rating_count"] >= min_count]
    agg["avg_rating"] = agg["avg_rating"].round(2)
    return agg.sort_values("avg_rating", ascending=False).reset_index(drop=True)


def rating_by_category(df: pd.DataFrame, min_count: int = 5) -> pd.DataFrame:
    """Average customer rating by category."""
    if "customer_rating" not in df.columns or "category" not in df.columns:
        return pd.DataFrame(columns=["category", "avg_rating", "rating_count"])
    
    agg = df.groupby("category")["customer_rating"].agg(
        avg_rating="mean", rating_count="count"
    ).reset_index()
    agg = agg[agg["rating_count"] >= min_count]
    agg["avg_rating"] = agg["avg_rating"].round(2)
    return agg.sort_values("avg_rating", ascending=False).reset_index(drop=True)


def sales_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """Vehicle count / sales by manufacturing country."""
    if "manufacturing_country" not in df.columns:
        return pd.DataFrame(columns=["manufacturing_country", "count", "share_pct"])
    
    if "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any():
        agg = df.groupby("manufacturing_country")["annual_sales_units"].sum().reset_index()
        agg.columns = ["manufacturing_country", "count"]
    else:
        agg = df["manufacturing_country"].value_counts().reset_index()
        agg.columns = ["manufacturing_country", "count"]
    
    total = agg["count"].sum()
    agg["share_pct"] = (agg["count"] / max(total, 1) * 100).round(2)
    return agg.sort_values("count", ascending=False).reset_index(drop=True)


def co2_savings_summary(df: pd.DataFrame) -> dict:
    """Summarize CO2 savings estimates."""
    if "co2_saved_tons_per_year" not in df.columns:
        return {}
    
    col = df["co2_saved_tons_per_year"].dropna()
    if len(col) == 0:
        return {}
    
    return {
        "total_co2_saved_tons": float(col.sum()),
        "avg_co2_saved_per_vehicle": float(col.mean()),
        "max_co2_saved": float(col.max()),
        "min_co2_saved": float(col.min()),
        "vehicle_count": int(len(col)),
    }
