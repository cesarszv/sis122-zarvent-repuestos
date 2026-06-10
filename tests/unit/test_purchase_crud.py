"""Tests for purchase_crud operations with mocked database connections.

Covers:

- ``create_purchase_order``: input validation, header+item inserts in a
  single transaction, expected totals.
- ``create_supplier``: input validation.
- ``receive_purchase_order``: full/partial reception increments stock
  by the right delta and recomputes the header status; refuses
  over-reception and reducing the received quantity.
- ``cancel_purchase_order`` (v1): only operates on ``Pending`` orders,
  does not touch inventory, and raises on missing or wrong-status
  orders.
"""

from unittest.mock import MagicMock, patch

import pytest

from zarvent_repuestos.constants import PurchaseOrderStatus
from zarvent_repuestos.crud.purchase_crud import (
    cancel_purchase_order,
    create_purchase_order,
    create_supplier,
    receive_purchase_order,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stock_increment_calls(mock_cursor):
    """Returns the params tuple for every UPDATE inventory_stock call."""
    calls = []
    for call_ in mock_cursor.execute.call_args_list:
        sql = call_.args[0]
        if "UPDATE inventory_stock" in sql:
            calls.append(call_.args[1])
    return calls


def _header_status_update(mock_cursor):
    """Returns the params tuple for the final header UPDATE, or None."""
    for call_ in mock_cursor.execute.call_args_list:
        sql = call_.args[0]
        if sql.strip().upper().startswith("UPDATE PURCHASE_ORDER SET STATUS"):
            return call_.args[1]
    return None


# ---------------------------------------------------------------------------
# create_purchase_order - validation
# ---------------------------------------------------------------------------

def test_create_purchase_order_empty_items_raises_value_error_before_connection():
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
    ) as connect:
        with pytest.raises(ValueError):
            create_purchase_order(supplier_id=1, expected_date=None, items=[])

    connect.assert_not_called()


def test_create_purchase_order_zero_quantity_raises_value_error_before_connection():
    items = [{"part_id": 1, "quantity_ordered": 0, "unit_cost": 10.0}]

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
    ) as connect:
        with pytest.raises(ValueError):
            create_purchase_order(
                supplier_id=1, expected_date=None, items=items,
            )

    connect.assert_not_called()


def test_create_purchase_order_negative_unit_cost_raises_value_error_before_connection():
    items = [{"part_id": 1, "quantity_ordered": 2, "unit_cost": -1.0}]

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
    ) as connect:
        with pytest.raises(ValueError):
            create_purchase_order(
                supplier_id=1, expected_date=None, items=items,
            )

    connect.assert_not_called()


# ---------------------------------------------------------------------------
# create_purchase_order - happy path
# ---------------------------------------------------------------------------

def test_create_purchase_order_header_and_item_inserts_in_single_transaction():
    items = [
        {"part_id": 1, "quantity_ordered": 5, "unit_cost": 10.0},
        {"part_id": 2, "quantity_ordered": 2, "unit_cost": 25.0},
    ]
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 42
    mock_conn.cursor.return_value = mock_cursor

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = create_purchase_order(
            supplier_id=1,
            expected_date="2026-06-15",
            items=items,
        )

    assert result == 42
    statements = [call_.args[0] for call_ in mock_cursor.execute.call_args_list]
    assert any("INSERT INTO purchase_order" in s for s in statements)
    assert any("INSERT INTO purchase_order_item" in s for s in statements)
    assert mock_cursor.execute.call_count >= 3
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()

    header_params = mock_cursor.execute.call_args_list[0].args[1]
    assert header_params[0] == 1
    assert header_params[3] == "Pending"
    assert header_params[4] == 100.0


# ---------------------------------------------------------------------------
# create_supplier - validation
# ---------------------------------------------------------------------------

def test_create_supplier_empty_business_name_raises_value_error_before_connection():
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
    ) as connect:
        with pytest.raises(ValueError):
            create_supplier(business_name="", tax_id="123")

    connect.assert_not_called()


def test_create_supplier_empty_tax_id_raises_value_error_before_connection():
    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
    ) as connect:
        with pytest.raises(ValueError):
            create_supplier(business_name="Acme", tax_id="   ")

    connect.assert_not_called()


# ---------------------------------------------------------------------------
# receive_purchase_order
# ---------------------------------------------------------------------------

