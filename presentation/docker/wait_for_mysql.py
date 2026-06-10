"""Polling helper: espera a que el servicio MySQL este listo para queries.

Se usa desde el entrypoint del contenedor `web` antes de ejecutar
`init_db.py` y `seed_project_data.py`. El healthcheck de
`docker-compose.yml` ya garantiza que el contenedor MySQL acepto una
conexion TCP, pero eso no implica que el servidor este listo para
autenticar usuarios ni ejecutar queries. Por eso esperamos a que un
SELECT 1 contra la base de la aplicacion devuelva una fila.

Variables de entorno leidas:
- `DB_HOST` (default: `mysql`).
- `DB_PORT` (default: `3306`).
- `DB_USER` (default: `zarvent_app`).
- `DB_PASSWORD` (default: `change_me`).
- `DB_NAME` (default: `sis122_zarvent_repuestos`).
- `WAIT_FOR_MYSQL_TIMEOUT_SECONDS` (default: `120`).
- `WAIT_FOR_MYSQL_INTERVAL_SECONDS` (default: `2`).

Exit codes:
- `0`: MySQL respondio antes del timeout.
- `1`: timeout agotado, MySQL no respondio.
"""

from __future__ import annotations

import os
import sys
import time

import mysql.connector


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        print(f"⚠️  {name}={raw!r} no es entero, usando default {default}", flush=True)
        return default


def wait_for_mysql() -> int:
    host = os.getenv("DB_HOST", "mysql")
    port = _env_int("DB_PORT", 3306)
    user = os.getenv("DB_USER", "zarvent_app")
    password = os.getenv("DB_PASSWORD", "change_me")
    database = os.getenv("DB_NAME", "sis122_zarvent_repuestos")
    timeout = _env_int("WAIT_FOR_MYSQL_TIMEOUT_SECONDS", 120)
    interval = _env_int("WAIT_FOR_MYSQL_INTERVAL_SECONDS", 2)

    deadline = time.monotonic() + timeout
    attempt = 0
    last_error: str | None = None

    print(
        f"⏳ Esperando MySQL en {host}:{port} como {user}@{database} "
        f"(timeout {timeout}s, intervalo {interval}s)...",
        flush=True,
    )

    while time.monotonic() < deadline:
        attempt += 1
        try:
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=5,
            )
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT 1")
                    row = cursor.fetchone()
                finally:
                    cursor.close()
            finally:
                connection.close()
            if row and row[0] == 1:
                print(f"✅ MySQL listo tras {attempt} intento(s).", flush=True)
                return 0
            last_error = "SELECT 1 no devolvio 1"
        except mysql.connector.Error as err:
            last_error = f"{type(err).__name__}: {err}"
        time.sleep(interval)

    print(
        f"❌ MySQL no respondio en {timeout}s. Ultimo error: {last_error}",
        flush=True,
    )
    return 1


if __name__ == "__main__":
    sys.exit(wait_for_mysql())
