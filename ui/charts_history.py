"""
Historical Charts - Visualization of historical data
Creates charts and graphs for historical analysis, trends, and comparisons.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List
from datetime import datetime
import pandas as pd


def create_monthly_totals_chart(monthly_totals: Dict[str, float]):
    """
    Create line chart of monthly spending totals.

    Args:
        monthly_totals: Dictionary of {month: total}

    Returns:
        plotly.graph_objects.Figure
    """
    months = list(monthly_totals.keys())
    totals = list(monthly_totals.values())

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=totals,
            mode="lines+markers",
            name="Monthly Total",
            line=dict(color="rgb(31, 119, 180)", width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor="rgba(31, 119, 180, 0.2)",
        )
    )

    # Add average line
    if totals:
        avg = sum(totals) / len(totals)
        fig.add_hline(
            y=avg,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Average: ${avg:,.2f}",
            annotation_position="right",
        )

    fig.update_layout(
        title="Monthly Spending Totals",
        xaxis_title="Month",
        yaxis_title="Total Amount ($)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
    )

    return fig


def create_category_monthly_chart(category_monthly: Dict[str, Dict[str, float]]):
    """
    Create stacked area chart of category spending by month.

    Args:
        category_monthly: Dictionary of {category: {month: total}}

    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # Get all months
    all_months = set()
    for category_data in category_monthly.values():
        all_months.update(category_data.keys())
    all_months = sorted(list(all_months))

    # Add trace for each category
    for category in sorted(category_monthly.keys()):
        values = [category_monthly[category].get(month, 0) for month in all_months]
        fig.add_trace(
            go.Scatter(
                x=all_months,
                y=values,
                name=category,
                mode="lines",
                stackgroup="one",
                fillcolor=None,
            )
        )

    fig.update_layout(
        title="Spending by Category Over Time",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
    )

    return fig


def create_category_comparison_chart(category_totals: Dict[str, float]):
    """
    Create horizontal bar chart of total spending by category.

    Args:
        category_totals: Dictionary of {category: total}

    Returns:
        plotly.graph_objects.Figure
    """
    categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    cat_names = [c[0] for c in categories]
    cat_values = [c[1] for c in categories]

    fig = go.Figure(
        data=[
            go.Bar(
                x=cat_values,
                y=cat_names,
                orientation="h",
                marker=dict(color=cat_values, colorscale="Viridis", showscale=True),
            )
        ]
    )

    fig.update_layout(
        title="Total Spending by Category",
        xaxis_title="Total Amount ($)",
        yaxis_title="Category",
        template="plotly_white",
        height=400,
        yaxis=dict(autorange="reversed"),
    )

    return fig


def create_month_over_month_chart(comparison_data: Dict):
    """
    Create bar chart comparing current vs previous month.

    Args:
        comparison_data: Dictionary from month_over_month_comparison

    Returns:
        plotly.graph_objects.Figure
    """
    current_month = comparison_data["current_month"]
    previous_month = comparison_data["previous_month"]
    current_total = comparison_data["current_total"]
    previous_total = comparison_data["previous_total"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=[previous_month, current_month],
                y=[previous_total, current_total],
                marker=dict(
                    color=[
                        (
                            "lightblue"
                            if previous_total >= current_total
                            else "lightcoral"
                        ),
                        (
                            "lightcoral"
                            if current_total > previous_total
                            else "lightgreen"
                        ),
                    ]
                ),
                text=[f"${previous_total:,.2f}", f"${current_total:,.2f}"],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title=f"Month-over-Month Comparison",
        xaxis_title="Month",
        yaxis_title="Total Amount ($)",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    return fig


def create_category_month_comparison_chart(comparison_data: Dict):
    """
    Create grouped bar chart for category comparison between months.

    Args:
        comparison_data: Dictionary from month_over_month_comparison

    Returns:
        plotly.graph_objects.Figure
    """
    cat_comparison = comparison_data["category_comparison"]
    current_month = comparison_data["current_month"]
    previous_month = comparison_data["previous_month"]

    categories = sorted(cat_comparison.keys())
    current_values = [cat_comparison[c]["current"] for c in categories]
    previous_values = [cat_comparison[c]["previous"] for c in categories]

    fig = go.Figure(
        data=[
            go.Bar(name=previous_month, x=categories, y=previous_values),
            go.Bar(name=current_month, x=categories, y=current_values),
        ]
    )

    fig.update_layout(
        title="Category Comparison: Current vs Previous Month",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        barmode="group",
        template="plotly_white",
        height=400,
        xaxis=dict(tickangle=-45),
    )

    return fig


def create_yearly_comparison_chart(yearly_data: Dict):
    """
    Create comparison chart between two years.

    Args:
        yearly_data: Dictionary from yearly_comparison

    Returns:
        plotly.graph_objects.Figure
    """
    year1 = yearly_data["year1"]
    year2 = yearly_data["year2"]
    year1_monthly = yearly_data["year1_monthly"]
    year2_monthly = yearly_data["year2_monthly"]

    months = sorted(set(year1_monthly.keys()) | set(year2_monthly.keys()))

    year1_values = [year1_monthly.get(m, 0) for m in months]
    year2_values = [year2_monthly.get(m, 0) for m in months]

    fig = go.Figure(
        data=[
            go.Bar(name=str(year1), x=months, y=year1_values),
            go.Bar(name=str(year2), x=months, y=year2_values),
        ]
    )

    fig.update_layout(
        title=f"Yearly Comparison: {year1} vs {year2}",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        barmode="group",
        template="plotly_white",
        height=400,
    )

    return fig


def create_spending_trend_chart(trend_data: Dict[str, float], category: str = None):
    """
    Create line chart of spending trend over time.

    Args:
        trend_data: Dictionary of {month: total}
        category: Category name (for title)

    Returns:
        plotly.graph_objects.Figure
    """
    months = list(trend_data.keys())
    values = list(trend_data.values())

    title = f"Spending Trend: {category}" if category else "Spending Trend"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=values,
            mode="lines+markers",
            name="Spending",
            line=dict(color="rgb(99, 110, 250)", width=2),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        template="plotly_white",
        height=400,
        hovermode="x unified",
    )

    return fig