def _build_receive_connection(ordered, current_received,
                              full_count, any_count, total_count):
    """Builds a mocked connection with preset fetchone responses.

    The first fetchone returns the locked line (item_id, part_id,
    ordered, received); the second returns the status-counts tuple.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (101, 7, ordered, current_received),
        (full_count, any_count, total_count),
    ]
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def test_receive_purchase_order_full_reception_marks_received_and_increments_stock():
    mock_conn, mock_cursor = _build_receive_connection(
        ordered=5, current_received=0,
        full_count=1, any_count=1, total_count=1,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ), patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value={"purchase_order_id": 1, "status": "Received"},
    ):
        result = receive_purchase_order(
            purchase_order_id=1,
            received_items=[
                {"purchase_order_item_id": 101, "quantity_received": 5},
            ],
        )

    assert result == {"purchase_order_id": 1, "status": "Received"}
    assert _stock_increment_calls(mock_cursor) == [(5, 7)]
    assert _header_status_update(mock_cursor) == ("Received", 1)
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()


def test_receive_purchase_order_partial_reception_uses_partial_delta():
    mock_conn, mock_cursor = _build_receive_connection(
        ordered=5, current_received=0,
        full_count=0, any_count=1, total_count=1,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ), patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value={"purchase_order_id": 1, "status": "Partially Received"},
    ):
        result = receive_purchase_order(
            purchase_order_id=1,
            received_items=[
                {"purchase_order_item_id": 101, "quantity_received": 2},
            ],
        )

    assert result == {
        "purchase_order_id": 1, "status": "Partially Received",
    }
    assert _stock_increment_calls(mock_cursor) == [(2, 7)]
    assert _header_status_update(mock_cursor) == ("Partially Received", 1)
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()


def test_receive_purchase_order_reducing_received_is_rejected():
    mock_conn, mock_cursor = _build_receive_connection(
        ordered=5, current_received=3,
        full_count=0, any_count=0, total_count=0,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ):
        with pytest.raises(ValueError):
            receive_purchase_order(
                purchase_order_id=1,
                received_items=[
                    {"purchase_order_item_id": 101, "quantity_received": 1},
                ],
            )

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert _stock_increment_calls(mock_cursor) == []


def test_receive_purchase_order_over_receiving_is_rejected():
    mock_conn, mock_cursor = _build_receive_connection(
        ordered=5, current_received=0,
        full_count=0, any_count=0, total_count=0,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ):
        with pytest.raises(ValueError):
            receive_purchase_order(
                purchase_order_id=1,
                received_items=[
                    {"purchase_order_item_id": 101, "quantity_received": 6},
                ],
            )

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    assert _stock_increment_calls(mock_cursor) == []


# ---------------------------------------------------------------------------
# cancel_purchase_order (v1)
# ---------------------------------------------------------------------------

def _build_cancel_connection(current_status):
    """Builds a mocked connection for cancel_purchase_order tests.

    The first ``fetchone`` returns the current status of the order, or
    ``None`` if the order does not exist. The mock uses positional
    tuple rows because that is what the production code accesses.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    if current_status is None:
        mock_cursor.fetchone.return_value = None
    else:
        mock_cursor.fetchone.return_value = (current_status,)
    return mock_conn, mock_cursor


def test_cancel_purchase_order_marks_status_cancelled():
    mock_conn, mock_cursor = _build_cancel_connection(
        current_status=PurchaseOrderStatus.PENDING,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ), patch(
        "zarvent_repuestos.crud.purchase_crud.get_purchase_order_details",
        return_value={"purchase_order_id": 1, "status": "Cancelled"},
    ):
        result = cancel_purchase_order(purchase_order_id=1)

    assert result["status"] == "Cancelled"
    mock_conn.commit.assert_called_once()
    # The final UPDATE must set the header status to 'Cancelled'.
    update_calls = [
        call_ for call_ in mock_cursor.execute.call_args_list
        if "UPDATE purchase_order SET status" in call_.args[0]
    ]
    assert len(update_calls) == 1
    assert update_calls[0].args[1] == (
        PurchaseOrderStatus.CANCELLED, 1,
    )


@pytest.mark.parametrize("non_pending_status", [
    PurchaseOrderStatus.PARTIALLY_RECEIVED,
    PurchaseOrderStatus.RECEIVED,
    PurchaseOrderStatus.CANCELLED,
])
def test_cancel_purchase_order_non_pending_raises_value_error(non_pending_status):
    mock_conn, mock_cursor = _build_cancel_connection(
        current_status=non_pending_status,
    )

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ):
        with pytest.raises(ValueError):
            cancel_purchase_order(purchase_order_id=1)

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


def test_cancel_purchase_order_missing_order_returns_none():
    mock_conn, mock_cursor = _build_cancel_connection(current_status=None)

    with patch(
        "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = cancel_purchase_order(purchase_order_id=9999)

    assert result is None
    mock_conn.commit.assert_not_called()
