"""Tests for v1 part CRUD additions (RF-02, RF-04)."""

import unittest
from unittest.mock import MagicMock, patch

from zarvent_repuestos.constants import PartStatus
from zarvent_repuestos.crud.part_crud import (
    deactivate_part,
    list_low_stock,
    reactivate_part,
    update_part,
)


def _make_connection():
    """Returns a (mock_conn, mock_cursor) pair for `get_database_connection`."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class UpdatePartTest(unittest.TestCase):
    """v1: `update_part` issues a single UPDATE with the editable fields."""

    def test_update_part_emits_single_update_and_commits(self):
        mock_conn, mock_cursor = _make_connection()
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

        self.assertTrue(ok)
        self.assertEqual(mock_cursor.execute.call_count, 1)
        sql = mock_cursor.execute.call_args.args[0]
        self.assertIn("UPDATE part", sql)
        params = mock_cursor.execute.call_args.args[1]
        # params: name, brand, unit, sale_price, purchase_cost, warranty_days, status, part_id
        self.assertEqual(params, ("Filtro de Aire", "Bosch", "pcs", 150.0, 90.0, 30, PartStatus.ACTIVE, 42))
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_update_part_returns_false_when_no_rows_affected(self):
        mock_conn, mock_cursor = _make_connection()
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

        self.assertFalse(ok)

    def test_update_part_rolls_back_on_db_error(self):
        import mysql.connector
        mock_conn, mock_cursor = _make_connection()
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

        self.assertFalse(ok)
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()


class SoftDeletePartTest(unittest.TestCase):
    """v1: soft-delete via `part.status`."""

    def test_deactivate_part_sets_status_inactive(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 1

        with patch(
            "zarvent_repuestos.crud.part_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = deactivate_part(7)

        self.assertTrue(ok)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (PartStatus.INACTIVE, 7))

    def test_reactivate_part_sets_status_active(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 1

        with patch(
            "zarvent_repuestos.crud.part_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = reactivate_part(7)

        self.assertTrue(ok)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (PartStatus.ACTIVE, 7))

    def test_reactivate_missing_part_returns_false(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.rowcount = 0

        with patch(
            "zarvent_repuestos.crud.part_crud.get_database_connection",
            return_value=mock_conn,
        ):
            ok = reactivate_part(9999)

        self.assertFalse(ok)


class ListLowStockTest(unittest.TestCase):
    """v1: stock bajo via la vista `vw_low_stock_parts` con fallback a query inline."""

    def test_list_low_stock_uses_view_when_available(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchall.return_value = [
            {"internal_code": "ZR-1", "name": "Filtro", "brand": "Bosch",
             "quantity_on_hand": 2, "reorder_level": 10},
        ]

        with patch(
            "zarvent_repuestos.crud.part_crud.get_database_connection",
            return_value=mock_conn,
        ):
            rows = list_low_stock(limit=5)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["internal_code"], "ZR-1")
        sql = mock_cursor.execute.call_args.args[0]
        self.assertIn("vw_low_stock_parts", sql)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (5,))

    def test_list_low_stock_falls_back_to_inline_query_on_view_error(self):
        import mysql.connector
        mock_conn, mock_cursor = _make_connection()
        # First execute (view) fails, second execute (inline) succeeds.
        mock_cursor.execute.side_effect = [
            mysql.connector.Error("View missing"),
            None,
        ]
        mock_cursor.fetchall.return_value = [
            {"internal_code": "ZR-2", "name": "Bujía", "brand": "NGK",
             "quantity_on_hand": 1, "reorder_level": 5},
        ]

        with patch(
            "zarvent_repuestos.crud.part_crud.get_database_connection",
            return_value=mock_conn,
        ):
            rows = list_low_stock(limit=3)

        self.assertEqual(len(rows), 1)
        # Two execute calls: view (failed) + inline (succeeded).
        self.assertEqual(mock_cursor.execute.call_count, 2)
        second_sql = mock_cursor.execute.call_args_list[1].args[0]
        self.assertIn("FROM part p", second_sql)


if __name__ == "__main__":
    unittest.main()
