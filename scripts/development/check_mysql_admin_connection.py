# Check a MySQL admin connection.

"""
Quick MySQL admin connection test.

This does not assume that root has an empty password.
Use it only to verify the admin credentials before running the SQL scripts.
"""

import getpass
from typing import Any, Optional, Tuple, cast

import mysql.connector


def main():
    password = getpass.getpass("Password for MySQL root: ")
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password=password,
    )
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT VERSION()")
        version_row = cast(Optional[Tuple[Any, ...]], cursor.fetchone())
        version = version_row[0] if version_row else "UNKNOWN"
        print(f"Connected correctly to MySQL {version}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
