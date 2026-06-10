#!/usr/bin/env bash
# Entry point del contenedor `web` de Zarvent Repuestos.
#
# Este script se ejecuta cada vez que el contenedor arranca. Su
# responsabilidad es preparar la base de datos y luego levantar Flask
# con la app. Los pasos son idempotentes: se puede reiniciar el
# contenedor sin perder datos ni duplicar el seed.
#
# Pasos:
#   1. Esperar a que MySQL acepte queries (no solo TCP).
#   2. Ejecutar `init_db.py` para crear las tablas que falten.
#   3. Ejecutar `seed_project_data.py` para cargar datos demo si la
#      base esta vacia.
#   4. Arrancar Flask con `flask run` en 0.0.0.0:5000.
#
# Si cualquier paso previo falla, el contenedor se detiene con un exit
# code distinto de 0. Eso permite que Docker lo marque como unhealthy
# y deja evidencia clara en `docker compose logs web`.

set -euo pipefail

WORKSPACE="/workspace"
SRC_DIR="${WORKSPACE}/src"
SCRIPTS_DIR="${WORKSPACE}/scripts"
DOCKER_HELPERS_DIR="${WORKSPACE}/presentation/docker"

echo "=================================================="
echo "  Zarvent Repuestos - contenedor web"
echo "  WORKSPACE: ${WORKSPACE}"
echo "  DB_HOST:   ${DB_HOST:-mysql}"
echo "  DB_PORT:   ${DB_PORT:-3306}"
echo "  DB_NAME:   ${DB_NAME:-sis122_zarvent_repuestos}"
echo "=================================================="

cd "${WORKSPACE}"

# 1. Esperar a MySQL.
echo ""
echo "▶ Paso 1/4: esperando a MySQL..."
python "${DOCKER_HELPERS_DIR}/wait_for_mysql.py"

# 2. Crear tablas (idempotente: CREATE TABLE IF NOT EXISTS).
echo ""
echo "▶ Paso 2/4: creando/verificando tablas..."
PYTHONPATH="${SRC_DIR}" python -m zarvent_repuestos.database.init_db

# 3. Cargar datos demo (idempotente: chequea si ya hay datos).
echo ""
echo "▶ Paso 3/4: cargando datos demo..."
cd "${WORKSPACE}"
python "${SCRIPTS_DIR}/database/seed_project_data.py"

# 4. Arrancar Flask.
echo ""
echo "▶ Paso 4/4: arrancando Flask en 0.0.0.0:5000..."
cd "${WORKSPACE}"
exec python -m flask \
    --app zarvent_repuestos.web.app:app \
    run \
    --host 0.0.0.0 \
    --port 5000 \
    --no-debugger \
    --no-reload
