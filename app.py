"""
Expense DSS Application - Entry Point
Main application launcher for the expense tracking and decision support system.
"""

import streamlit as st
from ui.layout import setup_page_config
from ui.views import show_add_expense, show_summary, show_insights
from ui.settings import show_settings
from ui.history_view import show_history
from ui.anomaly_view import show_anomalies
from ui.category_management import show_category_management
from data.database import init_database
from utils.migration import migrate_to_categories_table, add_foreign_key_constraint
import config


def initialize_settings():
    """Initialize user settings in session state on app startup."""
    if "currency_symbol" not in st.session_state:
        st.session_state.currency_symbol = config.CURRENCY_SYMBOL
    if "date_format" not in st.session_state:
        st.session_state.date_format = config.DATE_FORMAT
    if "forecast_days" not in st.session_state:
        st.session_state.forecast_days = config.FORECAST_DAYS
    if "min_data_points" not in st.session_state:
        st.session_state.min_data_points = config.MIN_DATA_POINTS
    if "custom_budgets" not in st.session_state:
        st.session_state.custom_budgets = dict(config.BUDGET_THRESHOLDS)
    if "warning_threshold" not in st.session_state:
        st.session_state.warning_threshold = config.WARNING_THRESHOLD
    if "critical_threshold" not in st.session_state:
        st.session_state.critical_threshold = config.CRITICAL_THRESHOLD
    if "high_spending_threshold" not in st.session_state:
        st.session_state.high_spending_threshold = config.HIGH_SPENDING_THRESHOLD
    if "frequent_expense_days" not in st.session_state:
        st.session_state.frequent_expense_days = config.FREQUENT_EXPENSE_DAYS
    if "frequent_expense_count" not in st.session_state:
        st.session_state.frequent_expense_count = config.FREQUENT_EXPENSE_COUNT

    # Initialize anomaly detection thresholds
    if "anomaly_overspending_threshold" not in st.session_state:
        st.session_state.anomaly_overspending_threshold = config.ANOMALY_DETECTION[
            "overspending_threshold"
        ]
    if "anomaly_spike_threshold" not in st.session_state:
        st.session_state.anomaly_spike_threshold = config.ANOMALY_DETECTION[
            "spike_threshold"
        ]
    if "anomaly_budget_risk_threshold" not in st.session_state:
        st.session_state.anomaly_budget_risk_threshold = config.ANOMALY_DETECTION[
            "budget_risk_threshold"
        ]
    if "anomaly_fixed_cost_threshold" not in st.session_state:
        st.session_state.anomaly_fixed_cost_threshold = config.ANOMALY_DETECTION[
            "fixed_cost_threshold"
        ]
    if "anomaly_rising_trend_threshold" not in st.session_state:
        st.session_state.anomaly_rising_trend_threshold = config.ANOMALY_DETECTION[
            "rising_trend_threshold"
        ]


def main():
    """Main application entry point."""
    # Initialize database
    init_database()

    # Run migrations
    migrate_to_categories_table()
    add_foreign_key_constraint()

    # Initialize settings
    initialize_settings()

    # Setup page configuration
    setup_page_config()

    # Sidebar navigation
    st.sidebar.title("📊 Expense DSS")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Add Expense",
            "Summary",
            "Insights & Recommendations",
            "Anomaly Detection",
            "Historical Analysis",
            "Category Management",
            "Settings",
        ],
    )

    # Route to appropriate view
    if page == "Add Expense":
        show_add_expense()
    elif page == "Summary":
        show_summary()
    elif page == "Insights & Recommendations":
        show_insights()
    elif page == "Anomaly Detection":
        show_anomalies()
    elif page == "Historical Analysis":
        show_history()
    elif page == "Category Management":
        show_category_management()
    elif page == "Settings":
        show_settings()


if __name__ == "__main__":
    main()
