# ⚙️ Configuration & Customization

Settings and options for customizing the Expense DSS application.

---

## 🎯 Quick Configuration

### Basic Settings

**In `config.py`:**

```python
# Database location
DB_PATH = "expense_dss.db"

# Initial budget thresholds
BUDGET_THRESHOLDS = {
    "Food": 400,
    "Transportation": 200,
    "Entertainment": 150,
    # ...
}
```

### Application Settings

Access via **Settings** menu in the Streamlit application:

- **Page Configuration** - Layout and appearance
- **Default Category** - For new expenses
- **Theme** - Light/dark mode (if available)
- **Display Format** - Numerical precision and formatting

---

## 🏷️ Custom Category Settings

### Creating Categories

1. Go to **Category Management**
2. Click **Add Category** tab
3. Enter category name (must be unique)
4. Set monthly budget (optional)
5. Click **Add Category**

### Managing Categories

Once created, manage in **Manage Categories** tab:

- **View** - See all categories with budgets
- **Edit Budget** - Update the monthly limit
- **Deactivate** - Hide category temporarily
- **Delete** - Remove custom category
- **Reactivate** - Restore deactivated category

### Category Configuration Tips

**Naming Conventions:**
- Use clear, descriptive names
- "Gym Membership" instead of "GM"
- "Coffee & Snacks" instead of "CS"
- Names are case-insensitive

**Budget Settings:**
- Set to 0 for unlimited/untracked
- Realistic amounts based on your spending
- Review and adjust monthly as needed
- System alerts when approaching budget

**Category Organization:**
- Group related items (e.g., "subscriptions")
- Keep number of categories manageable
- Deactivate unused categories rather than delete

---

## 💰 Budget Configuration

### Setting Budgets

**For Each Category:**
1. Go to **Category Management** → **Budget Settings**
2. Find category in list
3. Update budget amount
4. Changes apply immediately

**Budget Formula:**
```
Monthly Budget = Expected spending for that category
Example: Food = $400 means you plan to spend up to $400/month on food
```

### Budget Thresholds

Default thresholds in `config.py`:

```python
BUDGET_THRESHOLDS = {
    "Food": 400,
    "Transportation": 200,
    "Entertainment": 150,
    "Healthcare": 100,
    "Shopping": 200,
    "Utilities": 150,
    "Other": 100,
}
```

### Budget Alerts

The system shows:
- ✅ **Green** - Under budget
- ⚠️ **Yellow** - 80-100% of budget
- 🔴 **Red** - Over budget

---

## 📊 Expense Categories

### Default Categories

Pre-configured categories:

| Category | Default Budget | Type | Purpose |
|----------|---|---|---|
| Food | $400 | Variable | Groceries, restaurants, dining |
| Transportation | $200 | Variable | Gas, public transit, rides |
| Entertainment | $150 | Variable | Movies, games, hobbies |
| Healthcare | $100 | Variable | Medicine, doctor visits |
| Shopping | $200 | Variable | Clothing, general retail |
| Utilities | $150 | Fixed | Electricity, water, internet |
| Other | $100 | Variable | Miscellaneous expenses |

### Expense Types

**Fixed Expenses:**
- Recurring regularly
- Amount is predictable
- Examples: Rent, subscriptions, insurance
- Mark as "Fixed" when adding

**Variable Expenses:**
- Irregular or one-time
- Amount varies
- Examples: Dining, shopping, gas
- Mark as "Variable" when adding

---

## 🔧 Environment Variables

**Optional environment configuration:**

```bash
# Database location (if different from default)
export EXPENSE_DSS_DB_PATH="/path/to/database.db"

# Streamlit configuration (in ~/.streamlit/config.toml)
[theme]
primaryColor = "#FF6692"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#31333F"
```

### Streamlit Configuration

**File:** `~/.streamlit/config.toml`

```toml
[server]
maxUploadSize = 200  # MB
port = 8501

[theme]
primaryColor = "#FF6692"
backgroundColor = "#FFFFFF"

[logger]
level = "info"

[client]
showErrorDetails = true
```

