# 🏗️ System Architecture & Technical Details

Complete technical documentation of the Expense DSS system design and implementation.

---

## 📐 System Architecture

### Layered Design

```
┌─────────────────────────────────────────┐
│   UI Layer (Streamlit)                  │
│  - Dashboard, Forms, Settings           │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│   Service Layer                         │
│  - Category Service                     │
│  - Expense Service                      │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│   Data Layer                            │
│  - Database Models                      │
│  - Data Validation                      │
│  - Database Operations                  │
└────────────────┬────────────────────────┘
                 │
┌─────────────────▼────────────────────────┐
│   Database Layer (SQLite)               │
│  - categories table                     │
│  - expenses table                       │
└─────────────────────────────────────────┘
```

### Directory Structure

```
expense_dss/
├── app.py                           # Main Streamlit application entry point
├── config.py                        # Configuration constants and settings
├── requirements.txt                 # Python package dependencies
│
├── data/                            # Data layer
│   ├── __init__.py
│   ├── database.py                  # Database initialization and connection
│   ├── models.py                    # Data models and validation
│   └── expense_service.py           # Expense CRUD operations
│
├── services/                        # Business logic layer
│   ├── __init__.py
│   └── category_service.py          # Category management (12 functions)
│
├── ui/                              # Presentation layer
│   ├── __init__.py
│   ├── views.py                     # Main dashboard and views
│   ├── settings.py                  # Settings and configuration UI
│   ├── history.py                   # History and analytics UI
│   └── category_management.py       # Category management interface
│
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── migration.py                 # Database schema migrations
│   └── validators.py                # Input validation utilities
│
├── tests/                           # Test suite
│   ├── __init__.py
│   └── test_category_service.py     # Unit tests (30+ test cases)
│
└── venv/                            # Python virtual environment
```

---

## 💾 Database Schema

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
- `name` - Category name (unique, required)
- `budget` - Monthly budget limit (optional)
- `is_custom` - 1 if user-created, 0 if default
- `is_active` - 1 if active, 0 if deactivated
- `created_at` - Timestamp when created

**Indexes:**
- Primary key on `id`
- Unique constraint on `name`

### Expenses Table

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL CHECK(amount > 0),
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('fixed', 'variable')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(category) REFERENCES categories(name)
)
```

**Fields:**
- `id` - Unique identifier
- `amount` - Expense amount (required, must be positive)
- `date` - Expense date (YYYY-MM-DD format)
- `category` - Category name (foreign key)
- `type` - 'fixed' or 'variable'
- `description` - Optional expense description
- `created_at` - Timestamp when recorded

**Indexes:**
- Index on `date` for fast date-range queries
- Index on `category` for category aggregations

---

## 🔧 Service API Reference

### Category Service (`services/category_service.py`)

**12 Core Functions:**

#### 1. `get_all_categories(include_inactive=False)`
Returns all categories with optional inactive filtering.
```python
categories = get_all_categories()
# Returns: [{'id': 1, 'name': 'Food', 'budget': 300, ...}, ...]
```

#### 2. `get_category_by_name(name)`
Retrieve a specific category by name.
```python
category = get_category_by_name("Dining")
# Returns: {'id': 2, 'name': 'Dining', 'budget': 250, ...} or None
```

#### 3. `add_category(name, budget=0)`
Create a new custom category.
```python
category_id = add_category("Gym", budget=50)
# Returns: 15 (ID of new category)
```

#### 4. `update_category(name, budget=None)`
Update an existing category's budget.
```python
success = update_category("Gym", budget=60)
# Returns: True if successful
```

#### 5. `delete_category(name, force=False)`
Deactivate or delete a category.
```python
success = delete_category("Gym", force=False)  # Soft delete
success = delete_category("Gym", force=True)   # Hard delete
# Returns: True if successful
```

#### 6. `reactivate_category(name)`
Reactivate a deactivated category.
```python
success = reactivate_category("Gym")
# Returns: True if successful
```

#### 7. `get_category_names(include_inactive=False)`
Get list of category names only.
```python
names = get_category_names()
# Returns: ['Food', 'Transportation', 'Dining', ...]
```

#### 8. `get_category_budget(category_name)`
Get budget for a specific category.
```python
budget = get_category_budget("Food")
# Returns: 400.0
```

#### 9. `get_all_budgets()`
Get mapping of all categories to budgets.
```python
budgets = get_all_budgets()
# Returns: {'Food': 400, 'Transport': 200, 'Dining': 250}
```

#### 10. `get_custom_categories()`
Get only user-created categories.
```python
custom = get_custom_categories()
# Returns: [{'name': 'Gym', ...}, {'name': 'Hobbies', ...}]
```

#### 11. `get_default_categories()`
Get only default categories.
```python
defaults = get_default_categories()
# Returns: [{'name': 'Food', ...}, ...]
```

#### 12. `validate_category(category_name)`
Check if a category exists and is active.
```python
is_valid = validate_category("Food")
# Returns: True or False
```

### Expense Service (`data/expense_service.py`)

Similar CRUD operations for expenses:
- `add_expense()` - Record a new expense
- `get_expenses()` - Retrieve expenses with filtering
- `update_expense()` - Modify an expense
- `delete_expense()` - Remove an expense

---

## 🔒 Security Implementation

### SQL Injection Protection

**All database queries use parameterized statements:**

```python
# ✅ SAFE - Parameterized query
cursor.execute("INSERT INTO categories (name, budget) VALUES (?, ?)", (name, budget))

