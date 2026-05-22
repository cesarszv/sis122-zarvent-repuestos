import sys
from pathlib import Path

import mysql.connector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_connection


def main():
    try:
        connection = get_connection()
    except mysql.connector.Error as error:
        print("ERROR: could not connect to MySQL with the .env credentials.")
        print(error)
        print()
        print("Run scripts 001, 002, and 003 with a MySQL admin user first.")
        return 1

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]

        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table_exists = cursor.fetchone() is not None

        user_count = None
        if users_table_exists:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]

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
