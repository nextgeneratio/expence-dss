# 🚀 Quick Start Guide

Get up and running in minutes, whether you're a user or developer.

---

## 👤 For End Users

### Installation & First Run

1. **Prerequisites:**
   - Python 3.10+
   - pip (Python package manager)

2. **Install the application:**
   ```bash
   cd /path/to/expense_dss
   pip install -r requirements.txt
   ```

3. **Start the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open in your browser:**
   - Go to `http://localhost:8501`
   - Application opens automatically in most cases

### First Steps

**Creating Your First Custom Category:**
1. Click **"Category Management"** in the sidebar
2. Go to **"Add Category"** tab
3. Enter category name (e.g., "Gym", "Subscriptions")
4. Set an optional monthly budget
5. Click **"Add Category"** button

**Adding Your First Expense:**
1. Click **"Add Expense"** in the main menu
2. Enter the amount
3. Select date (defaults to today)
4. Choose category (including your custom ones)
5. Select expense type (Fixed or Variable)
6. Add optional description
7. Click **"Add Expense"** button

**Viewing Your Data:**
- **Dashboard**: See spending summary and top insights
- **Expense History**: View all past expenses with filtering
- **Budget Analysis**: Monitor spending against budgets

### Common Tasks

#### Change Budget Threshold
1. Go to **"Category Management"** → **"Budget Settings"**
2. Find your category
3. Update the budget amount
4. Changes apply immediately

#### Deactivate a Category
1. Go to **"Category Management"** → **"Manage Categories"**
2. Find the category
3. Click **"Deactivate"**
4. Category won't appear in new expenses (existing data preserved)

#### Delete a Custom Category
1. Go to **"Category Management"** → **"Manage Categories"**
2. Find your custom category
3. Click **"Delete"** (only available for custom categories)

---

## 👨‍💻 For Developers

### Development Environment Setup

**1. Clone the repository:**
```bash
git clone <repository-url>
cd expense_dss
```

**2. Create a virtual environment:**
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the application:**
```bash
streamlit run app.py
```

**5. Run tests:**
```bash
python -m pytest tests/ -v
```

### Project Structure

```
expense_dss/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration constants
├── requirements.txt          # Python dependencies
│
├── data/
│   ├── __init__.py
│   ├── database.py           # Database connection and schema
│   ├── models.py             # Data validation models
│   └── expense_service.py    # Expense CRUD operations
│
├── services/
│   ├── __init__.py
│   └── category_service.py   # Category CRUD operations
│
├── ui/
│   ├── __init__.py
│   ├── views.py              # Main Streamlit pages
│   ├── settings.py           # Settings and configuration UI
│   ├── history.py            # History and analytics UI
│   └── category_management.py # Category management UI
│
├── utils/
│   ├── __init__.py
│   ├── migration.py          # Database schema migrations
│   └── validators.py         # Input validation utilities
│
└── tests/
    ├── __init__.py
    └── test_*.py             # Unit tests
```

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Specific test file
python -m pytest tests/test_category_service.py -v

# With coverage
python -m pytest tests/ --cov=services --cov=data
```

### Development Workflow

1. **Make changes** to code files
2. **Run tests** to verify: `pytest tests/ -v`
3. **Test in app**: `streamlit run app.py`
4. **Check for errors**: Look for compilation errors: `python -m py_compile file.py`
5. **Verify imports**: `python -c "from module import submodule"`

### Key Development Files

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system design
- **[SECURITY.md](SECURITY.md)** - Security considerations
- **[FEATURES.md](FEATURES.md)** - Feature documentation
- **[CONFIGURATION.md](CONFIGURATION.md)** - Config options

---

## 🐛 Troubleshooting

### Application won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify dependencies are installed
pip install -r requirements.txt

# Check for port conflicts
# Default port is 8501 - if busy, use:
streamlit run app.py --server.port 8502
```

### Import errors
```bash
# Ensure you're in the right directory
cd /path/to/expense_dss

# Verify virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate    # Windows

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Database errors
- Database automatically initializes on first run
- If issues persist, delete `expense_dss.db` and restart
- Database is created in: `./expense_dss.db`

---

## 🔗 Next Steps

- **Learn all features**: See [FEATURES.md](FEATURES.md)
- **Understand architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Configure settings**: See [CONFIGURATION.md](CONFIGURATION.md)
- **Check security**: See [SECURITY.md](SECURITY.md)
- **View all docs**: See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**Need help?** Check the documentation or create an issue in the repository.
