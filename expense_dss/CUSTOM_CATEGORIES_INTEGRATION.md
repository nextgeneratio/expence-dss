# Custom Categories Feature - Integration Guide

## Quick Start

The custom category management feature is now fully integrated and ready to use.

### What's New

1. **Category Management Page** - New navigation menu item
2. **Dynamic Categories** - Add/edit/delete custom categories
3. **Database-Driven** - Categories stored in SQLite with full CRUD
4. **Flexible Budgets** - Set budgets per category
5. **Deactivation** - Soft-delete categories without losing data

## Using the Feature

### 1. Add a Custom Category

**Via Category Management Page:**
1. Select "Category Management" from sidebar
2. Click "Add Category" tab
3. Enter category name (e.g., "Gym Membership")
4. Set monthly budget (optional)
5. Click "Add Category"

**Via Settings Page:**
1. Select "Settings" from sidebar
2. Go to "Categories" tab
3. Enter category name and budget
4. Click "Add"

### 2. Manage Existing Categories

**Edit Budget:**
- Category Management → Category Budget Settings
- Adjust sliders for any category
- Click "Save All Budgets"

**Deactivate (Hide):**
- Category Management → Manage Categories
- Find category in list
- Click "Deactivate" button
- Category won't appear in dropdowns but data preserved

**Reactivate:**
- Category Management → Manage Categories
- Find deactivated category
- Click "Reactivate" button

**Delete Permanently:**
- Category Management → Manage Categories
- Click "Delete" button
- Confirm deletion (cannot be undone)
- Only works if no expenses use that category

### 3. Use Custom Categories in Expenses

**Adding Expenses:**
1. Select "Add Expense" from sidebar
2. Category dropdown now shows your custom categories
3. Select category
4. Budget for that category displays automatically
5. Fill in other details and submit

## Architecture Overview

```
User Interface
├── Category Management (Full UI)
├── Settings (Quick Add & Budget)
└── Add Expense (Category Selection)
    ↓
Service Layer
├── category_service (CRUD)
├── expense_service (validation)
└── analytics_service (usage)
    ↓
Data Layer
├── categories table (metadata)
├── expenses table (usage)
└── database schema
```

## File Structure

```
expense_dss/
├── services/
│   ├── category_service.py         [NEW] Category CRUD
│   └── ... (other services)
├── ui/
│   ├── category_management.py      [NEW] Full category UI
│   ├── views.py                    [UPDATED] Uses category_service
│   ├── settings.py                 [UPDATED] Added Categories tab
│   └── ... (other UI)
├── utils/
│   ├── migration.py                [NEW] Database migrations
│   └── ... (other utils)
├── data/
│   ├── database.py                 [UPDATED] Categories table
│   ├── models.py                   [UPDATED] Dynamic validation
│   └── ... (data layer)
├── tests/
│   ├── test_category_service.py    [NEW] 30+ tests
│   └── ... (other tests)
└── CUSTOM_CATEGORIES_FEATURE.md    [NEW] Full documentation
```

## Key Functions

### In category_service.py

```python
# Add category
category_id = category_service.add_category("Gym", 75.0)

# Get all active categories
categories = category_service.get_all_categories()

# Get just names
names = category_service.get_category_names()

# Update budget
category_service.update_category("Gym", budget=100.0)

# Deactivate
category_service.delete_category("Gym", force=False)

# Delete
category_service.delete_category("Gym", force=True)

# Reactivate
category_service.reactivate_category("Gym")

# Validate
is_valid = category_service.validate_category("Gym")

# Get budget
budget = category_service.get_category_budget("Gym")
```

## Database Schema

### Categories Table

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    budget REAL CHECK(budget > 0),
    is_custom BOOLEAN DEFAULT 1,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
- `id` - Unique identifier
- `name` - Category name (unique)
- `budget` - Monthly budget amount
- `is_custom` - 1 if user-created, 0 if system default
- `is_active` - 1 if active, 0 if deactivated
- `created_at` - When category was created

### Example Data

```
id | name            | budget | is_custom | is_active | created_at
---|-----------------|--------|-----------|-----------|-------------------
1  | Food & Dining   | 500    | 0         | 1         | 2024-01-01
2  | Transportation  | 300    | 0         | 1         | 2024-01-01
...
11 | Gym             | 75     | 1         | 1         | 2024-01-15
12 | Subscriptions   | 50     | 1         | 1         | 2024-01-15
```

## Migration Process

Automatic on first run:

1. **init_database()** - Creates schema
2. **migrate_to_categories_table()** - Adds categories table, populates defaults
3. **add_foreign_key_constraint()** - Ensures referential integrity

No user action required!

## Testing

Run the test suite:

```bash
cd expense_dss
pytest tests/test_category_service.py -v
```

Tests cover:
- ✅ Adding categories
- ✅ Duplicate detection
- ✅ Validation (empty, negative budget)
- ✅ Updates and deletion
- ✅ Filtering and queries
- ✅ Edge cases

## API Examples

### Python Usage

```python
from services import category_service

# Create custom category
id = category_service.add_category("Coffee Subscription", 15.0)

# List all active categories
all_cats = category_service.get_all_categories()
for cat in all_cats:
    print(f"{cat['name']}: ${cat['budget']}")

# Get category for form
names = category_service.get_category_names()  # For dropdown

# Check validity
if category_service.validate_category("Coffee Subscription"):
    # Safe to use in expense
    pass

# Get all budgets
budgets = category_service.get_all_budgets()
total = sum(budgets.values())
```

### In Streamlit UI

```python
import streamlit as st
from services import category_service

# Category selection
categories = category_service.get_category_names()
selected = st.selectbox("Category", categories)

# Show budget
budget = category_service.get_category_budget(selected)
st.info(f"Budget: ${budget:.2f}")

# Add new category
if st.button("Add Category"):
    category_service.add_category(name, budget)
    st.rerun()
```

## Backward Compatibility

- ✅ Old hardcoded categories still work
- ✅ Automatic migration on first run
- ✅ No data loss
- ✅ Existing expenses continue to work
- ✅ Config fallback if needed

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| Get all categories | O(1) | Cached in session |
| Add category | O(1) | Direct insert |
| Validate category | O(1) | UNIQUE index |
| Update budget | O(1) | Direct update |
| List categories | O(n) | n = category count (~15-20) |

## Troubleshooting

### Categories not showing

**Solution:**
1. Check Category Management → Manage Categories
2. Verify categories are active (✅ status)
3. Deactivated categories hidden from dropdowns

### Can't delete category

**Solution:**
1. Category has associated expenses
2. Option 1: Delete/reassign expenses first
3. Option 2: Deactivate instead (soft-delete)

### Migration errors

**Solution:**
1. Check database file exists: `data/expenses.db`
2. Ensure write permissions in `data/` directory
3. Check `app.py` runs migrations on startup

## Next Steps

1. **Test the feature** - Add a few custom categories
2. **Use in expenses** - Create expenses with custom categories
3. **Monitor** - Check Category Management for usage
4. **Customize** - Adjust budgets as needed

## Support

For issues, check:
- `CUSTOM_CATEGORIES_FEATURE.md` - Full documentation
- `tests/test_category_service.py` - Test examples
- `services/category_service.py` - Function documentation
- GitHub issues (if applicable)

## Version Info

- **Feature Added:** Custom Category Management v1.0
- **Compatibility:** All Python 3.7+, Streamlit 1.0+
- **Database:** SQLite 3.0+
- **Dependencies:** No new external dependencies

---

**Feature ready to use! Start by visiting Category Management in the sidebar.**
