"""CRUD operations for Customers and Persons."""

import mysql.connector
from typing import List, Optional, Dict, Any

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.models.customer import Customer, Person


class CustomerHasSalesError(Exception):
    """Raised when a customer cannot be deleted because sales orders protect them."""

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
    """Inserts a person and customer record in a single transaction."""
    conexion = get_database_connection()
    cursor = conexion.cursor()

    sql_person = """
    INSERT INTO person (first_name, last_name, identity_number, phone, email, address)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    sql_customer = """
    INSERT INTO customer (person_id, billing_name, tax_id)
    VALUES (%s, %s, %s)
    """

    try:
        # 1. Insert Person
        cursor.execute(sql_person, (first_name, last_name, identity_number, phone, email, address))
        person_id = cursor.lastrowid

        # 2. Insert Customer
        b_name = billing_name if billing_name else f"{first_name} {last_name}"
        t_id = tax_id if tax_id else identity_number
        cursor.execute(sql_customer, (person_id, b_name, t_id))

        conexion.commit()
        return True
    except mysql.connector.Error as err:
        conexion.rollback()
        print("❌ Error al crear cliente:", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def listar_clientes(search: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves all customers with their joined person details, with optional search."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id,
           p.first_name, p.last_name, p.identity_number, p.phone, p.email, p.address
    FROM customer c
    JOIN person p ON c.person_id = p.person_id
    WHERE 1=1
    """
    params: list[Any] = []

    if search:
        like = f"%{search}%"
        sql += (
            " AND (p.first_name LIKE %s OR p.last_name LIKE %s"
            " OR p.identity_number LIKE %s OR c.tax_id LIKE %s"
            " OR c.billing_name LIKE %s)"
        )
        params.extend([like, like, like, like, like])

    sql += " ORDER BY p.last_name, p.first_name"

    customers: list[Dict[str, Any]] = []
    try:
        cursor.execute(sql, tuple(params))
        customers = cursor.fetchall()
    except mysql.connector.Error as err:
        print("❌ Error al listar clientes:", err)
    finally:
        cursor.close()
        conexion.close()
    return customers


def buscar_cliente_por_doc(identity_number: str) -> Optional[Dict[str, Any]]:
    """Finds a customer by identity number."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id,
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
        print("❌ Error al buscar cliente:", err)
    finally:
        cursor.close()
        conexion.close()
    return customer


def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """Returns a single customer by id, or None if not found."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id,
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
        print("❌ Error al obtener cliente:", err)
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
        print("❌ Error al actualizar cliente:", err)
        return False
    finally:
        cursor.close()
        conexion.close()


def delete_customer(customer_id: int) -> bool:
    """Deletes a customer after verifying no sales are linked.

    Raises CustomerHasSalesError when the customer still has sales orders.
    """
    sales_count = _count_customer_sales(customer_id)
    if sales_count > 0:
        raise CustomerHasSalesError(customer_id, sales_count)

    conexion = get_database_connection()
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
        conexion.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as err:
        conexion.rollback()
        errno = getattr(err, "errno", None)
        if errno == 1451:
            # The pre-check found 0 but a concurrent INSERT created a sales_order
            # between the count and the DELETE. Recount to give the user a
            # truthful error message.
            fresh_count = _count_customer_sales(customer_id)
            raise CustomerHasSalesError(customer_id, fresh_count) from err
        print("❌ Error al eliminar cliente:", err)
        return False
    finally:
        cursor.close()
        conexion.close()
