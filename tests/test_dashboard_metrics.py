"""Tests for v1 dashboard metrics (RF-09)."""

import unittest
from unittest.mock import MagicMock, patch

from zarvent_repuestos.constants import PAYMENT_METHODS, PurchaseOrderStatus
from zarvent_repuestos.crud.sales_crud import (
    _count_pending_purchase_orders,
    _payments_by_method_today,
    obtener_metricas_dashboard,
)


def _make_connection():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class PendingPurchaseCountTest(unittest.TestCase):
    """v1: dashboard surfaces the count of `Pending` purchase orders."""

    def test_returns_count_from_query(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchone.return_value = (4,)

        with patch(
            "zarvent_repuestos.crud.sales_crud.get_database_connection",
            return_value=mock_conn,
        ):
            count = _count_pending_purchase_orders()

        self.assertEqual(count, 4)
        params = mock_cursor.execute.call_args.args[1]
        self.assertEqual(params, (PurchaseOrderStatus.PENDING,))

    def test_returns_zero_on_db_error(self):
        import mysql.connector
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

        with patch(
            "zarvent_repuestos.crud.sales_crud.get_database_connection",
            return_value=mock_conn,
        ):
            count = _count_pending_purchase_orders()

        self.assertEqual(count, 0)


class PaymentsByMethodTest(unittest.TestCase):
    """v1: dashboard exposes payments aggregated by method for today."""

    def test_returns_all_methods_even_when_some_have_no_payments(self):
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.fetchall.return_value = [
            {"method": "Efectivo", "total_amount": 100.0, "payments_count": 2},
            {"method": "Tarjeta de Crédito", "total_amount": 50.0, "payments_count": 1},
        ]

        with patch(
            "zarvent_repuestos.crud.sales_crud.get_database_connection",
            return_value=mock_conn,
        ):
            rows = _payments_by_method_today()

        methods = [r["method"] for r in rows]
        self.assertEqual(set(methods), set(PAYMENT_METHODS))
        # Methods without payments must be present with zero totals.
        for method in PAYMENT_METHODS:
            self.assertIn(method, methods)
        # Methods not in mock data must show zero.
        for row in rows:
            if row["method"] not in ("Efectivo", "Tarjeta de Crédito"):
                self.assertEqual(row["total_amount"], 0.0)
                self.assertEqual(row["payments_count"], 0)

    def test_returns_empty_list_on_db_error(self):
        import mysql.connector
        mock_conn, mock_cursor = _make_connection()
        mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

        with patch(
            "zarvent_repuestos.crud.sales_crud.get_database_connection",
            return_value=mock_conn,
        ):
            rows = _payments_by_method_today()

        # On error we still return one entry per known method, with zero.
        self.assertEqual(len(rows), len(PAYMENT_METHODS))
        for row in rows:
            self.assertEqual(row["total_amount"], 0.0)
            self.assertEqual(row["payments_count"], 0)


class DashboardMetricsStructureTest(unittest.TestCase):
    """v1: `obtener_metricas_dashboard` returns the new keys."""

    def test_metrics_dict_includes_new_keys(self):
        # Patch the helpers to keep the test hermetic. The metrics dict must
        # be returned with all the v1 keys regardless of DB state.
        fake_payments = [
            {"method": "Efectivo", "total_amount": 0.0, "payments_count": 0},
        ]

        def fake_payments_by_method():
            return fake_payments

        def fake_pending_count():
            return 0

        with patch(
            "zarvent_repuestos.crud.sales_crud._payments_by_method_today",
            fake_payments_by_method,
        ), patch(
            "zarvent_repuestos.crud.sales_crud._count_pending_purchase_orders",
            fake_pending_count,
        ), patch(
            "zarvent_repuestos.crud.sales_crud.get_database_connection"
        ) as connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_cursor.fetchall.return_value = []
            connect.return_value = mock_conn

            metrics = obtener_metricas_dashboard()

        for key in (
            "today_sales_amount",
            "categories_count",
            "low_stock_count",
            "low_stock_items",
            "total_orders_count",
            "recent_orders",
            "pending_purchase_count",
            "payments_by_method",
        ):
            self.assertIn(key, metrics)
        # payments_by_method is always a list.
        self.assertIsInstance(metrics["payments_by_method"], list)
        # All default values are populated.
        self.assertEqual(metrics["pending_purchase_count"], 0)
        # today_sales_amount is a number (>= 0) when the DB has seed data.
        self.assertIsInstance(metrics["today_sales_amount"], float)
        self.assertGreaterEqual(metrics["today_sales_amount"], 0.0)


if __name__ == "__main__":
    unittest.main()
