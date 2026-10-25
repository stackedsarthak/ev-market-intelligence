"""
EV Market Intelligence — Synthetic Dataset Generator
=====================================================
Generates a 5,000-row synthetic dataset mirroring the schema of the
Kaggle "Electric Vehicle Market Classification Dataset" by Harish Reddy.

Dataset is clearly labeled as synthetic demonstration data.
All values are statistically plausible but NOT real manufacturer data.
Seed = 42 for reproducibility.
"""

import numpy as np
import pandas as pd
import os

SEED = 42
N_ROWS = 5000
rng = np.random.default_rng(SEED)

# ─────────────────────────────────────────────────────────────────────────────
# Category definitions: each with its own parameter ranges
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES = {
    "Micro City Car":    dict(battery=(12, 25),  range_km=(120, 200), price=(8000, 20000),   seats=(2, 4),   power=(25, 60),    top_speed=(100, 130), accel=(8,  14), weight=(700,  1100), cargo=(100, 200)),
    "Hatchback":         dict(battery=(35, 55),  range_km=(250, 400), price=(20000, 38000),  seats=(4, 5),   power=(80, 150),   top_speed=(140, 180), accel=(6,  10), weight=(1200, 1600), cargo=(250, 400)),
    "Sedan":             dict(battery=(55, 80),  range_km=(350, 520), price=(35000, 60000),  seats=(5, 5),   power=(150, 250),  top_speed=(160, 200), accel=(5,   9), weight=(1500, 1900), cargo=(400, 550)),
    "Luxury Sedan":      dict(battery=(80, 110), range_km=(450, 650), price=(65000, 130000), seats=(4, 5),   power=(300, 600),  top_speed=(200, 260), accel=(2,   5), weight=(2000, 2600), cargo=(400, 600)),
    "Compact SUV":       dict(battery=(50, 75),  range_km=(300, 480), price=(30000, 55000),  seats=(5, 5),   power=(120, 220),  top_speed=(150, 190), accel=(5,   9), weight=(1600, 2000), cargo=(350, 550)),
    "Crossover":         dict(battery=(60, 85),  range_km=(350, 520), price=(38000, 65000),  seats=(5, 7),   power=(150, 280),  top_speed=(160, 210), accel=(4,   8), weight=(1700, 2100), cargo=(450, 700)),
    "Full-size SUV":     dict(battery=(90, 130), range_km=(420, 600), price=(55000, 95000),  seats=(6, 8),   power=(250, 500),  top_speed=(180, 220), accel=(4,   8), weight=(2400, 3200), cargo=(600, 1000)),
    "Luxury SUV":        dict(battery=(100, 140),range_km=(480, 680), price=(90000, 200000), seats=(6, 7),   power=(400, 800),  top_speed=(210, 260), accel=(2,   5), weight=(2600, 3500), cargo=(700, 1200)),
    "Sports Car":        dict(battery=(60, 100), range_km=(300, 500), price=(60000, 180000), seats=(2, 4),   power=(400, 1000), top_speed=(240, 330), accel=(1.5, 4), weight=(1500, 2200), cargo=(150, 350)),
    "Pickup Truck":      dict(battery=(100, 150),range_km=(400, 600), price=(45000, 90000),  seats=(4, 6),   power=(300, 600),  top_speed=(160, 200), accel=(4,   8), weight=(2500, 3500), cargo=(800, 1500)),
    "Van / MPV":         dict(battery=(65, 95),  range_km=(280, 420), price=(35000, 65000),  seats=(7, 9),   power=(120, 220),  top_speed=(140, 170), accel=(7,  12), weight=(2000, 2800), cargo=(800, 2000)),
    "Two-Wheeler Scooter":dict(battery=(3, 8),   range_km=(60, 150),  price=(1500, 5000),    seats=(1, 2),   power=(3, 12),     top_speed=(45, 80),   accel=(6,  12), weight=(80, 160),    cargo=(20, 50)),
    "Three-Wheeler":     dict(battery=(5, 15),   range_km=(80, 180),  price=(2000, 8000),    seats=(3, 4),   power=(5, 20),     top_speed=(55, 90),   accel=(8,  15), weight=(300, 600),   cargo=(100, 300)),
    "Electric Bus":      dict(battery=(200, 400),range_km=(250, 450), price=(180000, 450000),seats=(30, 60), power=(150, 350),  top_speed=(90, 120),  accel=(12, 20), weight=(8000, 18000),cargo=(2000, 5000)),
    "Electric Truck":    dict(battery=(250, 500),range_km=(300, 600), price=(120000, 350000),seats=(2, 4),   power=(250, 500),  top_speed=(100, 140), accel=(10, 18), weight=(10000, 25000),cargo=(5000, 15000)),
}

