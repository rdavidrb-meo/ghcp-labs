"""
Starter tests for Lab 3.
These tests are written AGAINST THE CORRECT BEHAVIOR,
so they will FAIL until the bugs in inventory.py are fixed.
"""

import pytest
from inventory import Product, Inventory


@pytest.fixture
def inv():
    inventory = Inventory()
    inventory.add_product(Product("SKU-001", "Widget", 9.99, stock=50))
    inventory.add_product(Product("SKU-002", "Gadget", 24.99, stock=5))
    return inventory


class TestRestock:
    def test_restock_adds_to_existing_stock(self, inv):
        inv.restock("SKU-001", 10)
        product = inv.get_product("SKU-001")
        assert product.stock == 60  # was 50, added 10


class TestSell:
    def test_sell_calculates_correct_total(self, inv):
        result = inv.sell("SKU-001", 3)
        assert result["status"] == "ok"
        # 3 × 9.99 = 29.97, not 29.0
        assert result["total"] == pytest.approx(29.97)


class TestLowStock:
    def test_low_stock_returns_products_below_threshold(self, inv):
        low = inv.get_low_stock(threshold=10)
        skus = [p.sku for p in low]
        # SKU-002 has stock=5, which is below 10
        assert "SKU-002" in skus
        assert "SKU-001" not in skus


class TestTotalValue:
    def test_total_value_is_price_times_stock(self, inv):
        # SKU-001: 9.99 * 50 = 499.50
        # SKU-002: 24.99 * 5 = 124.95
        # Total = 624.45
        assert inv.get_total_value() == pytest.approx(624.45)


class TestBulkPriceUpdate:
    def test_10_percent_increase(self, inv):
        inv.bulk_update_prices(10)
        product = inv.get_product("SKU-001")
        # 9.99 * 1.10 = 10.989
        assert product.price == pytest.approx(10.989)


class TestExportReport:
    def test_product_value_in_report(self, inv):
        import json
        report = json.loads(inv.export_report())
        widget = next(p for p in report["products"] if p["sku"] == "SKU-001")
        # value should be price * stock = 9.99 * 50 = 499.50
        assert widget["value"] == pytest.approx(499.50)


class TestTransactionFiltering:
    def test_filter_by_date(self, inv):
        from datetime import datetime, timedelta
        before = datetime.now() - timedelta(seconds=1)
        inv.sell("SKU-001", 1)
        results = inv.get_transactions(since=before)
        assert len(results) == 1
