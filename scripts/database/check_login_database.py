# Check the configured MySQL database and users table.

import sys
from pathlib import Path
from typing import Any, Optional, Tuple, cast

import mysql.connector


SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zarvent_repuestos.infrastructure.mysql.connection import get_connection


def main():
    try:
        connection = get_connection()
    except mysql.connector.Error as error:
        print("ERROR: could not connect to MySQL with the .env credentials.")
        print(error)
        print()
        print("Run the database setup scripts with a MySQL admin user first.")
        return 1

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT DATABASE()")
        database_row = cast(Optional[Tuple[Any, ...]], cursor.fetchone())
        database_name = database_row[0] if database_row else "UNKNOWN"

        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table_exists = cursor.fetchone() is not None

        user_count = None
        if users_table_exists:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count_row = cast(Optional[Tuple[Any, ...]], cursor.fetchone())
            user_count = user_count_row[0] if user_count_row else 0

        print(f"Database: {database_name}")
        print(f"Table users: {'OK' if users_table_exists else 'MISSING'}")
        if user_count is not None:
            print(f"Users registered: {user_count}")
        return 0
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
