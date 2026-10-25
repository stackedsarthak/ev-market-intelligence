"""
EV Market Intelligence — Chart Factory
========================================
All Plotly visualizations for the dashboard.
Consistent dark theme, color palette, and formatting.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional

# ─── Design System Colors ─────────────────────────────────────────────────────
COLORS = {
    "bg":         "#0B1020",
    "panel":      "#121A2B",
    "surface":    "#182338",
    "cyan":       "#00D4FF",
    "green":      "#3DDE91",
    "text":       "#F5F7FB",
    "text_dim":   "#A8B3C7",
    "border":     "#253554",
    "amber":      "#FFB347",
    "coral":      "#FF6B6B",
    "purple":     "#9B59B6",
}

CATEGORY_PALETTE = [
    "#00D4FF", "#3DDE91", "#FFB347", "#FF6B6B", "#9B59B6",
    "#F39C12", "#1ABC9C", "#E74C3C", "#3498DB", "#2ECC71",
    "#E67E22", "#8E44AD", "#16A085", "#D35400", "#2980B9",
]

BATTERY_COLORS = {
    "LFP":         "#3DDE91",
    "NMC":         "#00D4FF",
    "NCA":         "#FFB347",
    "Solid-State": "#9B59B6",
    "Sodium-Ion":  "#FF6B6B",
}


def _base_layout(title: str = "", height: int = 400) -> dict:
    """Base Plotly layout matching the design system."""
    return dict(
        title=dict(text=title, font=dict(color=COLORS["text"], size=15), x=0.01),
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["surface"],
        font=dict(color=COLORS["text_dim"], family="Inter, sans-serif", size=12),
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            bgcolor="rgba(18,26,43,0.9)",
            bordercolor=COLORS["border"],
            borderwidth=1,
            font=dict(color=COLORS["text_dim"]),
        ),
        xaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=False,
            tickfont=dict(color=COLORS["text_dim"]),
            title_font=dict(color=COLORS["text_dim"]),
        ),
        yaxis=dict(
            gridcolor=COLORS["border"],
            showgrid=True,
            zeroline=False,
            tickfont=dict(color=COLORS["text_dim"]),
            title_font=dict(color=COLORS["text_dim"]),
        ),
    )


def chart_annual_sales_trend(df: pd.DataFrame, color_by: Optional[str] = None) -> go.Figure:
    """Line chart: annual sales trend, optionally split by category or manufacturer."""
    if "model_year" not in df.columns:
        return _empty_chart("model_year column not available")
    
    use_sales = "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any()
    value_col = "annual_sales_units" if use_sales else None
    y_label = "Total Sales Units" if use_sales else "Vehicle Records"
    
    if color_by and color_by in df.columns and use_sales:
        agg = df.groupby(["model_year", color_by])["annual_sales_units"].sum().reset_index()
        agg.columns = ["model_year", color_by, "value"]
        categories = agg[color_by].unique()
        palette = CATEGORY_PALETTE[:len(categories)]
        fig = px.line(
            agg, x="model_year", y="value", color=color_by,
            color_discrete_sequence=palette,
            markers=True,
            labels={"model_year": "Year", "value": y_label, color_by: color_by.replace("_", " ").title()},
        )
    else:
        if use_sales:
            agg = df.groupby("model_year")["annual_sales_units"].sum().reset_index()
            agg.columns = ["model_year", "value"]
        else:
            agg = df.groupby("model_year").size().reset_index()
            agg.columns = ["model_year", "value"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=agg["model_year"], y=agg["value"],
            mode="lines+markers",
            line=dict(color=COLORS["cyan"], width=2.5),
            marker=dict(color=COLORS["cyan"], size=7),
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.1)",
            name=y_label,
            hovertemplate=f"<b>Year:</b> %{{x}}<br><b>{y_label}:</b> %{{y:,.0f}}<extra></extra>",
        ))
    
    layout = _base_layout("Annual EV Sales Trend", height=380)
    layout["xaxis"]["title"] = "Model Year"
    layout["yaxis"]["title"] = y_label
    fig.update_layout(**layout)
    return fig


def chart_category_sales_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: sales by vehicle category."""
    from src.metrics import category_sales
    cat = category_sales(df)
    if cat.empty:
        return _empty_chart("No category data available")
    
    cat = cat.sort_values("sales")
    colors = [COLORS["cyan"] if i == len(cat) - 1 else COLORS["border"] for i in range(len(cat))]
    colors[-1] = COLORS["cyan"]
    
    fig = go.Figure(go.Bar(
        y=cat["category"], x=cat["sales"],
        orientation="h",
        marker_color=[COLORS["green"] if v == cat["sales"].max() else COLORS["cyan"]
                      for v in cat["sales"]],
        text=[f"{v:.1f}%" for v in cat["share_pct"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Sales: %{x:,.0f}<br>Share: %{text}<extra></extra>",
    ))
    layout = _base_layout("Sales by Vehicle Category", height=500)
    layout["xaxis"]["title"] = "Sales / Records"
    layout["margin"]["r"] = 60
    fig.update_layout(**layout)
    return fig


def chart_manufacturer_share_bar(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Horizontal bar: manufacturer market share."""
    from src.metrics import manufacturer_market_share
    share = manufacturer_market_share(df).head(top_n)
    if share.empty:
        return _empty_chart("No manufacturer data available")
    
    share = share.sort_values("sales")
    bar_colors = [COLORS["green"] if i == len(share) - 1 else COLORS["cyan"]
                  for i in range(len(share))]
    
    fig = go.Figure(go.Bar(
        y=share["manufacturer"], x=share["sales"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{p:.1f}%" for p in share["share_pct"]],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Sales / Records: %{x:,.0f}<br>"
            "Market Share: %{text}<extra></extra>"
        ),
    ))
    layout = _base_layout(f"Manufacturer Market Share (Top {top_n})", height=500)
    layout["xaxis"]["title"] = "Sales / Records"
    layout["margin"]["r"] = 60
    fig.update_layout(**layout)
    return fig


def chart_battery_donut(df: pd.DataFrame) -> go.Figure:
    """Donut chart: battery technology distribution."""
    from src.metrics import battery_tech_distribution
    batt = battery_tech_distribution(df)
    if batt.empty:
        return _empty_chart("No battery type data available")
    
    colors = [BATTERY_COLORS.get(bt, COLORS["border"]) for bt in batt["battery_type"]]
    
    fig = go.Figure(go.Pie(
        labels=batt["battery_type"],
        values=batt["count"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=COLORS["panel"], width=2)),
        hovertemplate="<b>%{label}</b><br>Count: %{value:,.0f}<br>Share: %{percent}<extra></extra>",
        textinfo="label+percent",
        textfont=dict(color=COLORS["text"], size=12),
    ))
    layout = _base_layout("Battery Technology Distribution", height=380)
    layout["showlegend"] = True
    layout["annotations"] = [dict(
        text="Battery<br>Type",
        x=0.5, y=0.5,
        font_size=13, font_color=COLORS["text_dim"],
        showarrow=False
    )]
    fig.update_layout(**layout)
    return fig


def chart_range_by_category_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: average driving range by category."""
    from src.metrics import avg_range_by_category
    agg = avg_range_by_category(df)
    if agg.empty:
        return _empty_chart("No range data available")
    
    agg = agg.sort_values("avg_range_km")
    
    fig = go.Figure(go.Bar(
        y=agg["category"], x=agg["avg_range_km"],
        orientation="h",
        marker_color=[COLORS["green"] if v == agg["avg_range_km"].max() else COLORS["cyan"]
                      for v in agg["avg_range_km"]],
        text=[f"{v:.0f} km" for v in agg["avg_range_km"]],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg Range: %{x:.0f} km<br>"
            "Records: " + agg["count"].astype(str).values[0] + "<extra></extra>"
        ) if not agg.empty else "%{y}<extra></extra>",
    ))
    layout = _base_layout("Average Driving Range by Category", height=500)
    layout["xaxis"]["title"] = "Average Range (km)"
    layout["margin"]["r"] = 80
    fig.update_layout(**layout)
    return fig


def chart_customer_rating(df: pd.DataFrame, group_by: str = "manufacturer") -> go.Figure:
    """Bar chart: customer ratings by manufacturer or category."""
    if "customer_rating" not in df.columns:
        return _empty_chart("customer_rating column not available")
    
    if group_by not in df.columns:
        return _empty_chart(f"Column '{group_by}' not available")
    
    agg = df.groupby(group_by)["customer_rating"].agg(
        avg_rating="mean", count="count"
    ).reset_index()
    agg = agg[agg["count"] >= 5].sort_values("avg_rating", ascending=False).head(20)
    
    if agg.empty:
        return _empty_chart("Insufficient ratings data (minimum 5 ratings per group)")
    
    agg = agg.sort_values("avg_rating")
    
    fig = go.Figure(go.Bar(
        y=agg[group_by], x=agg["avg_rating"],
        orientation="h",
        marker=dict(
            color=agg["avg_rating"],
            colorscale=[[0, COLORS["coral"]], [0.5, COLORS["amber"]], [1, COLORS["green"]]],
            cmin=1, cmax=5,
            colorbar=dict(
                title="Rating",
                tickfont=dict(color=COLORS["text_dim"]),
                titlefont=dict(color=COLORS["text_dim"]),
            ),
        ),
        text=[f"{v:.2f} ★" for v in agg["avg_rating"]],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Avg Rating: %{x:.2f}/5.0<br>"
            "Rated vehicles: " + agg["count"].astype(str) + "<extra></extra>"
        ).values if hasattr(agg["count"].astype(str), 'values') else "%{y}<extra></extra>",
    ))
    
    # Fix hover template per-bar
    fig.data[0].hovertemplate = (
        "<b>%{y}</b><br>Avg Rating: %{x:.2f}/5.0<extra></extra>"
    )
    
    label = group_by.replace("_", " ").title()
    layout = _base_layout(f"Customer Ratings by {label}", height=max(350, len(agg) * 28 + 80))
    layout["xaxis"].update(title="Average Rating (1–5)", range=[0, 5.5])
    layout["margin"]["r"] = 80
    fig.update_layout(**layout)
    return fig


def chart_battery_capacity_vs_range(df: pd.DataFrame) -> go.Figure:
    """Scatter: battery capacity vs driving range, colored by category."""
    if "battery_capacity_kwh" not in df.columns or "range_km" not in df.columns:
        return _empty_chart("battery_capacity_kwh or range_km not available")
    
    sub = df.dropna(subset=["battery_capacity_kwh", "range_km"])
    if len(sub) == 0:
        return _empty_chart("No data after removing missing values")
    
    # Sample if too large for performance
    if len(sub) > 2000:
        sub = sub.sample(2000, random_state=42)
    
    color_col = "category" if "category" in sub.columns else None
    
    if color_col:
        cats = sorted(sub[color_col].unique())
        color_map = {c: CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i, c in enumerate(cats)}
        
        fig = px.scatter(
            sub, x="battery_capacity_kwh", y="range_km",
            color=color_col, color_discrete_map=color_map,
            opacity=0.7,
            labels={
                "battery_capacity_kwh": "Battery Capacity (kWh)",
                "range_km": "Driving Range (km)",
                color_col: "Category",
            },
            hover_data={
                col: True for col in ["manufacturer", "model_name", "price_usd"]
                if col in sub.columns
            },
        )
    else:
        fig = px.scatter(
            sub, x="battery_capacity_kwh", y="range_km",
            opacity=0.6,
            color_discrete_sequence=[COLORS["cyan"]],
            labels={
                "battery_capacity_kwh": "Battery Capacity (kWh)",
                "range_km": "Driving Range (km)",
            },
        )
    
    layout = _base_layout("Battery Capacity vs Driving Range", height=450)
    layout["xaxis"]["title"] = "Battery Capacity (kWh)"
    layout["yaxis"]["title"] = "Driving Range (km)"
    fig.update_layout(**layout)
    return fig


def chart_range_boxplot(df: pd.DataFrame) -> go.Figure:
    """Box plot: range distribution by category or battery type."""
    if "range_km" not in df.columns:
        return _empty_chart("range_km not available")
    
    group_col = "category" if "category" in df.columns else "battery_type"
    if group_col not in df.columns:
        return _empty_chart("No grouping column available")
    
    sub = df.dropna(subset=["range_km", group_col])
    if len(sub) == 0:
        return _empty_chart("No data after removing missing values")
    
    groups = sub[group_col].unique()
    
    fig = go.Figure()
    for i, grp in enumerate(sorted(groups)):
        grp_data = sub[sub[group_col] == grp]["range_km"]
        fig.add_trace(go.Box(
            y=grp_data,
            name=grp,
            marker_color=CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)],
            boxmean=True,
            hovertemplate=f"<b>{grp}</b><br>Range: %{{y:.0f}} km<extra></extra>",
        ))
    
    layout = _base_layout("Range Distribution by Category", height=500)
    layout["yaxis"]["title"] = "Driving Range (km)"
    layout["xaxis"]["tickangle"] = -30
    layout["showlegend"] = False
    fig.update_layout(**layout)
    return fig


