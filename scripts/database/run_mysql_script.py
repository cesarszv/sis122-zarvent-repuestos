# Run one MySQL SQL file from Python.

import argparse
import getpass
import re
from pathlib import Path

import mysql.connector


def read_sql_statements(path):
    sql = Path(path).read_text(encoding="utf-8")
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)

    lines = []
    for line in sql.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)

    cleaned_sql = "\n".join(lines)
    return [statement.strip() for statement in cleaned_sql.split(";") if statement.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Run one SQL script against local MySQL."
    )
    parser.add_argument("script_path", help="SQL file to execute.")
    parser.add_argument("--admin-user", default="root", help="MySQL admin user.")
    parser.add_argument("--host", default="127.0.0.1", help="MySQL host.")
    parser.add_argument("--port", default=3306, type=int, help="MySQL port.")
    args = parser.parse_args()

    password = getpass.getpass(f"Password for MySQL user {args.admin_user}: ")
    statements = read_sql_statements(args.script_path)

    connection = mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.admin_user,
        password=password,
    )
    cursor = connection.cursor()

    try:
        for statement in statements:
            cursor.execute(statement)
        connection.commit()
        print(f"OK: executed {args.script_path}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
