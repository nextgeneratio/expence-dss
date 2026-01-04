"""
Category Management UI
Provides interface for managing custom expense categories.
"""

import streamlit as st
from ui.layout import display_header, display_alert
from services import category_service


def show_category_management():
    """Display the Category Management page."""
    display_header(
        "📂 Category Management", "Add, edit, and manage your expense categories"
    )

    # Create two main sections: Add New Category and Manage Existing Categories
    tab1, tab2, tab3 = st.tabs(
        ["Add Category", "Manage Categories", "Category Budget Settings"]
    )

    # ==================== TAB 1: Add New Category ====================
    with tab1:
        st.subheader("Add a New Custom Category")

        col1, col2 = st.columns(2)

        with col1:
            new_category_name = st.text_input(
                "Category Name",
                placeholder="e.g., Gym, Subscriptions, Pets",
                max_chars=50,
                help="Enter a unique name for your custom category",
            )

        with col2:
            new_category_budget = st.number_input(
                "Monthly Budget",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                help="Optional: Set a monthly budget for this category (can be 0)",
            )

        if st.button("➕ Add Category", use_container_width=True):
            if not new_category_name:
                st.error("❌ Please enter a category name")
            else:
                try:
                    category_id = category_service.add_category(
                        name=new_category_name, budget=new_category_budget
                    )
                    st.success(
                        f"✅ Category '{new_category_name}' created successfully! (ID: {category_id})"
                    )
                    st.balloons()
                    # Reset input fields
                    st.session_state.pop("new_category_name", None)
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {str(e)}")

    # ==================== TAB 2: Manage Existing Categories ====================
    with tab2:
        st.subheader("Manage Your Categories")

        # Get all categories
        all_categories = category_service.get_all_categories(include_inactive=True)

        if not all_categories:
            st.info("📭 No categories found. Create one to get started!")
        else:
            # Separate custom and default categories
            custom_cats = [c for c in all_categories if c["is_custom"]]
            default_cats = [c for c in all_categories if not c["is_custom"]]

            # Display custom categories
            if custom_cats:
                st.markdown("### 🏷️ Custom Categories")

                for category in custom_cats:
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                    with col1:
                        status = "✅ Active" if category["is_active"] else "⏸️ Inactive"
                        st.markdown(
                            f"**{category['name']}** - Budget: ${category['budget']:.2f} *({status})*"
                        )

                    with col2:
                        if st.button(
                            "✏️ Edit",
                            key=f"edit_{category['id']}",
                            help="Edit this category",
                        ):
                            st.session_state.editing_category_id = category["id"]

                    with col3:
                        if category["is_active"]:
                            if st.button(
                                "⏸️ Deactivate",
                                key=f"deactivate_{category['id']}",
                                help="Deactivate this category",
                            ):
                                if category_service.delete_category(
                                    category["name"], force=False
                                ):
                                    st.success(
                                        f"✅ Category '{category['name']}' deactivated"
                                    )
                                    st.rerun()
                        else:
                            if st.button(
                                "🔄 Reactivate",
                                key=f"reactivate_{category['id']}",
                                help="Reactivate this category",
                            ):
                                if category_service.reactivate_category(
                                    category["name"]
                                ):
                                    st.success(
                                        f"✅ Category '{category['name']}' reactivated"
                                    )
                                    st.rerun()

                    with col4:
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{category['id']}",
                            help="Permanently delete this category",
                        ):
                            st.session_state.confirm_delete_category = category["name"]

                st.markdown("---")

            # Display default categories (read-only mostly)
            if default_cats:
                st.markdown("### 📌 Default Categories (System)")

                for category in default_cats:
                    status = "✅ Active" if category["is_active"] else "⏸️ Inactive"
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(
                            f"**{category['name']}** - Budget: ${category['budget']:.2f} *({status})*"
                        )

                    with col2:
                        if not category["is_active"]:
                            if st.button(
                                "🔄 Reactivate",
                                key=f"reactivate_default_{category['id']}",
                                help="Reactivate this default category",
                            ):
                                if category_service.reactivate_category(
                                    category["name"]
                                ):
                                    st.success(
                                        f"✅ Category '{category['name']}' reactivated"
                                    )
                                    st.rerun()

        # Handle delete confirmation
        if "confirm_delete_category" in st.session_state:
            category_to_delete = st.session_state.confirm_delete_category
            st.warning(
                f"⚠️ Are you sure you want to delete '{category_to_delete}'? This action cannot be undone."
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", key="confirm_delete"):
                    try:
                        category_service.delete_category(category_to_delete, force=True)
                        st.success(f"✅ Category '{category_to_delete}' deleted")
                        st.session_state.pop("confirm_delete_category", None)
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ Cannot delete: {str(e)}")

            with col2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    st.session_state.pop("confirm_delete_category", None)
                    st.rerun()

    # ==================== TAB 3: Budget Settings ====================
    with tab3:
        st.subheader("Category Budget Configuration")

        active_categories = category_service.get_all_categories(include_inactive=False)

        if not active_categories:
            st.info("📭 No active categories. Add or reactivate a category first.")
        else:
            st.info(
                "💡 Tip: Set a monthly budget for each category to track your spending against targets."
            )

            col1, col2 = st.columns(2)

            # Display budget inputs in two columns
            for idx, category in enumerate(active_categories):
                col = col1 if idx % 2 == 0 else col2

                with col:
                    budget_value = st.number_input(
                        f"{category['name']}",
                        min_value=0.0,
                        value=float(category["budget"]),
                        step=10.0,
                        format="%.2f",
                        key=f"budget_{category['name']}",
                        help=f"Monthly budget for {category['name']}",
                    )

                    # Update budget if changed
                    if budget_value != category["budget"]:
                        category_service.update_category(
                            category["name"], budget=budget_value
                        )
                        st.success(
                            f"✅ Budget for '{category['name']}' updated to ${budget_value:.2f}"
                        )

            if st.button("💾 Save All Budgets", use_container_width=True):
                st.success("✅ All budget changes have been saved!")
