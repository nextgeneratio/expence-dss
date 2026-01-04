"""
Data Validation Utilities
Provides validation functions for user inputs.
"""

from datetime import datetime
import config


def validate_amount(amount) -> tuple:
    """
    Validate expense amount (Rule: No negative amounts, must be number).

    Args:
        amount: Amount to validate

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if amount is None:
        return False, "Amount is required"

    # Check if it's a number
    if not isinstance(amount, (int, float)):
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return False, "Amount must be a number"

    # Rule: No negative amounts
    if amount <= 0:
        return False, "Amount must be positive (greater than 0)"

    return True, None


def validate_date(date_str: str) -> tuple:
    """
    Validate date string format (Rule: ISO format, no future dates).

    Args:
        date_str: Date string to validate (YYYY-MM-DD ISO format)

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        expense_date = datetime.strptime(date_str, config.DATE_FORMAT).date()

        # Rule: No future dates
        if expense_date > datetime.now().date():
            return False, f"Date cannot be in the future: {date_str}"

        return True, None
    except (ValueError, TypeError):
        return (
            False,
            f"Invalid date format. Expected ISO format (YYYY-MM-DD): {date_str}",
        )


def validate_category(category: str) -> tuple:
    """
    Validate expense category (Rule: Must exist in controlled list).

    Args:
        category: Category to validate

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Rule: Category must exist
    if category not in config.EXPENSE_CATEGORIES:
        return (
            False,
            f"Invalid category '{category}'. Must be one of: {', '.join(config.EXPENSE_CATEGORIES)}",
        )

    return True, None


def validate_type(expense_type: str) -> tuple:
    """
    Validate expense type.

    Args:
        expense_type: Expense type to validate

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if expense_type not in config.EXPENSE_TYPES:
        return (
            False,
            f"Invalid type '{expense_type}'. Must be one of: {', '.join(config.EXPENSE_TYPES)}",
        )

    return True, None


def validate_description(description: str, max_length: int = 500) -> bool:
    """
    Validate expense description.

    Args:
        description: Description to validate
        max_length: Maximum allowed length

    Returns:
        bool: True if valid, False otherwise
    """
    if description is None:
        return True
    return isinstance(description, str) and len(description) <= max_length


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate that start_date is before or equal to end_date.

    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)

    Returns:
        bool: True if valid range, False otherwise
    """
    try:
        start = datetime.strptime(start_date, config.DATE_FORMAT)
        end = datetime.strptime(end_date, config.DATE_FORMAT)
        return start <= end
    except (ValueError, TypeError):
        return False


def validate_expense_data(
    amount: float, date: str, category: str, type: str, description: str = None
) -> tuple:
    """
    Validate all expense data at once.

    Args:
        amount: Expense amount
        date: Date string (YYYY-MM-DD ISO format)
        category: Expense category
        type: Expense type (fixed/variable)
        description: Optional description

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Validate amount (Rule: No negative amounts, must be number)
    valid, error = validate_amount(amount)
    if not valid:
        return False, error

    # Validate date (Rule: ISO format, no future dates)
    valid, error = validate_date(date)
    if not valid:
        return False, error

    # Validate category (Rule: Must exist in controlled list)
    valid, error = validate_category(category)
    if not valid:
        return False, error

    # Validate type
    valid, error = validate_type(type)
    if not valid:
        return False, error

    # Validate description
    if not validate_description(description):
        return False, "Description is too long. Maximum 500 characters."

    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize text input by trimming and removing potentially harmful characters.

    Args:
        text: Text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    # Trim whitespace
    text = text.strip()

    # Remove null bytes and other control characters
    text = "".join(char for char in text if ord(char) >= 32 or char == "\n")

    return text
