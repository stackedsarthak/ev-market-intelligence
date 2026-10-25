"""
Tests for src/insights.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np

from src.preprocessing import preprocess
from src.insights import generate_all_insights


def make_df(n=30, seed=0):
    rng = np.random.default_rng(seed)
    manufacturers = ["Alpha", "Beta", "Gamma", "Delta"]
    categories = ["Sedan", "SUV", "Hatchback", "Pickup Truck"]
    battery_types = ["NMC", "LFP", "NCA", "Solid-State"]

    return pd.DataFrame({
        "vehicle_id": [f"VEH-{i:04d}" for i in range(n)],
        "model_name": [f"Model-{i}" for i in range(n)],
        "manufacturer": [manufacturers[i % 4] for i in range(n)],
        "model_year": [2020 + (i % 4) for i in range(n)],
        "manufacturing_country": ["Germany" if i % 2 == 0 else "USA" for i in range(n)],
        "market_region": ["Europe"] * n,
        "battery_capacity_kwh": rng.uniform(40, 100, n),
        "battery_type": [battery_types[i % 4] for i in range(n)],
        "battery_cycle_life": rng.choice([1000, 2000, np.nan], n),
        "battery_degradation_pct_5yr": rng.uniform(5, 20, n),
        "range_km": rng.uniform(200, 600, n),
        "efficiency_wh_per_km": rng.uniform(120, 200, n),
        "motor_power_kw": rng.uniform(100, 300, n),
        "torque_nm": rng.uniform(200, 500, n),
        "num_motors": [1] * n,
        "drivetrain": ["AWD"] * n,
        "top_speed_kmph": rng.uniform(150, 250, n),
        "acceleration_0_100_sec": rng.uniform(3, 9, n),
        "max_dc_charging_kw": rng.uniform(50, 350, n),
        "charging_dc_fast_time_min": rng.uniform(20, 60, n),
        "charging_ac_time_hr": rng.uniform(5, 15, n),
        "num_charging_ports": [1] * n,
        "num_seats": [5] * n,
        "weight_kg": rng.uniform(1500, 2500, n),
        "cargo_capacity_liters": rng.uniform(300, 600, n),
        "price_usd": rng.uniform(30000, 100000, n),
        "insurance_cost_usd_yearly": rng.uniform(1000, 3000, n),
        "warranty_years": [8] * n,
        "resale_value_pct_3yr": rng.choice([60.0, 70.0, np.nan], n),
        "safety_rating_stars": rng.uniform(3, 5, n),
        "autonomous_level": [2] * n,
        "infotainment_screen_inch": rng.uniform(8, 16, n),
        "co2_saved_tons_per_year": rng.uniform(1, 3, n),
        "annual_sales_units": np.where(rng.random(n) < 0.85, rng.uniform(1000, 10000, n), np.nan),
        "customer_rating": np.where(rng.random(n) < 0.88, rng.uniform(3.0, 5.0, n), np.nan),
        "category": [categories[i % 4] for i in range(n)],
        "recommended_use_case": ["Family"] * n,
    })


@pytest.fixture
def df():
    raw = make_df()
    clean, _ = preprocess(raw)
    return clean


@pytest.fixture
def empty_df():
    raw = make_df()
    clean, _ = preprocess(raw)
    return clean.iloc[0:0]


@pytest.fixture
def small_df():
    raw = make_df(n=3)
    clean, _ = preprocess(raw)
    return clean


# ─── generate_all_insights() ──────────────────────────────────────────────────

def test_generate_insights_returns_list(df):
    result = generate_all_insights(df)
    assert isinstance(result, list)


def test_generate_insights_not_empty(df):
    result = generate_all_insights(df)
    assert len(result) >= 1


def test_generate_insights_each_is_string(df):
    result = generate_all_insights(df)
    for insight in result:
        assert isinstance(insight, str), f"Expected str, got {type(insight)}"


def test_generate_insights_not_blank(df):
    result = generate_all_insights(df)
    for insight in result:
        assert insight.strip() != "", "Got a blank insight string"


def test_generate_insights_empty_df(empty_df):
    # Should not raise; should return a list (possibly with a neutral message)
    result = generate_all_insights(empty_df)
    assert isinstance(result, list)


def test_generate_insights_small_df(small_df):
    # 3-row dataset — should gracefully handle limited data
    result = generate_all_insights(small_df)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_generate_insights_no_sales_data(df):
    # Null out all annual_sales_units
    df_no_sales = df.copy()
    if "annual_sales_units" in df_no_sales.columns:
        df_no_sales["annual_sales_units"] = np.nan
    result = generate_all_insights(df_no_sales)
    assert isinstance(result, list)


def test_generate_insights_no_ratings(df):
    # Null out all customer_rating
    df_no_rating = df.copy()
    if "customer_rating" in df_no_rating.columns:
        df_no_rating["customer_rating"] = np.nan
    result = generate_all_insights(df_no_rating)
    assert isinstance(result, list)


def test_generate_insights_count_reasonable(df):
    result = generate_all_insights(df)
    # Should generate between 1 and 10 insights for a valid dataset
    assert 1 <= len(result) <= 10


def test_generate_insights_single_year():
    raw = make_df(30)
    raw["model_year"] = 2022  # only one year
    clean, _ = preprocess(raw)
    result = generate_all_insights(clean)
    # Should still return a list without raising
    assert isinstance(result, list)


def test_generate_insights_single_manufacturer():
    raw = make_df(20)
    raw["manufacturer"] = "OnlyOne"
    clean, _ = preprocess(raw)
    result = generate_all_insights(clean)
    assert isinstance(result, list)
    assert len(result) >= 1
