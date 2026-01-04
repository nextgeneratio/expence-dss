# Custom Category Management Feature

## Overview

The Custom Category Management feature allows users to define and manage their own expense categories in addition to the system-provided default categories. This provides flexibility for tracking domain-specific expenses while maintaining consistency with the core DSS system.

## Features

### 1. **Add Custom Categories**
- Users can create new expense categories with custom names
- Each category has a configurable monthly budget
- Custom categories are marked as `is_custom = 1` in the database
- Category names must be unique

### 2. **Edit Categories**
- Update budget thresholds for any category
- Modify existing category settings

### 3. **Deactivate/Reactivate Categories**
- Soft-delete by deactivating categories (marks `is_active = 0`)
- Reactivate previously deactivated categories
- Prevents data loss by keeping expense history intact

### 4. **Delete Categories**
- Force-delete custom categories (requires no associated expenses)
- Default categories cannot be deleted without explicit force flag
- Shows error if category has associated expenses

### 5. **Dynamic Category Validation**
- Expense validation now checks database instead of hardcoded config
- New expenses can only use active categories
- Invalid category references are caught at validation layer

## Architecture

### Database Schema

**Categories Table:**
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

**Expenses Table (Updated):**
```sql
CREATE TABLE expenses (
    ...
    category TEXT NOT NULL,
    ...
    FOREIGN KEY(category) REFERENCES categories(name)
)
```

### Service Layer: `services/category_service.py`

Core functions:

| Function | Purpose | Returns |
|----------|---------|---------|
| `get_all_categories()` | Retrieve all active categories | `List[Dict]` |
| `get_category_names()` | Get category names for dropdowns | `List[str]` |
| `get_category_by_name()` | Fetch specific category data | `Dict or None` |
| `add_category()` | Create new custom category | `int` (category_id) |
| `update_category()` | Update budget for category | `bool` |
| `delete_category()` | Deactivate or delete category | `bool` |
| `reactivate_category()` | Restore deactivated category | `bool` |
| `validate_category()` | Check if category exists & active | `bool` |
| `get_category_budget()` | Get budget for category | `float` |
| `get_all_budgets()` | Get budget dict for all | `Dict[str, float]` |
| `get_custom_categories()` | Get user-defined categories only | `List[Dict]` |
| `get_default_categories()` | Get system categories only | `List[Dict]` |

### UI Layers

#### 1. **Category Management Page** (`ui/category_management.py`)
Dedicated page with three tabs:

**Tab 1: Add Category**
- Text input for category name
- Number input for budget
- Validation and feedback

**Tab 2: Manage Categories**
- List all custom categories with status
- Edit, deactivate, reactivate, delete buttons per category
- Display default categories (read-only with reactivate option)
- Confirmation dialog for destructive actions

**Tab 3: Budget Settings**
- Quick budget adjustment for all active categories
- Displays current budget allocations
- Save all changes at once

#### 2. **Settings Page Integration** (`ui/settings.py`)
Added new Tab 3: Categories
- Quick category statistics (total, custom, default)
- Quick-add category form
- Link to full Category Management page

#### 3. **Add Expense Form** (`ui/views.py`)
- Updated category selector to use `category_service.get_category_names()`
- Now displays only active categories
- Shows budget for selected category dynamically

## Data Migration

### Migration Strategy

The system automatically handles migration from hardcoded to database-driven categories:

**`utils/migration.py` functions:**

1. **`migrate_to_categories_table()`**
   - Creates categories table if missing
   - Populates default categories from config
   - Uses `INSERT OR IGNORE` to prevent duplicates
   - Safe to call multiple times

2. **`add_foreign_key_constraint()`**
   - Checks for orphaned expenses
   - Creates categories for orphaned entries
   - Ensures referential integrity

3. **`get_migration_status()`**
   - Returns current migration state
   - Identifies data consistency issues
   - Used for health checks

**Automatic Initialization:**
- Called in `app.py` during startup
- `init_database()` creates base schema
- Migrations run before UI initialization

## Implementation Details

### Default Categories

System ships with 10 default categories:
- Food & Dining
- Transportation  
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Travel
- Personal Care
- Other

Default budgets configured in `config.py`:
```python
BUDGET_THRESHOLDS = {
    "Food & Dining": 500,
    "Transportation": 300,
    ...
}
```

### Validation Flow

```
Expense Creation
    ↓
Model Validation (_validate in models.py)
    ↓
_get_category_validator() → category_service.validate_category()
    ↓
Check: Is category active? (is_active = 1)
    ↓
Accept if valid, reject with error if invalid
```

### Budget Management

Budgets stored in two places for compatibility:

1. **Database** (`categories.budget`)
   - Persistent storage
   - Updated via `category_service.update_category()`
   - Primary source of truth

2. **Session State** (`st.session_state.custom_budgets`)
   - Used for display in settings
   - Synced with database on save
   - Fallback for legacy code

## API Usage Examples

### Adding a Custom Category

```python
from services import category_service

# Add category with budget
category_id = category_service.add_category(
    name="Gym Membership",
    budget=75.0
)
```

