"""CRUD and transactional operations for suppliers, purchase orders, and stock reception."""

import datetime
import mysql.connector
from typing import Any, Dict, List, Optional

from zarvent_repuestos.database.connection import get_database_connection


def _today_date() -> datetime.date:
    """Returns the current local date for header columns."""
    return datetime.date.today()


def _parse_iso_date(value: Optional[str]) -> Optional[datetime.date]:
    """Parses a YYYY-MM-DD string into a date object, or returns None."""
    if not value:
        return None
    return datetime.date.fromisoformat(value)


# --- SUPPLIER CRUD ---


def create_supplier(business_name: str, tax_id: str, phone: Optional[str] = None,
                    email: Optional[str] = None, address: Optional[str] = None) -> Optional[int]:
    """Inserts a supplier row and returns the new supplier_id, or None on failure."""
    if not business_name or not business_name.strip():
        raise ValueError("El nombre comercial del proveedor es obligatorio.")
    if not tax_id or not tax_id.strip():
        raise ValueError("El NIT del proveedor es obligatorio.")

    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = """
    INSERT INTO supplier (business_name, tax_id, phone, email, address, is_active)
    VALUES (%s, %s, %s, %s, %s, TRUE)
    """
    try:
        cursor.execute(sql, (business_name.strip(), tax_id.strip(), phone, email, address))
        conexion.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        conexion.rollback()
        print("❌ Error al crear proveedor:", err)
        return None
    finally:
        cursor.close()
        conexion.close()


def list_suppliers(active_only: bool = True) -> List[Dict[str, Any]]:
    """Returns suppliers ordered by business name. Optionally filters active only."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT supplier_id, business_name, tax_id, phone, email, address, is_active
    FROM supplier
    """
    if active_only:
        sql += " WHERE is_active = TRUE"
    sql += " ORDER BY business_name"
    rows: List[Dict[str, Any]] = []
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except mysql.connector.Error as err:
        print("❌ Error al listar proveedores:", err)
    finally:
        cursor.close()
        conexion.close()
    return rows


def get_supplier(supplier_id: int) -> Optional[Dict[str, Any]]:
    """Returns a single supplier by id, or None if not found."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT supplier_id, business_name, tax_id, phone, email, address, is_active
    FROM supplier
    WHERE supplier_id = %s
    """
    row = None
    try:
        cursor.execute(sql, (supplier_id,))
        row = cursor.fetchone()
    except mysql.connector.Error as err:
        print("❌ Error al obtener proveedor:", err)
    finally:
        cursor.close()
        conexion.close()
    return row


# --- PURCHASE ORDER CRUD ---


def create_purchase_order(supplier_id: int, expected_date: Optional[str],
                          items: List[Dict[str, Any]]) -> Optional[int]:
    """Creates a purchase order header plus its item lines in a single transaction.

    `items` format: [{"part_id": 1, "quantity_ordered": 5, "unit_cost": 12.50}]
    Returns the new purchase_order_id, or None on failure.
    """
    if not items:
        raise ValueError("La orden de compra debe tener al menos un ítem.")

    total_amount = 0.0
    parsed_items: List[Dict[str, Any]] = []
    for item in items:
        part_id = int(item["part_id"])
        quantity_ordered = int(item["quantity_ordered"])
        unit_cost = float(item["unit_cost"])

        if quantity_ordered <= 0:
            raise ValueError(
                f"La cantidad pedida del producto {part_id} debe ser mayor que cero."
            )
        if unit_cost < 0:
            raise ValueError(
                f"El costo unitario del producto {part_id} no puede ser negativo."
            )

        total_amount += quantity_ordered * unit_cost
        parsed_items.append({
            "part_id": part_id,
            "quantity_ordered": quantity_ordered,
            "unit_cost": unit_cost,
        })

    expected = _parse_iso_date(expected_date)
    order_date = _today_date()

    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql_header = """
    INSERT INTO purchase_order (supplier_id, order_date, expected_date, status, total_amount)
    VALUES (%s, %s, %s, %s, %s)
    """
    sql_item = """
    INSERT INTO purchase_order_item
        (purchase_order_id, part_id, quantity_ordered, quantity_received, unit_cost)
    VALUES (%s, %s, %s, 0, %s)
    """
    try:
        cursor.execute(sql_header, (
            supplier_id, order_date, expected, "Pending", round(total_amount, 2),
        ))
        purchase_order_id = cursor.lastrowid
        for parsed in parsed_items:
            cursor.execute(sql_item, (
                purchase_order_id,
                parsed["part_id"],
                parsed["quantity_ordered"],
                parsed["unit_cost"],
            ))
        conexion.commit()
        return purchase_order_id
    except (mysql.connector.Error, ValueError) as err:
        conexion.rollback()
        print("❌ Error al crear orden de compra:", err)
        raise
    finally:
        cursor.close()
        conexion.close()


