"""
Configuration file for Expense DSS
Contains app settings, thresholds, and constants.
"""

# Database Configuration
DB_PATH = "data/expenses.db"

# Expense Categories
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]

# Expense Types
EXPENSE_TYPES = ["fixed", "variable"]

# Budget Thresholds (monthly)
BUDGET_THRESHOLDS = {
    "Food & Dining": 500,
    "Transportation": 300,
    "Shopping": 400,
    "Entertainment": 200,
    "Bills & Utilities": 350,
    "Healthcare": 250,
    "Education": 300,
    "Travel": 500,
    "Personal Care": 150,
    "Other": 200,
}

# Alert Thresholds (percentage of budget)
WARNING_THRESHOLD = 0.80  # 80% of budget
CRITICAL_THRESHOLD = 0.95  # 95% of budget

# Prediction Settings
FORECAST_DAYS = 30  # Number of days to forecast
MIN_DATA_POINTS = 10  # Minimum data points needed for predictions

# DSS Rules Thresholds
HIGH_SPENDING_THRESHOLD = 1.2  # 20% above budget
FREQUENT_EXPENSE_DAYS = 7  # Days to check for frequent expenses
FREQUENT_EXPENSE_COUNT = 5  # Number of expenses to consider "frequent"

# Anomaly Detection Thresholds
OVERSPENDING_THRESHOLD = 1.1  # 10% over budget triggers alert
SPIKE_THRESHOLD = 0.3  # 30% month-over-month increase
BUDGET_RISK_THRESHOLD = 0.75  # 75% of budget = risk zone
FIXED_COST_THRESHOLD = 0.5  # Fixed costs > 50% of total = danger
RISING_TREND_THRESHOLD = 0.15  # 15% over 3 months = rising trend

# Anomaly Detection Configuration (organized as dict for settings)
ANOMALY_DETECTION = {
    "overspending_threshold": OVERSPENDING_THRESHOLD,
    "spike_threshold": SPIKE_THRESHOLD,
    "budget_risk_threshold": BUDGET_RISK_THRESHOLD,
    "fixed_cost_threshold": FIXED_COST_THRESHOLD,
    "rising_trend_threshold": RISING_TREND_THRESHOLD,
}

# UI Settings
DATE_FORMAT = "%Y-%m-%d"  # ISO format
DATE_TIMEZONE = "UTC"  # Single timezone for consistency
CURRENCY_SYMBOL = "$"
CHART_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "warning": "#ff9800",
    "danger": "#d62728",
}
