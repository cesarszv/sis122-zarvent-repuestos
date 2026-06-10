"""Tests for v1 part CRUD additions (RF-02, RF-04).

Covers:
- ``update_part``: emits a single UPDATE with the editable fields and
  rolls back on DB errors.
- Soft-delete via ``part.status`` (``deactivate_part`` /
  ``reactivate_part``).
- ``list_low_stock`` prefers the academic view
  ``vw_low_stock_parts`` and falls back to the inline query when the
  view is missing.
"""

from unittest.mock import patch

import mysql.connector

from zarvent_repuestos.constants import PartStatus
from zarvent_repuestos.crud.part_crud import (
    deactivate_part,
    list_low_stock,
    reactivate_part,
    update_part,
)


# --- update_part -------------------------------------------------------------

def test_update_part_emits_single_update_and_commits(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = update_part(
            part_id=42,
            name="Filtro de Aire",
            brand="Bosch",
            unit="pcs",
            sale_price=150.0,
            purchase_cost=90.0,
            warranty_days=30,
            status=PartStatus.ACTIVE,
        )

    assert ok is True
    assert mock_cursor.execute.call_count == 1
    sql = mock_cursor.execute.call_args.args[0]
    assert "UPDATE part" in sql
    params = mock_cursor.execute.call_args.args[1]
    # params: name, brand, unit, sale_price, purchase_cost, warranty_days,
    # status, part_id
    assert params == (
        "Filtro de Aire", "Bosch", "pcs", 150.0, 90.0, 30,
        PartStatus.ACTIVE, 42,
    )
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()


def test_update_part_returns_false_when_no_rows_affected(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = update_part(
            part_id=9999,
            name="X",
            brand=None,
            unit="pcs",
            sale_price=10.0,
            purchase_cost=5.0,
            warranty_days=0,
            status=PartStatus.ACTIVE,
        )

    assert ok is False


def test_update_part_rolls_back_on_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = update_part(
            part_id=1,
            name="X",
            brand=None,
            unit="pcs",
            sale_price=10.0,
            purchase_cost=5.0,
            warranty_days=0,
            status=PartStatus.ACTIVE,
        )

    assert ok is False
    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


# --- Soft delete (part.status) ----------------------------------------------

def test_deactivate_part_sets_status_inactive(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = deactivate_part(7)

    assert ok is True
    params = mock_cursor.execute.call_args.args[1]
    assert params == (PartStatus.INACTIVE, 7)


def test_reactivate_part_sets_status_active(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = reactivate_part(7)

    assert ok is True
    params = mock_cursor.execute.call_args.args[1]
    assert params == (PartStatus.ACTIVE, 7)


def test_reactivate_missing_part_returns_false(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = reactivate_part(9999)

    assert ok is False


# --- list_low_stock (view with fallback) ------------------------------------

def test_list_low_stock_uses_view_when_available(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {
            "internal_code": "ZR-1", "name": "Filtro", "brand": "Bosch",
            "quantity_on_hand": 2, "reorder_level": 10,
        },
    ]

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        rows = list_low_stock(limit=5)

    assert len(rows) == 1
    assert rows[0]["internal_code"] == "ZR-1"
    sql = mock_cursor.execute.call_args.args[0]
    assert "vw_low_stock_parts" in sql
    params = mock_cursor.execute.call_args.args[1]
    assert params == (5,)


def test_list_low_stock_falls_back_to_inline_query_on_view_error(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    # First execute (view) fails, second execute (inline) succeeds.
    mock_cursor.execute.side_effect = [
        mysql.connector.Error("View missing"),
        None,
    ]
    mock_cursor.fetchall.return_value = [
        {
            "internal_code": "ZR-2", "name": "Bujía", "brand": "NGK",
            "quantity_on_hand": 1, "reorder_level": 5,
        },
    ]

    with patch(
        "zarvent_repuestos.crud.part_crud.get_database_connection",
        return_value=mock_conn,
    ):
        rows = list_low_stock(limit=3)

    assert len(rows) == 1
    # Two execute calls: view (failed) + inline (succeeded).
    assert mock_cursor.execute.call_count == 2
    second_sql = mock_cursor.execute.call_args_list[1].args[0]
    assert "FROM part p" in second_sql
