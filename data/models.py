"""
Expense data model
Defines the Expense class and related data structures.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import config


def _get_category_validator():
    """
    Lazy import to avoid circular dependencies.
    Returns a function that validates categories.
    """
    try:
        from services.category_service import validate_category

        return validate_category
    except ImportError:
        # Fallback to config if category_service not available
        return lambda cat: cat in config.EXPENSE_CATEGORIES


@dataclass
class Expense:
    """
    Expense data model representing a single expense entry.

    Attributes:
        amount: Amount spent (must be positive number)
        date: Date of the expense (ISO format, UTC timezone)
        category: Expense category (must be from controlled list)
        type: Expense type (fixed or variable)
        description: Optional description of the expense
        id: Database ID (auto-generated)
        created_at: Timestamp when the record was created

    Rules:
        - No negative amounts
        - No future dates
        - Category must exist in EXPENSE_CATEGORIES
        - No silent duplicates
    """

    amount: float
    date: str
    category: str
    type: str
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validate expense data after initialization."""
        self._validate()

    def _validate(self):
        """Enforce data validation rules."""
        # Rule: No negative amounts
        if not isinstance(self.amount, (int, float)):
            raise ValueError(
                f"Amount must be a number, got {type(self.amount).__name__}"
            )
        if self.amount <= 0:
            raise ValueError(f"Amount must be positive, got {self.amount}")

        # Rule: No future dates
        try:
            expense_date = datetime.strptime(self.date, config.DATE_FORMAT).date()
            if expense_date > datetime.now().date():
                raise ValueError(f"Date cannot be in the future: {self.date}")
        except ValueError as e:
            if "future" in str(e):
                raise
            raise ValueError(
                f"Invalid date format. Expected ISO format (YYYY-MM-DD): {self.date}"
            )

        # Rule: Category must exist
        validate_category = _get_category_validator()
        if not validate_category(self.category):
            raise ValueError(
                f"Invalid category '{self.category}'. Category does not exist or is inactive."
            )

        # Rule: Type must be valid
        if self.type not in config.EXPENSE_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}'. Must be one of: {', '.join(config.EXPENSE_TYPES)}"
            )

    def to_dict(self):
        """
        Convert expense to dictionary.

        Returns:
            dict: Dictionary representation of the expense
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "category": self.category,
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an Expense instance from a dictionary.

        Args:
            data: Dictionary containing expense data

        Returns:
            Expense: New Expense instance
        """
        return cls(
            amount=float(data["amount"]),  # Ensure numeric type
            date=data["date"],
            category=data["category"],
            type=data["type"],
            description=data.get("description"),
            id=data.get("id"),
            created_at=data.get("created_at"),
        )

    @classmethod
    def from_row(cls, row):
        """
        Create an Expense instance from a database row.

        Args:
            row: Database row (sqlite3.Row)

        Returns:
            Expense: New Expense instance
        """
        return cls(
            amount=float(row["amount"]),  # Ensure numeric type
            date=row["date"],
            category=row["category"],
            type=row["type"],
            description=row["description"],
            id=row["id"],
            created_at=row["created_at"],
        )

    def __str__(self):
        """String representation of the expense."""
        return f"Expense({self.date}, {self.category}, {self.type}, ${self.amount:.2f})"

    def get_hash(self) -> str:
        """Generate a hash for duplicate detection."""
        return f"{self.date}|{self.category}|{self.amount}|{self.type}"
