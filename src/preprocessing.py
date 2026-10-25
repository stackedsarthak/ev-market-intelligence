"""
EV Market Intelligence — Preprocessing
========================================
Cleans, validates, and normalizes the raw DataFrame.
All transformations are documented and reversible.
"""

import pandas as pd
import numpy as np
from typing import Optional


# ─── Category normalization map ───────────────────────────────────────────────
CATEGORY_ALIASES = {
    "micro city": "Micro City Car",
    "hatchback": "Hatchback",
    "sedan": "Sedan",
    "luxury sedan": "Luxury Sedan",
    "compact suv": "Compact SUV",
    "crossover": "Crossover",
    "full-size suv": "Full-size SUV",
    "full size suv": "Full-size SUV",
    "luxury suv": "Luxury SUV",
    "sports car": "Sports Car",
    "pickup truck": "Pickup Truck",
    "pickup": "Pickup Truck",
    "van / mpv": "Van / MPV",
    "van": "Van / MPV",
    "mpv": "Van / MPV",
    "two-wheeler scooter": "Two-Wheeler Scooter",
    "two wheeler": "Two-Wheeler Scooter",
    "scooter": "Two-Wheeler Scooter",
    "three-wheeler": "Three-Wheeler",
    "three wheeler": "Three-Wheeler",
    "electric bus": "Electric Bus",
    "bus": "Electric Bus",
    "electric truck": "Electric Truck",
    "truck": "Electric Truck",
}

BATTERY_ALIASES = {
    "lfp": "LFP",
    "lithium iron phosphate": "LFP",
    "nmc": "NMC",
    "nickel manganese cobalt": "NMC",
    "nca": "NCA",
    "nickel cobalt aluminum": "NCA",
    "solid state": "Solid-State",
    "solid-state": "Solid-State",
    "sodium ion": "Sodium-Ion",
    "sodium-ion": "Sodium-Ion",
}

# Rating must be between 1 and 5
RATING_MIN = 1.0
RATING_MAX = 5.0

# Numeric columns and their valid ranges (for range-clipping and anomaly detection)
NUMERIC_RANGES = {
    "battery_capacity_kwh":       (1,    600),
    "range_km":                   (30,   1500),
    "efficiency_wh_per_km":       (30,   1000),
    "motor_power_kw":             (1,    2000),
    "torque_nm":                  (5,    10000),
    "top_speed_kmph":             (20,   500),
    "acceleration_0_100_sec":     (1,    30),
    "max_dc_charging_kw":         (1,    500),
    "charging_dc_fast_time_min":  (5,    600),
    "charging_ac_time_hr":        (0.5,  72),
    "num_seats":                  (1,    100),
    "weight_kg":                  (50,   30000),
    "cargo_capacity_liters":      (5,    20000),
    "price_usd":                  (500,  2000000),
    "insurance_cost_usd_yearly":  (50,   50000),
    "warranty_years":             (1,    20),
    "resale_value_pct_3yr":       (10,   100),
    "safety_rating_stars":        (1,    5),
    "autonomous_level":           (0,    5),
    "co2_saved_tons_per_year":    (0,    50),
    "annual_sales_units":         (0,    5000000),
    "customer_rating":            (1,    5),
    "model_year":                 (2010, 2030),
    "battery_degradation_pct_5yr":(0,   100),
    "battery_cycle_life":         (100,  10000),
}


def safe_numeric(series: pd.Series, col_name: str) -> pd.Series:
    """Convert to numeric, coercing errors to NaN."""
    return pd.to_numeric(series, errors="coerce")


def normalize_category(val: str) -> str:
    """Normalize vehicle category to standard label."""
    if pd.isna(val):
        return val
    key = str(val).strip().lower()
    return CATEGORY_ALIASES.get(key, str(val).strip())


def normalize_battery_type(val: str) -> str:
    """Normalize battery type to standard label."""
    if pd.isna(val):
        return val
    key = str(val).strip().lower()
    return BATTERY_ALIASES.get(key, str(val).strip())


