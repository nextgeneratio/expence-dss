"""
Category Service - CRUD operations for custom expense categories
Handles category creation, retrieval, updates, and deletion.
"""

from typing import List, Optional, Dict
from datetime import datetime
from data.database import get_connection, close_connection
import config


def get_all_categories(include_inactive: bool = False) -> List[Dict]:
    """
    Retrieve all categories.

    Args:
        include_inactive: Whether to include inactive categories

    Returns:
        List[Dict]: List of category dictionaries with fields: id, name, budget, is_custom, is_active
    """
    conn = get_connection()
    cursor = conn.cursor()

    if include_inactive:
        cursor.execute(
            "SELECT id, name, budget, is_custom, is_active FROM categories ORDER BY is_custom DESC, name"
        )
    else:
        cursor.execute(
            "SELECT id, name, budget, is_custom, is_active FROM categories WHERE is_active = 1 ORDER BY is_custom DESC, name"
        )

    rows = cursor.fetchall()
    close_connection(conn)

    return [dict(row) for row in rows]


def get_category_names(include_inactive: bool = False) -> List[str]:
    """
    Get list of category names only.

    Args:
        include_inactive: Whether to include inactive categories

    Returns:
        List[str]: List of category names
    """
    categories = get_all_categories(include_inactive=include_inactive)
    return [cat["name"] for cat in categories]


def get_category_by_name(name: str) -> Optional[Dict]:
    """
    Retrieve a category by name.

    Args:
        name: Category name

    Returns:
        Dict: Category data if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, budget, is_custom, is_active FROM categories WHERE name = ?",
        (name,),
    )

    row = cursor.fetchone()
    close_connection(conn)

    return dict(row) if row else None


def add_category(name: str, budget: float = 0) -> int:
    """
    Add a new custom category.

    Args:
        name: Category name (must be unique)
        budget: Monthly budget for this category (default 0)

    Returns:
        int: ID of the newly created category

    Raises:
        ValueError: If category name already exists
    """
    if not name or not isinstance(name, str):
        raise ValueError("Category name must be a non-empty string")

    if len(name.strip()) == 0:
        raise ValueError("Category name cannot be empty or whitespace only")

    if budget < 0:
        raise ValueError("Budget cannot be negative")

    # Check if category already exists
    existing = get_category_by_name(name)
    if existing:
        raise ValueError(f"Category '{name}' already exists")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO categories (name, budget, is_custom, is_active)
            VALUES (?, ?, 1, 1)
        """,
            (name.strip(), budget),
        )
        conn.commit()
        category_id = cursor.lastrowid
        close_connection(conn)
        return category_id
    except Exception as e:
        close_connection(conn)
        raise ValueError(f"Failed to add category: {str(e)}")


def update_category(name: str, budget: float = None) -> bool:
    """
    Update an existing category.

    Args:
        name: Category name
        budget: New budget value (optional)

    Returns:
        bool: True if updated successfully, False if category not found

    Raises:
        ValueError: If validation fails
    """
    if budget is not None and budget < 0:
        raise ValueError("Budget cannot be negative")

    conn = get_connection()
    cursor = conn.cursor()

    # Check if category exists
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    if not cursor.fetchone():
        close_connection(conn)
        return False

    if budget is not None:
        cursor.execute(
            "UPDATE categories SET budget = ? WHERE name = ?",
            (budget, name),
        )

    conn.commit()
    close_connection(conn)
    return True


def delete_category(name: str, force: bool = False) -> bool:
    """
    Delete or deactivate a category.

    Args:
        name: Category name
        force: If True, completely delete. If False, just deactivate (default)

    Returns:
        bool: True if deleted/deactivated, False if category not found or has active expenses

    Raises:
        ValueError: If trying to delete a default category
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if category exists and get its info
    cursor.execute("SELECT id, is_custom FROM categories WHERE name = ?", (name,))
    row = cursor.fetchone()

    if not row:
        close_connection(conn)
        return False

    is_custom = row["is_custom"]

    # Don't allow deletion of default categories unless force=True
    if not is_custom and not force:
        close_connection(conn)
        raise ValueError(
            f"Cannot delete default category '{name}'. Default categories can only be deactivated."
        )

    # Check for active expenses in this category
    cursor.execute("SELECT COUNT(*) as count FROM expenses WHERE category = ?", (name,))
    expense_count = cursor.fetchone()["count"]

    if expense_count > 0 and force:
        close_connection(conn)
        raise ValueError(
            f"Cannot delete category '{name}' as it has {expense_count} associated expenses. "
            "Please reassign or delete those expenses first."
        )

    if force:
        # Complete deletion
        cursor.execute("DELETE FROM categories WHERE name = ?", (name,))
    else:
        # Soft delete (deactivate)
        cursor.execute("UPDATE categories SET is_active = 0 WHERE name = ?", (name,))

    conn.commit()
    close_connection(conn)
    return True


def reactivate_category(name: str) -> bool:
    """
    Reactivate a deactivated category.

    Args:
        name: Category name

    Returns:
        bool: True if reactivated, False if category not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    if not cursor.fetchone():
        close_connection(conn)
        return False

    cursor.execute(
        "UPDATE categories SET is_active = 1 WHERE name = ?",
        (name,),
    )

    conn.commit()
    close_connection(conn)
    return True


def get_category_budget(category_name: str) -> float:
    """
    Get the budget for a specific category.

    Args:
        category_name: Category name

    Returns:
        float: Budget amount, or 0 if not found
    """
    category = get_category_by_name(category_name)
    return category["budget"] if category else 0


def get_all_budgets() -> Dict[str, float]:
    """
    Get all categories with their budgets.

    Returns:
        Dict[str, float]: Mapping of category names to budgets
    """
    categories = get_all_categories(include_inactive=False)
    return {cat["name"]: cat["budget"] for cat in categories}


def get_custom_categories() -> List[Dict]:
    """
    Get only custom categories (user-defined).

    Returns:
        List[Dict]: List of custom category dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, budget, is_custom, is_active FROM categories WHERE is_custom = 1 ORDER BY name"
    )

    rows = cursor.fetchall()
    close_connection(conn)

    return [dict(row) for row in rows]


def get_default_categories() -> List[Dict]:
    """
    Get only default categories.

    Returns:
        List[Dict]: List of default category dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, budget, is_custom, is_active FROM categories WHERE is_custom = 0 ORDER BY name"
    )

    rows = cursor.fetchall()
    close_connection(conn)

    return [dict(row) for row in rows]


def validate_category(category_name: str) -> bool:
    """
    Check if a category exists and is active.

    Args:
        category_name: Category name to validate

    Returns:
        bool: True if category exists and is active, False otherwise
    """
    category = get_category_by_name(category_name)
    return category is not None and category["is_active"]