### Managing Categories

```python
# Get all active categories
categories = category_service.get_all_categories()

# Get just names for dropdown
names = category_service.get_category_names()

# Update budget
category_service.update_category("Gym Membership", budget=100.0)

# Deactivate (soft delete)
category_service.delete_category("Gym Membership", force=False)

# Reactivate
category_service.reactivate_category("Gym Membership")

# Validate category
if category_service.validate_category("Gym Membership"):
    # Safe to use in expense
```

### Querying Categories

```python
# Get category details
cat = category_service.get_category_by_name("Gym Membership")
# Returns: {'id': 5, 'name': 'Gym Membership', 'budget': 75.0, 
#           'is_custom': 1, 'is_active': 1}

# Get all budgets as dict
budgets = category_service.get_all_budgets()
# Returns: {'Food & Dining': 500, 'Gym Membership': 75.0, ...}

# Get custom categories only
custom = category_service.get_custom_categories()

# Get default categories only
default = category_service.get_default_categories()
```

## Testing

Comprehensive test suite in `tests/test_category_service.py`:

**Test Classes:**
1. `TestCategoryOperations` - CRUD operations
2. `TestCategoryValidation` - Validation functions
3. `TestCategoryFiltering` - Category filtering
4. `TestCategoryEdgeCases` - Edge cases and error handling

**Coverage:**
- Adding categories (success and failures)
- Duplicate detection
- Validation (empty, negative budget)
- Update operations
- Soft/hard delete
- Reactivation
- Budget tracking
- Category filtering
- Whitespace trimming

**Running Tests:**
```bash
pytest tests/test_category_service.py -v
```

## Security Considerations

1. **Input Validation**
   - Category names validated for length and content
   - Budget values checked for negativity
   - Names trimmed of whitespace

2. **Data Integrity**
   - Unique constraint on category names
   - FK constraint between expenses and categories
   - Soft-delete prevents accidental data loss

3. **User Permissions**
   - No role-based access control currently
   - Default categories protected (cannot delete without force)
   - All users see all categories

## Performance

- **Indexing:** Automatic SQLite ROWID index on primary key
- **Query Performance:** O(1) lookups by category name due to UNIQUE constraint
- **Memory:** Categories cached in session state for dropdown rendering
- **Database:** Single SELECT per category operation

## Backward Compatibility

- ✅ Existing hardcoded categories still work via migration
- ✅ Expense model validates against both old and new systems
- ✅ Config fallback for categories if service unavailable
- ✅ Session state continues to work alongside database

## Known Limitations

1. **Category Renaming**
   - Current implementation doesn't support renaming
   - Workaround: Create new category, reassign expenses, delete old
   - Future enhancement: Add rename function with CASCADE UPDATE

2. **Bulk Operations**
   - No bulk add/update/delete
   - Future: Add batch import/export

3. **Category Merging**
   - Cannot merge expenses from multiple categories
   - Future: Add merge function with expense reassignment

## Future Enhancements

1. **Category Hierarchy** - Support category groups
2. **Budget History** - Track budget changes over time
3. **Category Templates** - Pre-built category sets for different use cases
4. **Export/Import** - CSV import/export of custom categories
5. **Category Suggestions** - AI-powered category recommendations
6. **Budget Analytics** - By-category budget efficiency tracking

## Configuration

Default categories and budgets defined in `config.py`:

```python
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    # ... more categories
]

BUDGET_THRESHOLDS = {
    "Food & Dining": 500,
    "Transportation": 300,
    # ... more budgets
}
```

To modify defaults, edit these constants and restart the application.

## Troubleshooting

### Issue: "Category does not exist or is inactive"

**Cause:** Trying to create expense with invalid category
**Solution:** 
1. Check Category Management page for active categories
2. Reactivate category if needed
3. Verify category name spelling

### Issue: "Cannot delete category with associated expenses"

**Cause:** Category has expenses but force-delete attempted
**Solution:**
1. Deactivate category instead (soft-delete)
2. Or reassign/delete expenses first
3. Then delete category

### Issue: Categories not showing in dropdown

**Cause:** Categories deactivated or not created
**Solution:**
1. Go to Category Management → Manage Categories
2. Check if categories are active (✅ Active status)
3. Reactivate if needed
4. Add new categories if needed

## Files Modified

- `data/database.py` - Added categories table schema
- `data/models.py` - Updated validation to use category service
- `services/expense_service.py` - No changes needed (uses model validation)
- `services/category_service.py` - NEW: Category CRUD operations
- `ui/views.py` - Updated to get categories from database
- `ui/settings.py` - Added Categories tab
- `ui/category_management.py` - NEW: Full category management UI
- `app.py` - Added migration calls
- `utils/migration.py` - NEW: Database migrations
- `tests/test_category_service.py` - NEW: 30+ test cases

## Summary

The Custom Category Management feature transforms the system from fixed to flexible category handling while maintaining data integrity, backward compatibility, and system reliability. Users can now customize their expense tracking to fit their needs exactly.
