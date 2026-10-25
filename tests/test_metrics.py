"""
Tests for src/metrics.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
import numpy as np

from src.preprocessing import preprocess
from src.metrics import (
    total_sales, unique_manufacturers, unique_models,
    avg_range, avg_battery_capacity, avg_customer_rating,
    leading_manufacturer, top_category,
    manufacturer_market_share, category_sales,
    annual_sales_trend, yoy_growth,
    battery_tech_distribution, avg_range_by_battery_type,
    rating_by_manufacturer, rating_by_category,
    sales_by_country, co2_savings_summary, manufacturer_comparison
)


def make_df(n=20):
    """Create a small test DataFrame."""
    rng = np.random.default_rng(0)
    manufacturers = ["Alpha", "Beta", "Gamma"]
    categories = ["Sedan", "SUV", "Hatchback"]
    battery_types = ["NMC", "LFP", "NCA"]
    years = [2020, 2021, 2022, 2023]

    return pd.DataFrame({
        "vehicle_id": [f"VEH-{i:04d}" for i in range(n)],
        "model_name": [f"Model-{i}" for i in range(n)],
        "manufacturer": [manufacturers[i % 3] for i in range(n)],
        "model_year": [years[i % 4] for i in range(n)],
        "manufacturing_country": ["Germany" if i % 2 == 0 else "USA" for i in range(n)],
        "market_region": ["Europe"] * n,
        "battery_capacity_kwh": rng.uniform(40, 100, n),
        "battery_type": [battery_types[i % 3] for i in range(n)],
        "battery_cycle_life": rng.choice([1000, 2000, np.nan], n),
        "battery_degradation_pct_5yr": rng.uniform(5, 20, n),
        "range_km": rng.uniform(200, 600, n),
        "efficiency_wh_per_km": rng.uniform(120, 200, n),
        "motor_power_kw": rng.uniform(100, 300, n),
        "torque_nm": rng.uniform(200, 500, n),
        "num_motors": rng.integers(1, 3, n),
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
        "autonomous_level": rng.integers(0, 4, n),
        "infotainment_screen_inch": rng.uniform(8, 16, n),
        "co2_saved_tons_per_year": rng.uniform(1, 3, n),
        "annual_sales_units": np.where(rng.random(n) < 0.85, rng.uniform(1000, 10000, n), np.nan),
        "customer_rating": np.where(rng.random(n) < 0.88, rng.uniform(3.0, 5.0, n), np.nan),
        "category": [categories[i % 3] for i in range(n)],
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
    return clean.iloc[0:0]  # empty but with correct schema


# ─── Basic KPI functions ───────────────────────────────────────────────────────

def test_total_sales_returns_number(df):
    result = total_sales(df)
    assert isinstance(result, (int, float))
    assert result >= 0


def test_total_sales_empty(empty_df):
    result = total_sales(empty_df)
    assert result == 0


def test_unique_manufacturers(df):
    result = unique_manufacturers(df)
    assert result == 3


def test_unique_manufacturers_empty(empty_df):
    assert unique_manufacturers(empty_df) == 0


def test_unique_models(df):
    result = unique_models(df)
    assert result == 20


def test_avg_range_is_positive(df):
    result = avg_range(df)
    assert result is not None
    assert result > 0


def test_avg_range_empty(empty_df):
    assert avg_range(empty_df) is None


def test_avg_battery_capacity_is_positive(df):
    result = avg_battery_capacity(df)
    assert result is not None
    assert result > 0


def test_avg_customer_rating_in_range(df):
    result = avg_customer_rating(df)
    if result is not None:
        assert 1.0 <= result <= 5.0


def test_avg_customer_rating_empty(empty_df):
    assert avg_customer_rating(empty_df) is None


def test_leading_manufacturer_is_string(df):
    result = leading_manufacturer(df)
    assert result is None or isinstance(result, str)


def test_top_category_is_string(df):
    result = top_category(df)
    assert result is None or isinstance(result, str)


# ─── Market share ─────────────────────────────────────────────────────────────

def test_manufacturer_market_share_returns_df(df):
    result = manufacturer_market_share(df)
    assert isinstance(result, pd.DataFrame)


def test_manufacturer_market_share_share_sums_to_100(df):
    result = manufacturer_market_share(df)
    if not result.empty and "share_pct" in result.columns:
        total = result["share_pct"].sum()
        assert abs(total - 100.0) < 0.1, f"Share sum = {total}"


def test_manufacturer_market_share_empty(empty_df):
    result = manufacturer_market_share(empty_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_manufacturer_market_share_has_required_cols(df):
    result = manufacturer_market_share(df)
    if not result.empty:
        assert "manufacturer" in result.columns
        assert "share_pct" in result.columns


# ─── Category sales ───────────────────────────────────────────────────────────

def test_category_sales_returns_df(df):
    result = category_sales(df)
    assert isinstance(result, pd.DataFrame)


def test_category_sales_all_categories_present(df):
    result = category_sales(df)
    if not result.empty:
        cats_in_data = set(df["category"].unique())
        cats_in_result = set(result["category"])
        assert cats_in_data == cats_in_result


# ─── Annual trends ────────────────────────────────────────────────────────────

def test_annual_sales_trend_returns_df(df):
    result = annual_sales_trend(df)
    assert isinstance(result, pd.DataFrame)


def test_annual_sales_trend_sorted(df):
    result = annual_sales_trend(df)
    if len(result) > 1 and "model_year" in result.columns:
        assert list(result["model_year"]) == sorted(result["model_year"].tolist())


# ─── YoY Growth ───────────────────────────────────────────────────────────────

def test_yoy_growth_returns_df(df):
    result = yoy_growth(df)
    assert isinstance(result, pd.DataFrame)


def test_yoy_growth_first_year_nan(df):
    result = yoy_growth(df)
    if len(result) >= 1 and "yoy_growth_pct" in result.columns:
        first_val = result.iloc[0]["yoy_growth_pct"]
        assert pd.isna(first_val)


def test_yoy_growth_empty(empty_df):
    result = yoy_growth(empty_df)
    assert isinstance(result, pd.DataFrame)


def test_yoy_growth_single_year():
    rng = np.random.default_rng(1)
    raw = make_df(10)
    raw["model_year"] = 2022  # only one year
    clean, _ = preprocess(raw)
    result = yoy_growth(clean)
    assert isinstance(result, pd.DataFrame)
    if not result.empty and "yoy_growth_pct" in result.columns:
        # All values should be NaN for single year
        assert result["yoy_growth_pct"].isna().all()


def test_yoy_growth_zero_denominator():
    rng = np.random.default_rng(2)
    raw = make_df(10)
    raw.loc[raw["model_year"] == 2020, "annual_sales_units"] = 0.0
    clean, _ = preprocess(raw)
    result = yoy_growth(clean)
    # Should not raise and should return a DataFrame
    assert isinstance(result, pd.DataFrame)


# ─── Battery tech ─────────────────────────────────────────────────────────────

def test_battery_tech_distribution_returns_df(df):
    result = battery_tech_distribution(df)
    assert isinstance(result, pd.DataFrame)


def test_avg_range_by_battery_type_returns_df(df):
    result = avg_range_by_battery_type(df)
    assert isinstance(result, pd.DataFrame)


# ─── Ratings ──────────────────────────────────────────────────────────────────

def test_rating_by_manufacturer_returns_df(df):
    result = rating_by_manufacturer(df)
    assert isinstance(result, pd.DataFrame)


def test_rating_by_manufacturer_ratings_in_range(df):
    result = rating_by_manufacturer(df)
    if not result.empty and "avg_rating" in result.columns:
        assert result["avg_rating"].between(1.0, 5.0).all()


def test_rating_by_category_returns_df(df):
    result = rating_by_category(df)
    assert isinstance(result, pd.DataFrame)


# ─── Geography ────────────────────────────────────────────────────────────────

def test_sales_by_country_returns_df(df):
    result = sales_by_country(df)
    assert isinstance(result, pd.DataFrame)


def test_sales_by_country_share_sums_to_100(df):
    result = sales_by_country(df)
    if not result.empty and "share_pct" in result.columns:
        total = result["share_pct"].sum()
        assert abs(total - 100.0) < 0.1


# ─── CO2 ──────────────────────────────────────────────────────────────────────

def test_co2_savings_summary_returns_dict_or_none(df):
    result = co2_savings_summary(df)
    assert result is None or isinstance(result, dict)


def test_co2_savings_summary_keys(df):
    result = co2_savings_summary(df)
    if result is not None:
        assert "total_co2_saved_tons" in result
        assert "avg_co2_saved_per_vehicle" in result
        assert "vehicle_count" in result


def test_co2_savings_summary_empty(empty_df):
    result = co2_savings_summary(empty_df)
    assert result is None or (isinstance(result, dict) and result.get("vehicle_count", 0) == 0)


# ─── Manufacturer comparison ──────────────────────────────────────────────────

def test_manufacturer_comparison_returns_df(df):
    result = manufacturer_comparison(df)
    assert isinstance(result, pd.DataFrame)


def test_manufacturer_comparison_has_manufacturer_col(df):
    result = manufacturer_comparison(df)
    if not result.empty:
        assert "manufacturer" in result.columns


def test_manufacturer_comparison_empty(empty_df):
    result = manufacturer_comparison(empty_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
