"""Check the local MySQL connection using environment variables."""

from __future__ import annotations

import os
import sys

import mysql.connector
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    config = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME", "sis122_zarvent_repuestos"),
        "user": os.getenv("DB_USER", "zarvent_app"),
        "password": os.getenv("DB_PASSWORD", ""),
    }

    try:
        with mysql.connector.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION(), DATABASE()")
                version, database = cursor.fetchone()
    except mysql.connector.Error as error:
        print(f"MySQL connection failed: {error}", file=sys.stderr)
        return 1

    print(f"MySQL connection OK: version={version}, database={database}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
