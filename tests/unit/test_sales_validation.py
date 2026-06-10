"""Validation tests for sales order creation.

These tests assert that invalid input is rejected before the CRUD
opens a database transaction. They use ``pytest.raises`` to capture
the expected ``ValueError``.
"""

from unittest.mock import patch

import pytest

from zarvent_repuestos.crud.sales_crud import crear_orden_venta


def test_invalid_quantity_is_rejected_before_database_connection():
    items = [{"part_id": 1, "quantity": -2, "unit_price": 10.0}]

    with patch(
        "zarvent_repuestos.crud.sales_crud.get_database_connection"
    ) as connect:
        with pytest.raises(ValueError):
            crear_orden_venta(
                customer_id=1, items=items, payment_method="Efectivo",
            )

    connect.assert_not_called()
