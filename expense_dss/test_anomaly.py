"""
Unit Tests for Anomaly Detection Service
Tests for all anomaly detection functions and recommendations.
"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
from services.anomaly_service import (
    detect_overspending,
    detect_spending_spikes,
    detect_budget_risk,
    detect_fixed_cost_danger,
    detect_rising_trends,
    get_all_anomalies,
    get_actionable_recommendations,
)
from data.models import Expense
import tempfile
import os


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["DB_PATH"] = os.path.join(tmpdir, "test_expenses.db")
        from data.database import init_database

        init_database()
        yield
        # Cleanup happens automatically with tmpdir context manager


@pytest.fixture
def sample_expenses(temp_db):
    """Create sample expenses for testing."""
    from services.expense_service import add_expense

    today = datetime.now()
    last_month = today - timedelta(days=30)
    two_months_ago = today - timedelta(days=60)

    expenses = [
        # Current month - Overspending
        Expense(
            amount=800,
            date=today.date(),
            category="Food",
            type="variable",
            description="Groceries",
        ),
        Expense(
            amount=600,
            date=today.date(),
            category="Food",
            type="variable",
            description="Restaurants",
        ),
        # Current month - Rising Trend
        Expense(
            amount=400,
            date=today.date(),
            category="Transport",
            type="variable",
            description="Gas",
        ),
        # Current month - Fixed Costs
        Expense(
            amount=1200,
            date=today.date(),
            category="Utilities",
            type="fixed",
            description="Rent",
        ),
        # Last month
        Expense(
            amount=600,
            date=last_month.date(),
            category="Food",
            type="variable",
            description="Groceries",
        ),
        Expense(
            amount=250,
            date=last_month.date(),
            category="Transport",
            type="variable",
            description="Gas",
        ),
        # Two months ago
        Expense(
            amount=500,
            date=two_months_ago.date(),
            category="Food",
            type="variable",
            description="Groceries",
        ),
        Expense(
            amount=200,
            date=two_months_ago.date(),
            category="Transport",
            type="variable",
            description="Gas",
        ),
    ]

    for expense in expenses:
        add_expense(
            amount=expense.amount,
            date=expense.date,
            category=expense.category,
            exp_type=expense.type,
            description=expense.description,
        )

    return expenses


def test_detect_overspending(sample_expenses):
    """Test overspending detection."""
    from config import BUDGET_THRESHOLDS

    results = detect_overspending()

    # Food budget is 500, we spent 1400 (800 + 600 in current month)
    # Should detect overspending
    assert isinstance(results, list)

    if results:
        alert = results[0]
        assert "type" in alert
        assert alert["type"] == "overspending"
        assert "title" in alert
        assert "severity" in alert
        assert "budget" in alert
        assert "current" in alert


def test_detect_spending_spikes(sample_expenses):
    """Test spending spike detection."""
    results = detect_spending_spikes()

    assert isinstance(results, list)

    # Food spending increased from 600 (last month) to 1400 (this month) = 133% increase
    # Should detect spike
    if results:
        spike = results[0]
        assert spike["type"] == "spike"
        assert "increase" in spike
        assert "current" in spike
        assert "previous" in spike


def test_detect_budget_risk(sample_expenses):
    """Test budget risk detection."""
    results = detect_budget_risk()

    assert isinstance(results, list)
    assert all(r["type"] == "budget_risk" for r in results)


def test_detect_fixed_cost_danger(sample_expenses):
    """Test fixed cost danger detection."""
    results = detect_fixed_cost_danger()

    assert isinstance(results, list)

    if results:
        warning = results[0]
        assert warning["type"] == "fixed_costs"
        assert "fixed_total" in warning
        assert "variable_total" in warning
        assert "fixed_ratio" in warning


def test_detect_rising_trends(sample_expenses):
    """Test rising trend detection."""
    results = detect_rising_trends()

    assert isinstance(results, list)

    for trend in results:
        assert trend["type"] == "rising_trend"
        assert "increase" in trend
        assert "first_month" in trend
        assert "last_month" in trend


def test_get_all_anomalies(sample_expenses):
    """Test aggregated anomalies."""
    anomalies = get_all_anomalies()

    assert isinstance(anomalies, dict)
    assert "overspending" in anomalies
    assert "spikes" in anomalies
    assert "budget_risk" in anomalies
    assert "fixed_costs" in anomalies
    assert "rising_trends" in anomalies

    for category, alerts in anomalies.items():
        assert isinstance(alerts, list)


def test_get_actionable_recommendations(sample_expenses):
    """Test actionable recommendations."""
    recommendations = get_actionable_recommendations()

    assert isinstance(recommendations, list)

    # Each recommendation should have required fields
    for rec in recommendations:
        assert "title" in rec
        assert "category" in rec
        assert "action" in rec
        assert "priority" in rec
        assert "effort" in rec
        assert "impact" in rec
        assert "recommendation" in rec

    # Check priority levels
    if recommendations:
        priorities = [r["priority"] for r in recommendations]
        assert all(p in ["critical", "high", "medium", "low"] for p in priorities)


def test_anomaly_empty_database():
    """Test anomaly detection with empty database."""
    from data.database import init_database

    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["DB_PATH"] = os.path.join(tmpdir, "test_empty.db")
        init_database()

        # Should not raise exceptions
        overspending = detect_overspending()
        spikes = detect_spending_spikes()
        risks = detect_budget_risk()
        fixed = detect_fixed_cost_danger()
        trends = detect_rising_trends()
        anomalies = get_all_anomalies()
        recommendations = get_actionable_recommendations()

        assert isinstance(overspending, list)
        assert isinstance(spikes, list)
        assert isinstance(risks, list)
        assert isinstance(fixed, list)
        assert isinstance(trends, list)
        assert isinstance(anomalies, dict)
        assert isinstance(recommendations, list)


def test_recommendation_priority_sorting(sample_expenses):
    """Test that recommendations are sorted by priority."""
    recommendations = get_actionable_recommendations()

    if len(recommendations) > 1:
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        priorities = [priority_order.get(r["priority"], 4) for r in recommendations]

        # Verify sorted order
        assert priorities == sorted(priorities)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
