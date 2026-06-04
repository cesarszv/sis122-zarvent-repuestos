"""Database and tables initialization script following the project's ERD schema."""

import mysql.connector
from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.connection import get_database_connection


def initialize_database():
    """Creates the database if it does not exist."""
    temp_config = DB_CONFIG.copy()
    db_name = temp_config.pop("database", "sis122_zarvent_repuestos")
    
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
        print("❌ Error al crear/verificar base de datos:", err)
        return False


def crear_tablas():
    """Creates all required tables in hierarchical order."""
    if not initialize_database():
        return

    try:
        conexion = get_database_connection()
    except mysql.connector.Error as err:
        print("❌ Error de conexión al crear tablas:", err)
        return

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

    # 2. Customer Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer (
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        person_id INT UNIQUE NOT NULL,
        billing_name VARCHAR(150),
        tax_id VARCHAR(50),
        FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # 3. Part Category Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS part_category (
        part_category_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT
    ) ENGINE=InnoDB;
    """)

    # 4. Part Table
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

    # 5. Inventory Stock Table
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

    # 6. Sales Order Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_order (
        sales_order_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        order_date DATE NOT NULL,
        status VARCHAR(50) DEFAULT 'pending',
        subtotal DECIMAL(10, 2) NOT NULL,
        discount_amount DECIMAL(10, 2) DEFAULT 0.00,
        total_amount DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT
    ) ENGINE=InnoDB;
    """)

    # 7. Sales Order Item Table
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

    # 8. Payment Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        payment_id INT AUTO_INCREMENT PRIMARY KEY,
        sales_order_id INT NOT NULL,
        payment_date DATE NOT NULL,
        method VARCHAR(50) NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        reference_number VARCHAR(100),
        status VARCHAR(50) DEFAULT 'completed',
        FOREIGN KEY (sales_order_id) REFERENCES sales_order (sales_order_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # 9. System Users Table for Login
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL
    ) ENGINE=InnoDB;
    """)

    conexion.commit()
    cursor.close()
    conexion.close()
    print("📦 Todas las tablas verificadas/creadas correctamente en MySQL.")


if __name__ == "__main__":
    crear_tablas()
