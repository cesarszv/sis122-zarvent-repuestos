"""One-click setup and seeding script for MySQL database, tables, and application users."""

import sys
import getpass
from pathlib import Path

import mysql.connector

# Ensure src/ is in the python path
SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.init_db import crear_tablas
from scripts.database import seed_project_data


def main():
    print("==================================================")
    print("      CONFIGURADOR DE BASE DE DATOS ZARVENT       ")
    print("==================================================")
    print("Este script configurará las credenciales y poblará la base de datos.")
    print()

    admin_user = input("Usuario administrador de MySQL [root]: ").strip() or "root"
    admin_password = getpass.getpass(f"Contraseña de MySQL para el usuario '{admin_user}': ")

    db_name = DB_CONFIG["database"]
    app_user = DB_CONFIG["user"]
    app_pass = DB_CONFIG["password"]

    print(f"\n1. Conectando como '{admin_user}' para crear base de datos y usuario de la app...")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=admin_user,
            password=admin_password
        )
    except mysql.connector.Error as err:
        print(f"❌ ERROR: No se pudo conectar como administrador: {err}")
        return 1

    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_name} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"   - Base de datos '{db_name}' verificada/creada.")

        # Create application user with .env credentials
        cursor.execute(f"CREATE USER IF NOT EXISTS '{app_user}'@'localhost' IDENTIFIED BY '{app_pass}'")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY '{app_pass}'")
        
        # Grant permissions
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO '{app_user}'@'localhost'")
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO '{app_user}'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        conn.commit()
        print(f"   - Usuario de MySQL '{app_user}' configurado con permisos sobre '{db_name}'.")
    except mysql.connector.Error as err:
        print(f"❌ ERROR en configuración administrativa: {err}")
        return 1
    finally:
        cursor.close()
        conn.close()

    print("\n2. Creando tablas físicas en la base de datos...")
    try:
        # Now that user is created, we can run the regular table initializer
        crear_tablas()
    except Exception as e:
        print(f"❌ ERROR al inicializar tablas: {e}")
        return 1

    print("\n3. Poblando catálogo de repuestos, clientes y ventas iniciales...")
    try:
        # Run seeder logic
        seed_project_data.main()
    except Exception as e:
        print(f"❌ ERROR al poblar datos: {e}")
        return 1

    print("\n==================================================")
    print("🎉 ¡BASE DE DATOS Y USUARIOS CONFIGURADOS CON ÉXITO!")
    print("==================================================")
    print("El servidor Flask ya puede conectarse. Recarga la página web.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
