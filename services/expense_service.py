"""
Expense Service - CRUD operations and TPS logic
Handles expense creation, retrieval, updates, and deletion.
Implements Transaction Processing System (TPS) functionality.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from data.database import get_connection, close_connection
from data.models import Expense
import config


def add_expense(
    amount: float, date: str, category: str, type: str, description: str = None
) -> int:
    """
    Add a new expense to the database.

    Args:
        amount: Amount spent (must be positive)
        date: Date of the expense (ISO format YYYY-MM-DD)
        category: Expense category (must be from controlled list)
        type: Expense type (fixed or variable)
        description: Optional description

    Returns:
        int: ID of the newly created expense

    Raises:
        ValueError: If validation rules are violated or duplicate detected
    """
    # Create expense object to validate (will raise ValueError if invalid)
    expense = Expense(
        amount=amount, date=date, category=category, type=type, description=description
    )

    conn = get_connection()
    cursor = conn.cursor()

    # Check for duplicates (Rule: No silent duplicates)
    cursor.execute(
        """
        SELECT id FROM expenses 
        WHERE date = ? AND category = ? AND amount = ? AND type = ?
        AND created_at > datetime('now', '-1 minute')
    """,
        (date, category, amount, type),
    )

    if cursor.fetchone():
        close_connection(conn)
        raise ValueError(
            "Duplicate expense detected: identical expense was added within the last minute"
        )

    cursor.execute(
        """
        INSERT INTO expenses (amount, date, category, type, description)
        VALUES (?, ?, ?, ?, ?)
    """,
        (amount, date, category, type, description),
    )

    expense_id = cursor.lastrowid
    conn.commit()
    close_connection(conn)

    return expense_id


def get_expense(expense_id: int) -> Optional[Expense]:
    """
    Retrieve a single expense by ID.

    Args:
        expense_id: ID of the expense

    Returns:
        Expense: Expense object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    close_connection(conn)

    return Expense.from_row(row) if row else None


def get_all_expenses() -> List[Expense]:
    """
    Retrieve all expenses.

    Returns:
        List[Expense]: List of all expenses
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY date DESC, created_at DESC")
    rows = cursor.fetchall()
    close_connection(conn)

    return [Expense.from_row(row) for row in rows]


def get_expenses_by_date_range(start_date: str, end_date: str) -> List[Expense]:
    """
    Retrieve expenses within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        List[Expense]: List of expenses in the date range
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
    """,
        (start_date, end_date),
    )

    rows = cursor.fetchall()
    close_connection(conn)

    return [Expense.from_row(row) for row in rows]


def get_expenses_by_category(category: str) -> List[Expense]:
    """
    Retrieve all expenses for a specific category.

    Args:
        category: Expense category

    Returns:
        List[Expense]: List of expenses in the category
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM expenses 
        WHERE category = ?
        ORDER BY date DESC
    """,
        (category,),
    )

    rows = cursor.fetchall()
    close_connection(conn)

    return [Expense.from_row(row) for row in rows]


def update_expense(
    expense_id: int,
    amount: float = None,
    date: str = None,
    category: str = None,
    type: str = None,
    description: str = None,
) -> bool:
    """
    Update an existing expense.

    Args:
        expense_id: ID of the expense to update
        amount: New amount (optional)
        date: New date (optional)
        category: New category (optional)
        type: New type (optional)
        description: New description (optional)

    Returns:
        bool: True if update was successful, False otherwise

    Raises:
        ValueError: If validation rules are violated
    """
    expense = get_expense(expense_id)
    if not expense:
        return False

    # Use existing values if new ones not provided
    amount = amount if amount is not None else expense.amount
    date = date or expense.date
    category = category or expense.category
    type = type or expense.type
    description = description if description is not None else expense.description

    # Validate updated expense
    updated_expense = Expense(
        amount=amount, date=date, category=category, type=type, description=description
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE expenses 
        SET amount = ?, date = ?, category = ?, type = ?, description = ?
        WHERE id = ?
    """,
        (amount, date, category, type, description, expense_id),
    )

    conn.commit()
    success = cursor.rowcount > 0
    close_connection(conn)

    return success


def delete_expense(expense_id: int) -> bool:
    """
    Delete an expense.

    Args:
        expense_id: ID of the expense to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    conn.commit()
    success = cursor.rowcount > 0
    close_connection(conn)

    return success


def get_total_by_category(
    start_date: str = None, end_date: str = None
) -> Dict[str, float]:
    """
    Calculate total spending by category.

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        Dict[str, float]: Dictionary mapping categories to total amounts
    """
    conn = get_connection()
    cursor = conn.cursor()

    if start_date and end_date:
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
            GROUP BY category
        """,
            (start_date, end_date),
        )
    else:
        cursor.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
        """
        )

    rows = cursor.fetchall()
    close_connection(conn)

    return {row["category"]: row["total"] for row in rows}


def get_total_spending(start_date: str = None, end_date: str = None) -> float:
    """
    Calculate total spending across all categories.

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        float: Total spending amount
    """
    conn = get_connection()
    cursor = conn.cursor()

    if start_date and end_date:
        cursor.execute(
            """
            SELECT SUM(amount) as total
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """,
            (start_date, end_date),
        )
    else:
        cursor.execute("SELECT SUM(amount) as total FROM expenses")

    row = cursor.fetchone()
    close_connection(conn)

    return row["total"] if row["total"] else 0.0


def get_monthly_total(year: int, month: int) -> float:
    """
    Get total spending for a specific month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        float: Total spending for the month
    """
    start_date = f"{year}-{month:02d}-01"

    # Calculate last day of month
    if month == 12:
        end_date = f"{year}-12-31"
    else:
        next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        end_date = last_day.strftime("%Y-%m-%d")

    return get_total_spending(start_date, end_date)
