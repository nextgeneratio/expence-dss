"""
Anomaly Detection View
Display detected spending anomalies and actionable recommendations.
"""

import streamlit as st
import pandas as pd
from ui.layout import display_header, display_alert
from services import anomaly_service
from utils.helpers import format_currency


def show_anomalies():
    """Display the Anomaly Detection page."""
    display_header(
        "🔍 Anomaly Detection", "Identify spending issues and get recommendations"
    )

    # Get anomaly data
    summary = anomaly_service.get_anomaly_summary()
    recommendations = anomaly_service.get_actionable_recommendations()

    # Summary metrics
    st.subheader("📊 Anomaly Summary")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Anomalies", summary["total_anomalies"])

    with col2:
        st.metric(
            "Overspending",
            summary["overspending_count"],
            delta="🔴" if summary["overspending_count"] > 0 else "✅",
        )

    with col3:
        st.metric(
            "Spikes",
            summary["spike_count"],
            delta="⚡" if summary["spike_count"] > 0 else "✅",
        )

    with col4:
        st.metric(
            "Budget Risk",
            summary["budget_risk_count"],
            delta="⚠️" if summary["budget_risk_count"] > 0 else "✅",
        )

    with col5:
        st.metric(
            "Fixed Costs",
            summary["fixed_cost_warnings"],
            delta="🔒" if summary["fixed_cost_warnings"] > 0 else "✅",
        )

    with col6:
        st.metric(
            "Rising Trends",
            summary["trend_warnings"],
            delta="📈" if summary["trend_warnings"] > 0 else "✅",
        )

    # Critical alerts
    if summary["critical_alerts"] > 0:
        st.warning(f"⚠️ **{summary['critical_alerts']} Critical Alert(s)**")

    st.markdown("---")

    # Create tabs for different anomalies
    (tab1, tab2, tab3, tab4, tab5, tab6) = st.tabs(
        [
            "All Recommendations",
            "Overspending",
            "Spikes",
            "Budget Risk",
            "Fixed Costs",
            "Trends",
        ]
    )

    # ==================== TAB 1: All Recommendations ====================
    with tab1:
        st.subheader("🎯 Action Plan")

        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                priority_color = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }
                priority_emoji = priority_color.get(rec["priority"], "⚪")

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"### {priority_emoji} {idx}. {rec['title']}")
                    st.write(f"**Category:** {rec['category']}")
                    st.write(f"**Action:** {rec['action']}")
                    st.write(f"**Impact:** {rec['impact']}")
                    st.write(f"**Effort:** {rec['effort']}")
                    st.write(f"\n{rec['recommendation']}")

                with col2:
                    priority_badge = {
                        "critical": "🔴 CRITICAL",
                        "high": "🟠 HIGH",
                        "medium": "🟡 MEDIUM",
                        "low": "🟢 LOW",
                    }
                    st.markdown(
                        f"<div style='text-align: center; padding: 10px; border-radius: 5px; background-color: #f0f0f0;'><b>{priority_badge.get(rec['priority'], 'N/A')}</b></div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")
        else:
            st.success("✅ No anomalies detected! Your spending is on track.")

    # ==================== TAB 2: Overspending ====================
    with tab2:
        st.subheader("💰 Overspending Alerts")

        overspending = summary["anomalies"]["overspending"]

        if overspending:
            for alert in overspending:
                col1, col2 = st.columns([3, 1])

                with col1:
                    severity_icon = "🔴" if alert["severity"] == "critical" else "🟠"
                    st.markdown(f"### {severity_icon} {alert['title']}")

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Budget", format_currency(alert["budget"]))
                    with col_b:
                        st.metric("Spent", format_currency(alert["current"]))
                    with col_c:
                        st.metric("Over", format_currency(alert["overage"]))

                    st.write(f"**Overage:** {alert['percentage']:.1f}%")
                    st.write(alert["message"])
                    st.info(alert["recommendation"])

                with col2:
                    st.metric("Action", f"Cut {alert['percentage']:.1f}%")

                st.markdown("---")
        else:
            st.success("✅ No categories are overspending!")

    # ==================== TAB 3: Spikes ====================
    with tab3:
        st.subheader("⚡ Spending Spikes")

        spikes = summary["anomalies"]["spikes"]

        if spikes:
            for spike in spikes:
                st.markdown(f"### {spike['title']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Previous Month", format_currency(spike["previous"]))
                with col2:
                    st.metric("Current Month", format_currency(spike["current"]))
                with col3:
                    st.metric("Increase", f"{spike['increase']:.1f}%")

                st.write(
                    f"**Amount Increase:** {format_currency(spike['amount_increase'])}"
                )
                st.write(spike["message"])
                st.info(spike["recommendation"])

                st.markdown("---")
        else:
            st.success("✅ No spending spikes detected!")

    # ==================== TAB 4: Budget Risk ====================
    with tab4:
        st.subheader("⚠️ Budget Risk Categories")

        risks = summary["anomalies"]["budget_risk"]

        if risks:
            for risk in risks:
                st.markdown(f"### {risk['title']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Budget", format_currency(risk["budget"]))
                with col2:
                    st.metric("Spent", format_currency(risk["current"]))
                with col3:
                    st.metric("Remaining", format_currency(risk["remaining"]))

                st.write(
                    f"**Usage:** {risk['percentage_used']:.1f}% of budget consumed"
                )

                # Progress bar
                st.progress(risk["percentage_used"] / 100)

                st.write(risk["message"])
                st.warning(risk["recommendation"])

                st.markdown("---")
        else:
            st.success("✅ All categories are below risk threshold!")

    # ==================== TAB 5: Fixed Costs ====================
    with tab5:
        st.subheader("🔒 Fixed vs Variable Analysis")

        fixed_warnings = summary["anomalies"]["fixed_costs"]

        if fixed_warnings:
            for warning in fixed_warnings:
                st.markdown(f"### {warning['title']}")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Fixed Costs", format_currency(warning["fixed_total"]))
                with col2:
                    st.metric(
                        "Variable Costs", format_currency(warning["variable_total"])
                    )

                st.metric("Fixed Percentage", f"{warning['fixed_ratio']:.1f}%")

                # Visual representation
                total = warning["fixed_total"] + warning["variable_total"]
                if total > 0:
                    import plotly.graph_objects as go

                    fig = go.Figure(
                        data=[
                            go.Bar(
                                x=["Fixed", "Variable"],
                                y=[warning["fixed_total"], warning["variable_total"]],
                                marker=dict(color=["#ff7f0e", "#1f77b4"]),
                            )
                        ]
                    )
                    fig.update_layout(
                        title="Fixed vs Variable Expenses",
                        yaxis_title="Amount ($)",
                        template="plotly_white",
                        height=400,
                        showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.write(warning["message"])
                st.warning(warning["recommendation"])

                st.markdown("---")
        else:
            st.success("✅ Fixed costs are at healthy levels!")

    # ==================== TAB 6: Trends ====================
    with tab6:
        st.subheader("📈 Rising Trend Alerts")

        trends = summary["anomalies"]["rising_trends"]

        if trends:
            for trend in trends:
                st.markdown(f"### {trend['title']}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("3 Months Ago", format_currency(trend["first_month"]))
                with col2:
                    st.metric("Current", format_currency(trend["last_month"]))
                with col3:
                    st.metric("Increase", f"{trend['increase']:.1f}%")

                st.write(trend["message"])
                st.info(trend["recommendation"])

                st.markdown("---")
        else:
            st.success("✅ No rising trends detected!")

    # Settings link
    st.markdown("---")
    st.info(
        "💡 Tip: Adjust anomaly detection thresholds in **Settings** tab to customize sensitivity"
    )