MANUFACTURERS = {
    "VoltAura":     "Germany",
    "TerraMotors":  "USA",
    "ZephyrEV":     "China",
    "NovaDrive":    "Japan",
    "ArcLightning": "South Korea",
    "ClearPath":    "Germany",
    "HelixEV":      "USA",
    "SolarSpeed":   "China",
    "PinnacleAuto": "Japan",
    "EcoWheels":    "India",
    "KineticCharge":"South Korea",
    "PulseEV":      "France",
    "VelocityCore": "USA",
    "HorizonAuto":  "China",
    "NexGen Motors":"Germany",
}

BATTERY_TYPES = ["LFP", "NMC", "NCA", "Solid-State", "Sodium-Ion"]
DRIVETRAINS = ["FWD", "RWD", "AWD"]
MARKET_REGIONS = ["North America", "Europe", "Asia-Pacific", "India", "Middle East", "Latin America"]
MANUFACTURING_COUNTRIES = ["China", "Germany", "USA", "Japan", "South Korea", "India", "France", "Mexico", "Thailand"]
RECOMMENDED_USE_CASES = ["Urban Commute", "Family Daily Use", "Highway / Long-Distance", "Performance / Enthusiast", "Commercial Delivery", "Public Transport", "Premium / Executive"]

MODEL_SUFFIXES = ["Pro", "Plus", "Elite", "Ultra", "Max", "GT", "Sport", "City", "Eco", "Air", "S", "X", "Z", "E", "One"]

def generate_model_name(manufacturer, category, idx):
    base = manufacturer[:3].upper()
    suffix = rng.choice(MODEL_SUFFIXES)
    num = rng.integers(100, 999)
    return f"{base}-{num} {suffix}"

def battery_type_for_category(category):
    # Categories determine battery type distribution
    if category in ("Micro City Car", "Three-Wheeler", "Two-Wheeler Scooter", "Electric Bus"):
        probs = [0.55, 0.25, 0.05, 0.05, 0.10]  # LFP favored for cost
    elif category in ("Sports Car", "Luxury Sedan", "Luxury SUV"):
        probs = [0.10, 0.35, 0.40, 0.10, 0.05]  # NCA/NMC for energy density
    elif category in ("Electric Truck", "Pickup Truck"):
        probs = [0.45, 0.35, 0.10, 0.05, 0.05]  # LFP/NMC for durability
    else:
        probs = [0.30, 0.40, 0.15, 0.10, 0.05]  # Mixed
    return rng.choice(BATTERY_TYPES, p=probs)

def recommended_use_for_category(category, range_km, num_seats, price):
    if category in ("Two-Wheeler Scooter", "Three-Wheeler", "Micro City Car"):
        return "Urban Commute"
    elif category in ("Van / MPV", "Full-size SUV") and num_seats >= 7:
        return "Family Daily Use"
    elif category in ("Electric Bus",):
        return "Public Transport"
    elif category in ("Electric Truck",):
        return "Commercial Delivery"
    elif category in ("Sports Car",) or (price > 80000 and range_km > 400):
        if category in ("Luxury Sedan", "Luxury SUV") or price > 90000:
            return "Premium / Executive"
        return "Performance / Enthusiast"
    elif range_km >= 450:
        return "Highway / Long-Distance"
    else:
        return "Family Daily Use"

