#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCHEMA_FILE="${SCHEMA_FILE:-$ROOT_DIR/database/schema.sql}"

POSTGRES_DB="${POSTGRES_DB:-zarvent_repuestos}"
POSTGRES_USER="${POSTGRES_USER:-$USER}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

command -v psql >/dev/null || {
    echo "psql is not installed. Install PostgreSQL client tools first."
    exit 1
}

command -v createdb >/dev/null || {
    echo "createdb is not installed. Install PostgreSQL client tools first."
    exit 1
}

command -v dropdb >/dev/null || {
    echo "dropdb is not installed. Install PostgreSQL client tools first."
    exit 1
}

dropdb \
    --if-exists \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --username "$POSTGRES_USER" \
    "$POSTGRES_DB"

createdb \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --username "$POSTGRES_USER" \
    "$POSTGRES_DB"

psql \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --file "$SCHEMA_FILE"

echo "Database '$POSTGRES_DB' reset and initialized."
