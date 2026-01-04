# Expense DSS (Decision Support System)

A comprehensive expense tracking and decision support system built with Python and Streamlit. This application helps users track expenses, analyze spending patterns, and receive intelligent recommendations for better financial management.

## Features

### 📊 Core Functionality
- **Expense Tracking**: Add, view, and manage daily expenses with detailed categorization
- **Transaction Processing System (TPS)**: Complete CRUD operations for expense management
- **Budget Management**: Set and monitor category-wise monthly budgets

### 📈 Analytics & Insights
- **Descriptive Analytics**: Statistical analysis of spending patterns
  - Mean, median, standard deviation calculations
  - Category-wise spending breakdown
  - Daily, weekly, and monthly trends
  
- **Predictive Analytics**: AI-powered spending forecasts
  - End-of-month projections
  - Category-wise predictions
  - Confidence levels for predictions

### 🎯 Decision Support
- **Smart Recommendations**: Intelligent spending suggestions based on:
  - Budget utilization alerts (warning, critical, exceeded)
  - High spending detection
  - Unusual pattern identification
  - Optimization opportunities
  
- **Savings Opportunities**: Identify areas where you can save money
- **Budget Status Tracking**: Real-time monitoring of budget health

### 📊 Visualizations
- Interactive pie charts for category distribution
- Line charts for spending trends
- Bar charts for budget utilization
- Comprehensive dashboards with multiple views

## Project Structure

```
expense_dss/
│
├── app.py                  # Entry point (UI launcher)
├── config.py               # App config, thresholds, constants
│
├── data/
│   ├── database.py         # DB connection & setup
│   └── models.py           # Expense data model
│
├── services/
│   ├── expense_service.py  # CRUD + totals (TPS logic)
│   ├── analytics_service.py# Descriptive & predictive analytics
│   └── decision_service.py # DSS rules & recommendations
│
├── ui/
│   ├── layout.py           # UI layout components
│   ├── views.py            # Screens (add, summary, insights)
│   └── charts.py           # Visualizations
│
├── utils/
│   ├── validators.py       # Data validation
│   └── helpers.py          # Date, formatting helpers
│
├── requirements.txt
└── README.md
```

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

### Adding Expenses
1. Navigate to **Add Expense** page
2. Select date, category, and enter amount
3. Optionally add a description
4. Click "Add Expense"

### Viewing Summary
1. Navigate to **Summary** page
2. Choose time period (Current Month, Last 30 Days, etc.)
3. View spending metrics, charts, and detailed breakdowns

### Getting Insights
1. Navigate to **Insights & Recommendations** page
2. Review alerts and warnings
3. Check spending predictions
4. Explore savings opportunities
5. Analyze spending patterns

## Configuration

Edit `config.py` to customize:

- **Budget Thresholds**: Set monthly budgets for each category
- **Alert Thresholds**: Configure warning and critical alert levels (default: 80% and 95%)
- **Categories**: Add or modify expense categories
- **Prediction Settings**: Adjust forecast parameters
- **UI Settings**: Customize date formats, currency symbols, and chart colors

### Default Budget Thresholds (Monthly)
- Food & Dining: $500
- Transportation: $300
- Shopping: $400
- Entertainment: $200
- Bills & Utilities: $350
- Healthcare: $250
- Education: $300
- Travel: $500
- Personal Care: $150
- Other: $200

## Technology Stack

- **Frontend**: Streamlit
- **Visualizations**: Plotly
- **Data Processing**: Pandas
- **Database**: SQLite
- **Language**: Python 3.8+

## Key Components

### Data Layer
- **database.py**: SQLite database management with connection pooling
- **models.py**: Expense data model with ORM-like functionality

### Services Layer
- **expense_service.py**: CRUD operations and aggregation queries
- **analytics_service.py**: Statistical analysis and predictive modeling
- **decision_service.py**: Rule-based recommendation engine

### UI Layer
- **layout.py**: Reusable UI components and styling
- **views.py**: Main application screens
- **charts.py**: Interactive Plotly visualizations

### Utilities
- **validators.py**: Input validation and sanitization
- **helpers.py**: Date formatting, currency conversion, and utility functions

## Decision Support Rules

The DSS engine applies the following rules:

1. **Budget Alerts**:
   - Warning: 80-95% of budget used
   - Critical: 95-100% of budget used
   - Exceeded: Over 100% of budget

2. **High Spending Detection**:
   - Identifies categories with 20%+ increase from previous month

3. **Pattern Analysis**:
   - Detects frequent small expenses
   - Identifies day-of-week spending patterns
   - Highlights most expensive categories

4. **Predictive Recommendations**:
   - Projects month-end spending
   - Suggests daily spending adjustments
   - Provides confidence levels for predictions

## Database Schema

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Export data to CSV/PDF
- [ ] Recurring expense templates
- [ ] Mobile responsive design
- [ ] Integration with banking APIs
- [ ] Machine learning for advanced predictions
- [ ] Custom category creation
- [ ] Multi-currency support
- [ ] Goal setting and tracking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For questions or issues, please open an issue in the repository.

---

**Made with ❤️ using Python and Streamlit**
