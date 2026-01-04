"""
Charts and Visualizations
Creates interactive charts using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import config


def create_category_pie_chart(category_totals: Dict[str, float]) -> go.Figure:
    """
    Create a pie chart showing spending by category.

    Args:
        category_totals: Dictionary mapping categories to totals

    Returns:
        go.Figure: Plotly figure object
    """
    if not category_totals:
        return go.Figure()

    categories = list(category_totals.keys())
    amounts = list(category_totals.values())

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=amounts,
                hole=0.3,
                hovertemplate="<b>%{label}</b><br>$%{value:.2f}<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(title="Spending Distribution", showlegend=True, height=400)

    return fig


def create_spending_trend_chart(daily_totals: List[Tuple[str, float]]) -> go.Figure:
    """
    Create a line chart showing spending trends over time.

    Args:
        daily_totals: List of (date, amount) tuples

    Returns:
        go.Figure: Plotly figure object
    """
    if not daily_totals:
        return go.Figure()

    dates = [item[0] for item in daily_totals]
    amounts = [item[1] for item in daily_totals]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=amounts,
            mode="lines+markers",
            name="Daily Spending",
            line=dict(color=config.CHART_COLORS["primary"], width=2),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>$%{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Daily Spending Trend",
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        hovermode="x unified",
        height=400,
    )

    return fig


def create_budget_utilization_chart(utilization: Dict[str, Dict]) -> go.Figure:
    """
    Create a bar chart showing budget utilization by category.

    Args:
        utilization: Dictionary with budget utilization data

    Returns:
        go.Figure: Plotly figure object
    """
    if not utilization:
        return go.Figure()

    categories = list(utilization.keys())
    percentages = [data["percentage"] for data in utilization.values()]
    spent = [data["spent"] for data in utilization.values()]
    budgets = [data["budget"] for data in utilization.values()]

    # Color based on status
    colors = []
    for data in utilization.values():
        status = data["status"]
        if status == "exceeded":
            colors.append(config.CHART_COLORS["danger"])
        elif status == "critical":
            colors.append(config.CHART_COLORS["warning"])
        elif status == "warning":
            colors.append("#FFD54F")
        else:
            colors.append(config.CHART_COLORS["success"])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=categories,
            y=percentages,
            marker_color=colors,
            text=[f"{p:.1f}%" for p in percentages],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Spent: $%{customdata[0]:.2f}<br>Budget: $%{customdata[1]:.2f}<br>Utilization: %{y:.1f}%<extra></extra>",
            customdata=list(zip(spent, budgets)),
        )
    )

    # Add reference line at 100%
    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="red",
        annotation_text="Budget Limit",
        annotation_position="right",
    )

    fig.update_layout(
        title="Budget Utilization by Category",
        xaxis_title="Category",
        yaxis_title="Utilization (%)",
        height=400,
        showlegend=False,
    )

    return fig


def create_category_comparison_chart(category_stats: Dict[str, Dict]) -> go.Figure:
    """
    Create a grouped bar chart comparing categories.

    Args:
        category_stats: Dictionary with category statistics

    Returns:
        go.Figure: Plotly figure object
    """
    if not category_stats:
        return go.Figure()

    categories = list(category_stats.keys())
    totals = [stats["total"] for stats in category_stats.values()]
    counts = [stats["count"] for stats in category_stats.values()]
    averages = [stats["mean"] for stats in category_stats.values()]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Total Spent",
            x=categories,
            y=totals,
            marker_color=config.CHART_COLORS["primary"],
            hovertemplate="<b>%{x}</b><br>Total: $%{y:.2f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            name="Transaction Count",
            x=categories,
            y=counts,
            marker_color=config.CHART_COLORS["secondary"],
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="Category Comparison",
        xaxis_title="Category",
        yaxis_title="Total Amount ($)",
        yaxis2=dict(title="Transaction Count", overlaying="y", side="right"),
        barmode="group",
        height=400,
        hovermode="x unified",
    )

    return fig


def create_monthly_comparison_chart(monthly_data: Dict[str, float]) -> go.Figure:
    """
    Create a bar chart comparing monthly spending.

    Args:
        monthly_data: Dictionary mapping months to totals

    Returns:
        go.Figure: Plotly figure object
    """
    if not monthly_data:
        return go.Figure()

    months = list(monthly_data.keys())
    amounts = list(monthly_data.values())

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=months,
            y=amounts,
            marker_color=config.CHART_COLORS["primary"],
            text=[f"${amt:.2f}" for amt in amounts],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>$%{y:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Monthly Spending Comparison",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        height=400,
    )

    return fig


def create_heatmap(data: Dict[str, Dict[str, float]]) -> go.Figure:
    """
    Create a heatmap visualization.

    Args:
        data: Nested dictionary with heatmap data

    Returns:
        go.Figure: Plotly figure object
    """
    if not data:
        return go.Figure()

    # Convert to matrix format
    y_labels = list(data.keys())
    x_labels = list(next(iter(data.values())).keys())
    z_values = [[data[y][x] for x in x_labels] for y in y_labels]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=x_labels,
            y=y_labels,
            colorscale="RdYlGn_r",
            hovertemplate="<b>%{y} - %{x}</b><br>$%{z:.2f}<extra></extra>",
        )
    )

    fig.update_layout(title="Spending Heatmap", height=400)

    return fig
