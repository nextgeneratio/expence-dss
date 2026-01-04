"""
Anomaly Detection Service
Detects spending anomalies and provides actionable recommendations.
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from data.models import Expense
from services.expense_service import get_all_expenses, get_expenses_by_date_range
from services.history_service import (
    get_monthly_totals,
    get_category_totals,
    get_spending_velocity,
    get_monthly_comparison,
)
import config

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def get_anomaly_settings():
    """Get anomaly detection settings from session state or config."""
    if HAS_STREAMLIT:
        try:
            return {
                "overspending_threshold": st.session_state.get(
                    "overspending_threshold", 1.1
                ),  # 10% over budget
                "spike_threshold": st.session_state.get(
                    "spike_threshold", 0.3
                ),  # 30% increase
                "budget_risk_threshold": st.session_state.get(
                    "budget_risk_threshold", 0.75
                ),  # 75% of budget
                "fixed_cost_threshold": st.session_state.get(
                    "fixed_cost_threshold", 0.5
                ),  # Fixed costs > 50% of total
                "rising_trend_threshold": st.session_state.get(
                    "rising_trend_threshold", 0.15
                ),  # 15% rise over 3 months
            }
        except Exception:
            pass

    return {
        "overspending_threshold": 1.1,
        "spike_threshold": 0.3,
        "budget_risk_threshold": 0.75,
        "fixed_cost_threshold": 0.5,
        "rising_trend_threshold": 0.15,
    }


def detect_overspending() -> List[Dict]:
    """
    Detect categories currently overspending against budget.

    Returns:
        List of overspending alerts with recommendations
    """
    alerts = []
    settings = get_anomaly_settings()
    custom_budgets = (
        st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
        if HAS_STREAMLIT
        else config.BUDGET_THRESHOLDS
    )

    # Get current month expenses
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, month_end)

    # Group by category
    category_totals = defaultdict(float)
    for exp in expenses:
        category_totals[exp.category] += exp.amount

    threshold = settings["overspending_threshold"]

    for category, total in category_totals.items():
        budget = custom_budgets.get(category, 0)
        if budget > 0:
            ratio = total / budget
            if ratio >= threshold:
                overage = total - budget
                percentage = (ratio - 1) * 100

                alerts.append(
                    {
                        "type": "overspending",
                        "severity": "warning" if ratio < 1.2 else "critical",
                        "category": category,
                        "title": f"🔴 Overspending Alert: {category}",
                        "current": round(total, 2),
                        "budget": budget,
                        "overage": round(overage, 2),
                        "percentage": round(percentage, 1),
                        "message": f"You've exceeded {category} budget by ${overage:,.2f} ({percentage:.1f}%)",
                        "recommendation": f"Reduce {category} spending by at least ${overage:,.2f} to stay on budget. Review recent transactions and cut non-essential items.",
                        "action": f"Cut {category} spending to ${budget:,.2f} or below",
                    }
                )

    return sorted(alerts, key=lambda x: x["percentage"], reverse=True)


def detect_spending_spikes() -> List[Dict]:
    """
    Detect unusual spending spikes in categories.

    Returns:
        List of spike anomalies
    """
    spikes = []
    settings = get_anomaly_settings()
    threshold = settings["spike_threshold"]

    # Get last 3 months of data
    expenses = get_all_expenses()
    if not expenses:
        return spikes

    # Group by category and month
    category_monthly = defaultdict(lambda: defaultdict(float))
    for exp in expenses:
        month = exp.date[:7]
        category_monthly[exp.category][month] += exp.amount

    # Detect spikes for each category
    for category, monthly_data in category_monthly.items():
        if len(monthly_data) < 2:
            continue

        sorted_months = sorted(monthly_data.items())
        latest_month = sorted_months[-1][1]
        previous_month = sorted_months[-2][1]

        if previous_month > 0:
            increase = (latest_month - previous_month) / previous_month
            if increase >= threshold:
                spikes.append(
                    {
                        "type": "spike",
                        "severity": "warning",
                        "category": category,
                        "title": f"⚡ Spending Spike: {category}",
                        "previous": round(previous_month, 2),
                        "current": round(latest_month, 2),
                        "increase": round(increase * 100, 1),
                        "amount_increase": round(latest_month - previous_month, 2),
                        "message": f"{category} spending increased by {increase * 100:.1f}% ({round(latest_month - previous_month, 2):+,.2f})",
                        "recommendation": f"Investigate recent {category} purchases. Identify one-time vs recurring expenses and adjust budget if needed.",
                        "action": f"Review and categorize the ${abs(latest_month - previous_month):,.2f} increase",
                    }
                )

    return sorted(spikes, key=lambda x: x["increase"], reverse=True)


def detect_budget_risk() -> List[Dict]:
    """
    Detect categories approaching their budget limits.

    Returns:
        List of at-risk categories
    """
    risks = []
    settings = get_anomaly_settings()
    threshold = settings["budget_risk_threshold"]
    custom_budgets = (
        st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
        if HAS_STREAMLIT
        else config.BUDGET_THRESHOLDS
    )

    # Get current month
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, month_end)

    category_totals = defaultdict(float)
    for exp in expenses:
        category_totals[exp.category] += exp.amount

    for category, total in category_totals.items():
        budget = custom_budgets.get(category, 0)
        if budget > 0:
            ratio = total / budget
            if threshold <= ratio < 1.0:
                remaining = budget - total
                percentage_used = ratio * 100

                risks.append(
                    {
                        "type": "budget_risk",
                        "severity": "info",
                        "category": category,
                        "title": f"⚠️ Budget Risk: {category}",
                        "current": round(total, 2),
                        "budget": budget,
                        "remaining": round(remaining, 2),
                        "percentage_used": round(percentage_used, 1),
                        "message": f"{category} is at {percentage_used:.1f}% of budget with ${remaining:,.2f} remaining",
                        "recommendation": f"Be cautious with {category} spending. You have ${remaining:,.2f} left. Consider pausing non-essential {category} purchases.",
                        "action": f"Limit {category} spending to ${remaining / (31 - today.day):,.2f}/day for rest of month",
                    }
                )

    return sorted(risks, key=lambda x: x["percentage_used"], reverse=True)


def detect_fixed_cost_danger() -> List[Dict]:
    """
    Detect if fixed costs are dangerously high.

    Returns:
        List of fixed cost warnings
    """
    warnings = []
    settings = get_anomaly_settings()
    threshold = settings["fixed_cost_threshold"]

    # Get current month
    today = datetime.now()
    month_start = today.replace(day=1).strftime("%Y-%m-%d")
    month_end = today.strftime("%Y-%m-%d")

    expenses = get_expenses_by_date_range(month_start, month_end)

    fixed_total = 0
    variable_total = 0
    for exp in expenses:
        if exp.type == "fixed":
            fixed_total += exp.amount
        else:
            variable_total += exp.amount

    total = fixed_total + variable_total

    if total > 0:
        fixed_ratio = fixed_total / total

        if fixed_ratio >= threshold:
            warnings.append(
                {
                    "type": "fixed_cost_danger",
                    "severity": "warning" if fixed_ratio < 0.65 else "critical",
                    "category": "Fixed Costs",
                    "title": f"🔒 Fixed Cost Warning",
                    "fixed_total": round(fixed_total, 2),
                    "variable_total": round(variable_total, 2),
                    "fixed_ratio": round(fixed_ratio * 100, 1),
                    "message": f"Fixed costs are {fixed_ratio * 100:.1f}% of total spending",
                    "recommendation": "High fixed costs reduce flexibility. Review subscriptions, recurring charges, and contract commitments. Look for opportunities to reduce or eliminate fixed expenses.",
                    "action": f"Reduce fixed costs below {round(threshold * 100, 0):.0f}% (currently {fixed_ratio * 100:.1f}%)",
                }
            )

    return warnings


def detect_rising_trends() -> List[Dict]:
    """
    Detect categories with rising spending trends (early warning).

    Returns:
        List of rising trend alerts
    """
    trends = []
    settings = get_anomaly_settings()
    threshold = settings["rising_trend_threshold"]

    # Get last 3 months
    monthly_totals = get_monthly_totals()
    if len(monthly_totals) < 3:
        return trends

    sorted_months = sorted(monthly_totals.items())
    last_three = sorted_months[-3:]

    if len(last_three) >= 2:
        first_month = last_three[0][1]
        last_month = last_three[-1][1]

        if first_month > 0:
            increase = (last_month - first_month) / first_month
            if increase >= threshold:
                trends.append(
                    {
                        "type": "rising_trend",
                        "severity": "info",
                        "category": "Overall Spending",
                        "title": f"📈 Rising Trend Alert",
                        "first_month": round(first_month, 2),
                        "last_month": round(last_month, 2),
                        "increase": round(increase * 100, 1),
                        "message": f"Overall spending is rising at {increase * 100:.1f}% over 3 months",
                        "recommendation": "Proactive action needed. Review all categories for increases. Set stricter budgets. Identify root causes and implement spending controls.",
                        "action": "Take preventive action to reverse the trend",
                    }
                )

    # Also check category-level trends
    expenses = get_all_expenses()
    if not expenses:
        return trends

    category_monthly = defaultdict(lambda: defaultdict(float))
    for exp in expenses:
        month = exp.date[:7]
        category_monthly[exp.category][month] += exp.amount

    for category, monthly_data in category_monthly.items():
        if len(monthly_data) < 3:
            continue

        sorted_months = sorted(monthly_data.items())
        last_three = sorted_months[-3:]

        if len(last_three) >= 2:
            first = last_three[0][1]
            last = last_three[-1][1]

            if first > 0:
                increase = (last - first) / first
                if increase >= threshold:
                    trends.append(
                        {
                            "type": "rising_trend",
                            "severity": "info",
                            "category": category,
                            "title": f"📈 Rising Trend: {category}",
                            "first_month": round(first, 2),
                            "last_month": round(last, 2),
                            "increase": round(increase * 100, 1),
                            "message": f"{category} spending is increasing {increase * 100:.1f}% monthly",
                            "recommendation": f"Implement preventive measures for {category}. Set stricter budget. Track daily spending. Identify and eliminate unnecessary expenses.",
                            "action": f"Reverse the {increase * 100:.1f}% trend",
                        }
                    )

    return sorted(trends, key=lambda x: x["increase"], reverse=True)


def get_all_anomalies() -> Dict[str, List[Dict]]:
    """
    Get all detected anomalies organized by type.

    Returns:
        Dict with anomaly type -> list of anomalies
    """
    return {
        "overspending": detect_overspending(),
        "spikes": detect_spending_spikes(),
        "budget_risk": detect_budget_risk(),
        "fixed_costs": detect_fixed_cost_danger(),
        "rising_trends": detect_rising_trends(),
    }


def get_anomaly_summary() -> Dict:
    """
    Get summary of all anomalies.

    Returns:
        Dict with counts and recommendations
    """
    all_anomalies = get_all_anomalies()

    return {
        "total_anomalies": sum(len(v) for v in all_anomalies.values()),
        "overspending_count": len(all_anomalies["overspending"]),
        "spike_count": len(all_anomalies["spikes"]),
        "budget_risk_count": len(all_anomalies["budget_risk"]),
        "fixed_cost_warnings": len(all_anomalies["fixed_costs"]),
        "trend_warnings": len(all_anomalies["rising_trends"]),
        "critical_alerts": sum(
            1
            for anomalies in all_anomalies.values()
            for a in anomalies
            if a.get("severity") == "critical"
        ),
        "anomalies": all_anomalies,
    }


def get_actionable_recommendations() -> List[Dict]:
    """
    Get top actionable recommendations based on detected anomalies.

    Returns:
        List of priority-sorted recommendations
    """
    recommendations = []
    summary = get_anomaly_summary()

    # Overspending recommendations
    for anomaly in summary["anomalies"]["overspending"]:
        recommendations.append(
            {
                "priority": (
                    "critical" if anomaly.get("severity") == "critical" else "high"
                ),
                "type": "overspending",
                "category": anomaly["category"],
                "title": anomaly["title"],
                "action": anomaly["action"],
                "impact": f"Save ${anomaly['overage']:,.2f}",
                "effort": "medium",
                "recommendation": anomaly["recommendation"],
            }
        )

    # Spike recommendations
    for anomaly in summary["anomalies"]["spikes"][:3]:  # Top 3 spikes
        recommendations.append(
            {
                "priority": "high",
                "type": "spike",
                "category": anomaly["category"],
                "title": anomaly["title"],
                "action": anomaly["action"],
                "impact": f"Investigate ${anomaly['amount_increase']:,.2f} increase",
                "effort": "low",
                "recommendation": anomaly["recommendation"],
            }
        )

    # Budget risk recommendations
    for anomaly in summary["anomalies"]["budget_risk"][:3]:  # Top 3 at risk
        recommendations.append(
            {
                "priority": "medium",
                "type": "budget_risk",
                "category": anomaly["category"],
                "title": anomaly["title"],
                "action": anomaly["action"],
                "impact": f"Protect ${anomaly['remaining']:,.2f} remaining",
                "effort": "low",
                "recommendation": anomaly["recommendation"],
            }
        )

    # Fixed cost recommendations
    if summary["anomalies"]["fixed_costs"]:
        anomaly = summary["anomalies"]["fixed_costs"][0]
        recommendations.append(
            {
                "priority": "high",
                "type": "fixed_costs",
                "category": "Fixed Costs",
                "title": anomaly["title"],
                "action": anomaly["action"],
                "impact": f"Reduce fixed costs by {round((anomaly['fixed_ratio'] - 40) if anomaly['fixed_ratio'] > 40 else 0, 1)}%",
                "effort": "high",
                "recommendation": anomaly["recommendation"],
            }
        )

    # Trend recommendations
    if summary["anomalies"]["rising_trends"]:
        for anomaly in summary["anomalies"]["rising_trends"][:2]:
            recommendations.append(
                {
                    "priority": "medium",
                    "type": "rising_trend",
                    "category": anomaly.get("category", "Overall"),
                    "title": anomaly["title"],
                    "action": anomaly["action"],
                    "impact": f"Prevent {anomaly['increase']:.1f}% rise",
                    "effort": "medium",
                    "recommendation": anomaly["recommendation"],
                }
            )

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))

    return recommendations
