# Historical Analysis Quick Reference

## 🎯 What's New

Three new modules added for comprehensive historical analysis:

1. **services/history_service.py** - Data aggregation logic
2. **ui/charts_history.py** - Visualization library
3. **ui/history_view.py** - User interface
4. **app.py** - Updated with Historical Analysis route

## 📊 Available Analyses

### Monthly Totals
```python
monthly_totals = history_service.get_monthly_totals()
# Returns: {"2025-12": 1500.50, "2026-01": 2300.75, ...}
```

### Category Breakdown
```python
category_totals = history_service.get_category_totals()
# Returns: {"Groceries": 5000, "Transportation": 2000, ...}

category_monthly = history_service.get_category_monthly_totals()
# Returns: {"Groceries": {"2025-12": 500, ...}, ...}
```

### Comparisons
```python
# Month-over-month
comparison = history_service.get_monthly_comparison("2026-01")
# Returns: {current_total, previous_total, change, change_percent, category_comparison}

# Year-over-year
yearly = history_service.get_yearly_comparison(2025, 2026)
# Returns: {year1_total, year2_total, year1_monthly, year2_monthly, ...}
```

### Trends
```python
# Spending trend for category
trend = history_service.get_spending_trend("Groceries", months=12)
# Returns: {"2025-01": 450, "2025-02": 480, ...}

# All categories trend
trend = history_service.get_spending_trend(months=12)
```

### Velocity Metrics
```python
velocity = history_service.get_spending_velocity()
# Returns: {
#   "daily_average": 50.00,
#   "weekly_average": 350.00,
#   "monthly_average": 1500.00,
#   "total_days_tracked": 365,
#   "total_amount": 547500.00
# }
```

### Distribution & Patterns
```python
# Fixed vs variable expenses
type_dist = history_service.get_expense_type_distribution("2026-01")
# Returns: {"fixed": 800, "variable": 500}

# Seasonal (quarterly)
seasonal = history_service.get_seasonal_analysis()
# Returns: {"2025-Q1": 4500, "2025-Q2": 4800, ...}

# Top categories
top = history_service.get_top_expense_categories(limit=5)
# Returns: [("Groceries", 5000), ("Transportation", 2000), ...]
```

## 📈 Visualization Functions

### Create Charts
```python
from ui import charts_history

# Monthly trend
fig = charts_history.create_monthly_totals_chart(monthly_totals)

# Category comparison
fig = charts_history.create_category_comparison_chart(category_totals)

# Heatmap
fig = charts_history.create_category_heatmap(category_monthly)

# Waterfall
fig = charts_history.create_waterfall_comparison(comparison_data)

# Trend
fig = charts_history.create_spending_trend_chart(trend, "Groceries")

# Seasonal
fig = charts_history.create_seasonal_chart(seasonal_data)
```

## 🎨 UI Tabs

### Tab 1: Monthly Overview
- Monthly spending chart with average line
- Quarterly seasonal analysis
- Running totals table
- Key metrics

### Tab 2: Category Analysis
- Category comparison bar chart
- Category heatmap (month × category)
- Category breakdown table
- Monthly details

### Tab 3: Month-over-Month
- Current vs previous month metrics
- Waterfall chart of changes
- Category comparison bars
- Detailed change table

### Tab 4: Yearly Comparison
- Select two years to compare
- Monthly breakdown by year
- Category comparison across years
- Growth rate metrics

### Tab 5: Trends & Velocity
- Daily/weekly/monthly velocity
- Category trend selection
- 12-month trend chart
- Spending velocity bars

### Tab 6: Detailed Breakdown
- Year summary with categories
- Monthly summary with details
- Category summary with trends
- Type distribution (fixed/variable)

## 🚀 How to Use

### 1. View Historical Analysis
```
streamlit run app.py
→ Click "📊 Historical Analysis" in sidebar
→ Choose desired analysis tab
```

