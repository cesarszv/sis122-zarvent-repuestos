"""One-click setup and seeding script for MySQL database, tables, and application users."""

import argparse
import getpass
import subprocess
import sys
from pathlib import Path

import mysql.connector

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from zarvent_repuestos.config.db_config import DB_CONFIG
from zarvent_repuestos.database.init_db import crear_tablas
import seed_project_data


def escape_sql_string(value):
    """Escapes a simple value for MySQL single-quoted strings."""
    return str(value).replace("\\", "\\\\").replace("'", "\\'")


def escape_sql_identifier(value):
    """Escapes a simple MySQL identifier wrapped with backticks."""
    return str(value).replace("`", "``")


def run_admin_sql_with_password(db_name, app_user, app_pass, admin_user):
    admin_password = getpass.getpass(f"Contraseña de MySQL para el usuario '{admin_user}': ")

    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=admin_user,
        password=admin_password,
    )
    cursor = conn.cursor()
    try:
        execute_admin_sql(cursor, db_name, app_user, app_pass)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def run_admin_sql_with_sudo_mysql(db_name, app_user, app_pass):
    statements = build_admin_sql(db_name, app_user, app_pass)
    subprocess.run(["sudo", "mysql"], input=statements, text=True, check=True)


def build_admin_sql(db_name, app_user, app_pass):
    app_user = escape_sql_string(app_user)
    app_pass = escape_sql_string(app_pass)
    db_name = escape_sql_identifier(db_name)

    return f"""
CREATE DATABASE IF NOT EXISTS `{db_name}`
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '{app_user}'@'localhost' IDENTIFIED BY '{app_pass}';
CREATE USER IF NOT EXISTS '{app_user}'@'%' IDENTIFIED BY '{app_pass}';
ALTER USER '{app_user}'@'localhost' IDENTIFIED BY '{app_pass}';
ALTER USER '{app_user}'@'%' IDENTIFIED BY '{app_pass}';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON `{db_name}`.* TO '{app_user}'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES,
      CREATE VIEW, DROP, SHOW VIEW
ON `{db_name}`.* TO '{app_user}'@'%';

FLUSH PRIVILEGES;
"""


def execute_admin_sql(cursor, db_name, app_user, app_pass):
    for statement in build_admin_sql(db_name, app_user, app_pass).split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Configura MySQL, crea tablas y carga datos demo."
    )
    parser.add_argument(
        "--admin-user",
        default="root",
        help="Usuario administrador de MySQL cuando se usa modo password.",
    )
    parser.add_argument(
        "--admin-mode",
        choices=["password", "sudo-mysql"],
        default="password",
        help="Usa password para MySQL por TCP o sudo mysql para root por socket en Linux.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("==================================================")
    print("      CONFIGURADOR DE BASE DE DATOS ZARVENT       ")
    print("==================================================")
    print("Este script configurará las credenciales y poblará la base de datos.")
    print()

    db_name = DB_CONFIG["database"]
    app_user = DB_CONFIG["user"]
    app_pass = DB_CONFIG["password"]

    print("\n1. Creando base de datos y usuario de la app...")
    try:
        if args.admin_mode == "sudo-mysql":
            run_admin_sql_with_sudo_mysql(db_name, app_user, app_pass)
        else:
            run_admin_sql_with_password(db_name, app_user, app_pass, args.admin_user)
        print(f"   - Base de datos '{db_name}' verificada/creada.")
        print(f"   - Usuario de MySQL '{app_user}' configurado con permisos sobre '{db_name}'.")
    except (mysql.connector.Error, subprocess.CalledProcessError) as err:
        print(f"❌ ERROR en configuración administrativa: {err}")
        return 1

    print("\n2. Creando tablas físicas en la base de datos...")
    try:
        if not crear_tablas():
            return 1
    except Exception as e:
        print(f"❌ ERROR al inicializar tablas: {e}")
        return 1

    print("\n3. Poblando catálogo de repuestos, clientes y ventas iniciales...")
    try:
        if seed_project_data.main() != 0:
            return 1
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