def create_seasonal_chart(seasonal_data: Dict[str, float]):
    """
    Create pie chart of seasonal spending distribution.

    Args:
        seasonal_data: Dictionary of {quarter: total}

    Returns:
        plotly.graph_objects.Figure
    """
    quarters = list(seasonal_data.keys())
    totals = list(seasonal_data.values())

    fig = go.Figure(data=[go.Pie(labels=quarters, values=totals, hole=0.3)])

    fig.update_layout(
        title="Spending Distribution by Quarter",
        template="plotly_white",
        height=400,
    )

    return fig


def create_expense_type_chart(type_distribution: Dict[str, float]):
    """
    Create pie chart of fixed vs variable expenses.

    Args:
        type_distribution: Dictionary of {type: total}

    Returns:
        plotly.graph_objects.Figure
    """
    types = list(type_distribution.keys())
    totals = list(type_distribution.values())

    colors = {"fixed": "rgb(255, 127, 14)", "variable": "rgb(44, 160, 44)"}
    color_list = [colors.get(t, "gray") for t in types]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=types,
                values=totals,
                marker=dict(colors=color_list),
                textinfo="label+percent+value",
                texttemplate="<b>%{label}</b><br>$%{value:,.2f}<br>(%{percent})",
            )
        ]
    )

    fig.update_layout(
        title="Fixed vs Variable Expenses",
        template="plotly_white",
        height=400,
    )

    return fig


def create_multi_metric_chart(metric_data: Dict):
    """
    Create multi-metric comparison chart.

    Args:
        metric_data: Dictionary with velocity metrics

    Returns:
        plotly.graph_objects.Figure
    """
    metrics = [
        ("Daily", metric_data.get("daily_average", 0)),
        ("Weekly", metric_data.get("weekly_average", 0)),
        ("Monthly", metric_data.get("monthly_average", 0)),
    ]

    names = [m[0] for m in metrics]
    values = [m[1] for m in metrics]

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=values,
                marker=dict(
                    color=[
                        "rgb(158, 154, 200)",
                        "rgb(111, 138, 255)",
                        "rgb(31, 119, 180)",
                    ]
                ),
                text=[f"${v:,.2f}" for v in values],
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title="Spending Velocity: Average by Time Period",
        xaxis_title="Time Period",
        yaxis_title="Average Amount ($)",
        template="plotly_white",
        height=400,
        showlegend=False,
    )

    return fig


def create_category_heatmap(category_monthly: Dict[str, Dict[str, float]]):
    """
    Create heatmap of spending by category and month.

    Args:
        category_monthly: Dictionary of {category: {month: total}}

    Returns:
        plotly.graph_objects.Figure
    """
    # Prepare data for heatmap
    categories = sorted(category_monthly.keys())
    all_months = set()
    for cat_data in category_monthly.values():
        all_months.update(cat_data.keys())
    all_months = sorted(list(all_months))

    # Create matrix
    matrix = []
    for category in categories:
        row = [category_monthly[category].get(month, 0) for month in all_months]
        matrix.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=all_months,
            y=categories,
            colorscale="YlOrRd",
            text=[[f"${val:,.0f}" for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
        )
    )

    fig.update_layout(
        title="Spending Heatmap: Category by Month",
        xaxis_title="Month",
        yaxis_title="Category",
        template="plotly_white",
        height=500,
    )

    return fig


def create_waterfall_comparison(comparison_data: Dict):
    """
    Create waterfall chart showing month-over-month changes.

    Args:
        comparison_data: Dictionary from month_over_month_comparison

    Returns:
        plotly.graph_objects.Figure
    """
    cat_comparison = comparison_data["category_comparison"]
    previous_month = comparison_data["previous_month"]
    current_month = comparison_data["current_month"]

    categories = sorted(cat_comparison.keys())
    x_labels = [previous_month] + categories + [current_month]

    # Calculate changes
    changes = []
    for cat in categories:
        change = cat_comparison[cat]["change"]
        changes.append(change)

    previous_total = comparison_data["previous_total"]
    current_total = comparison_data["current_total"]

    # Prepare waterfall data
    measure = ["relative"] * len(categories)
    measure = ["absolute"] + measure + ["total"]

    values = [previous_total] + changes + [current_total]

    fig = go.Figure(
        go.Waterfall(
            x=x_labels,
            y=values,
            measure=measure,
            text=[f"${v:,.0f}" for v in values],
            textposition="outside",
        )
    )

    fig.update_layout(
        title=f"Spending Changes: {previous_month} → {current_month}",
        xaxis_title="Category",
        yaxis_title="Amount ($)",
        template="plotly_white",
        height=400,
    )

    return fig
