"""Regression tests for ``/sales/receipt/<id>`` that ensure the
template iterates ``order['items']`` correctly (dict-key access, not
attribute access)."""

import datetime
from unittest.mock import patch


PRESET_ORDER = {
    "sales_order_id": 2,
    "order_date": datetime.date(2026, 6, 7),
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


def test_receipt_renders_200_with_preset_order(auth_client):
    with patch(
        "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
        return_value=PRESET_ORDER,
    ) as mock_get:
        response = auth_client.get("/sales/receipt/2")

    assert response.status_code == 200
    assert b"ZR-0001" in response.data
    assert b"Filtro Demo" in response.data
    assert b"Cliente Demo" in response.data
    mock_get.assert_called_once_with(2)


def test_receipt_renders_with_no_items(auth_client):
    empty_order = dict(PRESET_ORDER)
    empty_order["items"] = []
    empty_order["sales_order_id"] = 3

    with patch(
        "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
        return_value=empty_order,
    ):
        response = auth_client.get("/sales/receipt/3")

    assert response.status_code == 200
    assert b"Cliente Demo" in response.data
    assert b"ZR-0001" not in response.data


def test_receipt_returns_404_when_order_missing(auth_client):
    with patch(
        "zarvent_repuestos.crud.sales_crud.obtener_detalles_orden",
        return_value=None,
    ):
        response = auth_client.get("/sales/receipt/999")

    assert response.status_code == 404
