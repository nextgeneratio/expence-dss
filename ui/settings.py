"""
Settings UI
Provides configuration and customization options for the application.
"""

import streamlit as st
from ui.layout import display_header, display_alert
from services import category_service
import config


def show_settings():
    """Display the Settings page."""
    display_header("⚙️ Settings", "Customize your expense tracking experience")

    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Currency & Display",
            "Budget Thresholds",
            "Categories",
            "Alerts",
            "⚠️ Anomaly Detection",
        ]
    )

    # ==================== TAB 1: Currency & Display ====================
    with tab1:
        st.subheader("Currency & Display Settings")

        col1, col2 = st.columns(2)

        with col1:
            currency_symbol = st.text_input(
                "Currency Symbol",
                value=st.session_state.get("currency_symbol", config.CURRENCY_SYMBOL),
                max_chars=5,
                help="Enter the symbol to use for displaying amounts (e.g., $, €, £, ₹)",
            )

            if currency_symbol != st.session_state.get(
                "currency_symbol", config.CURRENCY_SYMBOL
            ):
                st.session_state.currency_symbol = currency_symbol
                st.success(f"✅ Currency symbol updated to: {currency_symbol}")

        with col2:
            date_format = st.selectbox(
                "Date Format",
                options=["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"],
                index=0,
                help="Select your preferred date format",
            )
            st.session_state.date_format = date_format

        st.markdown("---")

        # Forecast settings
        st.subheader("Forecasting Settings")

        col1, col2 = st.columns(2)

        with col1:
            forecast_days = st.slider(
                "Forecast Days",
                min_value=7,
                max_value=90,
                value=st.session_state.get("forecast_days", config.FORECAST_DAYS),
                step=1,
                help="Number of days to forecast spending",
            )
            st.session_state.forecast_days = forecast_days

        with col2:
            min_data_points = st.slider(
                "Minimum Data Points for Prediction",
                min_value=5,
                max_value=30,
                value=st.session_state.get("min_data_points", config.MIN_DATA_POINTS),
                step=1,
                help="Minimum number of expenses needed for accurate predictions",
            )
            st.session_state.min_data_points = min_data_points

    # ==================== TAB 2: Budget Thresholds ====================
    with tab2:
        st.subheader("Monthly Budget Thresholds by Category")
        st.info(
            "💡 For detailed category management, visit the **Category Management** page"
        )

        # Get all active categories from database
        categories = category_service.get_all_categories(include_inactive=False)

        if not categories:
            st.warning("⚠️ No active categories found. Please add categories first.")
        else:
            # Initialize session state for budgets if not exists
            if "custom_budgets" not in st.session_state:
                st.session_state.custom_budgets = category_service.get_all_budgets()

            col1, col2 = st.columns(2)

            # Display budget inputs in two columns
            for idx, category in enumerate(categories):
                col = col1 if idx % 2 == 0 else col2

                with col:
                    budget_value = st.number_input(
                        f"{category['name']}",
                        min_value=0.0,
                        value=float(
                            st.session_state.custom_budgets.get(
                                category["name"], category["budget"]
                            )
                        ),
                        step=10.0,
                        format="%.2f",
                        help=f"Set monthly budget for {category['name']}",
                        key=f"budget_input_{category['name']}",
                    )
                    st.session_state.custom_budgets[category["name"]] = budget_value

            # Display summary
            st.markdown("---")
            total_budget = sum(st.session_state.custom_budgets.values())
            currency = st.session_state.get("currency_symbol", config.CURRENCY_SYMBOL)
            st.info(f"📊 Total Monthly Budget: {currency}{total_budget:,.2f}")

            if st.button("💾 Save Budget Changes", key="save_budgets"):
                # Update all budgets in database
                for (
                    category_name,
                    budget_value,
                ) in st.session_state.custom_budgets.items():
                    category_service.update_category(category_name, budget=budget_value)
                st.success("✅ Budget thresholds saved!")

    # ==================== TAB 3: Categories ====================
    with tab4:
        st.subheader("Category Configuration")
        st.info(
            "📂 Full category management is available in the **Category Management** page"
        )

        # Display quick stats
        col1, col2, col3 = st.columns(3)

        all_cats = category_service.get_all_categories(include_inactive=True)
        custom_cats = category_service.get_custom_categories()
        default_cats = category_service.get_default_categories()

        with col1:
            st.metric("Total Categories", len(all_cats))

        with col2:
            st.metric("Custom Categories", len(custom_cats))

        with col3:
            st.metric("Default Categories", len(default_cats))

        st.markdown("---")

        # Quick add category
        st.subheader("Quick Add Category")

        col1, col2 = st.columns([2, 1])

        with col1:
            quick_cat_name = st.text_input(
                "Category Name",
                placeholder="e.g., Subscriptions",
                key="quick_add_category",
            )

        with col2:
            quick_cat_budget = st.number_input(
                "Budget",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="quick_add_budget",
            )

        if st.button("➕ Add", key="quick_add_btn"):
            if not quick_cat_name:
                st.error("❌ Please enter a category name")
            else:
                try:
                    category_service.add_category(quick_cat_name, quick_cat_budget)
                    st.success(f"✅ Category '{quick_cat_name}' created!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {str(e)}")

    # ==================== TAB 4: Alerts ====================
    with tab4:
        st.subheader("Alert & Notification Settings")

        col1, col2 = st.columns(2)

        with col1:
            warning_threshold = st.slider(
                "Warning Threshold (%)",
                min_value=50,
                max_value=90,
                value=int(
                    st.session_state.get("warning_threshold", config.WARNING_THRESHOLD)
                    * 100
                ),
                step=5,
                help="Alert when spending reaches this % of budget",
            )
            st.session_state.warning_threshold = warning_threshold / 100

        with col2:
            critical_threshold = st.slider(
                "Critical Threshold (%)",
                min_value=75,
                max_value=100,
                value=int(
                    st.session_state.get(
                        "critical_threshold", config.CRITICAL_THRESHOLD
                    )
                    * 100
                ),
                step=5,
                help="Critical alert when spending reaches this % of budget",
            )
            st.session_state.critical_threshold = critical_threshold / 100

        st.markdown("---")

        # High spending threshold
        high_spending = st.slider(
            "High Spending Threshold (% above budget)",
            min_value=10,
            max_value=50,
            value=int(
                (
                    st.session_state.get(
                        "high_spending_threshold", config.HIGH_SPENDING_THRESHOLD
                    )
                    - 1
                )
                * 100
            ),
            step=5,
            help="Identify high spending if exceeding budget by this %",
        )
        st.session_state.high_spending_threshold = 1 + (high_spending / 100)

        st.markdown("---")

        # Pattern detection settings
        st.subheader("Pattern Detection Settings")

        col1, col2 = st.columns(2)

        with col1:
            frequent_expense_days = st.slider(
                "Frequent Expense Detection Days",
                min_value=3,
                max_value=30,
                value=st.session_state.get(
                    "frequent_expense_days", config.FREQUENT_EXPENSE_DAYS
                ),
                step=1,
                help="Look for frequent expenses within this many days",
            )
            st.session_state.frequent_expense_days = frequent_expense_days

        with col2:
            frequent_expense_count = st.slider(
                "Frequent Expense Count Threshold",
                min_value=2,
                max_value=10,
                value=st.session_state.get(
                    "frequent_expense_count", config.FREQUENT_EXPENSE_COUNT
                ),
                step=1,
                help="Consider expenses as frequent if count exceeds this",
            )
            st.session_state.frequent_expense_count = frequent_expense_count

        if st.button("💾 Save Alert Settings", key="save_alerts"):
            st.success("✅ Alert settings saved!")

    # ==================== TAB 5: Anomaly Detection ====================
    with tab5:
        st.subheader("Anomaly Detection Thresholds")

        st.markdown(
            "Configure sensitivity levels for different types of spending anomalies. "
            "Lower values = more sensitive detection, Higher values = fewer alerts."
        )

        st.markdown("---")

        # Initialize session state for anomaly thresholds if not exists
        if "anomaly_overspending_threshold" not in st.session_state:
            st.session_state.anomaly_overspending_threshold = config.ANOMALY_DETECTION[
                "overspending_threshold"
            ]
        if "anomaly_spike_threshold" not in st.session_state:
            st.session_state.anomaly_spike_threshold = config.ANOMALY_DETECTION[
                "spike_threshold"
            ]
        if "anomaly_budget_risk_threshold" not in st.session_state:
            st.session_state.anomaly_budget_risk_threshold = config.ANOMALY_DETECTION[
                "budget_risk_threshold"
            ]
        if "anomaly_fixed_cost_threshold" not in st.session_state:
            st.session_state.anomaly_fixed_cost_threshold = config.ANOMALY_DETECTION[
                "fixed_cost_threshold"
            ]
        if "anomaly_rising_trend_threshold" not in st.session_state:
            st.session_state.anomaly_rising_trend_threshold = config.ANOMALY_DETECTION[
                "rising_trend_threshold"
            ]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Overspending Detection")
            overspending = st.slider(
                "Overspending Threshold",
                min_value=1.0,
                max_value=2.0,
                value=st.session_state.anomaly_overspending_threshold,
                step=0.05,
                help="Alert when spending exceeds budget by this factor (e.g., 1.1 = 10% over budget)",
                key="slider_overspending",
            )
            st.session_state.anomaly_overspending_threshold = overspending
            st.caption(
                f"Currently: {(overspending - 1) * 100:.0f}% over budget triggers alert"
            )

            st.markdown("### Spending Spike Detection")
            spike = st.slider(
                "Spike Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.anomaly_spike_threshold,
                step=0.05,
                help="Alert when month-over-month spending increase exceeds this ratio (e.g., 0.3 = 30% increase)",
                key="slider_spike",
            )
            st.session_state.anomaly_spike_threshold = spike
            st.caption(f"Currently: {spike * 100:.0f}% increase triggers alert")

            st.markdown("### Budget Risk Detection")
            budget_risk = st.slider(
                "Budget Risk Threshold",
                min_value=0.5,
                max_value=1.0,
                value=st.session_state.anomaly_budget_risk_threshold,
                step=0.05,
                help="Alert when spending reaches this % of budget (e.g., 0.75 = 75% of budget)",
                key="slider_budget_risk",
            )
            st.session_state.anomaly_budget_risk_threshold = budget_risk
            st.caption(
                f"Currently: {budget_risk * 100:.0f}% of budget triggers warning"
            )

        with col2:
            st.markdown("### Fixed Cost Danger Detection")
            fixed_cost = st.slider(
                "Fixed Cost Threshold",
                min_value=0.2,
                max_value=0.8,
                value=st.session_state.anomaly_fixed_cost_threshold,
                step=0.05,
                help="Alert when fixed costs exceed this % of total spending (e.g., 0.5 = 50%)",
                key="slider_fixed_cost",
            )
            st.session_state.anomaly_fixed_cost_threshold = fixed_cost
            st.caption(
                f"Currently: {fixed_cost * 100:.0f}% of total spending triggers alert"
            )

            st.markdown("### Rising Trend Detection")
            rising_trend = st.slider(
                "Rising Trend Threshold",
                min_value=0.0,
                max_value=0.5,
                value=st.session_state.anomaly_rising_trend_threshold,
                step=0.05,
                help="Alert when spending or category increase over 3 months exceeds this ratio (e.g., 0.15 = 15%)",
                key="slider_rising_trend",
            )
            st.session_state.anomaly_rising_trend_threshold = rising_trend
            st.caption(
                f"Currently: {rising_trend * 100:.0f}% increase triggers warning"
            )

        st.markdown("---")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Anomaly Settings", key="save_anomaly_settings"):
                st.success("✅ Anomaly detection thresholds saved!")

        with col2:
            if st.button("🔄 Reset to Defaults", key="reset_anomaly_settings"):
                st.session_state.anomaly_overspending_threshold = (
                    config.ANOMALY_DETECTION["overspending_threshold"]
                )
                st.session_state.anomaly_spike_threshold = config.ANOMALY_DETECTION[
                    "spike_threshold"
                ]
                st.session_state.anomaly_budget_risk_threshold = (
                    config.ANOMALY_DETECTION["budget_risk_threshold"]
                )
                st.session_state.anomaly_fixed_cost_threshold = (
                    config.ANOMALY_DETECTION["fixed_cost_threshold"]
                )
                st.session_state.anomaly_rising_trend_threshold = (
                    config.ANOMALY_DETECTION["rising_trend_threshold"]
                )
                st.success("✅ Reset to default anomaly thresholds!")
                st.rerun()

        with col3:
            st.info(
                "💡 Increase thresholds to be less sensitive, decrease for more alerts"
            )

    # ==================== Export/Import ====================
    st.markdown("---")
    st.subheader("Export & Import Configuration")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Export Settings as JSON"):
            import json

            settings_data = {
                "currency_symbol": st.session_state.get(
                    "currency_symbol", config.CURRENCY_SYMBOL
                ),
                "date_format": st.session_state.get("date_format", config.DATE_FORMAT),
                "forecast_days": st.session_state.get(
                    "forecast_days", config.FORECAST_DAYS
                ),
                "min_data_points": st.session_state.get(
                    "min_data_points", config.MIN_DATA_POINTS
                ),
                "custom_budgets": st.session_state.get(
                    "custom_budgets", config.BUDGET_THRESHOLDS
                ),
                "warning_threshold": st.session_state.get(
                    "warning_threshold", config.WARNING_THRESHOLD
                ),
                "critical_threshold": st.session_state.get(
                    "critical_threshold", config.CRITICAL_THRESHOLD
                ),
                "high_spending_threshold": st.session_state.get(
                    "high_spending_threshold", config.HIGH_SPENDING_THRESHOLD
                ),
                "frequent_expense_days": st.session_state.get(
                    "frequent_expense_days", config.FREQUENT_EXPENSE_DAYS
                ),
                "frequent_expense_count": st.session_state.get(
                    "frequent_expense_count", config.FREQUENT_EXPENSE_COUNT
                ),
            }

            st.download_button(
                label="Download Settings",
                data=json.dumps(settings_data, indent=2),
                file_name="expense_dss_settings.json",
                mime="application/json",
            )

    with col2:
        st.info("💡 Tip: Save your settings as JSON and share them with other users!")

    # ==================== Current Settings Summary ====================
    with st.expander("📋 View Current Settings Summary"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Display Settings**")
            st.write(
                f"- Currency Symbol: {st.session_state.get('currency_symbol', config.CURRENCY_SYMBOL)}"
            )
            st.write(
                f"- Date Format: {st.session_state.get('date_format', config.DATE_FORMAT)}"
            )
            st.write(
                f"- Forecast Days: {st.session_state.get('forecast_days', config.FORECAST_DAYS)}"
            )
            st.write(
                f"- Min Data Points: {st.session_state.get('min_data_points', config.MIN_DATA_POINTS)}"
            )

        with col2:
            st.write("**Alert Thresholds**")
            st.write(
                f"- Warning: {int(st.session_state.get('warning_threshold', config.WARNING_THRESHOLD) * 100)}%"
            )
            st.write(
                f"- Critical: {int(st.session_state.get('critical_threshold', config.CRITICAL_THRESHOLD) * 100)}%"
            )
            st.write(
                f"- High Spending: +{int((st.session_state.get('high_spending_threshold', config.HIGH_SPENDING_THRESHOLD) - 1) * 100)}%"
            )
            st.write(
                f"- Frequent Days: {st.session_state.get('frequent_expense_days', config.FREQUENT_EXPENSE_DAYS)}"
            )


def get_config_from_session():
    """
    Get configuration from session state or use defaults.

    Returns:
        dict: Configuration dictionary with user settings
    """
    return {
        "currency_symbol": st.session_state.get(
            "currency_symbol", config.CURRENCY_SYMBOL
        ),
        "date_format": st.session_state.get("date_format", config.DATE_FORMAT),
        "forecast_days": st.session_state.get("forecast_days", config.FORECAST_DAYS),
        "min_data_points": st.session_state.get(
            "min_data_points", config.MIN_DATA_POINTS
        ),
        "custom_budgets": st.session_state.get(
            "custom_budgets", config.BUDGET_THRESHOLDS
        ),
        "warning_threshold": st.session_state.get(
            "warning_threshold", config.WARNING_THRESHOLD
        ),
        "critical_threshold": st.session_state.get(
            "critical_threshold", config.CRITICAL_THRESHOLD
        ),
        "high_spending_threshold": st.session_state.get(
            "high_spending_threshold", config.HIGH_SPENDING_THRESHOLD
        ),
        "frequent_expense_days": st.session_state.get(
            "frequent_expense_days", config.FREQUENT_EXPENSE_DAYS
        ),
        "frequent_expense_count": st.session_state.get(
            "frequent_expense_count", config.FREQUENT_EXPENSE_COUNT
        ),
    }