def generate_dataset():
    rows = []
    cat_names = list(CATEGORIES.keys())
    mfr_names = list(MANUFACTURERS.keys())
    
    # Stratified: ~333 per category (15 cats × ~333 = 5000)
    cat_counts = {}
    for i, cat in enumerate(cat_names):
        if i < len(cat_names) - 1:
            cat_counts[cat] = N_ROWS // len(cat_names)
        else:
            cat_counts[cat] = N_ROWS - sum(cat_counts.values())
    
    # Slight imbalance to be realistic
    imbalance = [1.0, 1.1, 1.2, 1.0, 1.3, 1.1, 0.9, 0.7, 0.8, 0.7, 0.8, 1.2, 0.9, 0.4, 0.4]
    weights = np.array(imbalance)
    weights = weights / weights.sum()
    cat_indices = rng.choice(len(cat_names), size=N_ROWS, p=weights)
    
    for i in range(N_ROWS):
        cat_idx = cat_indices[i]
        category = cat_names[cat_idx]
        p = CATEGORIES[category]
        
        manufacturer = rng.choice(mfr_names)
        mfr_country = MANUFACTURERS[manufacturer]
        model_year = int(rng.integers(2018, 2027))
        model_name = generate_model_name(manufacturer, category, i)
        
        # Battery
        battery_cap = float(rng.uniform(*p["battery"]))
        bat_type = battery_type_for_category(category)
        
        # Range derived from battery capacity with efficiency variation
        base_range = float(rng.uniform(*p["range_km"]))
        # Ensure range is consistent with battery
        efficiency_wh_per_km = (battery_cap * 1000) / max(base_range, 1)
        # Clamp efficiency to realistic range
        efficiency_wh_per_km = float(np.clip(efficiency_wh_per_km, 50, 800))
        range_km = float((battery_cap * 1000) / efficiency_wh_per_km)
        
        # Motor & performance
        motor_power = float(rng.uniform(*p["power"]))
        torque = float(motor_power * rng.uniform(2.5, 5.5))
        num_motors = int(rng.choice([1, 2, 4], p=[0.5, 0.35, 0.15]))
        drivetrain = rng.choice(DRIVETRAINS, p=[0.35, 0.30, 0.35])
        if num_motors >= 2:
            drivetrain = "AWD"
        top_speed = float(rng.uniform(*p["top_speed"]))
        accel = float(rng.uniform(*p["accel"]))
        
        # Charging (derived from battery capacity)
        max_dc = float(np.clip(rng.uniform(20, 350), 20, 350))
        if category in ("Two-Wheeler Scooter", "Three-Wheeler"):
            max_dc = float(rng.uniform(3, 15))
        elif category in ("Electric Bus", "Electric Truck"):
            max_dc = float(rng.uniform(100, 350))
        
        dc_time = float((battery_cap * 0.8 * 60) / max(max_dc, 1))  # 80% charge in minutes
        dc_time = float(np.clip(dc_time, 15, 600))
        ac_power = float(rng.uniform(3.7, 22))
        ac_time = float((battery_cap / ac_power))
        num_ports = int(rng.choice([1, 2], p=[0.7, 0.3]))
        
        # Body
        num_seats = int(rng.integers(*p["seats"]) if p["seats"][0] < p["seats"][1] else p["seats"][0])
        weight = float(rng.uniform(*p["weight"]))
        cargo = float(rng.uniform(*p["cargo"]))
        
        # Price & ownership
        price = float(rng.uniform(*p["price"]))
        insurance = float(price * rng.uniform(0.015, 0.035))
        warranty = int(rng.choice([5, 7, 8, 10], p=[0.2, 0.35, 0.30, 0.15]))
        resale = float(rng.uniform(50, 80)) if rng.random() > 0.08 else np.nan
        
        # Battery specs
        cycle_life = float(rng.uniform(800, 3000)) if rng.random() > 0.1 else np.nan
        degradation = float(rng.uniform(5, 20))
        
        # Safety / tech
        safety = int(rng.integers(2, 6))
        auto_level = int(rng.choice([0, 1, 2, 3, 4, 5], p=[0.10, 0.15, 0.35, 0.25, 0.10, 0.05]))
        infotainment = float(rng.uniform(7, 17)) if rng.random() > 0.05 else np.nan
        
        # Environmental
        # CO2 saved: assume 15,000 km/yr vs average ICE at 150g/km
        co2_saved = float((15000 * 0.150) - (15000 * efficiency_wh_per_km / 1000 * 0.0005)) / 1000
        co2_saved = float(max(0.5, co2_saved + rng.uniform(-0.3, 0.3)))
        
        # Market
        annual_sales = float(rng.integers(500, 50000)) if rng.random() > 0.15 else np.nan
        customer_rating = float(round(rng.uniform(2.5, 5.0), 1)) if rng.random() > 0.12 else np.nan
        
        # Geography
        manuf_country = rng.choice(MANUFACTURING_COUNTRIES)
        market_region = rng.choice(MARKET_REGIONS)
        
        # Recommended use
        rec_use = recommended_use_for_category(category, range_km, num_seats, price)
        
        rows.append({
            "vehicle_id": f"EV-{i+1:05d}",
            "model_name": model_name,
            "manufacturer": manufacturer,
            "model_year": model_year,
            "manufacturing_country": manuf_country,
            "market_region": market_region,
            "battery_capacity_kwh": round(battery_cap, 2),
            "battery_type": bat_type,
            "battery_cycle_life": round(cycle_life, 0) if not np.isnan(cycle_life) else np.nan,
            "battery_degradation_pct_5yr": round(degradation, 2),
            "range_km": round(range_km, 1),
            "efficiency_wh_per_km": round(efficiency_wh_per_km, 2),
            "motor_power_kw": round(motor_power, 1),
            "torque_nm": round(torque, 1),
            "num_motors": num_motors,
            "drivetrain": drivetrain,
            "top_speed_kmph": round(top_speed, 1),
            "acceleration_0_100_sec": round(accel, 2),
            "max_dc_charging_kw": round(max_dc, 1),
            "charging_dc_fast_time_min": round(dc_time, 1),
            "charging_ac_time_hr": round(ac_time, 2),
            "num_charging_ports": num_ports,
            "num_seats": num_seats,
            "weight_kg": round(weight, 1),
            "cargo_capacity_liters": round(cargo, 1),
            "price_usd": round(price, 2),
            "insurance_cost_usd_yearly": round(insurance, 2),
            "warranty_years": warranty,
            "resale_value_pct_3yr": round(resale, 1) if not np.isnan(resale) else np.nan,
            "safety_rating_stars": safety,
            "autonomous_level": auto_level,
            "infotainment_screen_inch": round(infotainment, 1) if not np.isnan(infotainment) else np.nan,
            "co2_saved_tons_per_year": round(co2_saved, 3),
            "annual_sales_units": round(annual_sales, 0) if not np.isnan(annual_sales) else np.nan,
            "customer_rating": customer_rating,
            "category": category,
            "recommended_use_case": rec_use,
        })
    
    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    print("Generating EV Market synthetic dataset...")
    df = generate_dataset()
    
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "ev_market_data.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    
    print(f"✓ Dataset saved: {out_path}")
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    print(f"  Categories:\n{df['category'].value_counts().to_string()}")
    print(f"  Manufacturers: {df['manufacturer'].nunique()}")
    print(f"\n  Missing values summary:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string())
