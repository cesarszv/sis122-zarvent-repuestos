"""CRUD operations for parts, categories, and inventory stock."""

import logging
import mysql.connector
from typing import List, Optional, Dict, Any

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.models.part import Part, PartCategory


logger = logging.getLogger(__name__)


# --- CATEGORY CRUD ---

def crear_categoria(name: str, description: str = None) -> bool:
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

def crear_producto(part: Part, initial_stock: int = 0, location: str = "Aisle 1") -> bool:
    """Creates a part and its initial stock in a single transaction."""
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
            part.status
        ))
        part_id = cursor.lastrowid

        # 2. Insert Stock
        cursor.execute(sql_stock, (part_id, location, initial_stock, 10))

        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al crear producto con stock: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def listar_productos(search: Optional[str] = None, category_id: Optional[int] = None,
                     brand: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists parts with their category name and stock details, applying filters."""
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

    params = []

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
