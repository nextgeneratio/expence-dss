"""
Test Historical Analysis
Test script to verify historical aggregation and analysis functionality.
"""

import sys

sys.path.insert(0, "/mnt/storage/Coding/apps/python/DSS/expense_dss")

import config
from services import history_service
from datetime import datetime, timedelta

print("=" * 70)
print("HISTORICAL ANALYSIS TEST")
print("=" * 70)
print()

# Test 1: Monthly totals
print("Test 1: Monthly Totals")
print("-" * 70)
try:
    monthly_totals = history_service.get_monthly_totals()
    if monthly_totals:
        print(f"✅ Retrieved {len(monthly_totals)} months of data")
        print(f"   Latest month: {max(monthly_totals.keys())}")
        print(f"   Total spending (all months): ${sum(monthly_totals.values()):,.2f}")
        if len(monthly_totals) > 0:
            avg = sum(monthly_totals.values()) / len(monthly_totals)
            print(f"   Average per month: ${avg:,.2f}")
    else:
        print("⚠️  No monthly data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 2: Category totals
print("Test 2: Category Totals")
print("-" * 70)
try:
    category_totals = history_service.get_category_totals()
    if category_totals:
        print(f"✅ Retrieved {len(category_totals)} categories")
        top_cat = max(category_totals, key=category_totals.get)
        print(f"   Top category: {top_cat} (${category_totals[top_cat]:,.2f})")
        print("   All categories:")
        for cat, total in sorted(
            category_totals.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"     - {cat}: ${total:,.2f}")
    else:
        print("⚠️  No category data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 3: Month-over-month comparison
print("Test 3: Month-over-Month Comparison")
print("-" * 70)
try:
    comparison = history_service.get_monthly_comparison()
    print(f"✅ Month comparison generated")
    print(f"   Current month: {comparison['current_month']}")
    print(f"   Previous month: {comparison['previous_month']}")
    print(f"   Current total: ${comparison['current_total']:,.2f}")
    print(f"   Previous total: ${comparison['previous_total']:,.2f}")
    print(
        f"   Change: ${comparison['change']:,.2f} ({comparison['change_percent']:+.1f}%)"
    )
    if comparison["category_comparison"]:
        print("   Top category changes:")
        top_changes = sorted(
            comparison["category_comparison"].items(),
            key=lambda x: abs(x[1]["change"]),
            reverse=True,
        )[:3]
        for cat, data in top_changes:
            print(
                f"     - {cat}: ${data['change']:+,.2f} ({data['change_percent']:+.1f}%)"
            )
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 4: Category monthly distribution
print("Test 4: Category Monthly Distribution")
print("-" * 70)
try:
    category_monthly = history_service.get_category_monthly_totals()
    if category_monthly:
        print(f"✅ Retrieved category-monthly data")
        print(f"   Categories: {len(category_monthly)}")
        for cat, months in list(category_monthly.items())[:2]:
            print(f"   - {cat}: {len(months)} months of data")
            latest_month = max(months.keys())
            print(f"     Latest ({latest_month}): ${months[latest_month]:,.2f}")
    else:
        print("⚠️  No category-monthly data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 5: Spending velocity
print("Test 5: Spending Velocity")
print("-" * 70)
try:
    velocity = history_service.get_spending_velocity()
    print(f"✅ Velocity metrics calculated")
    print(f"   Daily average: ${velocity['daily_average']:,.2f}")
    print(f"   Weekly average: ${velocity['weekly_average']:,.2f}")
    print(f"   Monthly average: ${velocity['monthly_average']:,.2f}")
    print(f"   Total days tracked: {velocity['total_days_tracked']}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 6: Seasonal analysis
print("Test 6: Seasonal Analysis")
print("-" * 70)
try:
    seasonal = history_service.get_seasonal_analysis()
    if seasonal:
        print(f"✅ Seasonal analysis completed")
        print(f"   Quarters analyzed: {len(seasonal)}")
        for quarter, total in sorted(seasonal.items()):
            print(f"   - {quarter}: ${total:,.2f}")
    else:
        print("⚠️  No seasonal data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 7: Expense type distribution
print("Test 7: Expense Type Distribution")
print("-" * 70)
try:
    type_dist = history_service.get_expense_type_distribution()
    if type_dist:
        print(f"✅ Type distribution retrieved")
        for exp_type, total in sorted(type_dist.items()):
            print(f"   - {exp_type}: ${total:,.2f}")
    else:
        print("⚠️  No type distribution data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 8: Top expense categories
print("Test 8: Top Expense Categories")
print("-" * 70)
try:
    top_cats = history_service.get_top_expense_categories(limit=5)
    if top_cats:
        print(f"✅ Top {len(top_cats)} categories retrieved")
        for rank, (cat, total) in enumerate(top_cats, 1):
            print(f"   {rank}. {cat}: ${total:,.2f}")
    else:
        print("⚠️  No category data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 9: Spending trend
print("Test 9: Spending Trend (6 months)")
print("-" * 70)
try:
    trend = history_service.get_spending_trend(months=6)
    if trend:
        print(f"✅ Trend data retrieved: {len(trend)} months")
        print("   Monthly trend:")
        for month, total in sorted(trend.items()):
            print(f"     - {month}: ${total:,.2f}")
    else:
        print("⚠️  No trend data available yet")
except Exception as e:
    print(f"❌ Error: {e}")
print()

# Test 10: Yearly comparison
print("Test 10: Yearly Comparison")
print("-" * 70)
try:
    from services.expense_service import get_all_expenses

    expenses = get_all_expenses()
    years = sorted(set(int(e.date[:4]) for e in expenses))

    if len(years) >= 2:
        yearly = history_service.get_yearly_comparison(years[0], years[-1])
        print(f"✅ Yearly comparison: {years[0]} vs {years[-1]}")
        print(f"   Year {years[0]} total: ${yearly['year1_total']:,.2f}")
        print(f"   Year {years[-1]} total: ${yearly['year2_total']:,.2f}")
        print(f"   Change: ${yearly['change']:,.2f} ({yearly['change_percent']:+.1f}%)")
    else:
        print(f"⚠️  Need 2+ years of data. Have: {years}")
except Exception as e:
    print(f"❌ Error: {e}")
print()

print("=" * 70)
print("✅ HISTORICAL ANALYSIS TESTS COMPLETED")
print("=" * 70)
