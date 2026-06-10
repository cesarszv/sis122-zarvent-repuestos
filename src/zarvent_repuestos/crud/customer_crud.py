"""CRUD operations for Customers and Persons (RF-01).

Uses soft-delete via `customer.is_active`. Search matches first_name,
last_name, identity_number, tax_id, billing_name, and phone.
"""

import logging
import mysql.connector
from typing import Any, Dict, List, Optional

from zarvent_repuestos.constants import CustomerActiveFilter
from zarvent_repuestos.database.connection import get_database_connection


logger = logging.getLogger(__name__)


# Los tests importan esta excepcion para verificar que el pre-check
# rechaza la operacion cuando el cliente tiene ventas.
class CustomerHasSalesError(Exception):
    """Raised when a customer cannot be soft-deleted because sales orders protect them."""

    def __init__(self, customer_id: int, sales_count: int) -> None:
        self.customer_id = customer_id
        self.sales_count = sales_count
        message = (
            f"No se puede eliminar el cliente #{customer_id}: "
            f"tiene {sales_count} venta(s) registrada(s)."
        )
        super().__init__(message)


def _count_customer_sales(customer_id: int) -> int:
    """Returns the number of sales orders linked to the customer."""
    conexion = get_database_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM sales_order WHERE customer_id = %s",
            (customer_id,),
        )
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    finally:
        cursor.close()
        conexion.close()


