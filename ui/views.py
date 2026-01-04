"""
UI Views - Screens for different app sections
Implements the main UI screens: Add Expense, Summary, and Insights.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from ui.layout import (
    display_header,
    display_metric_card,
    display_alert,
    display_empty_state,
)
from ui.charts import (
    create_category_pie_chart,
    create_spending_trend_chart,
    create_budget_utilization_chart,
    create_category_comparison_chart,
)
from services import (
    expense_service,
    analytics_service,
    decision_service,
    category_service,
)
from utils.validators import validate_amount, validate_date
from utils.helpers import format_currency, get_current_month_range
import config


def show_add_expense():
    """Display the Add Expense screen."""
    display_header("Add New Expense", "Track your daily expenses")

    # Get active categories from database
    category_names = category_service.get_category_names(include_inactive=False)

    if not category_names:
        st.error("❌ No active categories found. Please add categories first.")
        st.info("📂 Go to Category Management to add categories.")
        return

    with st.form("expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input(
                "Date",
                value=datetime.now(),
                max_value=datetime.now(),
                help="Select the date of the expense",
            )

            category = st.selectbox(
                "Category",
                options=category_names,
                help="Select expense category",
            )

            expense_type = st.selectbox(
                "Type",
                options=config.EXPENSE_TYPES,
                help="Select whether this is a fixed or variable expense",
            )

        with col2:
            amount = st.number_input(
                "Amount ($)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                help="Enter the expense amount",
            )

            # Show budget info for selected category
            budget = category_service.get_category_budget(category)
            st.info(f"Monthly budget for {category}: {format_currency(budget)}")

        description = st.text_area(
            "Description (Optional)", help="Add any additional notes about this expense"
        )

        submitted = st.form_submit_button("Add Expense", type="primary")

        if submitted:
            # Validate inputs
            date_str = date.strftime(config.DATE_FORMAT)

            valid, error = validate_amount(amount)
            if not valid:
                st.error(error)
            else:
                valid, error = validate_date(date_str)
                if not valid:
                    st.error(error)
                else:
                    try:
                        expense_id = expense_service.add_expense(
                            amount=amount,
                            date=date_str,
                            category=category,
                            type=expense_type,
                            description=description or None,
                        )
                        st.success(f"✅ Expense added successfully! (ID: {expense_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error adding expense: {str(e)}")

    # Show recent expenses
    st.markdown("### Recent Expenses")
    recent_expenses = expense_service.get_all_expenses()[:10]

    if recent_expenses:
        df = pd.DataFrame(
            [
                {
                    "Date": exp.date,
                    "Category": exp.category,
                    "Type": exp.type.capitalize(),
                    "Amount": format_currency(exp.amount),
                    "Description": exp.description or "-",
                }
                for exp in recent_expenses
            ]
        )
        st.dataframe(df, use_container_width=True)
    else:
        display_empty_state("No expenses recorded yet. Add your first expense above!")


def show_summary():
    """Display the Summary screen."""
    display_header("Expense Summary", "Overview of your spending")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        view_type = st.selectbox(
            "View",
            [
                "Current Month",
                "Last 30 Days",
                "Last 90 Days",
                "All Time",
                "Custom Range",
            ],
        )

    # Determine date range based on selection
    if view_type == "Current Month":
        start_date, end_date = get_current_month_range()
    elif view_type == "Last 30 Days":
        end_date = datetime.now().strftime(config.DATE_FORMAT)
        start_date = (datetime.now() - timedelta(days=30)).strftime(config.DATE_FORMAT)
    elif view_type == "Last 90 Days":
        end_date = datetime.now().strftime(config.DATE_FORMAT)
        start_date = (datetime.now() - timedelta(days=90)).strftime(config.DATE_FORMAT)
    elif view_type == "Custom Range":
        with col2:
            date_range = st.date_input("Select Date Range", value=[])
            if len(date_range) == 2:
                start_date = date_range[0].strftime(config.DATE_FORMAT)
                end_date = date_range[1].strftime(config.DATE_FORMAT)
            else:
                st.warning("Please select both start and end dates")
                return
    else:  # All Time
        start_date = None
        end_date = None

    # Get data
    if start_date and end_date:
        expenses = expense_service.get_expenses_by_date_range(start_date, end_date)
        total_spending = expense_service.get_total_spending(start_date, end_date)
        category_totals = expense_service.get_total_by_category(start_date, end_date)
    else:
        expenses = expense_service.get_all_expenses()
        total_spending = expense_service.get_total_spending()
        category_totals = expense_service.get_total_by_category()

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_metric_card("Total Spending", format_currency(total_spending))

    with col2:
        display_metric_card("Total Transactions", str(len(expenses)))

    with col3:
        avg_expense = total_spending / len(expenses) if expenses else 0
        display_metric_card("Average Expense", format_currency(avg_expense))

    with col4:
        display_metric_card("Categories", str(len(category_totals)))

    st.markdown("---")

    # Charts
    if expenses:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Spending by Category")
            fig = create_category_pie_chart(category_totals)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Budget Utilization")
            utilization = analytics_service.get_budget_utilization()
            fig = create_budget_utilization_chart(utilization)
            st.plotly_chart(fig, use_container_width=True)

        # Spending trend
        st.subheader("Spending Trend")
        trends = analytics_service.get_spending_trends(30)
        fig = create_spending_trend_chart(trends["daily_totals"])
        st.plotly_chart(fig, use_container_width=True)

        # Detailed breakdown
        st.subheader("Category Breakdown")
        custom_budgets = st.session_state.get(
            "custom_budgets", config.BUDGET_THRESHOLDS
        )
        category_df = pd.DataFrame(
            [
                {
                    "Category": cat,
                    "Total": format_currency(total),
                    "Budget": format_currency(custom_budgets.get(cat, 0)),
                    "Transactions": len([e for e in expenses if e.category == cat]),
                }
                for cat, total in sorted(
                    category_totals.items(), key=lambda x: x[1], reverse=True
                )
            ]
        )
        st.dataframe(category_df, use_container_width=True)
    else:
        display_empty_state("No expenses found for the selected period")


def show_insights():
    """Display the Insights & Recommendations screen."""
    display_header("Insights & Recommendations", "AI-powered spending analysis")

    # Get decision support data
    dss_summary = decision_service.get_decision_summary()
    recommendations = dss_summary["recommendations"]
    savings = dss_summary["savings_opportunities"]

    # Display recommendations
    st.subheader("📋 Recommendations")

    if recommendations:
        # Group by severity
        critical = [r for r in recommendations if r.get("severity") == "critical"]
        warnings = [r for r in recommendations if r.get("severity") == "warning"]
        info = [r for r in recommendations if r.get("severity") == "info"]

        if critical:
            st.markdown("#### 🚨 Critical Alerts")
            for rec in critical:
                with st.expander(f"⚠️ {rec['title']}", expanded=True):
                    st.error(rec["message"])
                    st.info(f"**Action:** {rec['action']}")

        if warnings:
            st.markdown("#### ⚠️ Warnings")
            for rec in warnings:
                with st.expander(f"⚠️ {rec['title']}"):
                    st.warning(rec["message"])
                    st.info(f"**Action:** {rec['action']}")

        if info:
            st.markdown("#### ℹ️ Insights")
            for rec in info:
                with st.expander(f"💡 {rec['title']}"):
                    st.info(rec["message"])
                    if rec.get("action"):
                        st.info(f"**Suggestion:** {rec['action']}")
    else:
        st.success("✅ Great job! No concerning patterns detected.")

    st.markdown("---")

    # Savings opportunities
    st.subheader("💰 Savings Opportunities")

    if savings:
        for opp in savings:
            with st.expander(f"✨ {opp['title']}"):
                st.success(opp["message"])
                st.info(f"**Tip:** {opp['action']}")
    else:
        st.info("No savings opportunities identified at this time.")

    st.markdown("---")

    # Predictive analytics
    st.subheader("🔮 Spending Predictions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Overall Projection")
        overall_prediction = analytics_service.predict_monthly_spending()

        if overall_prediction["confidence"] != "low":
            st.metric(
                "Projected Month-End Total",
                format_currency(overall_prediction["projected_total"]),
                delta=format_currency(
                    overall_prediction["projected_total"]
                    - overall_prediction["current_total"]
                ),
            )
            st.caption(f"Confidence: {overall_prediction['confidence'].title()}")
            st.progress(
                min(
                    overall_prediction["current_total"]
                    / overall_prediction["projected_total"],
                    1.0,
                )
            )
        else:
            st.info(overall_prediction["message"])

    with col2:
        st.markdown("#### Category Predictions")
        selected_category = st.selectbox("Select Category", config.EXPENSE_CATEGORIES)

        cat_prediction = analytics_service.predict_monthly_spending(selected_category)

        if cat_prediction["confidence"] != "low":
            custom_budgets = st.session_state.get(
                "custom_budgets", config.BUDGET_THRESHOLDS
            )
            budget = custom_budgets.get(selected_category, 0)
            st.metric(
                f"Projected {selected_category}",
                format_currency(cat_prediction["projected_total"]),
                delta=format_currency(cat_prediction["projected_total"] - budget),
                delta_color="inverse",
            )
            st.caption(f"Confidence: {cat_prediction['confidence'].title()}")
            st.progress(
                min(cat_prediction["current_total"] / budget, 1.0) if budget > 0 else 0
            )
        else:
            st.info(cat_prediction["message"])

    st.markdown("---")

    # Spending patterns
    st.subheader("📊 Spending Patterns")
    patterns = analytics_service.get_spending_patterns()

    if patterns.get("weekday_averages"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Average Spending by Day")
            day_df = pd.DataFrame(
                [
                    {"Day": day, "Average": format_currency(avg)}
                    for day, avg in patterns["weekday_averages"].items()
                ]
            )
            st.dataframe(day_df, use_container_width=True)

        with col2:
            st.markdown("#### Quick Facts")
            if patterns.get("most_expensive_day"):
                day, amount = patterns["most_expensive_day"]
                st.info(
                    f"💸 Most expensive day: **{day}** ({format_currency(amount)} avg)"
                )

            if patterns.get("most_frequent_category"):
                st.info(
                    f"🔄 Most frequent category: **{patterns['most_frequent_category']}**"
                )
