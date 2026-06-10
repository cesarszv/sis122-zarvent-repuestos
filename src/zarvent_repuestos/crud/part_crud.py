"""CRUD operations for parts, categories, and inventory stock (RF-02, RF-04).

v1 refactor: completes the CRUD with `get_part`, `update_part`,
`deactivate_part`, `reactivate_part` (soft-delete via `part.status`) and
exposes `create_category` so the UI can manage categories too. The `list`
endpoints now accept a `status_filter` and the low-stock listing prefers the
`vw_low_stock_parts` view, falling back to an inline query when the view is
missing (e.g. permission-restricted MySQL user).
"""

import logging
import mysql.connector
from typing import List, Optional, Dict, Any

from zarvent_repuestos.constants import PartStatus
from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.models.part import Part, PartCategory


logger = logging.getLogger(__name__)


# --- CATEGORY CRUD ---

def crear_categoria(name: str, description: Optional[str] = None) -> bool:
    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = "INSERT INTO part_category (name, description) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (name, description))
        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al crear categoría: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def listar_categorias() -> List[PartCategory]:
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = "SELECT part_category_id, name, description FROM part_category ORDER BY name"
    categories = []
    try:
        cursor.execute(sql)
        for row in cursor.fetchall():
            categories.append(PartCategory(
                part_category_id=row["part_category_id"],
                name=row["name"],
                description=row["description"]
            ))
    except mysql.connector.Error as err:
        logger.error("Error al listar categorías: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return categories


# --- PART CRUD ---

def crear_producto(part: Part, initial_stock: int = 0, location: str = "Aisle 1",
                   reorder_level: int = 10) -> bool:
    """Creates a part and its initial stock in a single transaction.

    v1: caller now controls `reorder_level` (the v0 hardcoded 10 is gone).
    """
    conexion = get_database_connection()
    cursor = conexion.cursor()

    sql_part = """
    INSERT INTO part (part_category_id, internal_code, oem_code, name, brand, unit, sale_price, purchase_cost, warranty_days, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    sql_stock = """
    INSERT INTO inventory_stock (part_id, location_name, quantity_on_hand, reorder_level)
    VALUES (%s, %s, %s, %s)
    """

    try:
        # 1. Insert Part
        cursor.execute(sql_part, (
            part.part_category_id,
            part.internal_code,
            part.oem_code,
            part.name,
            part.brand,
            part.unit,
            part.sale_price,
            part.purchase_cost,
            part.warranty_days,
            part.status,
        ))
        part_id = cursor.lastrowid

        # 2. Insert Stock
        cursor.execute(sql_stock, (part_id, location, initial_stock, reorder_level))

        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al crear producto con stock: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def get_part(part_id: int) -> Optional[Dict[str, Any]]:
    """Returns a single part (joined with category and stock) or None."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    sql = """
    SELECT p.part_id, p.part_category_id, p.internal_code, p.oem_code, p.name,
           p.brand, p.unit, p.sale_price, p.purchase_cost, p.warranty_days, p.status,
           c.name AS category_name,
           s.quantity_on_hand, s.location_name, s.reorder_level
    FROM part p
    JOIN part_category c ON p.part_category_id = c.part_category_id
    LEFT JOIN inventory_stock s ON p.part_id = s.part_id
    WHERE p.part_id = %s
    """
    row = None
    try:
        cursor.execute(sql, (part_id,))
        row = cursor.fetchone()
    except mysql.connector.Error as err:
        logger.error("Error al obtener repuesto: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return row


def listar_productos(search: Optional[str] = None, category_id: Optional[int] = None,
                     brand: Optional[str] = None,
                     status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists parts with their category name and stock details, applying filters.

    v1: defaults to active parts. Use `status_filter=PartStatus.INACTIVE` or
    `PartStatus.ALL` to override.
    """
    if status_filter is None:
        status_filter = PartStatus.DEFAULT
    if status_filter not in PartStatus.ALL:
        status_filter = PartStatus.DEFAULT

    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT p.part_id, p.part_category_id, p.internal_code, p.oem_code, p.name,
           p.brand, p.unit, p.sale_price, p.purchase_cost, p.warranty_days, p.status,
           c.name AS category_name,
           s.quantity_on_hand, s.location_name, s.reorder_level
    FROM part p
    JOIN part_category c ON p.part_category_id = c.part_category_id
    LEFT JOIN inventory_stock s ON p.part_id = s.part_id
    WHERE 1=1
    """

    params: list[Any] = []

    if status_filter == PartStatus.ACTIVE:
        sql += " AND p.status = %s"
        params.append(PartStatus.ACTIVE)
    elif status_filter == PartStatus.INACTIVE:
        sql += " AND p.status = %s"
        params.append(PartStatus.INACTIVE)

    if search:
        search_wild = f"%{search}%"
        sql += " AND (p.internal_code LIKE %s OR p.oem_code LIKE %s OR p.name LIKE %s OR p.brand LIKE %s)"
        params.extend([search_wild, search_wild, search_wild, search_wild])

    if category_id:
        sql += " AND p.part_category_id = %s"
        params.append(category_id)

    if brand:
        sql += " AND p.brand = %s"
        params.append(brand)

    sql += " ORDER BY p.internal_code"

    products = []
    try:
        cursor.execute(sql, tuple(params))
        products = cursor.fetchall()
    except mysql.connector.Error as err:
        logger.error("Error al buscar productos: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return products


def update_part(part_id: int, name: str, brand: Optional[str], unit: str,
                sale_price: float, purchase_cost: float, warranty_days: int,
                status: str) -> bool:
    """Updates the editable fields of a part in a single transaction.

    `internal_code` and `part_category_id` are NOT editable in v1 to keep the
    PK/FK constraints and historical sales references stable.
    """
    conexion = get_database_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            UPDATE part
            SET name = %s, brand = %s, unit = %s, sale_price = %s,
                purchase_cost = %s, warranty_days = %s, status = %s
            WHERE part_id = %s
            """,
            (name, brand, unit, sale_price, purchase_cost, warranty_days, status, part_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al actualizar repuesto: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def set_part_status(part_id: int, status: str) -> bool:
    """Soft-activates or soft-deactivates a part via `part.status`.

    Used by `deactivate_part` and `reactivate_part`. Refuses invalid status
    values to keep the column consistent.
    """
    if status not in PartStatus.ALL:
        return False
    conexion = get_database_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE part SET status = %s WHERE part_id = %s",
            (status, part_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al cambiar status de repuesto: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def deactivate_part(part_id: int) -> bool:
    """Soft-deletes a part (status='inactive'). Historical sales keep their FK."""
    return set_part_status(part_id, PartStatus.INACTIVE)


def reactivate_part(part_id: int) -> bool:
    """Re-activates a previously soft-deleted part."""
    return set_part_status(part_id, PartStatus.ACTIVE)


def list_low_stock(limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the top-N lowest-stock parts. Uses the academic view when present.

    Falls back to the equivalent inline query when `vw_low_stock_parts` is not
    accessible (e.g. permission-restricted MySQL user).
    """
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)
    rows: list[Dict[str, Any]] = []
    try:
        try:
            cursor.execute(
                "SELECT internal_code, name, brand, quantity_on_hand, reorder_level "
                "FROM vw_low_stock_parts LIMIT %s",
                (limit,),
            )
        except mysql.connector.Error:
            # View missing or not accessible. Fall back to the inline query.
            cursor.execute(
                """
                SELECT p.internal_code, p.name, p.brand,
                       s.quantity_on_hand, s.reorder_level
                FROM part p
                JOIN inventory_stock s ON p.part_id = s.part_id
                WHERE s.quantity_on_hand <= s.reorder_level
                ORDER BY s.quantity_on_hand ASC
                LIMIT %s
                """,
                (limit,),
            )
        rows = cursor.fetchall()
    except mysql.connector.Error as err:
        logger.error("Error al listar repuestos con stock bajo: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return rows


def obtener_marcas() -> List[str]:
    """Retrieves all distinct brand names from the parts catalog."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    sql = "SELECT DISTINCT brand FROM part WHERE brand IS NOT NULL AND brand != '' ORDER BY brand"
    brands = []
    try:
        cursor.execute(sql)
        brands = [row[0] for row in cursor.fetchall()]
    except mysql.connector.Error as err:
        logger.error("Error al obtener marcas: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return brands
