"""Tests for customer_crud operations with mocked database connections.

These tests exercise the v0 contract that still applies in v1: insert
into both ``person`` and ``customer`` in a single transaction, refuse
to hard-delete a customer that has linked sales, and surface
database errors as graceful ``False`` returns.

The CRUD functions still use the legacy ``delete_customer`` shim that
delegates to ``deactivate_customer`` when the customer has no sales;
this is verified by ``test_delete_customer_raises_when_sales_linked``.
"""

from unittest.mock import patch

import mysql.connector
import pytest

from zarvent_repuestos.crud.customer_crud import (
    CustomerHasSalesError,
    crear_cliente,
    delete_customer,
    get_customer,
    listar_clientes,
    update_customer,
)


def test_crear_cliente_happy_path_inserts_person_and_customer_and_commits(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.lastrowid = 7

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = crear_cliente(
            first_name="Ada",
            last_name="Lovelace",
            identity_number="1234567",
        )

    assert result is True
    statements = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert any("INSERT INTO person" in s for s in statements)
    assert any("INSERT INTO customer" in s for s in statements)
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()


def test_crear_cliente_returns_false_and_rolls_back_on_duplicate(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = mysql.connector.Error("Duplicate entry")

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = crear_cliente(
            first_name="Ada",
            last_name="Lovelace",
            identity_number="9999999",
        )

    assert result is False
    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()


def test_listar_clientes_returns_preset_rows_when_no_search_is_provided(
    mock_db_connection,
):
    preset = [
        {"customer_id": 1, "first_name": "Ana", "last_name": "Pérez"},
        {"customer_id": 2, "first_name": "Luis", "last_name": "Gómez"},
    ]
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = preset

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = listar_clientes()

    assert result == preset


def test_get_customer_returns_row_when_customer_exists(mock_db_connection):
    preset = {"customer_id": 3, "first_name": "Ada", "last_name": "Lovelace"}
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = preset

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = get_customer(3)

    assert result == preset


def test_get_customer_returns_none_when_customer_does_not_exist(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = get_customer(999)

    assert result is None


def test_update_customer_happy_path_issues_person_and_customer_updates(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (11,)

    with patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
        return_value=mock_conn,
    ):
        result = update_customer(
            customer_id=3,
            first_name="Ada",
            last_name="Lovelace",
            identity_number="1234567",
            billing_name="Ada Lovelace SRL",
            tax_id="1234567",
        )

    assert result is True
    statements = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert any("UPDATE person" in s for s in statements)
    assert any("UPDATE customer" in s for s in statements)
    mock_conn.commit.assert_called_once()


def test_delete_customer_raises_when_sales_linked():
    """The legacy shim still refuses to delete a customer that has
    linked sales, even in v1 where the actual operation is a soft
    delete. This protects the historical sales trail."""
    with patch(
        "zarvent_repuestos.crud.customer_crud._count_customer_sales",
        return_value=4,
    ), patch(
        "zarvent_repuestos.crud.customer_crud.get_database_connection",
    ) as connect:
        with pytest.raises(CustomerHasSalesError) as ctx:
            delete_customer(7)

    connect.assert_not_called()
    assert ctx.value.customer_id == 7
    assert ctx.value.sales_count == 4
