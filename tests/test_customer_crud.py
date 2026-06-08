"""Tests for customer_crud operations with mocked database connections."""

import unittest
from unittest.mock import MagicMock, patch

import mysql.connector

from zarvent_repuestos.crud.customer_crud import (
    CustomerHasSalesError,
    crear_cliente,
    delete_customer,
    get_customer,
    listar_clientes,
    update_customer,
)


def _make_connection():
    """Builds a mocked MySQL connection with a single cursor."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class CrearClienteTest(unittest.TestCase):
    def test_happy_path_inserts_person_and_customer_and_commits(self):
        mock_conn, mock_cursor = _make_connection()
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

        self.assertTrue(result)
        statements = [call.args[0] for call in mock_cursor.execute.call_args_list]
        self.assertTrue(any("INSERT INTO person" in s for s in statements))
        self.assertTrue(any("INSERT INTO customer" in s for s in statements))
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_returns_false_and_rolls_back_when_db_raises_duplicate(self):
        mock_conn, mock_cursor = _make_connection()
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

        self.assertFalse(result)
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()


class ListarClientesTest(unittest.TestCase):
    def test_returns_preset_rows_when_no_search_is_provided(self):
        preset = [
            {"customer_id": 1, "first_name": "Ana", "last_name": "Pérez"},
            {"customer_id": 2, "first_name": "Luis", "last_name": "Gómez"},
        ]
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchall.return_value = preset

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            result = listar_clientes()

        self.assertEqual(result, preset)


class GetCustomerTest(unittest.TestCase):
    def test_returns_row_when_customer_exists(self):
        preset = {"customer_id": 3, "first_name": "Ada", "last_name": "Lovelace"}
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchone.return_value = preset

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            result = get_customer(3)

        self.assertEqual(result, preset)

    def test_returns_none_when_customer_does_not_exist(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchone.return_value = None

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            result = get_customer(999)

        self.assertIsNone(result)


class UpdateCustomerTest(unittest.TestCase):
    def test_happy_path_issues_person_and_customer_updates(self):
        mock_conn, mock_cursor = _make_connection()
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

        self.assertTrue(result)
        statements = [call.args[0] for call in mock_cursor.execute.call_args_list]
        self.assertTrue(any("UPDATE person" in s for s in statements))
        self.assertTrue(any("UPDATE customer" in s for s in statements))
        mock_conn.commit.assert_called_once()


class DeleteCustomerTest(unittest.TestCase):
    def test_raises_customer_has_sales_error_when_sales_count_is_positive(self):
        with patch(
            "zarvent_repuestos.crud.customer_crud._count_customer_sales",
            return_value=4,
        ), patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(CustomerHasSalesError) as ctx:
                delete_customer(7)

        connect.assert_not_called()
        self.assertEqual(ctx.exception.customer_id, 7)
        self.assertEqual(ctx.exception.sales_count, 4)


if __name__ == "__main__":
    unittest.main()
