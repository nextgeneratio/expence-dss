"""
Historical Analytics Service - Aggregation and Comparison
Provides historical data aggregation, monthly analysis, and trend comparisons.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from data.models import Expense
from services.expense_service import get_all_expenses, get_expenses_by_date_range
import config


def get_monthly_totals() -> Dict[str, float]:
    """
    Get total spending for each month (last 12 months).

    Returns:
        Dict: Month string (YYYY-MM) -> Total amount
    """
    expenses = get_all_expenses()
    monthly_totals = defaultdict(float)

    for expense in expenses:
        # Extract YYYY-MM from date string
        month_key = expense.date[:7]  # YYYY-MM format
        monthly_totals[month_key] += expense.amount

    # Sort by month
    sorted_totals = dict(sorted(monthly_totals.items()))
    return sorted_totals


def get_category_monthly_totals() -> Dict[str, Dict[str, float]]:
    """
    Get total spending by category for each month.

    Returns:
        Dict: {category: {month: total, ...}, ...}
    """
    expenses = get_all_expenses()
    category_monthly = defaultdict(lambda: defaultdict(float))

    for expense in expenses:
        month_key = expense.date[:7]  # YYYY-MM format
        category_monthly[expense.category][month_key] += expense.amount

    # Convert to regular dicts and sort
    result = {}
    for category in sorted(category_monthly.keys()):
        result[category] = dict(sorted(category_monthly[category].items()))

    return result


def get_category_totals() -> Dict[str, float]:
    """
    Get total spending by category (all time).

    Returns:
        Dict: {category: total, ...}
    """
    expenses = get_all_expenses()
    category_totals = defaultdict(float)

    for expense in expenses:
        category_totals[expense.category] += expense.amount

    return dict(sorted(category_totals.items()))


def get_category_year_totals(year: int = None) -> Dict[str, float]:
    """
    Get total spending by category for a specific year.

    Args:
        year: Year to filter (default: current year)

    Returns:
        Dict: {category: total, ...}
    """
    if year is None:
        year = datetime.now().year

    expenses = get_all_expenses()
    category_totals = defaultdict(float)

    for expense in expenses:
        expense_year = int(expense.date[:4])
        if expense_year == year:
            category_totals[expense.category] += expense.amount

    return dict(sorted(category_totals.items()))


def get_monthly_comparison(
    current_month: str = None, previous_month: str = None
) -> Dict:
    """
    Compare spending between current and previous month.

    Args:
        current_month: Month to analyze (YYYY-MM format, default: current)
        previous_month: Previous month for comparison (YYYY-MM, default: last month)

    Returns:
        Dict: Comparison data with totals and changes
    """
    if current_month is None:
        today = datetime.now()
        current_month = today.strftime("%Y-%m")
        previous_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    elif previous_month is None:
        curr_date = datetime.strptime(current_month, "%Y-%m")
        prev_date = curr_date.replace(day=1) - timedelta(days=1)
        previous_month = prev_date.strftime("%Y-%m")

    current_start = f"{current_month}-01"
    # Get last day of current month
    if current_month == datetime.now().strftime("%Y-%m"):
        current_end = datetime.now().strftime("%Y-%m-%d")
    else:
        curr_date = datetime.strptime(current_month, "%Y-%m")
        next_month = curr_date.replace(day=28) + timedelta(days=4)
        current_end = (next_month.replace(day=1) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )

    prev_start = f"{previous_month}-01"
    prev_date = datetime.strptime(previous_month, "%Y-%m")
    prev_end = (prev_date.replace(day=28) + timedelta(days=4)).replace(
        day=1
    ) - timedelta(days=1)
    prev_end = prev_end.strftime("%Y-%m-%d")

    current_expenses = get_expenses_by_date_range(current_start, current_end)
    previous_expenses = get_expenses_by_date_range(prev_start, prev_end)

    current_total = sum(e.amount for e in current_expenses)
    previous_total = sum(e.amount for e in previous_expenses)

    change = current_total - previous_total
    change_percent = (change / previous_total * 100) if previous_total > 0 else 0

    # Category comparison
    current_by_cat = defaultdict(float)
    previous_by_cat = defaultdict(float)

    for exp in current_expenses:
        current_by_cat[exp.category] += exp.amount

    for exp in previous_expenses:
        previous_by_cat[exp.category] += exp.amount

    category_comparison = {}
    all_categories = set(current_by_cat.keys()) | set(previous_by_cat.keys())

    for cat in sorted(all_categories):
        curr = current_by_cat.get(cat, 0)
        prev = previous_by_cat.get(cat, 0)
        cat_change = curr - prev
        cat_change_percent = (cat_change / prev * 100) if prev > 0 else 0

        category_comparison[cat] = {
            "current": round(curr, 2),
            "previous": round(prev, 2),
            "change": round(cat_change, 2),
            "change_percent": round(cat_change_percent, 2),
        }

    return {
        "current_month": current_month,
        "previous_month": previous_month,
        "current_total": round(current_total, 2),
        "previous_total": round(previous_total, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "category_comparison": category_comparison,
    }


def get_expense_type_distribution(month: str = None) -> Dict[str, float]:
    """
    Get distribution of expenses by type (fixed/variable).

    Args:
        month: Month to analyze (YYYY-MM format, default: current)

    Returns:
        Dict: {type: total, ...}
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")

    month_start = f"{month}-01"
    month_date = datetime.strptime(month, "%Y-%m")
    month_end = (month_date.replace(day=28) + timedelta(days=4)).replace(
        day=1
    ) - timedelta(days=1)
    month_end = month_end.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, month_end)

    type_totals = defaultdict(float)
    for expense in expenses:
        type_totals[expense.type] += expense.amount

    return dict(sorted(type_totals.items()))


