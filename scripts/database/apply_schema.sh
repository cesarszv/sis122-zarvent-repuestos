#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCHEMA_FILE="${SCHEMA_FILE:-$ROOT_DIR/database/schema.sql}"
DATABASE_URL="${DATABASE_URL:-postgresql://zarvent:zarvent_dev_password@localhost:5432/zarvent_repuestos}"

command -v psql >/dev/null || {
    echo "psql is not installed. Install PostgreSQL client tools first."
    exit 1
}

psql "$DATABASE_URL" --file "$SCHEMA_FILE"
