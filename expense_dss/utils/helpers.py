"""
Helper Utilities
Provides common helper functions for date formatting, currency, etc.
"""

from datetime import datetime, timedelta
from typing import Tuple
import config

try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


def format_currency(amount: float) -> str:
    """
    Format amount as currency string using dynamic currency from settings.

    Args:
        amount: Amount to format

    Returns:
        str: Formatted currency string
    """
    # Use currency from session state if available (settings page), otherwise fall back to config
    if HAS_STREAMLIT:
        try:
            currency = st.session_state.get("currency_symbol", config.CURRENCY_SYMBOL)
        except Exception:
            currency = config.CURRENCY_SYMBOL
    else:
        currency = config.CURRENCY_SYMBOL

    return f"{currency}{amount:,.2f}"


def format_date(date_str: str, output_format: str = "%B %d, %Y") -> str:
    """
    Format date string to a different format.

    Args:
        date_str: Input date string (YYYY-MM-DD)
        output_format: Desired output format

    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, config.DATE_FORMAT)
        return date_obj.strftime(output_format)
    except (ValueError, TypeError):
        return date_str


def get_current_month_range() -> Tuple[str, str]:
    """
    Get the start and end dates of the current month.

    Returns:
        tuple: (start_date, end_date) as strings (YYYY-MM-DD)
    """
    now = datetime.now()
    start_date = now.replace(day=1).strftime(config.DATE_FORMAT)

    # Get last day of current month
    if now.month == 12:
        last_day = 31
    else:
        next_month = now.replace(month=now.month + 1, day=1)
        last_day = (next_month - timedelta(days=1)).day

    end_date = now.replace(day=last_day).strftime(config.DATE_FORMAT)

    return start_date, end_date


def get_previous_month_range() -> Tuple[str, str]:
    """
    Get the start and end dates of the previous month.

    Returns:
        tuple: (start_date, end_date) as strings (YYYY-MM-DD)
    """
    now = datetime.now()

    # Get first day of previous month
    if now.month == 1:
        start_date = now.replace(year=now.year - 1, month=12, day=1)
    else:
        start_date = now.replace(month=now.month - 1, day=1)

    # Get last day of previous month
    end_date = now.replace(day=1) - timedelta(days=1)

    return start_date.strftime(config.DATE_FORMAT), end_date.strftime(
        config.DATE_FORMAT
    )


def get_date_range(days: int) -> Tuple[str, str]:
    """
    Get date range for the last N days.

    Args:
        days: Number of days to go back

    Returns:
        tuple: (start_date, end_date) as strings (YYYY-MM-DD)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    return start_date.strftime(config.DATE_FORMAT), end_date.strftime(
        config.DATE_FORMAT
    )


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage.

    Args:
        part: Part value
        whole: Whole value

    Returns:
        float: Percentage value
    """
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def get_month_name(month: int) -> str:
    """
    Get month name from month number.

    Args:
        month: Month number (1-12)

    Returns:
        str: Month name
    """
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    if 1 <= month <= 12:
        return months[month - 1]
    return "Unknown"


def parse_date(date_str: str) -> datetime:
    """
    Parse date string to datetime object.

    Args:
        date_str: Date string (YYYY-MM-DD)

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValueError: If date string is invalid
    """
    return datetime.strptime(date_str, config.DATE_FORMAT)


def get_week_range(date: datetime = None) -> Tuple[str, str]:
    """
    Get the start and end dates of the week containing the given date.

    Args:
        date: Date to find week for (defaults to today)

    Returns:
        tuple: (start_date, end_date) as strings (YYYY-MM-DD)
    """
    if date is None:
        date = datetime.now()

    # Get Monday of the week
    start_date = date - timedelta(days=date.weekday())
    # Get Sunday of the week
    end_date = start_date + timedelta(days=6)

    return start_date.strftime(config.DATE_FORMAT), end_date.strftime(
        config.DATE_FORMAT
    )


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append when truncated

    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def days_between(start_date: str, end_date: str) -> int:
    """
    Calculate number of days between two dates.

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)

    Returns:
        int: Number of days between dates
    """
    try:
        start = datetime.strptime(start_date, config.DATE_FORMAT)
        end = datetime.strptime(end_date, config.DATE_FORMAT)
        return (end - start).days
    except (ValueError, TypeError):
        return 0
