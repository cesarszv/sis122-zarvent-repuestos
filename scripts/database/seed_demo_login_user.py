"""Create or update the demo login user."""

import sys
from pathlib import Path

import mysql.connector


SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from zarvent_repuestos.access.user_service import hash_password
from zarvent_repuestos.database.connection import get_database_connection


DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def main():
    username = sys.argv[1] if len(sys.argv) >= 2 else DEFAULT_USERNAME
    password = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_PASSWORD
    password_hashed = hash_password(password)

    try:
        connection = get_database_connection()
    except mysql.connector.Error as error:
        print("ERROR: could not connect to MySQL with the .env credentials.")
        print(error)
        return 1

    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (username, password)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE password = VALUES(password)
            """,
            (username, password_hashed),
        )
        connection.commit()
        print(f"OK: demo user ready: {username}")
        print("Default password is admin123 if no password argument was passed.")
        return 0
    except mysql.connector.Error as error:
        connection.rollback()
        print("ERROR: could not create the demo user.")
        print(error)
        return 1
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
