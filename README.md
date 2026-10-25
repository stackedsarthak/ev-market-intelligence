# EV Market Intelligence

> **"Understand the Market. Accelerate the Future."**

A production-quality, interactive data analytics dashboard for exploring electric vehicle market performance, manufacturer intelligence, battery technology, and sustainability metrics.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.22%2B-purple?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Screenshots

The dashboard features a dark-mode analytics UI with electric cyan/green accents, inspired by automotive technology dashboards.

---

## Features

### 9 Interactive Pages
1. **Executive Overview** — KPI cards, trend charts, and AI-generated insights
2. **Sales & Market Trends** — Annual trends, YoY growth rates, category breakdown
3. **Manufacturer Intelligence** — Competitive analysis, heatmaps, multi-manufacturer comparison
4. **Battery & Vehicle Performance** — Range analysis, scatter plots, charging analytics
5. **Geography & Manufacturing** — Country-level production analysis
6. **Customer Insights** — Satisfaction ratings, rating vs range/price correlation
7. **Sustainability & Research** — CO₂ estimates, battery sustainability metrics
8. **Data Explorer** — Full dataset inspection, search, pagination, CSV download
9. **Methodology & About** — Data dictionary, methodology, limitations

### Key Capabilities
- **All charts interactive** via Plotly — hover, zoom, pan, filter
- **Global sidebar filters** — Year range, manufacturer, category, battery type, country
- **Upload your own dataset** — Replace demo data with custom CSV/Excel
- **CSV downloads** — Filtered and full dataset available on any page
- **Data quality report** — Missing values, duplicates, type summary

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web framework | [Streamlit](https://streamlit.io) |
| Data processing | [Pandas](https://pandas.pydata.org), [NumPy](https://numpy.org) |
| Visualisation | [Plotly Express](https://plotly.com/python/plotly-express/) + Graph Objects |
| Testing | [Pytest](https://pytest.org) |
| Language | Python 3.11+ |

---

## Project Structure

```
EV PROJECT/
├── app.py                      # Main page — Executive Overview
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml             # Dark theme configuration
├── pages/
│   ├── 1_Sales_Trends.py
│   ├── 2_Manufacturer_Intelligence.py
│   ├── 3_Battery_Performance.py
│   ├── 4_Geography.py
│   ├── 5_Customer_Insights.py
│   ├── 6_Sustainability.py
│   ├── 7_Data_Explorer.py
│   └── 8_Methodology.py
├── src/
│   ├── __init__.py
│   ├── generate_dataset.py     # Synthetic dataset generator (seed=42)
│   ├── data_loader.py          # CSV loading, schema validation
│   ├── preprocessing.py        # Type coercion, normalization, filtering
│   ├── metrics.py              # KPI and aggregation functions
│   ├── insights.py             # Rule-based insight generation
│   ├── charts.py               # Plotly chart factory functions
│   └── ui_components.py        # Streamlit UI widgets and CSS
├── data/
│   ├── ev_market_data.csv      # Generated demo dataset (5,000 rows, 37 columns)
│   └── data_dictionary.md
└── tests/
    ├── __init__.py
    ├── test_preprocessing.py
    ├── test_metrics.py
    └── test_insights.py
```

---

## Quick Start

### Prerequisites
- Python 3.11 or newer
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ev-market-intelligence.git
cd ev-market-intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the demo dataset
python src/generate_dataset.py

# 4. Run the application
python -m streamlit run app.py
```

Open your browser at **http://localhost:8501**

### Running Tests

```bash
python -m pytest tests/ -v
```

---

## Dataset

The demo dataset is **synthetically generated** (not real market data):

- **5,000 records** across 15 vehicle categories and 15 manufacturers
- **37 columns** covering specifications, performance, pricing, and sustainability
- **Model years:** 2018–2026
- **Reproducible:** Fixed seed (SEED=42)
- **Intentional missingness:** `annual_sales_units` (~15%), `customer_rating` (~12%)

See [`data/data_dictionary.md`](data/data_dictionary.md) for full column documentation.

> The dataset is inspired by the structure of the Kaggle dataset
> [Electric Vehicle Market Classification Dataset](https://www.kaggle.com/datasets/tharishreddy22/electric-vehicle-market-classification-dataset)
> (MIT License). All values in this project are synthetically generated.

---

## Design System

| Token | Value |
|---|---|
| Background | `#0B1020` (midnight navy) |
| Main panels | `#121A2B` |
| Secondary surface | `#182338` |
| Primary accent | `#00D4FF` (electric cyan) |
| Secondary accent | `#3DDE91` (electric green) |
| Main text | `#F5F7FB` |
| Secondary text | `#A8B3C7` |
| Warning | `#FFB347` (amber) |
| Negative | `#FF6B6B` (coral) |
| Borders | `#253554` |

---

## Uploading Your Own Data

Navigate to **Data Explorer → Upload Your Dataset**. The file must include at minimum:

```
vehicle_id, manufacturer, model_name, category, model_year,
battery_capacity_kwh, battery_type, range_km
```

CSV and Excel (`.xlsx`, `.xls`) formats are supported.

---

## Limitations

- All data is synthetic. Do not use for real investment or purchasing decisions.
- Market share is relative to the filtered dataset, not the global EV market.
- CO₂ estimates use simplified assumptions (see Methodology page for details).
- Geographic maps are not included — country data is shown as ranked bar charts.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Acknowledgements

- Dataset structure inspired by [Harish Reddy's EV Market Classification Dataset](https://www.kaggle.com/datasets/tharishreddy22/electric-vehicle-market-classification-dataset) (MIT License)
- Built with [Streamlit](https://streamlit.io), [Plotly](https://plotly.com), [Pandas](https://pandas.pydata.org)