---

## 💾 Database Configuration

### Database Location

Default: `./expense_dss.db` (in application directory)

**To change location:**
1. Edit `config.py`:
   ```python
   DB_PATH = "/custom/path/expense_dss.db"
   ```
2. Restart application

### Database Backup

**Manual Backup:**
```bash
# Copy database file
cp expense_dss.db expense_dss_backup_$(date +%Y%m%d).db
```

**Automated Backups:**
- Create a cron job (Linux/Mac)
- Create a scheduled task (Windows)

### Database Reset

**To reset database (⚠️ WARNING: Deletes all data):**
```bash
# Remove database file
rm expense_dss.db

# Or on Windows:
del expense_dss.db

# Restart application - new database created
```

---

## 🔐 Security Configuration

### Input Validation

**Enabled by default:**
- Category names: Non-empty, unique
- Budgets: Non-negative numbers
- Amounts: Positive numbers required
- Types: 'fixed' or 'variable' only
- Dates: YYYY-MM-DD format

### Database Security

**SQL Injection Protection:**
- All queries use parameterized statements
- No string interpolation in SQL
- User input never directly in queries

**Access Control:**
- Single-user application (local use)
- No built-in user authentication
- If multi-user needed, add authentication layer

See [SECURITY.md](SECURITY.md) for complete security information.

---

## 🎨 UI Customization

### Streamlit Theme

**Light/Dark Mode:**
1. Go to **Settings** in Streamlit app
2. Select "Light" or "Dark" theme
3. Changes persist across sessions

### Page Layout

**In Streamlit (built-in):**
- Default: Sidebar layout
- Can switch to: Full-width layout

### Display Options

**In application Settings:**
- Number precision (2 decimal places)
- Currency symbol ($ by default)
- Date format (MM/DD/YYYY default)

---

## 📈 Analytics Configuration

### Dashboard Display

**Customizable metrics:**
- Total spending (month to date)
- Budget utilization (by category)
- Spending trends (daily, weekly)
- Top categories

### Report Options

**Available reports:**
- Daily expense summary
- Category breakdown
- Budget vs actual
- Spending trends
- Anomaly detection results

---

## 🚀 Performance Configuration

### Query Optimization

**Indexes are created on:**
- `expenses.date` - Fast date queries
- `expenses.category` - Fast category aggregation

**Database size limits:**
- SQLite supports: ~100,000+ expenses
- No hard limit in application code
- Performance degrades with very large datasets (1M+ records)

### Caching

**No application-level caching currently.**
- Possible enhancement: Cache category lists
- Possible enhancement: Cache budget calculations

---

## 📋 Common Configuration Tasks

### Task: Change Default Budget for Food Category

```python
# In config.py
BUDGET_THRESHOLDS = {
    "Food": 500,  # Changed from 400 to 500
    # ... other categories
}
```

### Task: Add a New Default Category

```python
# In config.py - add to EXPENSE_CATEGORIES
EXPENSE_CATEGORIES = [
    # ... existing categories
    "Gym",  # New category
]

# Add budget for new category
BUDGET_THRESHOLDS = {
    # ... existing budgets
    "Gym": 50,  # Budget for new category
}
```

### Task: Change Database Location

```python
# In config.py
DB_PATH = "/var/data/expense_dss/database.db"

# Create directory if needed
mkdir -p /var/data/expense_dss
```

### Task: Enable Debug Logging

```bash
# Set environment variable
export STREAMLIT_LOGGER_LEVEL=debug

# Or edit ~/.streamlit/config.toml
[logger]
level = "debug"
```

---

## 🔗 See Also

- **[SECURITY.md](SECURITY.md)** - Security settings
- **[FEATURES.md](FEATURES.md)** - Feature configuration
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical configuration
- **[QUICK_START.md](QUICK_START.md)** - Getting started
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All documentation

---

**For advanced configuration or custom modifications, see [ARCHITECTURE.md](ARCHITECTURE.md)**
