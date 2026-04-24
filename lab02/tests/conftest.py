"""
Shared fixtures for the lab02 test suite.

Part 2 task: Move your make_order factory fixture here so it can be
used by ALL test files (test_process_order, test_validation, test_notify).
"""

import pytest

from order_processor import Order, OrderItem


@pytest.fixture
def make_order():
	"""Factory fixture that returns a callable to build test orders."""

	def _factory(**overrides):
		defaults = dict(
			order_id="ORD-001",
			customer_email="test@example.com",
			items=[OrderItem("PROD-1", "Widget", 2, 10.00)],
			discount_pct=0.0,
		)
		defaults.update(overrides)
		return Order(**defaults)

	return _factory