def preprocess(df: pd.DataFrame):
    """
    Main preprocessing pipeline.
    Returns (cleaned_df, list_of_warnings).
    """
    warnings = []
    df = df.copy()
    
    # ── 1. Strip whitespace from string columns ─────────────────────────────
    str_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        # Convert literal "nan" strings back to NaN
        df[col] = df[col].replace({"nan": np.nan, "NaN": np.nan, "None": np.nan, "": np.nan})
    
    # ── 2. Convert numeric columns safely ───────────────────────────────────
    for col in NUMERIC_RANGES:
        if col in df.columns:
            original_na = df[col].isna().sum()
            df[col] = safe_numeric(df[col], col)
            new_na = df[col].isna().sum()
            coerced = new_na - original_na
            if coerced > 0:
                warnings.append(f"Warning: Column '{col}': {coerced} non-numeric values converted to NaN.")
    
    # ── 3. Clamp numeric outliers ────────────────────────────────────────────
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col in df.columns:
            n_before = df[col].isna().sum()
            df[col] = df[col].clip(lower=lo, upper=hi)
    
    # ── 4. Normalize category labels ────────────────────────────────────────
    if "category" in df.columns:
        df["category"] = df["category"].apply(normalize_category)
    
    # ── 5. Normalize battery type labels ────────────────────────────────────
    if "battery_type" in df.columns:
        df["battery_type"] = df["battery_type"].apply(normalize_battery_type)
    
    # ── 6. Validate customer ratings ────────────────────────────────────────
    if "customer_rating" in df.columns:
        invalid_ratings = df["customer_rating"].notna() & (
            (df["customer_rating"] < RATING_MIN) | (df["customer_rating"] > RATING_MAX)
        )
        if invalid_ratings.sum() > 0:
            df.loc[invalid_ratings, "customer_rating"] = np.nan
            warnings.append(
                f"Warning: customer_rating: {invalid_ratings.sum()} values outside [{RATING_MIN}, {RATING_MAX}] set to NaN."
            )
    
    # ── 7. Validate model_year ───────────────────────────────────────────────
    if "model_year" in df.columns:
        s = safe_numeric(df["model_year"], "model_year")
        # Round to int safely, preserving NaN via nullable Int64
        df["model_year"] = s.round(0).astype("Int64") if s.notna().any() else s

    # ── 8. Detect duplicates ─────────────────────────────────────────────────
    if "vehicle_id" in df.columns:
        dupes = df.duplicated(subset=["vehicle_id"]).sum()
        if dupes > 0:
            warnings.append(f"Warning: {dupes} duplicate vehicle_id rows detected (kept first occurrence).")
            df = df.drop_duplicates(subset=["vehicle_id"], keep="first")
    else:
        dupes = df.duplicated().sum()
        if dupes > 0:
            warnings.append(f"Warning: {dupes} fully duplicate rows detected (kept first occurrence).")
            df = df.drop_duplicates(keep="first")

    # ── 9. Ensure integer types where appropriate ────────────────────────────
    for col in ["num_motors", "num_seats", "num_charging_ports", "warranty_years",
                "autonomous_level"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            df[col] = s.round(0).astype("Int64") if s.notna().any() else s
    
    return df, warnings


def get_quality_report(df: pd.DataFrame) -> dict:
    """Return a data quality summary dictionary."""
    total = len(df)
    report = {
        "total_rows": total,
        "total_columns": len(df.columns),
        "duplicate_rows": df.duplicated().sum(),
        "missing_by_column": df.isnull().sum().to_dict(),
        "missing_pct_by_column": (df.isnull().sum() / max(total, 1) * 100).round(1).to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }
    return report


def apply_filters(
    df: pd.DataFrame,
    years: Optional[tuple] = None,
    manufacturers: Optional[list] = None,
    categories: Optional[list] = None,
    battery_types: Optional[list] = None,
    countries: Optional[list] = None,
) -> pd.DataFrame:
    """Apply sidebar filters to a DataFrame. Returns filtered copy."""
    out = df.copy()
    
    if years and "model_year" in out.columns:
        out = out[out["model_year"].between(years[0], years[1])]
    
    if manufacturers and "manufacturer" in out.columns:
        out = out[out["manufacturer"].isin(manufacturers)]
    
    if categories and "category" in out.columns:
        out = out[out["category"].isin(categories)]
    
    if battery_types and "battery_type" in out.columns:
        out = out[out["battery_type"].isin(battery_types)]
    
    if countries and "manufacturing_country" in out.columns:
        out = out[out["manufacturing_country"].isin(countries)]
    
    return out
