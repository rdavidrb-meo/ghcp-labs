"""
Part 2 — Fixtures & Parametrize (15 min)
=========================================
Goal: Use pytest fixtures (factory pattern) and @pytest.mark.parametrize
to test validate_order() with clean, data-driven tests.

validate_order() has 8+ conditions. Use parametrize to hit them all
without writing 8 separate test functions.

Hints (try on your own first!):
  - Fixture factory: the fixture returns a *function*, not an object
  - Boundary tests: discount=0 and discount=100 are valid (empty error list)
  - Use @pytest.mark.parametrize("order_kwargs,expected_errors", [...])
"""

import pytest
from order_processor import OrderItem, validate_order


# ── Part B: Parametrized validation tests ────────────────────────────

class TestValidateOrder:

    def test_valid_order_has_no_errors(self, make_order):
        order = make_order()
        assert validate_order(order) == []

    @pytest.mark.parametrize(
        "order_kwargs, expected_error",
        [
            ({"order_id": ""}, "order_id is required"),
            ({"order_id": " "}, "order_id is required"),
            ({"customer_email": "no-at"}, "customer_email is invalid"),
            ({"customer_email": ""}, "customer_email is invalid"),
            ({"items": []}, "at least one item"),
            ({"discount_pct": -5}, "between 0 and 100"),
            ({"discount_pct": 101}, "between 0 and 100"),
        ],
    )
    def test_single_validation_error(self, make_order, order_kwargs, expected_error):
        order = make_order(**order_kwargs)
        errors = validate_order(order)
        assert any(expected_error in e for e in errors)

    @pytest.mark.parametrize("discount", [0, 100])
    def test_boundary_discounts_are_valid(self, make_order, discount):
        order = make_order(discount_pct=discount)
        assert validate_order(order) == []

    @pytest.mark.parametrize(
        "items, expected_error",
        [
            ([OrderItem("PROD-1", "Widget", 0, 10.00)], "quantity must be positive"),
            ([OrderItem("PROD-1", "Widget", 1, -0.01)], "unit_price cannot be negative"),
        ],
    )
    def test_item_level_validation(self, make_order, items, expected_error):
        order = make_order(items=items)
        errors = validate_order(order)
        assert any(expected_error in e for e in errors)
