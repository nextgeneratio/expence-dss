# Quick Reference: Settings Integration

## Files Modified Summary

| File | Changes | Impact |
|------|---------|--------|
| `ui/settings.py` | **NEW** - Complete settings UI | Users can now customize app |
| `app.py` | Added `initialize_settings()` and Settings route | Settings initialized on startup |
| `utils/helpers.py` | `format_currency()` uses `st.session_state` | Currency updates dynamically |
| `ui/views.py` | 3 locations use `st.session_state.get("custom_budgets")` | Budgets update in real-time |
| `services/analytics_service.py` | `get_budget_utilization()` uses session budgets | Analytics use custom budgets |
| `services/decision_service.py` | 3 functions use session state for thresholds | Recommendations use custom settings |

## Settings Initialized in app.py

```
currency_symbol (str) → Default: "$"
date_format (str) → Default: "%Y-%m-%d"
forecast_days (int) → Default: 30
min_data_points (int) → Default: 10
custom_budgets (dict) → Default: BUDGET_THRESHOLDS from config
warning_threshold (float) → Default: 0.80
critical_threshold (float) → Default: 0.95
high_spending_threshold (float) → Default: 1.20
frequent_expense_days (int) → Default: 7
frequent_expense_count (int) → Default: 3
```

## Settings Tab Layout

### Tab 1: Currency & Display
```
Input: Currency Symbol (e.g., $, €)
Select: Date Format
Slider: Forecast Days (7-90)
Slider: Min Data Points (5-30)
```

### Tab 2: Budget Thresholds  
```
For each of 10 categories:
  Input: Budget amount
Display: Total Monthly Budget
Button: Save Budget Changes
```

### Tab 3: Alerts & Notifications
```
Slider: Warning Threshold (50-90%)
Slider: Critical Threshold (75-100%)
Slider: High Spending (% increase)
Slider: Frequent Expense Days (3-30)
Slider: Frequent Expense Count (2-10)
Button: Save Alert Settings
Expandable: Current Settings Summary
```

## How Each File Uses Settings

### app.py
```python
initialize_settings()  # Called at startup
st.session_state contains all user settings
show_settings()  # Routes to settings page
```

### ui/settings.py  
```python
show_settings()  # Main UI function
get_config_from_session()  # Gets current settings
Three tabs with controls
JSON export feature
```

### utils/helpers.py
```python
format_currency(amount):
  currency = st.session_state.get("currency_symbol", config.CURRENCY_SYMBOL)
  return f"{currency}{amount:,.2f}"
```

### ui/views.py
```python
show_add_expense():
  budget = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS).get(category, 0)

show_summary():
  custom_budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)

show_insights():
  custom_budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
```

### services/analytics_service.py
```python
get_budget_utilization():
  budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
  # Use budgets for utilization calculations
```

### services/decision_service.py
```python
check_high_spending():
  threshold = st.session_state.get("high_spending_threshold", config.HIGH_SPENDING_THRESHOLD)

check_unusual_patterns():
  frequent_days = st.session_state.get("frequent_expense_days", config.FREQUENT_EXPENSE_DAYS)
  frequent_count = st.session_state.get("frequent_expense_count", config.FREQUENT_EXPENSE_COUNT)

suggest_optimizations():
  budgets = st.session_state.get("custom_budgets", config.BUDGET_THRESHOLDS)
```

## Key Implementation Patterns

### Pattern 1: Safe Session State Access
```python
# Always provide fallback to config
value = st.session_state.get("setting_name", config.DEFAULT_VALUE)
```

### Pattern 2: Conditional Streamlit
```python
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Use in services
if HAS_STREAMLIT:
    try:
        value = st.session_state.get("setting", config.DEFAULT)
    except Exception:
        value = config.DEFAULT
else:
    value = config.DEFAULT
```

### Pattern 3: Initialize on Startup
```python
# In app.py
if "setting_name" not in st.session_state:
    st.session_state.setting_name = config.DEFAULT_VALUE
```

## What Users Can Now Do

✅ Change currency symbol to any symbol
✅ Set custom budget per category
✅ Adjust when warnings appear (yellow)
✅ Adjust when critical alerts appear (red)  
✅ Change forecast window for predictions
✅ Set minimum data for accurate predictions
✅ Configure frequent expense detection
✅ Export settings as JSON

## What Gets Updated Automatically

When user changes settings:
- ✅ Add Expense form shows new budget
- ✅ Summary page shows new budgets
- ✅ Currency displays with new symbol everywhere
- ✅ Budget utilization recalculates
- ✅ Alert thresholds apply to recommendations
- ✅ Pattern detection uses new settings

## Testing

All files pass:
- ✅ Syntax check: `python3 -m py_compile`
- ✅ Import test: `test_settings.py`
- ✅ No breaking changes to existing code

## Backward Compatibility

✅ Config defaults still available
✅ Services work without Streamlit
✅ Existing code unchanged
✅ New features are optional
✅ Falls back to config if needed

## Ready to Use!

```bash
streamlit run app.py
```

Then click **Settings** in sidebar to customize!