def chart_stacked_area_by_category(df: pd.DataFrame) -> go.Figure:
    """Stacked area: category composition over years."""
    if "model_year" not in df.columns or "category" not in df.columns:
        return _empty_chart("model_year or category not available")
    
    use_sales = "annual_sales_units" in df.columns and df["annual_sales_units"].notna().any()
    
    if use_sales:
        agg = df.groupby(["model_year", "category"])["annual_sales_units"].sum().reset_index()
        agg.columns = ["model_year", "category", "value"]
    else:
        agg = df.groupby(["model_year", "category"]).size().reset_index()
        agg.columns = ["model_year", "category", "value"]
    
    categories = sorted(agg["category"].unique())
    fig = go.Figure()
    
    for i, cat in enumerate(categories):
        sub = agg[agg["category"] == cat]
        fig.add_trace(go.Scatter(
            x=sub["model_year"], y=sub["value"],
            name=cat,
            mode="lines",
            stackgroup="one",
            fillcolor=CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)],
            line=dict(color=CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)], width=0.5),
            hovertemplate=f"<b>{cat}</b><br>Year: %{{x}}<br>Value: %{{y:,.0f}}<extra></extra>",
        ))
    
    y_label = "Sales Units" if use_sales else "Vehicle Records"
    layout = _base_layout("Category Composition Over Time", height=420)
    layout["xaxis"]["title"] = "Model Year"
    layout["yaxis"]["title"] = y_label
    fig.update_layout(**layout)
    return fig


