"""CRUD operations for Customers and Persons."""

import mysql.connector
from typing import List, Optional, Dict, Any

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.models.customer import Customer, Person


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


def listar_clientes() -> List[Dict[str, Any]]:
    """Retrieves all customers with their joined person details."""
    conexion = get_database_connection()
    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT c.customer_id, c.person_id, c.billing_name, c.tax_id,
           p.first_name, p.last_name, p.identity_number, p.phone, p.email, p.address
    FROM customer c
    JOIN person p ON c.person_id = p.person_id
    ORDER BY p.last_name, p.first_name
    """

    customers = []
    try:
        cursor.execute(sql)
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
