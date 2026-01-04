# ✨ Features & User Guide

Complete guide to all Expense DSS features with examples and usage instructions.

---

## 📋 User Guide

### Expense Management

#### Adding Expenses
Navigate to **Add Expense** from the main menu:

1. **Amount** - Enter the expense amount (required)
2. **Date** - Select the date (defaults to today)
3. **Category** - Choose from predefined or custom categories:
   - Default: Food, Transportation, Entertainment, etc.
   - Custom: Your own created categories
4. **Expense Type** - Select:
   - **Fixed**: Regular recurring expenses (rent, subscriptions)
   - **Variable**: One-time or irregular expenses
5. **Description** - Optional details (e.g., "Lunch at Joe's", "Uber to office")
6. **Add** - Click button to save

**Example:**
```
Amount: 45.50
Date: 2024-01-15
Category: Dining
Type: Variable
Description: Dinner with friends
```

#### Viewing Expenses
**Expense History** tab shows:
- All recorded expenses with dates and amounts
- Sortable by date, category, amount
- Filter by date range or category
- Quick statistics (total, count, average)

#### Tracking Expenses
**Dashboard** shows:
- Total spending this month
- Spending by category (pie chart)
- Recent expenses
- Budget status (on/over budget indicators)

### 🎯 Custom Expense Categories

**Create unlimited custom categories tailored to your needs.**

#### Creating Categories
1. Click **"Category Management"** in sidebar
2. Go to **"Add Category"** tab
3. Enter unique category name:
   - Example: "Gym Membership", "Subscriptions", "Hobbies"
   - Names are case-insensitive
   - Must be unique (can't duplicate existing categories)
4. Set optional monthly budget:
   - Leave at 0 for unlimited/untracked
   - Enter amount for budget tracking
5. Click **"Add Category"**

#### Managing Categories
1. Go to **"Category Management"** → **"Manage Categories"**
2. View all active custom and default categories
3. For each category, you can:
   - **Edit Budget** - Change the monthly budget limit
   - **Deactivate** - Hide category (data is preserved)
   - **Delete** - Remove custom category (only custom allowed)
   - **Reactivate** - Restore deactivated categories

#### Budget Settings
1. Go to **"Category Management"** → **"Budget Settings"**
2. View all categories and their budgets
3. Update budget for any category
4. Real-time validation ensures non-negative budgets

**Why Custom Categories?**
- Track specific spending areas important to you
- Set individual budgets for different areas
- Better decision-making with detailed categorization
- Analyze trends in your priorities

### 💰 Budget Management

#### Setting Budgets
1. Go to **Category Management** → **Budget Settings**
2. For each category, enter monthly budget
3. Leave at 0 for no budget limit

#### Viewing Budget Status
**Dashboard** shows:
- Green indicator: Under budget
- Yellow indicator: Approaching budget
- Red indicator: Over budget

**Budget Analysis** page shows:
- Category-by-category breakdown
- Percentage of budget used
- Remaining budget
- Spending rate ($/day)

---

## 🤖 Decision Support Features

### AI-Powered Insights

**Get intelligent recommendations based on your spending:**

- **Spending Trends** - Identify patterns in your expenses
- **Category Recommendations** - Suggestions for managing specific categories
- **Budget Optimization** - Recommendations for budget adjustments
- **Anomaly Alerts** - Unusual spending patterns detected

**Example Insights:**
- "Your Dining expenses are 20% over budget"
- "Your Transportation spending has increased 30% this month"
- "Consider adjusting your Entertainment budget based on trends"

### Anomaly Detection

**Automatic detection of unusual spending patterns:**

**How it works:**
1. System analyzes historical spending patterns
2. Detects expenses that deviate significantly
3. Alerts you to potential unusual transactions
4. Helps identify fraud or unexpected spending

**Example:**
- Normal dinner: $25
- Anomaly detected: $150 in Dining (unusual transaction flagged)

### Historical Analysis

**Understand your spending over time:**

- **Daily trends** - Day-by-day spending patterns
- **Weekly summaries** - Week-over-week comparisons
- **Monthly reports** - Month-to-month analysis
- **Category trends** - How each category changes over time
- **Predictions** - Forecast end-of-month spending

---

## 📊 Technical Overview

### Architecture

The application uses a **layered architecture**:

```
User Interface (Streamlit)
        ↓
Business Logic (Services)
        ↓
Data Access (Models & Database)
        ↓
SQLite Database
```

### Layers

1. **UI Layer** (`ui/`)
   - Streamlit pages and components
   - User input handling
   - Results display

2. **Service Layer** (`services/`)
   - Business logic
   - Category operations
   - Expense processing

3. **Data Layer** (`data/`)
   - Database operations
   - Data validation
   - Model definitions

4. **Utility Layer** (`utils/`)
   - Database migrations
   - Input validation
   - Helper functions

### Database

- **Type**: SQLite
- **Location**: `expense_dss.db`
- **Tables**: 
  - `categories` - Category definitions and budgets
  - `expenses` - Recorded expenses

### Security

All database operations use **parameterized queries** to prevent SQL injection. See [SECURITY.md](SECURITY.md) for details.

---

## ⚙️ Settings & Customization

### Application Settings
Go to **Settings** in the sidebar:

- **Theme** - Light/Dark mode (if available)
- **Display Format** - Customize how data is shown
- **Default Category** - Choose default for new expenses
- **Budget Notifications** - Alert settings

For detailed settings, see [CONFIGURATION.md](CONFIGURATION.md).

---

## 📈 Analytics Dashboard

**Main Dashboard shows:**

1. **Summary Cards**
   - Total spending (current month)
   - Average daily spending
   - Categories tracked
   - Budget status (X of Y categories on budget)

2. **Visualizations**
   - Pie chart: Spending by category
   - Bar chart: Category budgets vs actual
   - Line chart: Spending over time

3. **Recent Activity**
   - Last 5 expenses added
   - Quick access to add new expense

4. **Insights**
   - Top recommendations
   - Alert notifications

---

## 🔗 See Also

- **[QUICK_START.md](QUICK_START.md)** - Getting started
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical details
- **[CONFIGURATION.md](CONFIGURATION.md)** - Settings options
- **[SECURITY.md](SECURITY.md)** - Security information
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All documentation

---

**For technical implementation details, see [ARCHITECTURE.md](ARCHITECTURE.md)**
