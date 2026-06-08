"""Tests for purchase_crud operations with mocked database connections."""

import unittest
from unittest.mock import MagicMock, patch

from zarvent_repuestos.crud.purchase_crud import (
    create_purchase_order,
    create_supplier,
    receive_purchase_order,
)


def _stock_increment_calls(mock_cursor):
    """Returns the params tuple for every UPDATE inventory_stock call."""
    calls = []
    for call in mock_cursor.execute.call_args_list:
        sql = call.args[0]
        if "UPDATE inventory_stock" in sql:
            calls.append(call.args[1])
    return calls


def _header_status_update(mock_cursor):
    """Returns the params tuple for the final header UPDATE, or None."""
    for call in mock_cursor.execute.call_args_list:
        sql = call.args[0]
        if sql.strip().upper().startswith("UPDATE PURCHASE_ORDER SET STATUS"):
            return call.args[1]
    return None


class CreatePurchaseOrderValidationTest(unittest.TestCase):
    def test_empty_items_raises_value_error_before_connection(self):
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(ValueError):
                create_purchase_order(supplier_id=1, expected_date=None, items=[])

        connect.assert_not_called()

    def test_zero_quantity_raises_value_error_before_connection(self):
        items = [{"part_id": 1, "quantity_ordered": 0, "unit_cost": 10.0}]

        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(ValueError):
                create_purchase_order(
                    supplier_id=1, expected_date=None, items=items,
                )

        connect.assert_not_called()

    def test_negative_unit_cost_raises_value_error_before_connection(self):
        items = [{"part_id": 1, "quantity_ordered": 2, "unit_cost": -1.0}]

        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(ValueError):
                create_purchase_order(
                    supplier_id=1, expected_date=None, items=items,
                )

        connect.assert_not_called()


class CreatePurchaseOrderHappyPathTest(unittest.TestCase):
    def test_header_and_item_inserts_happen_in_a_single_transaction(self):
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

        self.assertEqual(result, 42)
        statements = [call.args[0] for call in mock_cursor.execute.call_args_list]
        self.assertTrue(any("INSERT INTO purchase_order" in s for s in statements))
        self.assertTrue(any("INSERT INTO purchase_order_item" in s for s in statements))
        self.assertGreaterEqual(mock_cursor.execute.call_count, 3)
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

        header_params = mock_cursor.execute.call_args_list[0].args[1]
        self.assertEqual(header_params[0], 1)
        self.assertEqual(header_params[3], "Pending")
        self.assertEqual(header_params[4], 100.0)


class CreateSupplierValidationTest(unittest.TestCase):
    def test_empty_business_name_raises_value_error_before_connection(self):
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(ValueError):
                create_supplier(business_name="", tax_id="123")

        connect.assert_not_called()

    def test_empty_tax_id_raises_value_error_before_connection(self):
        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
        ) as connect:
            with self.assertRaises(ValueError):
                create_supplier(business_name="Acme", tax_id="   ")

        connect.assert_not_called()


class ReceivePurchaseOrderTest(unittest.TestCase):
    def _build_connection(self, ordered, current_received, full_count, any_count, total_count):
        """Builds a mocked connection with preset fetchone responses."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            (101, 7, ordered, current_received),
            (full_count, any_count, total_count),
        ]
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    def test_full_reception_marks_header_received_and_increments_stock_by_delta(self):
        mock_conn, mock_cursor = self._build_connection(
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

        self.assertEqual(result, {"purchase_order_id": 1, "status": "Received"})
        self.assertEqual(_stock_increment_calls(mock_cursor), [(5, 7)])
        self.assertEqual(_header_status_update(mock_cursor), ("Received", 1))
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_partial_reception_marks_header_partially_received_and_uses_partial_delta(self):
        mock_conn, mock_cursor = self._build_connection(
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

        self.assertEqual(
            result,
            {"purchase_order_id": 1, "status": "Partially Received"},
        )
        self.assertEqual(_stock_increment_calls(mock_cursor), [(2, 7)])
        self.assertEqual(
            _header_status_update(mock_cursor),
            ("Partially Received", 1),
        )
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()

    def test_reducing_received_is_rejected_with_value_error(self):
        mock_conn, mock_cursor = self._build_connection(
            ordered=5, current_received=3,
            full_count=0, any_count=0, total_count=0,
        )

        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
            return_value=mock_conn,
        ):
            with self.assertRaises(ValueError):
                receive_purchase_order(
                    purchase_order_id=1,
                    received_items=[
                        {"purchase_order_item_id": 101, "quantity_received": 1},
                    ],
                )

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        self.assertEqual(_stock_increment_calls(mock_cursor), [])

    def test_over_receiving_is_rejected_with_value_error(self):
        mock_conn, mock_cursor = self._build_connection(
            ordered=5, current_received=0,
            full_count=0, any_count=0, total_count=0,
        )

        with patch(
            "zarvent_repuestos.crud.purchase_crud.get_database_connection",
            return_value=mock_conn,
        ):
            with self.assertRaises(ValueError):
                receive_purchase_order(
                    purchase_order_id=1,
                    received_items=[
                        {"purchase_order_item_id": 101, "quantity_received": 6},
                    ],
                )

        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
        self.assertEqual(_stock_increment_calls(mock_cursor), [])


if __name__ == "__main__":
    unittest.main()
