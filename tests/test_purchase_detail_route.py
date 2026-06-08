"""Regression tests for /purchases/<id> that ensure the template iterates
order['items'] correctly (dict-key access, not attribute access, which would
resolve to dict.items() and raise TypeError)."""

import datetime
import unittest
from unittest.mock import patch

from zarvent_repuestos.web.app import app


def _preset_order(items=None, status="Pending"):
    return {
        "purchase_order_id": 1,
        "order_date": datetime.date(2026, 6, 7),
        "expected_date": datetime.date(2026, 6, 14),
        "status": status,
        "total_amount": 200.0,
        "supplier_id": 1,
        "business_name": "AutoPartes Demo",
        "tax_id": "10293874001",
        "phone": "+591 2 245 7788",
        "email": "demo@example.com",
        "address": "Av. Demo 123",
        "items": items if items is not None else [
            {
                "purchase_order_item_id": 11,
                "part_id": 1,
                "quantity_ordered": 4,
                "quantity_received": 0,
                "unit_cost": 50.0,
                "internal_code": "ZR-0001",
                "name": "Filtro Demo",
                "brand": "DemoBrand",
            }
        ],
    }


class PurchaseDetailRouteTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def _login(self):
        with patch(
            "zarvent_repuestos.web.app.authenticate_user",
            return_value={"id": 1, "username": "admin"},
        ):
            self.client.post("/", data={"username": "admin", "password": "admin123"})

    def test_purchase_detail_renders_200_with_preset_order(self):
        self._login()
        order = _preset_order()
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
            return_value=order,
        ):
            response = self.client.get("/purchases/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ZR-0001", response.data)
        self.assertIn(b"Filtro Demo", response.data)
        self.assertIn(b"AutoPartes Demo", response.data)

    def test_purchase_detail_renders_with_no_items(self):
        self._login()
        order = _preset_order(items=[])
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
            return_value=order,
        ):
            response = self.client.get("/purchases/2")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AutoPartes Demo", response.data)
        self.assertNotIn(b"ZR-0001", response.data)

    def test_purchase_detail_returns_404_when_order_missing(self):
        self._login()
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
            return_value=None,
        ):
            response = self.client.get("/purchases/999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