### 2. Basic Workflow
```
Tab 1: See overall monthly trends
Tab 2: Identify top categories
Tab 3: Compare recent months
Tab 4: Analyze year-over-year growth
Tab 5: Review spending velocity
Tab 6: Deep dive into specifics
```

### 3. Interpret Charts
- **Line Charts**: Trend over time
- **Heatmaps**: Intensity of spending
- **Bars**: Category or period comparison
- **Pie Charts**: Distribution/percentage
- **Waterfall**: Change breakdown

## 📊 Key Metrics

### Totals
- Monthly totals (12 months)
- All-time totals
- Year totals
- Category totals

### Changes
- Month-over-month change
- Percentage change month-to-month
- Year-over-year change
- Percentage change year-to-year

### Averages
- Daily average spending
- Weekly average spending
- Monthly average spending
- Average per category

### Patterns
- Seasonal trends (quarterly)
- Category trends (12 months)
- Expense type distribution
- Top categories

## 🔍 Analysis Examples

### Q1: What categories drove spending this year?
→ Tab 2: Category Analysis → View heatmap and breakdown

### Q2: Am I spending more or less than last year?
→ Tab 4: Yearly Comparison → Select years

### Q3: What's my typical daily spending?
→ Tab 5: Trends & Velocity → View velocity metrics

### Q4: Why did expenses spike last month?
→ Tab 3: Month-over-Month → View waterfall and categories

### Q5: Which quarters are expensive?
→ Tab 1: Monthly Overview → View seasonal chart

### Q6: Is a specific category trending up or down?
→ Tab 5: Trends & Velocity → Select category and view trend

## 💡 Tips

1. **Start with Monthly Overview** for high-level insights
2. **Use Category Analysis** to identify top spenders
3. **Check Month-over-Month** for recent changes
4. **Compare Years** to understand growth patterns
5. **Review Trends** for category-specific insights
6. **Deep Dive** in Tab 6 when you need details

## 🎓 Data Interpretation

### Green signals (Good):
- Spending decreasing month-over-month
- Categories within budget
- Consistent patterns (predictable)

### Red flags (Watch out):
- Spending increasing sharply
- Categories exceeding budget
- Sudden spikes or anomalies

### Analysis insights:
- High seasonal variance → Plan for seasonal months
- Consistent growth → Adjust budgets upward
- Category concentration → Diversify or focus
- Velocity increasing → Review spending

## 📱 Mobile & Desktop

✅ Responsive charts work on all devices
✅ Tables scroll horizontally if needed
✅ Interactive hover details
✅ Downloadable PNG charts
✅ Tab-based organization for easy navigation

## 🔧 Advanced Usage

### Custom Analyses via Console
```python
from services import history_service

# Get last 6 months
trend = history_service.get_spending_trend(months=6)

# Get specific year
year_data = history_service.get_category_year_totals(2025)

# Get top 10 categories
top10 = history_service.get_top_expense_categories(limit=10)
```

### Integrate with Decision Service
```python
# Use historical data to improve recommendations
monthly_avg = sum(get_monthly_totals().values()) / len(get_monthly_totals())

# Alert if current > monthly_avg * 1.5
```

## ✅ Test Coverage

All functions tested:
- ✅ get_monthly_totals
- ✅ get_category_totals
- ✅ get_monthly_comparison
- ✅ get_yearly_comparison
- ✅ get_spending_trend
- ✅ get_spending_velocity
- ✅ get_seasonal_analysis
- ✅ get_expense_type_distribution
- ✅ get_top_expense_categories

Run tests: `python3 test_history.py`

## 📖 Documentation

Full details in `HISTORICAL_ANALYSIS.md`

## Summary

Historical analysis provides:
- **10+** aggregation functions
- **12+** chart types
- **6-tab** comprehensive UI
- **Real-time** calculations
- **Flexible** filtering
- **Production-ready** code