def get_yearly_comparison(year1: int, year2: int) -> Dict:
    """
    Compare spending totals between two years.

    Args:
        year1: First year
        year2: Second year to compare

    Returns:
        Dict: Comparison data for both years
    """
    year1_expenses = []
    year2_expenses = []

    all_expenses = get_all_expenses()

    for expense in all_expenses:
        expense_year = int(expense.date[:4])
        if expense_year == year1:
            year1_expenses.append(expense)
        elif expense_year == year2:
            year2_expenses.append(expense)

    year1_total = sum(e.amount for e in year1_expenses)
    year2_total = sum(e.amount for e in year2_expenses)

    change = year2_total - year1_total
    change_percent = (change / year1_total * 100) if year1_total > 0 else 0

    # Monthly breakdown for each year
    year1_monthly = defaultdict(float)
    year2_monthly = defaultdict(float)

    for exp in year1_expenses:
        month = exp.date[5:7]  # MM format
        year1_monthly[f"Month {month}"] += exp.amount

    for exp in year2_expenses:
        month = exp.date[5:7]  # MM format
        year2_monthly[f"Month {month}"] += exp.amount

    # Category breakdown
    year1_by_cat = defaultdict(float)
    year2_by_cat = defaultdict(float)

    for exp in year1_expenses:
        year1_by_cat[exp.category] += exp.amount

    for exp in year2_expenses:
        year2_by_cat[exp.category] += exp.amount

    return {
        "year1": year1,
        "year2": year2,
        "year1_total": round(year1_total, 2),
        "year2_total": round(year2_total, 2),
        "change": round(change, 2),
        "change_percent": round(change_percent, 2),
        "year1_monthly": dict(sorted(year1_monthly.items())),
        "year2_monthly": dict(sorted(year2_monthly.items())),
        "year1_categories": dict(sorted(year1_by_cat.items())),
        "year2_categories": dict(sorted(year2_by_cat.items())),
    }


def get_top_expense_categories(
    limit: int = 5, month: str = None
) -> List[Tuple[str, float]]:
    """
    Get top spending categories.

    Args:
        limit: Number of top categories to return
        month: Month to analyze (YYYY-MM, default: all time)

    Returns:
        List: Sorted list of (category, total) tuples
    """
    if month:
        month_start = f"{month}-01"
        month_date = datetime.strptime(month, "%Y-%m")
        month_end = (month_date.replace(day=28) + timedelta(days=4)).replace(
            day=1
        ) - timedelta(days=1)
        month_end = month_end.strftime("%Y-%m-%d")
        expenses = get_expenses_by_date_range(month_start, month_end)
    else:
        expenses = get_all_expenses()

    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense.category] += expense.amount

    sorted_categories = sorted(
        category_totals.items(), key=lambda x: x[1], reverse=True
    )
    return sorted_categories[:limit]


def get_spending_trend(category: str = None, months: int = 12) -> Dict[str, float]:
    """
    Get spending trend for a category over time.

    Args:
        category: Specific category to analyze (None = all categories)
        months: Number of months to look back

    Returns:
        Dict: {month: total, ...} sorted by month
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)

    expenses = get_expenses_by_date_range(
        start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )

    monthly_totals = defaultdict(float)

    for expense in expenses:
        if category is None or expense.category == category:
            month_key = expense.date[:7]
            monthly_totals[month_key] += expense.amount

    return dict(sorted(monthly_totals.items()))


def get_spending_velocity() -> Dict:
    """
    Calculate spending velocity metrics (daily, weekly, monthly averages).

    Returns:
        Dict: Velocity metrics
    """
    expenses = get_all_expenses()

    if not expenses:
        return {
            "daily_average": 0,
            "weekly_average": 0,
            "monthly_average": 0,
            "total_days_tracked": 0,
        }

    # Get date range
    dates = [datetime.strptime(e.date, "%Y-%m-%d") for e in expenses]
    first_date = min(dates)
    last_date = max(dates)
    total_days = (last_date - first_date).days + 1

    total_amount = sum(e.amount for e in expenses)

    if total_days == 0:
        total_days = 1

    return {
        "daily_average": round(total_amount / total_days, 2),
        "weekly_average": round(total_amount / (total_days / 7), 2),
        "monthly_average": round(total_amount / (total_days / 30), 2),
        "total_days_tracked": total_days,
        "total_amount": round(total_amount, 2),
    }


def get_seasonal_analysis() -> Dict[str, float]:
    """
    Analyze spending patterns by quarter.

    Returns:
        Dict: {quarter: total, ...}
    """
    expenses = get_all_expenses()
    quarterly_totals = defaultdict(float)

    for expense in expenses:
        date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
        quarter = (date_obj.month - 1) // 3 + 1
        year = date_obj.year
        quarter_key = f"{year}-Q{quarter}"
        quarterly_totals[quarter_key] += expense.amount

    return dict(sorted(quarterly_totals.items()))
