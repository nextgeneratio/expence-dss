"""
Database connection and setup
Handles SQLite database initialization and connection management.
"""

import sqlite3
from pathlib import Path
import config


def get_connection():
    """
    Create and return a database connection.

    Returns:
        sqlite3.Connection: Database connection object
    """
    db_path = Path(config.DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database():
    """
    Initialize the database schema.
    Creates the categories and expenses tables if they don't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create categories table
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
            cursor.execute(
                """
                INSERT OR IGNORE INTO categories (name, budget, is_custom, is_active)
                VALUES (?, ?, 0, 1)
            """,
                (category, config.BUDGET_THRESHOLDS.get(category, 0)),
            )
        except sqlite3.IntegrityError:
            pass

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK(amount > 0),
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('fixed', 'variable')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(category) REFERENCES categories(name)
        )
    """
    )

    # Create index on date for faster queries
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_expense_date 
        ON expenses(date)
    """
    )

    # Create index on category for faster aggregations
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_expense_category 
        ON expenses(category)
    """
    )

    conn.commit()
    conn.close()


def close_connection(conn):
    """
    Close the database connection.

    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()
