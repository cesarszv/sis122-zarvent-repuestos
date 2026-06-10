"""Tests for v1 customer CRUD additions (RF-01 soft-delete)."""

import unittest
from unittest.mock import MagicMock, patch

from zarvent_repuestos.crud.customer_crud import (
    deactivate_customer,
    reactivate_customer,
)


def _make_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class SoftDeleteCustomerTest(unittest.TestCase):
    """v1: `is_active` flag replaces the v0 hard-delete flow."""

    def test_deactivate_customer_sets_is_active_false(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 1

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = deactivate_customer(7)

        self.assertTrue(ok)
        sql = mock_cursor.execute.call_args.args[0]
        self.assertIn("UPDATE customer", sql)
        self.assertIn("is_active", sql)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (False, 7))
        mock_conn.commit.assert_called_once()

    def test_reactivate_customer_sets_is_active_true(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 1

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = reactivate_customer(7)

        self.assertTrue(ok)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (True, 7))

    def test_reactivate_missing_customer_returns_false(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 0

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = reactivate_customer(9999)

        self.assertFalse(ok)

    def test_deactivate_customer_rolls_back_on_db_error(self):
        import mysql.connector
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

        with patch(
            "zarvent_repuestos.crud.customer_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = deactivate_customer(7)

        self.assertFalse(ok)
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
