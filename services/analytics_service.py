"""
Analytics Service - Descriptive & Predictive Analytics
Provides statistical analysis and forecasting for expenses.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from data.models import Expense
from services.expense_service import get_all_expenses, get_expenses_by_date_range
import config

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_spending_statistics(expenses: List[Expense]) -> Dict:
    """
    Calculate descriptive statistics for expenses.

    Args:
        expenses: List of Expense objects

    Returns:
        Dict: Dictionary containing statistical measures
    """
    if not expenses:
        return {
            "count": 0,
            "total": 0,
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
            "std_dev": 0,
        }

    amounts = [exp.amount for exp in expenses]

    return {
        "count": len(amounts),
        "total": sum(amounts),
        "mean": statistics.mean(amounts),
        "median": statistics.median(amounts),
        "min": min(amounts),
        "max": max(amounts),
        "std_dev": statistics.stdev(amounts) if len(amounts) > 1 else 0,
    }


def get_category_statistics() -> Dict[str, Dict]:
    """
    Get spending statistics for each category.

    Returns:
        Dict[str, Dict]: Statistics for each category
    """
    expenses = get_all_expenses()

    # Group expenses by category
    by_category = defaultdict(list)
    for expense in expenses:
        by_category[expense.category].append(expense)

    # Calculate statistics for each category
    stats = {}
    for category, cat_expenses in by_category.items():
        stats[category] = get_spending_statistics(cat_expenses)

    return stats


def get_spending_trends(days: int = 30) -> Dict[str, List[Tuple[str, float]]]:
    """
    Analyze spending trends over time.

    Args:
        days: Number of days to analyze

    Returns:
        Dict: Trends data including daily totals and category trends
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    expenses = get_expenses_by_date_range(
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    # Group by date
    daily_totals = defaultdict(float)
    category_daily = defaultdict(lambda: defaultdict(float))

    for expense in expenses:
        daily_totals[expense.date] += expense.amount
        category_daily[expense.category][expense.date] += expense.amount

    # Sort by date
    daily_trend = sorted(daily_totals.items())

    category_trends = {}
    for category, dates in category_daily.items():
        category_trends[category] = sorted(dates.items())

    return {"daily_totals": daily_trend, "category_trends": category_trends}


def predict_monthly_spending(category: str = None) -> Dict:
    """
    Predict end-of-month spending based on current trends.

    Args:
        category: Optional category to predict (None for all)

    Returns:
        Dict: Prediction data including projected total and confidence
    """
    now = datetime.now()
    month_start = now.replace(day=1).strftime("%Y-%m-%d")
    current_date = now.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, current_date)

    if category:
        expenses = [e for e in expenses if e.category == category]

    if len(expenses) < config.MIN_DATA_POINTS:
        return {
            "projected_total": 0,
            "current_total": 0,
            "daily_average": 0,
            "confidence": "low",
            "message": "Insufficient data for prediction",
        }

    # Calculate current spending
    current_total = sum(exp.amount for exp in expenses)

    # Calculate days elapsed and remaining
    days_elapsed = (now - datetime.strptime(month_start, "%Y-%m-%d")).days + 1
    days_in_month = (
        now.replace(month=now.month % 12 + 1, day=1) - timedelta(days=1)
    ).day
    days_remaining = days_in_month - days_elapsed

    # Calculate daily average
    daily_average = current_total / days_elapsed

    # Project to end of month
    projected_total = current_total + (daily_average * days_remaining)

    # Determine confidence based on data consistency
    amounts = [exp.amount for exp in expenses]
    std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
    cv = std_dev / daily_average if daily_average > 0 else 0  # Coefficient of variation

    if cv < 0.5:
        confidence = "high"
    elif cv < 1.0:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "projected_total": round(projected_total, 2),
        "current_total": round(current_total, 2),
        "daily_average": round(daily_average, 2),
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "confidence": confidence,
    }


def get_spending_patterns() -> Dict:
    """
    Identify spending patterns and habits.

    Returns:
        Dict: Analysis of spending patterns
    """
    expenses = get_all_expenses()

    if not expenses:
        return {"patterns": []}

    # Group by day of week
    by_weekday = defaultdict(list)
    for expense in expenses:
        date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
        weekday = date_obj.strftime("%A")
        by_weekday[weekday].append(expense.amount)

    weekday_averages = {
        day: statistics.mean(amounts) for day, amounts in by_weekday.items()
    }

    # Find most expensive day
    most_expensive_day = (
        max(weekday_averages.items(), key=lambda x: x[1]) if weekday_averages else None
    )

    # Analyze category frequency
    category_counts = defaultdict(int)
    for expense in expenses:
        category_counts[expense.category] += 1

    most_frequent_category = (
        max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
    )

    return {
        "weekday_averages": weekday_averages,
        "most_expensive_day": most_expensive_day,
        "most_frequent_category": most_frequent_category,
        "category_frequencies": dict(category_counts),
    }


def get_budget_utilization() -> Dict[str, Dict]:
    """
    Calculate budget utilization for each category.

    Returns:
        Dict: Budget utilization data for each category
    """
    now = datetime.now()
    month_start = now.replace(day=1).strftime("%Y-%m-%d")
    current_date = now.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, current_date)

    # Calculate spending by category
    category_spending = defaultdict(float)
    for expense in expenses:
        category_spending[expense.category] += expense.amount

    # Get budget thresholds from session state if available, otherwise use config
    if HAS_STREAMLIT:
        try:
            budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
        except Exception:
            budgets = config.BUDGET_THRESHOLDS
    else:
        budgets = config.BUDGET_THRESHOLDS

    # Calculate utilization for each category
    utilization = {}
    for category, budget in budgets.items():
        spent = category_spending.get(category, 0)
        percentage = (spent / budget * 100) if budget > 0 else 0

        utilization[category] = {
            "budget": budget,
            "spent": round(spent, 2),
            "remaining": round(budget - spent, 2),
            "percentage": round(percentage, 2),
            "status": get_budget_status(percentage),
        }

    return utilization


def get_budget_status(percentage: float) -> str:
    """
    Determine budget status based on utilization percentage.

    Args:
        percentage: Budget utilization percentage

    Returns:
        str: Status (safe, warning, critical, exceeded)
    """
    if percentage < config.WARNING_THRESHOLD * 100:
        return "safe"
    elif percentage < config.CRITICAL_THRESHOLD * 100:
        return "warning"
    elif percentage < 100:
        return "critical"
    else:
        return "exceeded"