def chart_manufacturer_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap: manufacturer vs battery technology count."""
    if "manufacturer" not in df.columns or "battery_type" not in df.columns:
        return _empty_chart("manufacturer or battery_type not available")
    
    pivot = df.groupby(["manufacturer", "battery_type"]).size().unstack(fill_value=0)
    if pivot.empty:
        return _empty_chart("Insufficient data for heatmap")
    
    # Sort manufacturers by total count
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
    
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, COLORS["surface"]], [0.5, COLORS["cyan"]], [1, COLORS["green"]]],
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Count: %{z}<extra></extra>",
        text=pivot.values,
        texttemplate="%{text}",
        textfont=dict(color=COLORS["text"], size=11),
    ))
    layout = _base_layout("Manufacturer × Battery Technology", height=max(400, len(pivot) * 30 + 80))
    layout["xaxis"]["title"] = "Battery Technology"
    layout["yaxis"]["title"] = "Manufacturer"
    layout.pop("xaxis", None)  # Let plotly handle axes
    fig.update_layout(**_base_layout("Manufacturer × Battery Technology", height=max(400, len(pivot) * 30 + 80)))
    return fig


def chart_country_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: vehicle count / sales by manufacturing country."""
    from src.metrics import sales_by_country
    agg = sales_by_country(df)
    if agg.empty:
        return _empty_chart("No manufacturing_country data available")
    
    agg = agg.sort_values("count")
    
    fig = go.Figure(go.Bar(
        y=agg["manufacturing_country"], x=agg["count"],
        orientation="h",
        marker_color=[COLORS["green"] if v == agg["count"].max() else COLORS["cyan"]
                      for v in agg["count"]],
        text=[f"{p:.1f}%" for p in agg["share_pct"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Count: %{x:,.0f}<br>Share: %{text}<extra></extra>",
    ))
    layout = _base_layout("Vehicles by Manufacturing Country", height=400)
    layout["xaxis"]["title"] = "Count"
    layout["margin"]["r"] = 60
    fig.update_layout(**layout)
    return fig


def chart_yoy_growth(df: pd.DataFrame) -> go.Figure:
    """Bar chart: year-over-year growth percentage."""
    from src.metrics import yoy_growth
    trend = yoy_growth(df)
    if len(trend) < 2:
        return _empty_chart("Need at least 2 years of data for growth analysis")
    
    trend = trend.dropna(subset=["yoy_growth_pct"])
    if trend.empty:
        return _empty_chart("No growth data after removing NaN values")
    
    colors = [COLORS["green"] if g >= 0 else COLORS["coral"] for g in trend["yoy_growth_pct"]]
    
    fig = go.Figure(go.Bar(
        x=trend["model_year"], y=trend["yoy_growth_pct"],
        marker_color=colors,
        text=[f"{v:+.1f}%" for v in trend["yoy_growth_pct"]],
        textposition="outside",
        hovertemplate="<b>Year %{x}</b><br>YoY Growth: %{y:+.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["border"])
    layout = _base_layout("Year-over-Year Growth", height=350)
    layout["xaxis"]["title"] = "Model Year"
    layout["yaxis"]["title"] = "Growth (%)"
    fig.update_layout(**layout)
    return fig


def chart_price_vs_range(df: pd.DataFrame) -> go.Figure:
    """Scatter: price vs range (for customer/sustainability pages)."""
    if "price_usd" not in df.columns or "range_km" not in df.columns:
        return _empty_chart("price_usd or range_km not available")
    
    sub = df.dropna(subset=["price_usd", "range_km"])
    if len(sub) == 0:
        return _empty_chart("No data after removing missing values")
    if len(sub) > 2000:
        sub = sub.sample(2000, random_state=42)
    
    color_col = "category" if "category" in sub.columns else None
    
    if color_col:
        cats = sorted(sub[color_col].unique())
        color_map = {c: CATEGORY_PALETTE[i % len(CATEGORY_PALETTE)] for i, c in enumerate(cats)}
        fig = px.scatter(
            sub, x="price_usd", y="range_km",
            color=color_col, color_discrete_map=color_map,
            opacity=0.65,
            labels={"price_usd": "Price (USD)", "range_km": "Driving Range (km)"},
            hover_data={col: True for col in ["manufacturer", "model_name"] if col in sub.columns},
        )
    else:
        fig = px.scatter(
            sub, x="price_usd", y="range_km", opacity=0.6,
            color_discrete_sequence=[COLORS["cyan"]],
            labels={"price_usd": "Price (USD)", "range_km": "Driving Range (km)"},
        )
    
    layout = _base_layout("Price vs Driving Range", height=430)
    layout["xaxis"]["title"] = "Price (USD)"
    layout["yaxis"]["title"] = "Driving Range (km)"
    fig.update_layout(**layout)
    return fig


def chart_efficiency_by_category(df: pd.DataFrame) -> go.Figure:
    """Bar: average efficiency (Wh/km) by category."""
    if "efficiency_wh_per_km" not in df.columns:
        return _empty_chart("efficiency_wh_per_km not available")
    
    agg = df.groupby("category")["efficiency_wh_per_km"].mean().reset_index() \
        if "category" in df.columns else None
    
    if agg is None or agg.empty:
        return _empty_chart("No efficiency data")
    
    agg = agg.sort_values("efficiency_wh_per_km")
    
    fig = go.Figure(go.Bar(
        y=agg["category"], x=agg["efficiency_wh_per_km"],
        orientation="h",
        marker_color=[COLORS["green"] if v == agg["efficiency_wh_per_km"].min() else COLORS["cyan"]
                      for v in agg["efficiency_wh_per_km"]],
        text=[f"{v:.0f} Wh/km" for v in agg["efficiency_wh_per_km"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Avg Efficiency: %{x:.1f} Wh/km<extra></extra>",
    ))
    layout = _base_layout("Average Efficiency by Category", height=500)
    layout["xaxis"]["title"] = "Energy Consumption (Wh/km)"
    layout["margin"]["r"] = 100
    fig.update_layout(**layout)
    return fig


def chart_co2_savings(df: pd.DataFrame) -> go.Figure:
    """Bar: average CO2 savings by category."""
    if "co2_saved_tons_per_year" not in df.columns:
        return _empty_chart("co2_saved_tons_per_year not available")
    
    if "category" not in df.columns:
        return _empty_chart("category not available")
    
    agg = df.groupby("category")["co2_saved_tons_per_year"].mean().reset_index()
    agg.columns = ["category", "avg_co2_saved"]
    agg = agg.sort_values("avg_co2_saved", ascending=False)
    
    fig = go.Figure(go.Bar(
        x=agg["category"], y=agg["avg_co2_saved"],
        marker_color=[COLORS["green"] if v == agg["avg_co2_saved"].max() else COLORS["cyan"]
                      for v in agg["avg_co2_saved"]],
        text=[f"{v:.2f} t" for v in agg["avg_co2_saved"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg CO₂ Saved: %{y:.2f} tons/yr<extra></extra>",
    ))
    layout = _base_layout("Estimated CO₂ Savings by Category (tons/yr per vehicle, estimated)", height=400)
    layout["xaxis"]["title"] = "Vehicle Category"
    layout["yaxis"]["title"] = "Avg CO₂ Saved (tons/yr)"
    layout["xaxis"]["tickangle"] = -30
    fig.update_layout(**layout)
    return fig


def chart_safety_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram: safety rating distribution."""
    if "safety_rating_stars" not in df.columns:
        return _empty_chart("safety_rating_stars not available")
    
    counts = df["safety_rating_stars"].value_counts().sort_index()
    
    fig = go.Figure(go.Bar(
        x=counts.index.astype(str) + " ★",
        y=counts.values,
        marker_color=COLORS["amber"],
        hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>",
    ))
    layout = _base_layout("Safety Rating Distribution", height=330)
    layout["xaxis"]["title"] = "Safety Stars"
    layout["yaxis"]["title"] = "Number of Vehicles"
    fig.update_layout(**layout)
    return fig


def _empty_chart(message: str, height: int = 300) -> go.Figure:
    """Return an empty chart with a message."""
    fig = go.Figure()
    fig.add_annotation(
        text=f"ℹ {message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(color=COLORS["text_dim"], size=13),
    )
    layout = _base_layout("", height=height)
    layout["xaxis"]["visible"] = False
    layout["yaxis"]["visible"] = False
    fig.update_layout(**layout)
    return fig
