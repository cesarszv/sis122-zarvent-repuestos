"""Database and tables initialization script following the project's ERD schema.

This module is the source of truth for the physical schema at runtime. It runs
on every Flask startup (`web/app.py`) and is idempotent (CREATE TABLE IF NOT
EXISTS). For the academic reference of the schema, see `database/schema.sql`,
which mirrors the statements below and adds the analytical views.

v1 changes (v1 refactor):

- `customer.is_active` column added (soft-delete for RF-01).
- Idempotent migration block that adds `is_active` to pre-existing schemas.
- Creation of two academic views (`vw_low_stock_parts`,
  `vw_daily_sales_summary`) used by the dashboard and inventory views.
"""

import logging

import mysql.connector
from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.connection import get_database_connection


logger = logging.getLogger(__name__)


def initialize_database():
    """Verifies the database exists, creating it only when the user can do it."""
    db_name = DB_CONFIG.get("database", "sis122_zarvent_repuestos")

    try:
        conexion = get_database_connection()
        conexion.close()
        print(f"📦 Base de datos '{db_name}' verificada.")
        return True
    except mysql.connector.Error as err:
        if getattr(err, "errno", None) != 1049:
            logger.error("Error al conectar con la base de datos: %s", err)
            return False

    temp_config = DB_CONFIG.copy()
    temp_config.pop("database", None)

    try:
        conexion = mysql.connector.connect(**temp_config)
        cursor = conexion.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_name} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        print(f"📦 Base de datos '{db_name}' verificada/creada.")
        return True
    except mysql.connector.Error as err:
        logger.error("Error al crear la base de datos: %s", err)
        return False


def _ensure_customer_is_active_column(cursor) -> None:
    """Adds `customer.is_active` if it does not exist (idempotent migration)."""
    try:
        cursor.execute(
            """
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME   = 'customer'
              AND COLUMN_NAME  = 'is_active'
            """
        )
        exists = cursor.fetchone()[0]
    except mysql.connector.Error as err:
        logger.warning(
            "No se pudo consultar INFORMATION_SCHEMA (errno=%s): %s",
            getattr(err, "errno", None),
            err,
        )
        return
    if exists:
        return
    try:
        cursor.execute(
            "ALTER TABLE customer ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE AFTER tax_id"
        )
    except mysql.connector.Error as err:
        logger.warning(
            "No se pudo agregar customer.is_active (errno=%s): %s",
            getattr(err, "errno", None),
            err,
        )


def _create_views(cursor) -> None:
    """Creates or replaces the academic analytical views used by the dashboard.

    Failures are logged but never break startup: the application code falls
    back to inline queries when the views are missing. This keeps `crear_tablas`
    resilient to permission-restricted deployments (e.g. a MySQL user without
    CREATE VIEW privilege).
    """
    for stmt in (
        """
        CREATE OR REPLACE VIEW vw_low_stock_parts AS
        SELECT
            p.part_id,
            p.internal_code,
            p.name,
            p.brand,
            s.quantity_on_hand,
            s.reorder_level,
            (s.reorder_level - s.quantity_on_hand) AS shortage
        FROM part p
        JOIN inventory_stock s ON p.part_id = s.part_id
        WHERE s.quantity_on_hand <= s.reorder_level
        ORDER BY s.quantity_on_hand ASC
        """,
        """
        CREATE OR REPLACE VIEW vw_daily_sales_summary AS
        SELECT
            order_date,
            COUNT(*)              AS orders_count,
            SUM(subtotal)         AS subtotal_total,
            SUM(discount_amount)  AS discount_total,
            SUM(total_amount)     AS total_amount
        FROM sales_order
        WHERE status = 'Paid'
        GROUP BY order_date
        ORDER BY order_date DESC
        """,
    ):
        try:
            cursor.execute(stmt)
        except mysql.connector.Error as err:
            # Permission denied (errno 1142) and similar should not block startup;
            # the CRUDs fall back to inline queries when the view is missing.
            logger.warning(
                "No se pudo crear/actualizar la vista analitica (errno=%s): %s",
                getattr(err, "errno", None),
                err,
            )


