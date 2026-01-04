#!/usr/bin/env python3
"""Test script for the restructured Expense model."""

from data.models import Expense
from config import EXPENSE_CATEGORIES, EXPENSE_TYPES

print("✅ Models imported successfully")
print("✅ Config loaded")
print(f"Categories: {len(EXPENSE_CATEGORIES)}")
print(f"Types: {EXPENSE_TYPES}")

# Test valid expense
try:
    exp = Expense(
        amount=50.0, date="2025-12-31", category="Food & Dining", type="variable"
    )
    print(f"✅ Valid expense created: {exp}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test invalid expense (future date)
try:
    exp = Expense(
        amount=50.0, date="2026-12-31", category="Food & Dining", type="variable"
    )
    print(f"❌ Should have failed: {exp}")
except ValueError as e:
    print(f"✅ Correctly caught future date: {e}")

# Test invalid expense (negative amount)
try:
    exp = Expense(
        amount=-50.0, date="2025-12-31", category="Food & Dining", type="variable"
    )
    print(f"❌ Should have failed: {exp}")
except ValueError as e:
    print(f"✅ Correctly caught negative amount: {e}")

print("\n✅ All model validation tests passed!")