def list_purchase_orders(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns purchase orders with their supplier name, optionally filtered by status."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT po.purchase_order_id, po.order_date, po.expected_date, po.status, po.total_amount,
           s.supplier_id, s.business_name, s.tax_id
    FROM purchase_order po
    JOIN supplier s ON po.supplier_id = s.supplier_id
    WHERE 1=1
    """
    params: List[Any] = []
    if status:
        sql += " AND po.status = %s"
        params.append(status)
    sql += " ORDER BY po.purchase_order_id DESC"

    rows: List[Dict[str, Any]] = []
    try:
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall()
    except mysql.connector.Error as err:
        print("❌ Error al listar órdenes de compra:", err)
    finally:
        cursor.close()
        conexion.close()
    return rows


def get_purchase_order_details(purchase_order_id: int) -> Optional[Dict[str, Any]]:
    """Returns the purchase order header, supplier info, and all its item lines."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql_header = """
    SELECT po.purchase_order_id, po.order_date, po.expected_date, po.status, po.total_amount,
           s.supplier_id, s.business_name, s.tax_id, s.phone, s.email, s.address
    FROM purchase_order po
    JOIN supplier s ON po.supplier_id = s.supplier_id
    WHERE po.purchase_order_id = %s
    """
    sql_items = """
    SELECT i.purchase_order_item_id, i.part_id, i.quantity_ordered, i.quantity_received,
           i.unit_cost, p.internal_code, p.name, p.brand
    FROM purchase_order_item i
    JOIN part p ON i.part_id = p.part_id
    WHERE i.purchase_order_id = %s
    ORDER BY i.purchase_order_item_id
    """
    try:
        cursor.execute(sql_header, (purchase_order_id,))
        order = cursor.fetchone()
        if not order:
            return None
        cursor.execute(sql_items, (purchase_order_id,))
        order["items"] = cursor.fetchall()
        return order
    except mysql.connector.Error as err:
        print("❌ Error al obtener detalles de orden de compra:", err)
        return None
    finally:
        cursor.close()
        conexion.close()


def receive_purchase_order(purchase_order_id: int,
                           received_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Updates quantity_received per line, increases inventory_stock, and recalculates status.

    `received_items` format: [{"purchase_order_item_id": 1, "quantity_received": 5}]
    The final value is cumulative (the absolute received count, not a delta).
    """
    if not received_items:
        raise ValueError("Debes indicar al menos una cantidad recibida.")

    conexion = get_database_connection()
    cursor = conexion.cursor()

    sql_lock_item = """
    SELECT purchase_order_item_id, part_id, quantity_ordered, quantity_received
    FROM purchase_order_item
    WHERE purchase_order_id = %s AND purchase_order_item_id = %s
    FOR UPDATE
    """
    sql_update_item = """
    UPDATE purchase_order_item
    SET quantity_received = %s
    WHERE purchase_order_item_id = %s
    """
    sql_increment_stock = """
    UPDATE inventory_stock
    SET quantity_on_hand = quantity_on_hand + %s
    WHERE part_id = %s
    """
    sql_count_full = """
    SELECT
        SUM(CASE WHEN quantity_received >= quantity_ordered THEN 1 ELSE 0 END) AS full_count,
        SUM(CASE WHEN quantity_received > 0 THEN 1 ELSE 0 END) AS any_count,
        COUNT(*) AS total_count
    FROM purchase_order_item
    WHERE purchase_order_id = %s
    """
    sql_update_header = """
    UPDATE purchase_order SET status = %s WHERE purchase_order_id = %s
    """

    try:
        for entry in received_items:
            item_id = int(entry["purchase_order_item_id"])
            new_received = int(entry["quantity_received"])

            cursor.execute(sql_lock_item, (purchase_order_id, item_id))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"La línea {item_id} no pertenece a la orden {purchase_order_id}.")

            current_received = int(row[3])
            quantity_ordered = int(row[2])
            part_id = int(row[1])

            if new_received < current_received:
                raise ValueError(
                    f"No puedes reducir la cantidad recibida de la línea {item_id} "
                    f"(actual: {current_received}, nuevo: {new_received})."
                )
            if new_received > quantity_ordered:
                raise ValueError(
                    f"La línea {item_id} no puede recibir {new_received} unidades; "
                    f"solo se pidieron {quantity_ordered}."
                )

            delta = new_received - current_received
            cursor.execute(sql_update_item, (new_received, item_id))
            if delta > 0:
                cursor.execute(sql_increment_stock, (delta, part_id))

        cursor.execute(sql_count_full, (purchase_order_id,))
        counts = cursor.fetchone()
        full_count = int(counts[0] or 0)
        any_count = int(counts[1] or 0)
        total_count = int(counts[2] or 0)

        if full_count == total_count and total_count > 0:
            new_status = "Received"
        elif any_count > 0:
            new_status = "Partially Received"
        else:
            new_status = "Pending"

        cursor.execute(sql_update_header, (new_status, purchase_order_id))
        conexion.commit()
        return get_purchase_order_details(purchase_order_id)
    except (mysql.connector.Error, ValueError) as err:
        conexion.rollback()
        print("❌ Error al recibir orden de compra:", err)
        raise
    finally:
        cursor.close()
        conexion.close()
