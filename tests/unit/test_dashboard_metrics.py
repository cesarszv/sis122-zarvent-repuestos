"""Tests for dashboard metrics (RF-09) with mocked database connections.

The dashboard is composed of small per-metric helpers (``_count_pending``,
``_payments_by_method_today``) and an aggregator
(``obtener_metricas_dashboard``). The tests verify the helpers in
isolation and the aggregator's contract: the returned dict always
exposes the v1 keys and the list of payments is always complete (one
entry per known method).
"""

from unittest.mock import patch

import mysql.connector

from zarvent_repuestos.constants import PAYMENT_METHODS, PurchaseOrderStatus
from zarvent_repuestos.crud.sales_crud import (
    _count_pending_purchase_orders,
    _payments_by_method_today,
    obtener_metricas_dashboard,
)


# --- _count_pending_purchase_orders -----------------------------------------

def test_count_pending_purchase_orders_returns_count_from_query(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (4,)

    with patch(
        "zarvent_repuestos.crud.sales_crud.get_database_connection",
        return_value=mock_conn,
    ):
        count = _count_pending_purchase_orders()

    assert count == 4
    params = mock_cursor.execute.call_args.args[1]
    assert params == (PurchaseOrderStatus.PENDING,)


def test_count_pending_purchase_orders_returns_zero_on_db_error(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

    with patch(
        "zarvent_repuestos.crud.sales_crud.get_database_connection",
        return_value=mock_conn,
    ):
        count = _count_pending_purchase_orders()

    assert count == 0


# --- _payments_by_method_today ----------------------------------------------

def test_payments_by_method_returns_all_methods_even_when_some_have_no_payments(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
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
    # The result must include every known payment method, even when the
    # database returned no rows for some of them.
    assert set(methods) == set(PAYMENT_METHODS)
    for method in PAYMENT_METHODS:
        assert method in methods
    # Methods absent from the mock data must be filled with zero totals.
    for row in rows:
        if row["method"] not in ("Efectivo", "Tarjeta de Crédito"):
            assert row["total_amount"] == 0.0
            assert row["payments_count"] == 0


def test_payments_by_method_returns_zero_rows_for_each_method_on_db_error(
    mock_db_connection,
):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.execute.side_effect = mysql.connector.Error("DB boom")

    with patch(
        "zarvent_repuestos.crud.sales_crud.get_database_connection",
        return_value=mock_conn,
    ):
        rows = _payments_by_method_today()

    # On error we still return one entry per known method, with zero.
    assert len(rows) == len(PAYMENT_METHODS)
    for row in rows:
        assert row["total_amount"] == 0.0
        assert row["payments_count"] == 0


# --- obtener_metricas_dashboard (aggregator contract) -----------------------

def test_obtener_metricas_dashboard_includes_v1_keys(mock_db_connection):
    """The metrics dict must include every key rendered by the
    dashboard template, even when the per-helper functions are stubbed
    out. We patch the helpers to keep the test hermetic."""
    fake_payments = [
        {"method": "Efectivo", "total_amount": 0.0, "payments_count": 0},
    ]

    def fake_payments_by_method():
        return fake_payments

    def fake_pending_count():
        return 0

    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []

    with patch(
        "zarvent_repuestos.crud.sales_crud._payments_by_method_today",
        fake_payments_by_method,
    ), patch(
        "zarvent_repuestos.crud.sales_crud._count_pending_purchase_orders",
        fake_pending_count,
    ), patch(
        "zarvent_repuestos.crud.sales_crud.get_database_connection",
        return_value=mock_conn,
    ):
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
        assert key in metrics
    assert isinstance(metrics["payments_by_method"], list)
    assert metrics["pending_purchase_count"] == 0
    # today_sales_amount must be a number >= 0 even when the DB returns
    # no rows.
    assert isinstance(metrics["today_sales_amount"], float)
    assert metrics["today_sales_amount"] >= 0.0
