"""Tests for v1 customer CRUD additions (RF-01 soft-delete).

These tests use the ``mock_db_connection`` fixture from the root
conftest instead of defining their own ``_make_connection()`` helper.
"""

from unittest.mock import patch

import mysql.connector

from zarvent_repuestos.crud.customer_crud import (
    deactivate_customer,
    reactivate_customer,
)


def test_deactivate_customer_sets_is_active_false(mock_db_connection):
    """v1: `is_active` flag replaces the v0 hard-delete flow."""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = deactivate_customer(7)

    assert ok is True
    sql = mock_cursor.execute.call_args.args[0]
    assert "UPDATE customer" in sql
    assert "is_active" in sql
    params = mock_cursor.execute.call_args.args[1]
    assert params == (False, 7)
    mock_conn.commit.assert_called_once()


def test_reactivate_customer_sets_is_active_true(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = reactivate_customer(7)

    assert ok is True
    params = mock_cursor.execute.call_args.args[1]
    assert params == (True, 7)


def test_reactivate_missing_customer_returns_false(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = reactivate_customer(9999)

    assert ok is False


def test_deactivate_customer_rolls_back_on_db_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        ok = deactivate_customer(7)

    assert ok is False
    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
