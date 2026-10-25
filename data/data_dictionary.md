# EV Market Intelligence — Data Dictionary

## Overview
This dataset is a **synthetic demonstration dataset** generated for the EV Market Intelligence dashboard.
It contains 5,000 vehicle records across 15 categories, 15 manufacturers, and model years 2018–2026.

> **Important:** All manufacturer names, model names, and numeric values are synthetically generated.
> This is not real market data.

---

## Columns

| # | Column | Type | Unit | Nullable | Description |
|---|---|---|---|---|---|
| 1 | `vehicle_id` | string | — | No | Unique vehicle record identifier (VEH-XXXXX) |
| 2 | `model_name` | string | — | No | Fictional vehicle model designation |
| 3 | `manufacturer` | string | — | No | Fictional manufacturer name (15 manufacturers) |
| 4 | `model_year` | integer | year | No | Model year (2018–2026) |
| 5 | `manufacturing_country` | string | — | No | Country where vehicle was assembled |
| 6 | `market_region` | string | — | No | Target market region |
| 7 | `battery_capacity_kwh` | float | kWh | No | Usable battery energy capacity |
| 8 | `battery_type` | string | — | No | Chemistry: LFP, NMC, NCA, Solid-State, Sodium-Ion |
| 9 | `battery_cycle_life` | float | cycles | Yes (~30%) | Rated cycles before significant degradation |
| 10 | `battery_degradation_pct_5yr` | float | % | No | Capacity loss estimated at 5 years |
| 11 | `range_km` | float | km | No | Estimated driving range per full charge |
| 12 | `efficiency_wh_per_km` | float | Wh/km | No | Energy consumption per kilometre |
| 13 | `motor_power_kw` | float | kW | No | Peak motor output power |
| 14 | `torque_nm` | float | N·m | No | Peak motor torque |
| 15 | `num_motors` | integer | — | No | Number of electric motors (1–4) |
| 16 | `drivetrain` | string | — | No | FWD, RWD, or AWD |
| 17 | `top_speed_kmph` | float | km/h | No | Maximum vehicle speed |
| 18 | `acceleration_0_100_sec` | float | seconds | No | 0–100 km/h acceleration time |
| 19 | `max_dc_charging_kw` | float | kW | No | Maximum DC fast-charging power accepted |
| 20 | `charging_dc_fast_time_min` | float | minutes | No | Estimated 0–80% DC fast charge time |
| 21 | `charging_ac_time_hr` | float | hours | No | Estimated full AC charge time |
| 22 | `num_charging_ports` | integer | — | No | Number of charging ports (1–2) |
| 23 | `num_seats` | integer | — | No | Seating capacity |
| 24 | `weight_kg` | float | kg | No | Kerb weight |
| 25 | `cargo_capacity_liters` | float | litres | No | Cargo/boot volume |
| 26 | `price_usd` | float | USD | No | Estimated base retail price |
| 27 | `insurance_cost_usd_yearly` | float | USD/yr | No | Estimated annual insurance premium |
| 28 | `warranty_years` | integer | years | No | Manufacturer warranty duration |
| 29 | `resale_value_pct_3yr` | float | % | Yes (~20%) | Estimated resale value at 3 years (% of original) |
| 30 | `safety_rating_stars` | float | 1–5 | No | Safety test rating |
| 31 | `autonomous_level` | integer | 0–5 | No | SAE autonomous driving level |
| 32 | `infotainment_screen_inch` | float | inches | No | Primary infotainment screen diagonal |
| 33 | `co2_saved_tons_per_year` | float | t CO₂/yr | No | Estimated annual CO₂ savings vs ICE baseline |
| 34 | `annual_sales_units` | float | units | Yes (~15%) | Annual sales volume |
| 35 | `customer_rating` | float | 1.0–5.0 | Yes (~12%) | Customer satisfaction score |
| 36 | `category` | string | — | No | Vehicle category (see below) |
| 37 | `recommended_use_case` | string | — | No | Suggested primary use case |

---

## Vehicle Categories

| Category | Typical Range (km) | Typical Price (USD) |
|---|---|---|
| Micro City Car | 120–220 | 12,000–25,000 |
| Hatchback | 200–350 | 22,000–42,000 |
| Sedan | 300–500 | 30,000–60,000 |
| Luxury Sedan | 400–650 | 60,000–120,000 |
| Compact SUV | 280–450 | 35,000–65,000 |
| Crossover | 300–480 | 38,000–70,000 |
| Full-size SUV | 350–550 | 55,000–100,000 |
| Luxury SUV | 400–650 | 70,000–150,000 |
| Sports Car | 300–500 | 60,000–200,000 |
| Pickup Truck | 300–550 | 40,000–90,000 |
| Van/MPV | 250–400 | 35,000–70,000 |
| Two-Wheeler Scooter | 80–160 | 3,000–10,000 |
| Three-Wheeler | 100–200 | 5,000–15,000 |
| Electric Bus | 250–500 | 150,000–400,000 |
| Electric Truck | 200–450 | 100,000–350,000 |

---

## Battery Types

| Type | Full Name | Key Characteristics |
|---|---|---|
| LFP | Lithium Iron Phosphate | High cycle life, thermally stable, lower energy density |
| NMC | Nickel Manganese Cobalt | High energy density, good range, moderate cost |
| NCA | Nickel Cobalt Aluminium | Very high energy density, used in performance vehicles |
| Solid-State | Solid-State Lithium | Emerging technology, high energy density, high cost |
| Sodium-Ion | Sodium-Ion | Low cost, abundant materials, lower energy density |

---

## Manufacturers & Origins

| Manufacturer | Origin Country |
|---|---|
| VoltAura | Germany |
| TerraMotors | USA |
| ZephyrEV | China |
| NovaDrive | Japan |
| ArcLightning | South Korea |
| ClearPath | Germany |
| HelixEV | USA |
| SolarSpeed | China |
| PinnacleAuto | Japan |
| EcoWheels | India |
| KineticCharge | South Korea |
| PulseEV | France |
| VelocityCore | USA |
| HorizonAuto | China |
| NexGen Motors | Germany |

---

## Generation Parameters

- **Rows:** 5,000
- **Random seed:** 42 (reproducible)
- **Generator:** `src/generate_dataset.py`
- **Model years:** 2018–2026
- **Missing data:** Intentionally introduced for `annual_sales_units` (~15%), `customer_rating` (~12%),
  `battery_cycle_life` (~30%), `resale_value_pct_3yr` (~20%)

---

*This data dictionary was automatically generated for the EV Market Intelligence demonstration dashboard.*
