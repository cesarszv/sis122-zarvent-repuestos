"""Regression tests for /sales/receipt/<id> that ensure the template
iterates `order['items']` correctly (dict-key access, not attribute access)."""

import unittest
from unittest.mock import patch

from zarvent_repuestos.web.app import app


PRESET_ORDER = {
    "sales_order_id": 2,
    "order_date": __import__("datetime").date(2026, 6, 7),
    "status": "Paid",
    "subtotal": 100.0,
    "discount_amount": 0.0,
    "total_amount": 100.0,
    "billing_name": "Cliente Demo",
    "tax_id": "1234567",
    "phone": "70000000",
    "email": None,
    "address": None,
    "items": [
        {
            "sales_order_item_id": 1,
            "quantity": 2,
            "unit_price": 50.0,
            "discount_amount": 0.0,
            "internal_code": "ZR-0001",
            "name": "Filtro Demo",
            "brand": "DemoBrand",
        }
    ],
}


class ReceiptRouteTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def _login(self):
        with patch(
            "zarvent_repuestos.web.app.authenticate_user",
            return_value={"id": 1, "username": "admin"},
        ):
            return self.client.post(
                "/", data={"username": "admin", "password": "admin123"}
            )

    def test_receipt_renders_200_with_preset_order(self):
        with patch(
            "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
            return_value=PRESET_ORDER,
        ) as mock_get:
            login_response = self._login()
            self.assertEqual(login_response.status_code, 302)

            response = self.client.get("/sales/receipt/2")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ZR-0001", response.data)
        self.assertIn(b"Filtro Demo", response.data)
        self.assertIn(b"Cliente Demo", response.data)
        mock_get.assert_called_once_with(2)

    def test_receipt_renders_with_no_items(self):
        empty_order = dict(PRESET_ORDER)
        empty_order["items"] = []
        empty_order["sales_order_id"] = 3

        with patch(
            "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
            return_value=empty_order,
        ):
            self._login()
            response = self.client.get("/sales/receipt/3")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cliente Demo", response.data)
        self.assertNotIn(b"ZR-0001", response.data)

    def test_receipt_returns_404_when_order_missing(self):
        with patch(
            "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
            return_value=None,
        ):
            self._login()
            response = self.client.get("/sales/receipt/999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
