"""
Decision Service - DSS Rules & Recommendations
Provides intelligent recommendations based on spending patterns and rules.
"""

from typing import List, Dict
from datetime import datetime, timedelta
from services.expense_service import get_expenses_by_date_range, get_total_by_category
from services.analytics_service import predict_monthly_spending, get_budget_utilization
import config

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def generate_recommendations() -> List[Dict]:
    """
    Generate personalized spending recommendations based on DSS rules.

    Returns:
        List[Dict]: List of recommendation objects
    """
    recommendations = []

    # Check budget alerts
    recommendations.extend(check_budget_alerts())

    # Check for high spending categories
    recommendations.extend(check_high_spending())

    # Check for unusual patterns
    recommendations.extend(check_unusual_patterns())

    # Provide optimization suggestions
    recommendations.extend(suggest_optimizations())

    return recommendations


def check_budget_alerts() -> List[Dict]:
    """
    Check for budget threshold violations.

    Returns:
        List[Dict]: Budget alert recommendations
    """
    alerts = []
    utilization = get_budget_utilization()

    for category, data in utilization.items():
        status = data["status"]
        percentage = data["percentage"]

        if status == "exceeded":
            alerts.append(
                {
                    "type": "alert",
                    "severity": "critical",
                    "category": category,
                    "title": f"Budget Exceeded: {category}",
                    "message": f"You've exceeded your {category} budget by ${abs(data['remaining']):.2f} ({percentage:.1f}% utilized).",
                    "action": f"Reduce {category} spending immediately or adjust your budget.",
                }
            )
        elif status == "critical":
            alerts.append(
                {
                    "type": "alert",
                    "severity": "warning",
                    "category": category,
                    "title": f"Budget Critical: {category}",
                    "message": f"You've used {percentage:.1f}% of your {category} budget with ${data['remaining']:.2f} remaining.",
                    "action": f"Be cautious with {category} expenses for the rest of the month.",
                }
            )
        elif status == "warning":
            alerts.append(
                {
                    "type": "alert",
                    "severity": "info",
                    "category": category,
                    "title": f"Budget Warning: {category}",
                    "message": f"You've used {percentage:.1f}% of your {category} budget.",
                    "action": f"Monitor {category} spending closely.",
                }
            )

    return alerts


def check_high_spending() -> List[Dict]:
    """
    Identify categories with unusually high spending.

    Returns:
        List[Dict]: High spending recommendations
    """
    recommendations = []

    # Compare current month to previous month
    now = datetime.now()
    current_month_start = now.replace(day=1).strftime("%Y-%m-%d")
    current_date = now.strftime("%Y-%m-%d")

    # Previous month
    prev_month_end = now.replace(day=1) - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1).strftime("%Y-%m-%d")
    prev_month_end_str = prev_month_end.strftime("%Y-%m-%d")

    current_totals = get_total_by_category(current_month_start, current_date)
    previous_totals = get_total_by_category(prev_month_start, prev_month_end_str)

    for category, current_amount in current_totals.items():
        prev_amount = previous_totals.get(category, 0)

        # Get threshold from session state if available
        if HAS_STREAMLIT:
            try:
                threshold = st.session_state.get(
                    "high_spending_threshold", config.HIGH_SPENDING_THRESHOLD
                )
            except Exception:
                threshold = config.HIGH_SPENDING_THRESHOLD
        else:
            threshold = config.HIGH_SPENDING_THRESHOLD

        if prev_amount > 0:
            increase = (current_amount - prev_amount) / prev_amount

            if increase > threshold - 1:  # Percentage increase
                recommendations.append(
                    {
                        "type": "insight",
                        "severity": "info",
                        "category": category,
                        "title": f"Increased Spending: {category}",
                        "message": f"Your {category} spending is {increase*100:.1f}% higher than last month (${current_amount:.2f} vs ${prev_amount:.2f}).",
                        "action": f"Review recent {category} expenses to identify the increase.",
                    }
                )

    return recommendations