# ❌ UNSAFE - String interpolation (not used)
# cursor.execute(f"INSERT INTO categories (name, budget) VALUES ('{name}', {budget})")
```

### Input Validation

**All user inputs are validated:**

1. **Category Names:**
   - Non-empty string required
   - No leading/trailing whitespace
   - Unique constraint at database level

2. **Budgets:**
   - Non-negative numbers only
   - Validated before database operations
   - Database CHECK constraint enforces > 0

3. **Expense Amounts:**
   - Must be positive
   - Validated in model layer
   - Database CHECK constraint enforces > 0

4. **Expense Types:**
   - Only 'fixed' or 'variable' allowed
   - Database CHECK constraint enforces

5. **Dates:**
   - YYYY-MM-DD format validated
   - Handled by Streamlit date picker

See [SECURITY.md](SECURITY.md) for complete security details.

---

## 🔄 Data Flow

### Adding an Expense

```
1. User fills form in Streamlit UI
                  ↓
2. Input validation (amount > 0, category exists)
                  ↓
3. Create Expense model (further validation)
                  ↓
4. Call expense_service.add_expense()
                  ↓
5. Parameterized SQL INSERT
                  ↓
6. Database stores expense
                  ↓
7. Return success/error to UI
                  ↓
8. Display confirmation to user
```

### Adding a Custom Category

```
1. User enters category name and budget in UI
                  ↓
2. Validate inputs (name not empty, unique, budget >= 0)
                  ↓
3. Call category_service.add_category()
                  ↓
4. Check name uniqueness
                  ↓
5. Parameterized SQL INSERT
                  ↓
6. Database stores category
                  ↓
7. Return category ID
                  ↓
8. Update UI to reflect new category
```

---

## 🚀 Database Migrations

The `utils/migration.py` module handles automatic schema updates:

**Features:**
- Runs on application startup
- Creates tables if they don't exist
- Adds categories table if missing
- Populates default categories
- Creates indexes for performance
- Uses parameterized queries throughout

**Migration Sequence:**
1. Check if tables exist
2. Create categories table if needed
3. Insert default categories
4. Create expenses table if needed
5. Create performance indexes
6. Commit and close connection

---

## 🧪 Testing

### Test Coverage

**Unit tests** in `tests/test_category_service.py`:
- 30+ test cases
- Tests all 12 category service functions
- Tests error conditions
- Tests validation logic
- Tests database interactions

**Running Tests:**
```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_category_service.py -v

# With coverage report
python -m pytest tests/ --cov=services --cov=data
```

### Test Categories

- ✅ Add category tests
- ✅ Get category tests
- ✅ Update category tests
- ✅ Delete category tests
- ✅ Validation tests
- ✅ Error handling tests
- ✅ Database integrity tests

---

## ⚙️ Configuration

Configuration is managed in `config.py`:

```python
# Database location
DB_PATH = "expense_dss.db"

# Default expense categories
EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Entertainment",
    # ... more categories
]

# Budget thresholds per category
BUDGET_THRESHOLDS = {
    "Food": 400,
    "Transportation": 200,
    # ... more thresholds
}
```

For detailed configuration options, see [CONFIGURATION.md](CONFIGURATION.md).

---

## 📊 Performance Considerations

### Database Indexes

Indexes are created on frequently queried fields:
- `idx_expense_date` - Fast date-range queries
- `idx_expense_category` - Fast category aggregations

### Query Optimization

- Uses `WHERE` clauses to filter early
- Indexes prevent full table scans
- Connection pooling could be added for high concurrency

### Scalability

Current implementation suitable for:
- Individual users (100K+ expenses)
- Small teams (with multiple databases)
- Production deployment with SQLite

For larger scales, consider:
- PostgreSQL or MySQL
- Caching layer (Redis)
- Connection pooling

---

## 🔗 Integration Points

### Adding New Features

**To add a new feature:**

1. **Database Schema** - Add table in `data/database.py`
2. **Service Layer** - Create service in `services/`
3. **UI Layer** - Add Streamlit components in `ui/`
4. **Tests** - Add unit tests in `tests/`
5. **Documentation** - Update relevant `.md` files

### External Integrations

Currently the system is self-contained. Potential integrations:
- Bank account APIs for automatic import
- Email notifications
- Cloud storage backup
- Mobile app API

---

## 🔗 See Also

- **[SECURITY.md](SECURITY.md)** - Security details and best practices
- **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration options
- **[FEATURES.md](FEATURES.md)** - Feature documentation
- **[QUICK_START.md](QUICK_START.md)** - Getting started
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All documentation

---

**For security implementation details, see [SECURITY.md](SECURITY.md)**
**For configuration options, see [CONFIGURATION.md](CONFIGURATION.md)**