def crear_tablas():
    """Creates all required tables in hierarchical order, plus analytical views."""
    if not initialize_database():
        return False

    try:
        conexion = get_database_connection()
    except mysql.connector.Error as err:
        logger.error("Error de conexión al crear tablas: %s", err)
        return False

    cursor = conexion.cursor()

    # 1. Person Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person (
        person_id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        identity_number VARCHAR(50) UNIQUE NOT NULL,
        phone VARCHAR(50),
        email VARCHAR(100),
        address VARCHAR(255)
    ) ENGINE=InnoDB;
    """)

    # 2. Customer Table (RF-01) - v1 adds is_active for soft-delete
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT UNIQUE NOT NULL,
        billing_name VARCHAR(150),
        tax_id VARCHAR(50),
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # 3. Supplier Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS supplier (
        supplier_id INT AUTO_INCREMENT PRIMARY KEY,
        business_name VARCHAR(150) NOT NULL,
        tax_id VARCHAR(50) UNIQUE NOT NULL,
        phone VARCHAR(50),
        email VARCHAR(100),
        address VARCHAR(255),
        is_active BOOLEAN DEFAULT TRUE
    ) ENGINE=InnoDB;
    """)

    # 4. Part Category Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS part_category (
        part_category_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT
    ) ENGINE=InnoDB;
    """)

    # 5. Part Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS part (
        part_id INT AUTO_INCREMENT PRIMARY KEY,
        part_category_id INT NOT NULL,
        internal_code VARCHAR(50) UNIQUE NOT NULL,
        oem_code VARCHAR(50),
        name VARCHAR(150) NOT NULL,
        brand VARCHAR(100),
        unit VARCHAR(20) DEFAULT 'pcs',
        sale_price DECIMAL(10, 2) NOT NULL,
        purchase_cost DECIMAL(10, 2) NOT NULL,
        warranty_days INT DEFAULT 0,
        status VARCHAR(50) DEFAULT 'active',
        FOREIGN KEY (part_category_id) REFERENCES part_category (part_category_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 6. Inventory Stock Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_stock (
        inventory_stock_id INT AUTO_INCREMENT PRIMARY KEY,
        part_id INT UNIQUE NOT NULL,
        location_name VARCHAR(100),
        quantity_on_hand INT NOT NULL DEFAULT 0,
        reorder_level INT NOT NULL DEFAULT 10,
        FOREIGN KEY (part_id) REFERENCES part (part_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # 7. Sales Order Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_order (
        sales_order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        order_date DATE NOT NULL,
        status VARCHAR(50) DEFAULT 'Paid',
        subtotal DECIMAL(10, 2) NOT NULL,
        discount_amount DECIMAL(10, 2) DEFAULT 0.00,
        total_amount DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 8. Sales Order Item Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_order_item (
        sales_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
        sales_order_id INT NOT NULL,
        part_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        discount_amount DECIMAL(10, 2) DEFAULT 0.00,
        FOREIGN KEY (sales_order_id) REFERENCES sales_order (sales_order_id) ON DELETE CASCADE,
        FOREIGN KEY (part_id) REFERENCES part (part_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 9. Payment Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        payment_id INT AUTO_INCREMENT PRIMARY KEY,
        sales_order_id INT NOT NULL,
        payment_date DATE NOT NULL,
        method VARCHAR(50) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        reference_number VARCHAR(100),
        status VARCHAR(50) DEFAULT 'Completed',
        FOREIGN KEY (sales_order_id) REFERENCES sales_order (sales_order_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # 10. Purchase Order Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_order (
        purchase_order_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_id INT NOT NULL,
        order_date DATE NOT NULL,
        expected_date DATE,
        status VARCHAR(50) DEFAULT 'Pending',
        total_amount DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES supplier (supplier_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 11. Purchase Order Item Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchase_order_item (
        purchase_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
        purchase_order_id INT NOT NULL,
        part_id INT NOT NULL,
        quantity_ordered INT NOT NULL,
        quantity_received INT NOT NULL DEFAULT 0,
        unit_cost DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (purchase_order_id) REFERENCES purchase_order (purchase_order_id) ON DELETE CASCADE,
        FOREIGN KEY (part_id) REFERENCES part (part_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 12. System Users Table for Login
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    ) ENGINE=InnoDB;
    """)

    # Idempotent migrations (v1) - safe to run on existing schemas.
    _ensure_customer_is_active_column(cursor)

    # Academic analytical views (v1) - CREATE OR REPLACE makes them idempotent.
    _create_views(cursor)

    conexion.commit()
    cursor.close()
    conexion.close()
    print("📦 Todas las tablas verificadas/creadas correctamente en MySQL.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if crear_tablas() else 1)
