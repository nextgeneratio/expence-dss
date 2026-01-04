"""
Historical Analysis View
Display historical analysis, trends, and comparisons with visualizations.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from ui.layout import display_header, display_metric_card
from ui.charts_history import (
    create_monthly_totals_chart,
    create_category_monthly_chart,
    create_category_comparison_chart,
    create_month_over_month_chart,
    create_category_month_comparison_chart,
    create_yearly_comparison_chart,
    create_spending_trend_chart,
    create_seasonal_chart,
    create_expense_type_chart,
    create_multi_metric_chart,
    create_category_heatmap,
    create_waterfall_comparison,
)
from services import history_service
from utils.helpers import format_currency


def show_history():
    """Display the Historical Analysis page."""
    display_header(
        "📊 Historical Analysis", "Track trends and compare spending patterns"
    )

    # Create tabs for different analyses
    (
        tab1,
        tab2,
        tab3,
        tab4,
        tab5,
        tab6,
    ) = st.tabs(
        [
            "Monthly Overview",
            "Category Analysis",
            "Month-over-Month",
            "Yearly Comparison",
            "Trends & Velocity",
            "Detailed Breakdown",
        ]
    )

    # ==================== TAB 1: Monthly Overview ====================
    with tab1:
        st.subheader("📈 Monthly Spending Overview")

        # Get data
        monthly_totals = history_service.get_monthly_totals()
        seasonal_data = history_service.get_seasonal_analysis()

        if monthly_totals:
            col1, col2 = st.columns([3, 1])

            with col1:
                # Monthly totals chart
                fig = create_monthly_totals_chart(monthly_totals)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Stats
                st.metric(
                    "Total All Time",
                    format_currency(sum(monthly_totals.values())),
                )
                st.metric(
                    "Average Monthly",
                    format_currency(
                        sum(monthly_totals.values()) / len(monthly_totals)
                        if monthly_totals
                        else 0
                    ),
                )
                st.metric(
                    "Highest Month",
                    format_currency(
                        max(monthly_totals.values()) if monthly_totals else 0
                    ),
                )
                st.metric(
                    "Lowest Month",
                    format_currency(
                        min(monthly_totals.values()) if monthly_totals else 0
                    ),
                )

            # Seasonal analysis
            st.markdown("---")
            st.subheader("🌍 Seasonal Pattern Analysis")

            col1, col2 = st.columns([2, 1])

            with col1:
                fig = create_seasonal_chart(seasonal_data)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.info("**Seasonal Spending**")
                for quarter, total in sorted(seasonal_data.items()):
                    st.write(f"{quarter}: {format_currency(total)}")

            # Monthly data table
            st.markdown("---")
            st.subheader("📋 Monthly Data Table")

            df = pd.DataFrame(
                [
                    {
                        "Month": month,
                        "Total": format_currency(total),
                        "Amount": total,  # For sorting
                    }
                    for month, total in sorted(monthly_totals.items())
                ]
            )

            # Add running total
            amounts = [row["Amount"] for row in df.to_dict("records")]
            running_total = 0
            running_totals = []
            for amt in amounts:
                running_total += amt
                running_totals.append(running_total)

            df["Running Total"] = [format_currency(rt) for rt in running_totals]
            df = df.drop("Amount", axis=1)

            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No expense data available yet.")

    # ==================== TAB 2: Category Analysis ====================
    with tab2:
        st.subheader("🏷️ Category Analysis")

        col1, col2 = st.columns([2, 1])

        # Get data
        category_totals = history_service.get_category_totals()
        category_monthly = history_service.get_category_monthly_totals()

        with col1:
            # Category comparison chart
            if category_totals:
                fig = create_category_comparison_chart(category_totals)
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Category stats
            st.metric("Total Categories", len(category_totals))
            st.metric(
                "Top Category",
                (
                    max(category_totals, key=category_totals.get)
                    if category_totals
                    else "N/A"
                ),
            )
            if category_totals:
                st.metric(
                    "Top Category Amount",
                    format_currency(max(category_totals.values())),
                )

        # Category trend over time
        st.markdown("---")
        st.subheader("📉 Category Trends Over Time")

        if category_monthly:
            fig = create_category_heatmap(category_monthly)
            st.plotly_chart(fig, use_container_width=True)

            # Category breakdown table
            st.markdown("---")
            st.subheader("📊 Category Breakdown")

            df = pd.DataFrame(
                [
                    {
                        "Category": cat,
                        "Total": format_currency(total),
                        "Avg/Month": format_currency(
                            total / len(category_monthly.get(cat, {}))
                            if category_monthly.get(cat)
                            else 0
                        ),
                        "Months": len(category_monthly.get(cat, {})),
                    }
                    for cat, total in sorted(
                        category_totals.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )

            st.dataframe(df, use_container_width=True, hide_index=True)

    # ==================== TAB 3: Month-over-Month ====================
    with tab3:
        st.subheader("📊 Month-over-Month Analysis")

        # Month selector
        today = datetime.now()
        month_options = []
        for i in range(12):
            date = today - timedelta(days=30 * i)
            month_options.append(date.strftime("%Y-%m"))

        col1, col2 = st.columns(2)

        with col1:
            selected_month = st.selectbox("Select Month", month_options, index=0)

        # Get comparison data
        comparison = history_service.get_monthly_comparison(selected_month)

        # Display metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                comparison["current_month"],
                format_currency(comparison["current_total"]),
            )

        with col2:
            st.metric(
                comparison["previous_month"],
                format_currency(comparison["previous_total"]),
            )

        with col3:
            change = comparison["change"]
            delta_color = "inverse" if change > 0 else "normal"
            st.metric(
                "Change",
                format_currency(abs(change)),
                delta=f"{comparison['change_percent']:.1f}%",
                delta_color=delta_color,
            )

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            fig = create_month_over_month_chart(comparison)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = create_waterfall_comparison(comparison)
            st.plotly_chart(fig, use_container_width=True)

        # Category comparison
        st.markdown("---")
        st.subheader("🏷️ Category Changes")

        fig = create_category_month_comparison_chart(comparison)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed category comparison table
        st.markdown("---")

        cat_comp = comparison["category_comparison"]
        df = pd.DataFrame(
            [
                {
                    "Category": cat,
                    "Previous": format_currency(data["previous"]),
                    "Current": format_currency(data["current"]),
                    "Change": format_currency(data["change"]),
                    "Change %": f"{data['change_percent']:+.1f}%",
                }
                for cat, data in sorted(
                    cat_comp.items(),
                    key=lambda x: abs(x[1]["change"]),
                    reverse=True,
                )
            ]
        )

        st.dataframe(df, use_container_width=True, hide_index=True)

    # ==================== TAB 4: Yearly Comparison ====================
    with tab4:
        st.subheader("📅 Yearly Comparison")

        # Get available years
        from services.expense_service import get_all_expenses

        expenses = get_all_expenses()
        years = sorted(set(int(e.date[:4]) for e in expenses))

        if len(years) >= 2:
            col1, col2 = st.columns(2)

            with col1:
                year1 = st.selectbox("First Year", years, index=0)

            with col2:
                year2 = st.selectbox("Second Year", years, index=-1)

            if year1 != year2:
                # Get comparison data
                yearly_data = history_service.get_yearly_comparison(year1, year2)

                # Display metrics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(str(year1), format_currency(yearly_data["year1_total"]))

                with col2:
                    st.metric(str(year2), format_currency(yearly_data["year2_total"]))

                with col3:
                    change = yearly_data["change"]
                    delta_color = "inverse" if change > 0 else "normal"
                    st.metric(
                        "Change",
                        format_currency(abs(change)),
                        delta=f"{yearly_data['change_percent']:.1f}%",
                        delta_color=delta_color,
                    )

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    fig = create_yearly_comparison_chart(yearly_data)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Category comparison
                    y1_cats = yearly_data["year1_categories"]
                    y2_cats = yearly_data["year2_categories"]

                    all_cats = sorted(set(y1_cats.keys()) | set(y2_cats.keys()))

                    cat_comp_data = {
                        "Category": all_cats,
                        str(year1): [y1_cats.get(c, 0) for c in all_cats],
                        str(year2): [y2_cats.get(c, 0) for c in all_cats],
                    }

                    import plotly.express as px

                    df_cats = pd.DataFrame(cat_comp_data)
                    fig = px.bar(
                        df_cats,
                        x="Category",
                        y=[str(year1), str(year2)],
                        barmode="group",
                        title=f"Category Comparison: {year1} vs {year2}",
                    )
                    fig.update_layout(template="plotly_white", height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please select different years for comparison.")
        else:
            st.info(
                "Need at least 2 years of data for yearly comparison. "
                f"Currently have data from: {', '.join(map(str, years))}"
            )

    # ==================== TAB 5: Trends & Velocity ====================
    with tab5:
        st.subheader("🚀 Spending Trends & Velocity")

        # Spending velocity
        st.subheader("💨 Spending Velocity")

        velocity = history_service.get_spending_velocity()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Daily Average", format_currency(velocity["daily_average"]))

        with col2:
            st.metric("Weekly Average", format_currency(velocity["weekly_average"]))

        with col3:
            st.metric("Monthly Average", format_currency(velocity["monthly_average"]))

        with col4:
            st.metric("Total Tracked", f"{velocity['total_days_tracked']} days")

        # Velocity chart
        fig = create_multi_metric_chart(velocity)
        st.plotly_chart(fig, use_container_width=True)

        # Category trends
        st.markdown("---")
        st.subheader("📉 Category Trends (12 months)")

        categories = history_service.get_category_totals()

        if categories:
            selected_category = st.selectbox(
                "Select Category", sorted(categories.keys())
            )

            trend = history_service.get_spending_trend(selected_category, months=12)

            if trend:
                fig = create_spending_trend_chart(trend, selected_category)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No trend data available for {selected_category}")

    # ==================== TAB 6: Detailed Breakdown ====================
    with tab6:
        st.subheader("🔍 Detailed Breakdown")

        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Year Summary", "Monthly Summary", "Category Summary"],
        )

        if analysis_type == "Year Summary":
            from services.expense_service import get_all_expenses

            expenses = get_all_expenses()
            years = sorted(set(int(e.date[:4]) for e in expenses))

            if years:
                selected_year = st.selectbox("Select Year", years)

                category_year_totals = history_service.get_category_year_totals(
                    selected_year
                )

                st.metric(
                    "Total for Year",
                    format_currency(sum(category_year_totals.values())),
                )

                # Chart
                fig = create_category_comparison_chart(category_year_totals)
                st.plotly_chart(fig, use_container_width=True)

                # Table
                df = pd.DataFrame(
                    [
                        {
                            "Category": cat,
                            "Total": format_currency(total),
                        }
                        for cat, total in sorted(
                            category_year_totals.items(),
                            key=lambda x: x[1],
                            reverse=True,
                        )
                    ]
                )

                st.dataframe(df, use_container_width=True, hide_index=True)

        elif analysis_type == "Monthly Summary":
            from services.expense_service import get_all_expenses

            expenses = get_all_expenses()
            months = sorted(set(e.date[:7] for e in expenses))

            if months:
                selected_month = st.selectbox("Select Month", months)

                # Get expenses for selected month
                month_start = f"{selected_month}-01"
                month_date = datetime.strptime(selected_month, "%Y-%m")
                month_end = (month_date.replace(day=28) + timedelta(days=4)).replace(
                    day=1
                ) - timedelta(days=1)
                month_end = month_end.strftime("%Y-%m-%d")

                from services.expense_service import get_expenses_by_date_range

                month_expenses = get_expenses_by_date_range(month_start, month_end)
                month_total = sum(e.amount for e in month_expenses)

                st.metric("Total for Month", format_currency(month_total))

                # Type distribution
                type_dist = history_service.get_expense_type_distribution(
                    selected_month
                )
                fig = create_expense_type_chart(type_dist)
                st.plotly_chart(fig, use_container_width=True)

                # Category breakdown
                category_totals = {}
                for exp in month_expenses:
                    category_totals[exp.category] = (
                        category_totals.get(exp.category, 0) + exp.amount
                    )

                fig = create_category_comparison_chart(category_totals)
                st.plotly_chart(fig, use_container_width=True)

                # Detailed table
                df = pd.DataFrame(
                    [
                        {
                            "Date": exp.date,
                            "Category": exp.category,
                            "Type": exp.type.capitalize(),
                            "Amount": format_currency(exp.amount),
                            "Description": exp.description or "-",
                        }
                        for exp in sorted(
                            month_expenses, key=lambda x: x.date, reverse=True
                        )
                    ]
                )

                st.dataframe(df, use_container_width=True, hide_index=True)

        else:  # Category Summary
            category_totals = history_service.get_category_totals()
            category_monthly = history_service.get_category_monthly_totals()

            if category_totals:
                selected_category = st.selectbox(
                    "Select Category", sorted(category_totals.keys())
                )

                cat_total = category_totals[selected_category]
                st.metric("Total for Category", format_currency(cat_total))

                # Trend chart
                if selected_category in category_monthly:
                    trend = category_monthly[selected_category]
                    fig = create_spending_trend_chart(trend, selected_category)
                    st.plotly_chart(fig, use_container_width=True)

                # Monthly breakdown table
                if selected_category in category_monthly:
                    df = pd.DataFrame(
                        [
                            {
                                "Month": month,
                                "Amount": format_currency(total),
                            }
                            for month, total in sorted(
                                category_monthly[selected_category].items()
                            )
                        ]
                    )

                    st.dataframe(df, use_container_width=True, hide_index=True)