def check_unusual_patterns() -> List[Dict]:
    """
    Detect unusual spending patterns.

    Returns:
        List[Dict]: Pattern-based recommendations
    """
    recommendations = []

    # Check for frequent small expenses
    now = datetime.now()

    # Get frequent expense settings from session state if available
    if HAS_STREAMLIT:
        try:
            frequent_days = st.session_state.get(
                "frequent_expense_days", config.FREQUENT_EXPENSE_DAYS
            )
            frequent_count = st.session_state.get(
                "frequent_expense_count", config.FREQUENT_EXPENSE_COUNT
            )
        except Exception:
            frequent_days = config.FREQUENT_EXPENSE_DAYS
            frequent_count = config.FREQUENT_EXPENSE_COUNT
    else:
        frequent_days = config.FREQUENT_EXPENSE_DAYS
        frequent_count = config.FREQUENT_EXPENSE_COUNT

    week_ago = (now - timedelta(days=frequent_days)).strftime("%Y-%m-%d")
    current_date = now.strftime("%Y-%m-%d")

    recent_expenses = get_expenses_by_date_range(week_ago, current_date)

    # Group by category
    category_counts = {}
    for expense in recent_expenses:
        category_counts[expense.category] = category_counts.get(expense.category, 0) + 1

    for category, count in category_counts.items():
        if count >= frequent_count:
            total = sum(e.amount for e in recent_expenses if e.category == category)
            avg = total / count

            recommendations.append(
                {
                    "type": "insight",
                    "severity": "info",
                    "category": category,
                    "title": f"Frequent Expenses: {category}",
                    "message": f"You've made {count} {category} expenses in the last {frequent_days} days (avg ${avg:.2f}).",
                    "action": f"Consider consolidating {category} purchases to reduce transaction frequency.",
                }
            )

    return recommendations


def suggest_optimizations() -> List[Dict]:
    """
    Suggest spending optimizations based on predictions and patterns.

    Returns:
        List[Dict]: Optimization recommendations
    """
    suggestions = []

    # Get predictions for each category
    if HAS_STREAMLIT:
        try:
            budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
        except Exception:
            budgets = config.BUDGET_THRESHOLDS
    else:
        budgets = config.BUDGET_THRESHOLDS

    for category in config.EXPENSE_CATEGORIES:
        prediction = predict_monthly_spending(category)

        if prediction["confidence"] in ["medium", "high"]:
            projected = prediction["projected_total"]
            budget = budgets.get(category, 0)

            if projected > budget:
                overage = projected - budget
                daily_avg = prediction["daily_average"]
                days_remaining = prediction["days_remaining"]

                # Calculate required daily spending to stay on budget
                current = prediction["current_total"]
                required_daily = (
                    (budget - current) / days_remaining if days_remaining > 0 else 0
                )
                reduction = daily_avg - required_daily

                if reduction > 0:
                    suggestions.append(
                        {
                            "type": "recommendation",
                            "severity": "warning",
                            "category": category,
                            "title": f"Budget Projection: {category}",
                            "message": f"At your current rate (${daily_avg:.2f}/day), you'll exceed your {category} budget by ${overage:.2f}.",
                            "action": f"Reduce daily {category} spending to ${required_daily:.2f} to stay within budget.",
                        }
                    )

    return suggestions


def get_savings_opportunities() -> List[Dict]:
    """
    Identify potential savings opportunities.

    Returns:
        List[Dict]: Savings opportunity recommendations
    """
    opportunities = []
    utilization = get_budget_utilization()

    # Find categories with low spending
    for category, data in utilization.items():
        if data["percentage"] < 50 and data["spent"] > 0:
            opportunities.append(
                {
                    "type": "opportunity",
                    "severity": "success",
                    "category": category,
                    "title": f"Savings Opportunity: {category}",
                    "message": f"You've only used {data['percentage']:.1f}% of your {category} budget (${data['spent']:.2f} of ${data['budget']:.2f}).",
                    "action": f"Great job! Consider reallocating some of the ${data['remaining']:.2f} to other categories or savings.",
                }
            )

    return opportunities


def get_decision_summary() -> Dict:
    """
    Generate a comprehensive decision support summary.

    Returns:
        Dict: Complete DSS summary with all recommendations and insights
    """
    return {
        "recommendations": generate_recommendations(),
        "savings_opportunities": get_savings_opportunities(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
