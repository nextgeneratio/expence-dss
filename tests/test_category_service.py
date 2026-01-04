"""
Unit tests for category management functionality
Tests CRUD operations and validation for custom categories.
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services import category_service
from data.database import init_database, get_connection, close_connection
import config


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db_path = temp_file.name
    temp_file.close()

    # Set config to use temp database
    original_db_path = config.DB_PATH
    config.DB_PATH = temp_db_path

    # Initialize the temporary database
    init_database()

    yield temp_db_path

    # Cleanup
    config.DB_PATH = original_db_path
    Path(temp_db_path).unlink(missing_ok=True)


class TestCategoryOperations:
    """Test category CRUD operations."""

    def test_add_category(self, temp_db):
        """Test adding a new category."""
        category_id = category_service.add_category("Groceries", 300.0)
        assert isinstance(category_id, int)
        assert category_id > 0

        # Verify it was added
        category = category_service.get_category_by_name("Groceries")
        assert category is not None
        assert category["name"] == "Groceries"
        assert category["budget"] == 300.0
        assert category["is_custom"] == 1

    def test_add_duplicate_category_fails(self, temp_db):
        """Test that adding duplicate category raises error."""
        category_service.add_category("Groceries", 300.0)

        with pytest.raises(ValueError, match="already exists"):
            category_service.add_category("Groceries", 400.0)

    def test_add_empty_category_fails(self, temp_db):
        """Test that adding empty category name fails."""
        with pytest.raises(ValueError, match="non-empty string"):
            category_service.add_category("", 300.0)

        with pytest.raises(ValueError, match="whitespace only"):
            category_service.add_category("   ", 300.0)

    def test_add_negative_budget_fails(self, temp_db):
        """Test that negative budget fails."""
        with pytest.raises(ValueError, match="negative"):
            category_service.add_category("Groceries", -100.0)

    def test_get_all_categories(self, temp_db):
        """Test retrieving all categories."""
        # Should have default categories
        categories = category_service.get_all_categories()
        assert len(categories) > 0

        # Add custom category
        category_service.add_category("Subscriptions", 50.0)

        categories = category_service.get_all_categories()
        assert any(c["name"] == "Subscriptions" for c in categories)

    def test_get_category_names(self, temp_db):
        """Test getting category names only."""
        category_service.add_category("Gym", 75.0)
        category_service.add_category("Movies", 25.0)

        names = category_service.get_category_names()
        assert "Gym" in names
        assert "Movies" in names

    def test_update_category_budget(self, temp_db):
        """Test updating a category's budget."""
        category_service.add_category("Groceries", 300.0)

        success = category_service.update_category("Groceries", budget=400.0)
        assert success is True

        category = category_service.get_category_by_name("Groceries")
        assert category["budget"] == 400.0

    def test_update_nonexistent_category_fails(self, temp_db):
        """Test updating non-existent category returns False."""
        success = category_service.update_category("NonExistent", budget=100.0)
        assert success is False

    def test_deactivate_custom_category(self, temp_db):
        """Test deactivating a custom category."""
        category_service.add_category("Groceries", 300.0)

        success = category_service.delete_category("Groceries", force=False)
        assert success is True

        category = category_service.get_category_by_name("Groceries")
        assert category["is_active"] == 0

    def test_reactivate_category(self, temp_db):
        """Test reactivating a deactivated category."""
        category_service.add_category("Groceries", 300.0)
        category_service.delete_category("Groceries", force=False)

        success = category_service.reactivate_category("Groceries")
        assert success is True

        category = category_service.get_category_by_name("Groceries")
        assert category["is_active"] == 1

    def test_cannot_delete_default_category_without_force(self, temp_db):
        """Test that default categories cannot be deleted without force."""
        # Food & Dining is a default category
        with pytest.raises(ValueError, match="Cannot delete default category"):
            category_service.delete_category("Food & Dining", force=False)

    def test_get_category_budget(self, temp_db):
        """Test getting budget for a specific category."""
        category_service.add_category("Groceries", 350.0)

        budget = category_service.get_category_budget("Groceries")
        assert budget == 350.0

        # Non-existent category should return 0
        budget = category_service.get_category_budget("NonExistent")
        assert budget == 0


class TestCategoryValidation:
    """Test category validation functions."""

    def test_validate_active_category(self, temp_db):
        """Test validating an active category."""
        category_service.add_category("Groceries", 300.0)

        assert category_service.validate_category("Groceries") is True

    def test_validate_nonexistent_category(self, temp_db):
        """Test validating non-existent category returns False."""
        assert category_service.validate_category("NonExistent") is False

    def test_validate_inactive_category(self, temp_db):
        """Test validating inactive category returns False."""
        category_service.add_category("Groceries", 300.0)
        category_service.delete_category("Groceries", force=False)

        assert category_service.validate_category("Groceries") is False


class TestCategoryFiltering:
    """Test filtering categories by type."""

    def test_get_custom_categories(self, temp_db):
        """Test retrieving only custom categories."""
        category_service.add_category("Gym", 75.0)
        category_service.add_category("Subscriptions", 50.0)

        custom = category_service.get_custom_categories()
        assert all(c["is_custom"] == 1 for c in custom)
        assert any(c["name"] == "Gym" for c in custom)

    def test_get_default_categories(self, temp_db):
        """Test retrieving only default categories."""
        default = category_service.get_default_categories()
        assert all(c["is_custom"] == 0 for c in default)
        assert len(default) > 0

    def test_get_all_budgets(self, temp_db):
        """Test getting all budgets as dictionary."""
        category_service.add_category("Groceries", 300.0)
        category_service.add_category("Gym", 75.0)

        budgets = category_service.get_all_budgets()
        assert budgets["Groceries"] == 300.0
        assert budgets["Gym"] == 75.0
        assert len(budgets) > 2  # Should include default categories too


class TestCategoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_category_name_with_whitespace(self, temp_db):
        """Test that category names are trimmed."""
        category_service.add_category("  Gym  ", 75.0)

        category = category_service.get_category_by_name("Gym")
        assert category is not None
        assert category["name"] == "Gym"

    def test_category_with_zero_budget(self, temp_db):
        """Test creating category with zero budget."""
        category_id = category_service.add_category("Hobbies", 0.0)
        assert category_id > 0

        category = category_service.get_category_by_name("Hobbies")
        assert category["budget"] == 0.0

    def test_get_category_names_excludes_inactive(self, temp_db):
        """Test that inactive categories are excluded by default."""
        category_service.add_category("Groceries", 300.0)
        category_service.delete_category("Groceries", force=False)

        names = category_service.get_category_names(include_inactive=False)
        assert "Groceries" not in names

    def test_get_category_names_includes_inactive_when_requested(self, temp_db):
        """Test that inactive categories are included when requested."""
        category_service.add_category("Groceries", 300.0)
        category_service.delete_category("Groceries", force=False)

        names = category_service.get_category_names(include_inactive=True)
        assert "Groceries" in names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