def crear_cliente(first_name: str, last_name: str, identity_number: str,
                  billing_name: Optional[str] = None, tax_id: Optional[str] = None,
                  phone: Optional[str] = None, email: Optional[str] = None,
                  address: Optional[str] = None) -> bool:
    """Inserts a person and customer record in a single transaction.

    New customers default to `is_active = TRUE` so they appear in the default
    list view.
    """
    conexion = get_database_connection()
    cursor = conexion.cursor()

    sql_person = """
    INSERT INTO person (first_name, last_name, identity_number, phone, email, address)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    sql_customer = """
    INSERT INTO customer (person_id, billing_name, tax_id, is_active)
    VALUES (%s, %s, %s, TRUE)
    """

    try:
        cursor.execute(sql_person, (first_name, last_name, identity_number, phone, email, address))
        person_id = cursor.lastrowid

        b_name = billing_name if billing_name else f"{first_name} {last_name}"
        t_id = tax_id if tax_id else identity_number
        cursor.execute(sql_customer, (person_id, b_name, t_id))

        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al crear cliente: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def listar_clientes(search: Optional[str] = None,
                    status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all customers with their joined person details, with optional search.

    `status_filter` is one of CustomerActiveFilter.ACTIVE / INACTIVE / ALL.
    Default (None) is ACTIVE for backward compatibility.
    Search matches: first_name, last_name, identity_number, tax_id, billing_name
    and (v1) phone.
    """
    if status_filter is None:
        status_filter = CustomerActiveFilter.DEFAULT
    if status_filter not in CustomerActiveFilter.CHOICES:
        status_filter = CustomerActiveFilter.DEFAULT

    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id, c.is_active,
           p.first_name, p.last_name, p.identity_number, p.phone, p.email, p.address
    FROM customer c
    JOIN person p ON c.person_id = p.person_id
    WHERE 1=1
    """
    params: list[Any] = []

    if status_filter == CustomerActiveFilter.ACTIVE:
        sql += " AND c.is_active = TRUE"
    elif status_filter == CustomerActiveFilter.INACTIVE:
        sql += " AND c.is_active = FALSE"

    if search:
        like = f"%{search}%"
        sql += (
            " AND (p.first_name LIKE %s OR p.last_name LIKE %s"
            " OR p.identity_number LIKE %s OR c.tax_id LIKE %s"
            " OR c.billing_name LIKE %s OR p.phone LIKE %s)"
        )
        params.extend([like, like, like, like, like, like])

    sql += " ORDER BY p.last_name, p.first_name"

    customers: list[Dict[str, Any]] = []
    try:
        cursor.execute(sql, tuple(params))
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        logger.error("Error al listar clientes: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return customers


def buscar_cliente_por_doc(identity_number: str) -> Optional[Dict[str, Any]]:
    """Finds a customer by identity number (no status filter, includes inactive)."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id, c.is_active,
           p.first_name, p.last_name, p.identity_number, p.phone, p.email, p.address
    FROM customer c
    JOIN person p ON c.person_id = p.person_id
    WHERE p.identity_number = %s
    """

    customer = None
    try:
        cursor.execute(sql, (identity_number,))
        customer = cursor.fetchone()
    except mysql.connector.Error as err:
        logger.error("Error al buscar cliente: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return customer


def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """Returns a single customer by id, or None if not found."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id, c.is_active,
           p.first_name, p.last_name, p.identity_number, p.phone, p.email, p.address
    FROM customer c
    JOIN person p ON c.person_id = p.person_id
    WHERE c.customer_id = %s
    """

    customer = None
    try:
        cursor.execute(sql, (customer_id,))
        customer = cursor.fetchone()
    except mysql.connector.Error as err:
        logger.error("Error al obtener cliente: %s", err)
    finally:
        cursor.close()
        conexion.close()
    return customer


def update_customer(customer_id: int, first_name: str, last_name: str,
                    identity_number: str, billing_name: str, tax_id: str,
                    phone: Optional[str] = None, email: Optional[str] = None,
                    address: Optional[str] = None) -> bool:
    """Updates person and customer fields in a single transaction."""
    conexion = get_database_connection()
    cursor = conexion.cursor()

    sql_get_person = "SELECT person_id FROM customer WHERE customer_id = %s"
    sql_update_person = """
    UPDATE person
    SET first_name = %s, last_name = %s, identity_number = %s,
        phone = %s, email = %s, address = %s
    WHERE person_id = %s
    """
    sql_update_customer = """
    UPDATE customer
    SET billing_name = %s, tax_id = %s
    WHERE customer_id = %s
    """

    try:
        cursor.execute(sql_get_person, (customer_id,))
        row = cursor.fetchone()
        if not row:
            return False
        person_id = row[0]

        cursor.execute(sql_update_person, (
            first_name, last_name, identity_number,
            phone, email, address, person_id,
        ))
        cursor.execute(sql_update_customer, (billing_name, tax_id, customer_id))
        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al actualizar cliente: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def set_customer_active(customer_id: int, is_active: bool) -> bool:
    """Soft-activate or soft-deactivate a customer.

    Used by both `deactivate_customer` and `reactivate_customer` to keep the
    v1 web routes small. The operation never touches `person`, so the trail
    of sales orders linked to the customer is preserved.

    Returns True on a successful UPDATE. Returns False if the customer does
    not exist (cursor.rowcount == 0).
    """
    conexion = get_database_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE customer SET is_active = %s WHERE customer_id = %s",
            (bool(is_active), customer_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        logger.error("Error al cambiar is_active de cliente: %s", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def deactivate_customer(customer_id: int) -> bool:
    """Soft-deletes a customer. The `person` row is preserved for traceability.

    This replaces the v0 `DELETE FROM customer` flow. Because the customer row
    is still there (with `is_active = FALSE`), the linked `sales_order` rows
    keep their `customer_id` and the historical receipts stay readable.
    """
    return set_customer_active(customer_id, False)


def reactivate_customer(customer_id: int) -> bool:
    """Re-activates a previously soft-deleted customer."""
    return set_customer_active(customer_id, True)



def delete_customer(customer_id: int) -> bool:
    """Soft-deletes a customer, refusing if there are linked sales.

    Preservado para tests que verifican `CustomerHasSalesError`.
    La app usa `deactivate_customer` directamente.
    """
    sales_count = _count_customer_sales(customer_id)
    if sales_count > 0:
        raise CustomerHasSalesError(customer_id, sales_count)
    return deactivate_customer(customer_id)
