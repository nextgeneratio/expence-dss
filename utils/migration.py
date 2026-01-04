"""
Database Migration Utilities
Handles database schema migrations and data migrations for existing systems.
"""

import sqlite3
from pathlib import Path
from data.database import get_connection, close_connection
import config


def migrate_to_categories_table():
    """
    Migrate from hardcoded categories in config to categories table in database.

    This function:
    1. Creates the categories table if it doesn't exist
    2. Populates default categories from config
    3. Handles existing expenses that reference categories

    Safe to call multiple times - will not duplicate entries.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Create categories table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                budget REAL CHECK(budget > 0),
                is_custom BOOLEAN DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert default categories if they don't exist
        for category in config.EXPENSE_CATEGORIES:
            try:
                budget = config.BUDGET_THRESHOLDS.get(category, 0)
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO categories (name, budget, is_custom, is_active)
                    VALUES (?, ?, 0, 1)
                """,
                    (category, budget),
                )
            except sqlite3.IntegrityError:
                pass

        conn.commit()
        close_connection(conn)
        return True, "Categories table migrated successfully"

    except Exception as e:
        close_connection(conn)
        return False, f"Migration failed: {str(e)}"


def add_foreign_key_constraint():
    """
    Add foreign key constraint between expenses and categories.

    Note: SQLite doesn't support adding FK constraints after table creation,
    so this function documents the constraint and ensures consistency.

    Returns:
        Tuple[bool, str]: Success status and message
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if all expenses have valid categories
        cursor.execute(
            """
            SELECT DISTINCT e.category 
            FROM expenses e 
            WHERE e.category NOT IN (SELECT name FROM categories)
        """
        )

        orphaned = cursor.fetchall()

        if orphaned:
            # Log orphaned categories
            orphaned_categories = [row[0] for row in orphaned]

            # Create default categories for any orphaned entries
            for category in orphaned_categories:
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO categories (name, budget, is_custom, is_active)
                        VALUES (?, 0, 0, 1)
                    """,
                        (category,),
                    )
                except sqlite3.IntegrityError:
                    pass

            conn.commit()
            msg = f"Created categories for orphaned entries: {orphaned_categories}"
        else:
            msg = "All expenses reference valid categories"

        close_connection(conn)
        return True, msg

    except Exception as e:
        close_connection(conn)
        return False, f"FK consistency check failed: {str(e)}"


def get_migration_status() -> dict:
    """
    Get the current migration status of the database.

    Returns:
        dict: Migration status including:
            - has_categories_table: Whether categories table exists
            - categories_count: Number of categories
            - expenses_count: Number of expenses
            - orphaned_expenses: Count of expenses without valid categories
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if categories table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
        )
        has_categories = cursor.fetchone() is not None

        categories_count = 0
        expenses_count = 0
        orphaned_count = 0

        if has_categories:
            cursor.execute("SELECT COUNT(*) FROM categories")
            categories_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM expenses")
            expenses_count = cursor.fetchone()[0]

            # Check for orphaned expenses
            cursor.execute(
                """
                SELECT COUNT(*) FROM expenses e
                WHERE e.category NOT IN (SELECT name FROM categories)
            """
            )
            orphaned_count = cursor.fetchone()[0]

        close_connection(conn)

        return {
            "has_categories_table": has_categories,
            "categories_count": categories_count,
            "expenses_count": expenses_count,
            "orphaned_expenses": orphaned_count,
            "is_migrated": has_categories and orphaned_count == 0,
        }

    except Exception as e:
        close_connection(conn)
        return {
            "error": str(e),
            "has_categories_table": False,
            "is_migrated": False,
        }
