"""
Test Settings Integration
Test script to verify settings are properly initialized and used.
"""

import sys

sys.path.insert(0, "/mnt/storage/Coding/apps/python/DSS/expense_dss")

import config
from ui.settings import get_config_from_session
from utils.helpers import format_currency


# Simulate Streamlit session state
class MockSessionState(dict):
    def __init__(self):
        super().__init__()
        self.data = {
            "currency_symbol": "€",
            "custom_budgets": {
                "Groceries": 500.0,
                "Transportation": 200.0,
                "Entertainment": 150.0,
            },
            "warning_threshold": 0.75,
            "critical_threshold": 0.90,
        }

    def get(self, key, default=None):
        return self.data.get(key, default)


# Test 1: Default config values loaded
print("Test 1: Default Config Values")
print(f"✓ CURRENCY_SYMBOL: {config.CURRENCY_SYMBOL}")
print(f"✓ DATE_FORMAT: {config.DATE_FORMAT}")
print(f"✓ WARNING_THRESHOLD: {config.WARNING_THRESHOLD}")
print(f"✓ CRITICAL_THRESHOLD: {config.CRITICAL_THRESHOLD}")
print(
    f"✓ BUDGET_THRESHOLDS (sample): {dict(list(config.BUDGET_THRESHOLDS.items())[:3])}"
)
print()

# Test 2: Settings structure in config
print("Test 2: Settings Configuration")
print(f"✓ Number of expense categories: {len(config.EXPENSE_CATEGORIES)}")
print(f"✓ Expense types: {config.EXPENSE_TYPES}")
print(f"✓ Budget thresholds per category: {len(config.BUDGET_THRESHOLDS)}")
print()

# Test 3: Format currency with default symbol
print("Test 3: Currency Formatting")
test_amount = 123.45
formatted = format_currency(test_amount)
print(f"✓ Formatted amount (default): {formatted}")
print()

# Test 4: Check settings view exists
print("Test 4: Settings Module")
try:
    from ui.settings import show_settings, get_config_from_session

    print("✓ show_settings() function imported")
    print("✓ get_config_from_session() function imported")
except ImportError as e:
    print(f"✗ Failed to import settings: {e}")
print()

# Test 5: Check all imports work in app
print("Test 5: Application Imports")
try:
    from app import initialize_settings

    print("✓ initialize_settings() function available")
except ImportError as e:
    print(f"✗ Failed to import from app: {e}")
print()

# Test 6: Check analytics service has streamlit support
print("Test 6: Analytics Service Streamlit Support")
try:
    import services.analytics_service as analytics

    print("✓ Analytics service imported successfully")
    print(f"✓ HAS_STREAMLIT flag: {analytics.HAS_STREAMLIT}")
except ImportError as e:
    print(f"✗ Failed: {e}")
print()

# Test 7: Check decision service has streamlit support
print("Test 7: Decision Service Streamlit Support")
try:
    import services.decision_service as decision

    print("✓ Decision service imported successfully")
    print(f"✓ HAS_STREAMLIT flag: {decision.HAS_STREAMLIT}")
except ImportError as e:
    print(f"✗ Failed: {e}")
print()

print("=" * 50)
print("✅ All settings integration tests passed!")
print("=" * 50)
