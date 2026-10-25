"""
EV Market Intelligence — Methodology & About
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

from src.data_loader import load_bundled_data, REQUIRED_COLUMNS
from src.preprocessing import preprocess
from src.ui_components import inject_global_css, page_header, section_header, data_source_badge

st.set_page_config(page_title="Methodology · EV Market", page_icon="📖", layout="wide")
inject_global_css()

@st.cache_data(show_spinner=False)
def get_clean_data():
    raw = load_bundled_data()
    return preprocess(raw)

is_uploaded = "uploaded_df" in st.session_state and st.session_state["uploaded_df"] is not None

page_header("Methodology & About", "Data sources, methodology, assumptions, and project information.", "📖")
data_source_badge(is_uploaded)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Dictionary", "🔬 Methodology", "⚠️ Limitations", "ℹ️ About"])

with tab1:
    section_header("Data Dictionary", "All 37 columns in the EV Market dataset")
    st.markdown("""
    | Column | Type | Unit | Description |
    |---|---|---|---|
    | `vehicle_id` | string | — | Unique vehicle record identifier |
    | `model_name` | string | — | Fictional vehicle model name |
    | `manufacturer` | string | — | Fictional manufacturer name |
    | `model_year` | integer | year | Model year (2018–2026) |
    | `manufacturing_country` | string | — | Country where vehicle was assembled |
    | `market_region` | string | — | Target market region |
    | `battery_capacity_kwh` | float | kWh | Usable battery energy capacity |
    | `battery_type` | string | — | Battery chemistry: LFP, NMC, NCA, Solid-State, Sodium-Ion |
    | `battery_cycle_life` | float (nullable) | cycles | Rated charge/discharge cycles before significant degradation |
    | `battery_degradation_pct_5yr` | float | % | Estimated capacity loss after 5 years of use |
    | `range_km` | float | km | Estimated driving range per full charge |
    | `efficiency_wh_per_km` | float | Wh/km | Energy consumption per kilometre |
    | `motor_power_kw` | float | kW | Peak motor output power |
    | `torque_nm` | float | N·m | Peak motor torque |
    | `num_motors` | integer | — | Number of electric motors |
    | `drivetrain` | string | — | FWD, RWD, or AWD |
    | `top_speed_kmph` | float | km/h | Maximum speed |
    | `acceleration_0_100_sec` | float | seconds | 0–100 km/h acceleration time |
    | `max_dc_charging_kw` | float | kW | Maximum DC fast-charging power accepted |
    | `charging_dc_fast_time_min` | float | minutes | Estimated time for 0–80% DC fast charge |
    | `charging_ac_time_hr` | float | hours | Estimated time for full AC charge |
    | `num_charging_ports` | integer | — | Number of onboard charging ports |
    | `num_seats` | integer | — | Seating capacity |
    | `weight_kg` | float | kg | Kerb weight |
    | `cargo_capacity_liters` | float | litres | Cargo/boot volume |
    | `price_usd` | float | USD | Estimated base retail price |
    | `insurance_cost_usd_yearly` | float | USD/yr | Estimated annual insurance premium |
    | `warranty_years` | integer | years | Manufacturer warranty duration |
    | `resale_value_pct_3yr` | float (nullable) | % | Estimated resale value at 3 years as % of original price |
    | `safety_rating_stars` | float | 1–5 stars | Safety test rating |
    | `autonomous_level` | integer | 0–5 | SAE autonomous driving level |
    | `infotainment_screen_inch` | float | inches | Primary infotainment screen size |
    | `co2_saved_tons_per_year` | float | tonnes CO₂/yr | Estimated annual CO₂ savings vs ICE baseline |
    | `annual_sales_units` | float (nullable) | units | Annual sales volume (15% missing by design) |
    | `customer_rating` | float (nullable) | 1.0–5.0 | Customer satisfaction rating (12% missing) |
    | `category` | string | — | Vehicle category (15 types) |
    | `recommended_use_case` | string | — | Suggested primary use case |
    """)

    st.markdown("**Vehicle Categories (15):**")
    categories = ["Micro City Car", "Hatchback", "Sedan", "Luxury Sedan", "Compact SUV",
                  "Crossover", "Full-size SUV", "Luxury SUV", "Sports Car", "Pickup Truck",
                  "Van/MPV", "Two-Wheeler Scooter", "Three-Wheeler", "Electric Bus", "Electric Truck"]
    cols = st.columns(3)
    for i, cat in enumerate(categories):
        cols[i % 3].markdown(f"- {cat}")

with tab2:
    section_header("Methodology")

    st.markdown("""
    ### Data Generation
    The demonstration dataset is **synthetically generated** using Python NumPy and Pandas with a
    fixed random seed (SEED=42) for full reproducibility. Key design decisions:

    - **5,000 vehicle records** across 15 categories and 15 manufacturers.
    - **Category-conditioned distributions**: Each vehicle category has realistic parameter ranges
      (e.g., Electric Buses have large battery capacity; Two-Wheelers have small batteries).
    - **Correlated variables**: Range is derived from battery capacity and efficiency with added
      noise to simulate real-world variability.
    - **Intentional missingness**: `annual_sales_units` is 15% missing; `customer_rating` is 12% missing;
      `battery_cycle_life` and `resale_value_pct_3yr` are nullable.

    ### Data Preprocessing Pipeline
    All data is passed through a standardised pipeline (`src/preprocessing.py`):
    1. **Type coercion** — Numeric columns are converted with error handling.
    2. **Range clamping** — Outliers are clipped to physically plausible bounds (e.g., range_km: 50–1500).
    3. **Normalisation** — Battery type aliases are mapped to canonical names.
    4. **Rating validation** — Customer ratings outside 1.0–5.0 are nulled.
    5. **Duplicate detection** — Duplicate `vehicle_id` records are flagged.

    ### Metrics & KPIs
    | Metric | Source |
    |---|---|
    | Market share | `annual_sales_units` sum, falling back to record count when all NaN |
    | YoY growth | (current − prior) / prior × 100, only when two consecutive years exist |
    | Average range | `range_km` mean, excluding NaN |
    | CO₂ savings | `co2_saved_tons_per_year` field, derived during generation from efficiency data |
    | Customer rating | `customer_rating` mean, requiring ≥5 rated records per group |

    ### Charts
    All charts are built with Plotly (Express and Graph Objects). Chart functions always return a
    `go.Figure` — empty datasets produce a placeholder chart rather than an error.

    ### Filtering
    All sidebar filters are applied simultaneously and affect every metric and chart on the active
    page. Market share percentages are always computed relative to the **currently filtered dataset**,
    not global or total market data.
    """)

with tab3:
    section_header("Limitations & Caveats")
    st.markdown("""
    ### Data Limitations
    - **All data is synthetic.** No real manufacturer, sales, or customer data is used.
    - Manufacturer and model names are fictional. Do not treat them as real entities.
    - Sales figures are simulated estimates, not verified market statistics.
    - Customer ratings are randomly generated within plausible distributions.

    ### Metric Limitations
    - **Market share** is relative to the filtered dataset, not the global EV market.
    - **YoY growth** requires at least 2 consecutive years. Single-year views show no growth figure.
    - **CO₂ savings** use a simplified model. Real lifecycle emissions are not included.
    - **Average range** does not reflect real WLTP, EPA, or NEDC test cycle results.

    ### Design Limitations
    - Geographic map visualisation is not included — geographic fields use country-level bar charts.
    - Quarterly trends are not available — data granularity is annual (model_year).
    - This application is not connected to any real-time data source or API.

    ### Appropriate Use
    This dashboard is suitable for:
    - Academic and educational demonstration.
    - Portfolio and internship showcase.
    - Proof-of-concept for analytics dashboard design.

    It is **not** suitable for:
    - Real purchasing or investment decisions.
    - Policy or regulatory analysis.
    - Competitive intelligence about actual manufacturers.
    """)

with tab4:
    section_header("About This Application")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ## EV Market Intelligence
        **"Understand the Market. Accelerate the Future."**

        A production-quality interactive analytics dashboard for exploring the electric vehicle market
        through data-driven insights.

        ### Technology Stack
        | Component | Technology |
        |---|---|
        | Web framework | Streamlit |
        | Data processing | Pandas, NumPy |
        | Visualisation | Plotly Express + Graph Objects |
        | Testing | Pytest |
        | Language | Python 3.11+ |

        ### Application Pages
        1. **Executive Overview** — KPIs, trend overview, and AI-generated insights
        2. **Sales & Market Trends** — Annual trends, YoY growth, category breakdown
        3. **Manufacturer Intelligence** — Competitive analysis and comparisons
        4. **Battery & Vehicle Performance** — Engineering specs and range analysis
        5. **Geography & Manufacturing** — Country-level production analysis
        6. **Customer Insights** — Satisfaction ratings and model comparisons
        7. **Sustainability & Research** — CO₂ estimates and battery sustainability
        8. **Data Explorer** — Full dataset inspection and download
        9. **Methodology & About** — This page

        ### Colour Palette
        - Background: `#0B1020` · Panels: `#121A2B` · Surfaces: `#182338`
        - Primary accent: `#00D4FF` (electric cyan) · Secondary: `#3DDE91` (electric green)
        - Text: `#F5F7FB` · Dim text: `#A8B3C7` · Borders: `#253554`
        """)
    with col2:
        st.markdown("""
        ### Quick Stats
        """)
        df_full, _ = get_clean_data()
        st.metric("Dataset rows", f"{len(df_full):,}")
        st.metric("Columns", f"{len(df_full.columns)}")
        st.metric("Vehicle categories", "15")
        st.metric("Manufacturers", str(df_full["manufacturer"].nunique() if "manufacturer" in df_full.columns else 15))
        st.metric("Model years", "2018–2026")
        st.metric("Seed", "42 (reproducible)")

        st.markdown("""
        ### Links
        - [Generate fresh dataset](/)
        - [Data Explorer](/7_Data_Explorer)
        """)
