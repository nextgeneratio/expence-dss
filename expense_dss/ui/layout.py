"""
UI Layout Components
Defines common layout components and page configuration.
"""

import streamlit as st
import config


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Expense DSS",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS
    st.markdown(
        """
        <style>
        .big-font {
            font-size: 24px !important;
            font-weight: bold;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .alert-critical {
            background-color: #ffebee;
            border-left: 4px solid #d32f2f;
            padding: 10px;
            margin: 10px 0;
        }
        .alert-warning {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            padding: 10px;
            margin: 10px 0;
        }
        .alert-info {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 10px;
            margin: 10px 0;
        }
        .alert-success {
            background-color: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 10px;
            margin: 10px 0;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def display_header(title: str, subtitle: str = None):
    """
    Display a page header.

    Args:
        title: Main page title
        subtitle: Optional subtitle
    """
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")


def display_metric_card(
    label: str, value: str, delta: str = None, delta_color: str = "normal"
):
    """
    Display a metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        delta_color: Color for delta (normal, inverse, off)
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def display_alert(message: str, severity: str = "info"):
    """
    Display an alert box.

    Args:
        message: Alert message
        severity: Alert severity (critical, warning, info, success)
    """
    css_class = f"alert-{severity}"
    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)


def create_sidebar_filters():
    """
    Create common sidebar filters.

    Returns:
        dict: Dictionary containing filter values
    """
    st.sidebar.markdown("### Filters")

    date_range = st.sidebar.date_input(
        "Date Range", value=None, help="Filter by date range"
    )

    categories = st.sidebar.multiselect(
        "Categories", options=config.EXPENSE_CATEGORIES, help="Filter by categories"
    )

    return {"date_range": date_range, "categories": categories}


def display_empty_state(message: str = "No data available", icon: str = "📭"):
    """
    Display an empty state message.

    Args:
        message: Message to display
        icon: Icon emoji
    """
    st.info(f"{icon} {message}")


def create_two_columns():
    """
    Create a two-column layout.

    Returns:
        tuple: Two column objects
    """
    return st.columns(2)


def create_three_columns():
    """
    Create a three-column layout.

    Returns:
        tuple: Three column objects
    """
    return st.columns(3)


def display_dataframe(df, use_container_width: bool = True):
    """
    Display a dataframe with consistent styling.

    Args:
        df: Pandas DataFrame to display
        use_container_width: Whether to use full container width
    """
    st.dataframe(df, use_container_width=use_container_width)
