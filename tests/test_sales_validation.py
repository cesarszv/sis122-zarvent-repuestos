"""Validation tests for sales order creation."""

import unittest
from unittest.mock import patch

from zarvent_repuestos.crud.sales_crud import crear_orden_venta


class SalesValidationTest(unittest.TestCase):
    def test_invalid_quantity_is_rejected_before_database_connection(self):
        items = [{"part_id": 1, "quantity": -2, "unit_price": 10.0}]

        with patch("zarvent_repuestos.crud.sales_crud.get_database_connection") as connect:
            with self.assertRaises(ValueError):
                crear_orden_venta(customer_id=1, items=items, payment_method="Efectivo")

        connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
