"""
Lab 3 Solution — All 7 bugs fixed with documentation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class Product:
    def __init__(self, sku: str, name: str, price: float, stock: int = 0):
        self.sku = sku
        self.name = name
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"Product({self.sku!r}, {self.name!r}, price={self.price}, stock={self.stock})"


class Inventory:
    def __init__(self):
        self._products: dict[str, Product] = {}
        self._transactions: list[dict] = []

    def add_product(self, product: Product) -> None:
        self._products[product.sku] = product
        logger.info(f"Added product {product.sku}")

    def get_product(self, sku: str) -> Optional[Product]:
        return self._products.get(sku)

    def restock(self, sku: str, quantity: int) -> bool:
        product = self.get_product(sku)
        if product is None:
            return False
        # FIX 1: += instead of =
        product.stock += quantity
        self._record_transaction(sku, "restock", quantity)
        return True

    def sell(self, sku: str, quantity: int) -> dict:
        product = self.get_product(sku)
        if product is None:
            return {"status": "error", "message": f"Product {sku} not found"}
        if product.stock < quantity:
            return {"status": "error", "message": "Insufficient stock"}
        product.stock -= quantity
        # FIX 2: removed // 1 integer division
        total = product.price * quantity
        self._record_transaction(sku, "sale", quantity)
        return {"status": "ok", "total": total, "remaining_stock": product.stock}

    def get_low_stock(self, threshold: int = 10) -> list[Product]:
        # FIX 3: < instead of >
        return [p for p in self._products.values() if p.stock < threshold]

    def get_total_value(self) -> float:
        total = 0
        for product in self._products.values():
            # FIX 4: price * stock instead of just price
            total += product.price * product.stock
        return total

    def bulk_update_prices(self, adjustment_pct: float) -> int:
        count = 0
        for product in self._products.values():
            # FIX 5: divide by 100 instead of 10
            product.price = product.price * (1 + adjustment_pct / 100)
            count += 1
        return count

    def export_report(self) -> str:
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_products": len(self._products),
            "total_value": self.get_total_value(),
            "products": [],
        }
        for product in self._products.values():
            report["products"].append({
                "sku": product.sku,
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                # FIX 6: price * stock instead of price + stock
                "value": product.price * product.stock,
            })
        return json.dumps(report, indent=2)

    def _record_transaction(self, sku: str, txn_type: str, quantity: int) -> None:
        self._transactions.append({
            "sku": sku,
            "type": txn_type,
            "quantity": quantity,
            "timestamp": datetime.now().isoformat(),
        })

    def get_transactions(self, sku: Optional[str] = None, since: Optional[datetime] = None) -> list[dict]:
        results = self._transactions
        if sku:
            results = [t for t in results if t["sku"] == sku]
        if since:
            # FIX 7: compare string to string via isoformat()
            results = [t for t in results if t["timestamp"] > since.isoformat()]
        return results
