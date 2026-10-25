"""
EV Market Intelligence — Data Loader
=====================================
Handles loading the bundled CSV, caching, and user-uploaded CSVs with schema validation.
"""

import os
import io
import pandas as pd
import streamlit as st

# ─── Required columns ────────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "vehicle_id", "manufacturer", "model_name", "category", "model_year",
    "battery_capacity_kwh", "battery_type", "range_km",
]

OPTIONAL_COLUMNS = [
    "manufacturing_country", "market_region", "efficiency_wh_per_km",
    "motor_power_kw", "torque_nm", "num_motors", "drivetrain",
    "top_speed_kmph", "acceleration_0_100_sec",
    "max_dc_charging_kw", "charging_dc_fast_time_min", "charging_ac_time_hr",
    "num_charging_ports", "num_seats", "weight_kg", "cargo_capacity_liters",
    "price_usd", "insurance_cost_usd_yearly", "warranty_years",
    "resale_value_pct_3yr", "safety_rating_stars", "autonomous_level",
    "infotainment_screen_inch", "co2_saved_tons_per_year",
    "annual_sales_units", "customer_rating", "recommended_use_case",
    "battery_cycle_life", "battery_degradation_pct_5yr",
]

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ev_market_data.csv")


@st.cache_data(ttl=3600, show_spinner=False)
def load_bundled_data() -> pd.DataFrame:
    """Load the bundled synthetic demonstration dataset.
    If the CSV is missing (e.g. after a fresh cloud deploy that excluded data/),
    auto-generates it on the fly using the dataset generator.
    """
    if not os.path.exists(DATA_PATH):
        # Auto-generate if missing (Streamlit Community Cloud safety fallback)
        try:
            import sys
            src_dir = os.path.dirname(__file__)
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            from generate_dataset import generate  # type: ignore
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            df = generate()
            df.to_csv(DATA_PATH, index=False)
            return df
        except Exception:
            raise FileNotFoundError(
                f"Dataset not found at {DATA_PATH} and auto-generation failed.\n"
                "Run: python src/generate_dataset.py"
            )
    df = pd.read_csv(DATA_PATH, low_memory=False)
    return df


def validate_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Validate that a DataFrame has the required columns.
    Returns (is_valid, list_of_missing_columns).
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return len(missing) == 0, missing


def load_uploaded_data(uploaded_file) -> tuple[pd.DataFrame | None, str]:
    """
    Load and validate a user-uploaded CSV file.
    Returns (dataframe_or_None, status_message).
    Does NOT overwrite the bundled dataset.
    """
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "❌ Unsupported file format. Please upload a CSV or Excel file."
        
        if len(df) == 0:
            return None, "❌ Uploaded file contains no rows."
        
        if len(df) > 500_000:
            return None, "❌ File too large. Maximum 500,000 rows supported."
        
        valid, missing_cols = validate_schema(df)
        if not valid:
            return None, (
                f"❌ Uploaded file is missing required columns: {', '.join(missing_cols)}.\n"
                f"Required: {', '.join(REQUIRED_COLUMNS)}"
            )
        
        return df, f"✅ Loaded {len(df):,} rows and {len(df.columns)} columns from uploaded file."
    
    except Exception as e:
        return None, f"❌ Error reading file: {str(e)}"


def get_data_source_label(is_uploaded: bool) -> str:
    if is_uploaded:
        return "📂 User-uploaded dataset"
    return "🔬 Synthetic demonstration data — not verified real-world market statistics"
