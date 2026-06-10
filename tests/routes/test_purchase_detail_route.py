"""Regression tests for ``/purchases/<id>`` that ensure the template
iterates ``order['items']`` correctly (dict-key access, not attribute
access, which would resolve to ``dict.items()`` and raise
``TypeError``).
"""

import datetime
from unittest.mock import patch


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


def test_purchase_detail_renders_200_with_preset_order(auth_client):
    order = _preset_order()
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value=order,
    ):
        response = auth_client.get("/purchases/1")

    assert response.status_code == 200
    assert b"ZR-0001" in response.data
    assert b"Filtro Demo" in response.data
    assert b"AutoPartes Demo" in response.data


def test_purchase_detail_renders_with_no_items(auth_client):
    order = _preset_order(items=[])
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value=order,
    ):
        response = auth_client.get("/purchases/2")

    assert response.status_code == 200
    assert b"AutoPartes Demo" in response.data
    assert b"ZR-0001" not in response.data


def test_purchase_detail_returns_404_when_order_missing(auth_client):
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value=None,
    ):
        response = auth_client.get("/purchases/999")

    assert response.status_code == 404
