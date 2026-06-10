# Especificacion Docker

## Objetivo

Dockerizar **Zarvent Repuestos** y dejar un artefacto versionado dentro de
`./presentation` que pueda copiarse a un USB y ejecutarse en una computadora
con Docker Desktop (Linux, macOS o Windows) sin instalar Python, `uv` ni
MySQL en el sistema host.

El objetivo no es cambiar la aplicacion. El objetivo es empacar el proyecto
actual para que Flask, MySQL y los datos demo funcionen de forma reproducible
en la defensa.

## Decisiones finales (v1)

1. **MySQL host port = `3307`** en lugar de `3306`. Razon: en la universidad
   suele haber otro MySQL local en `3306`. Usar `3307` evita colisionar con
   servicios preexistentes de la maquina del profesor o de la maquina del
   estudiante.
2. **Artefacto normal, no offline**. La primera ejecucion en Windows puede
   requerir internet si Docker Desktop no tiene cacheadas las imagenes
   `python:3.14-slim` y `mysql:8.4` o el resolver de `uv` no tiene
   descargadas las ruedas de las dependencias. Esto se documenta en el
   README de `presentation/`.
3. **`presentation/source/` se genera**. El codigo fuente no se versiona
   dentro de `presentation/source/`. Se regenera con
   `uv run python scripts/presentation/build_docker_artifact.py`. Esto evita
   duplicar el repo en git y deja una sola fuente de verdad.
4. **Validacion Docker cubre el prototipo real**, no todas las tablas del
   ERD extendido. Las tablas que valida este spec son las que
   `src/zarvent_repuestos/database/init_db.py` crea en runtime. Las tablas
   del ERD que no estan implementadas en la demo
   (`return_order`, `return_order_item`, `vehicle_model`,
   `part_compatibility`, etc.) quedan como alcance documental.

## Requisitos

1. Al finalizar, debe existir un artefacto dentro de `./presentation` que
   pueda copiarse a un USB. El artefacto se regenera localmente con el
   script de build.
2. En cualquier maquina con Docker Desktop, debe poder ejecutarse todo el
   proyecto usando solamente el contenido copiado desde `./presentation`.
3. El artefacto debe incluir instrucciones cortas para arrancar, detener y
   reiniciar el entorno.
4. Una vez en ejecucion, debe ser posible inspeccionar la base de datos
   desde JetBrains DataGrip conectandose al contenedor de MySQL por el
   puerto publicado en `localhost`.
5. El proyecto debe conservar el flujo real del repositorio: aplicacion
   Flask en Python, base de datos MySQL y seed de datos demo.
6. Durante la presentacion debe poder abrirse el codigo fuente del
   proyecto desde `presentation/source`. Si se edita el codigo, el
   contenedor web debe poder reiniciarse y tomar esos cambios.

## Stack del proyecto

- Aplicacion: Python con Flask.
- Version local declarada: `.python-version` usa `3.14`.
- Compatibilidad declarada en `pyproject.toml`: `requires-python = ">=3.9"`.
- Dependencias Python reales:
  - `flask>=3.1.0`
  - `mysql-connector-python>=9.4.0`
  - `python-dotenv>=1.2.1`
  - `bcrypt>=5.0.0`
- Gestor de entorno del repositorio: `uv`.
- Base de datos: MySQL.
- Imagen MySQL: `mysql:8.4`.
- Base por defecto: `sis122_zarvent_repuestos`.
- Usuario MySQL de la aplicacion: `zarvent_app`.
- Password demo por defecto: `change_me`.
- Puerto MySQL dentro del contenedor: `3306`.
- **Puerto MySQL publicado al host: `3307`** (configurable via
  `MYSQL_HOST_PORT`).
- Variable de clave Flask: `FLASK_SECRET_KEY`.

## Aplicacion web

- Modulo Flask principal: `zarvent_repuestos.web.app`.
- Comando local actual:

```bash
uv run python -m zarvent_repuestos.web.app
```

- Comando equivalente para ejecucion controlada (mismo que usa el
  entrypoint del contenedor `web`):

```bash
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload
```

- El contenedor web publica la aplicacion en `http://127.0.0.1:5000`.

## Codigo fuente en la defensa

Docker no reemplaza al codigo fuente. Docker solo crea el entorno donde se
ejecuta la aplicacion.

El artefacto `presentation/source/` contiene una copia del repositorio
generada por `scripts/presentation/build_docker_artifact.py`. Se
excluyen unicamente caches y basura temporal:

- `.git/`
- `.venv/`
- `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`
- `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`
- `*.egg-info/`
- `presentation/source/` (evita recursion al regenerar)
- `presentation/.env` (estado local regenerable)

Se incluye intencionalmente el `.env` del repo para que la defensa arranque
sin pasos extra. Las variables de entorno definidas en
`docker-compose.yml` para el servicio `web` tienen prioridad sobre el
`.env` gracias al orden de carga de `python-dotenv`.

El contenedor web monta `presentation/source/` como volumen en
`/workspace`, lo que permite editar archivos desde el host (Windows) y
luego `docker compose restart web` para tomar los cambios de Python. Los
templates de Flask tienen `TEMPLATES_AUTO_RELOAD = True`, asi que un
cambio en un `.html` no exige reiniciar el contenedor.

## Base de datos

Dentro del contenedor `web`, las variables de entorno se configuran asi:

```env
DB_HOST=mysql
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=zarvent_app
DB_PASSWORD=change_me
FLASK_SECRET_KEY=zarvent-academic-secret-key-122
```

`DB_HOST=mysql` resuelve al servicio definido en `docker-compose.yml` por
su nombre. `127.0.0.1` desde el contenedor `web` apunta a si mismo, NO a
la maquina host.

### Provisionamiento del usuario `zarvent_app`

El contenedor `mysql:8.4` crea el usuario con `MYSQL_USER` y
`MYSQL_PASSWORD` automaticamente. Para que el usuario pueda crear
tablas, vistas, indices, etc. (que es lo que hace `init_db.py`), se monta
un init script en `/docker-entrypoint-initdb.d/01-grants.sql` que aplica
los GRANTs necesarios usando las mismas variables de entorno.

### Tablas creadas por la aplicacion (validacion del spec)

`src/zarvent_repuestos/database/init_db.py` crea, en este orden:

- `person`
- `customer`
- `supplier`
- `part_category`
- `part`
- `inventory_stock`
- `sales_order`
- `sales_order_item`
- `payment`
- `purchase_order`
- `purchase_order_item`
- `users`

Ademas aplica dos vistas academicas (`vw_low_stock_parts`,
`vw_daily_sales_summary`) si el usuario tiene permiso `CREATE VIEW`.

### Tablas del ERD extendido fuera del alcance runtime

El ERD documentado en `docs/database/erd.md` incluye
`return_order`, `return_order_item`, `vehicle_model`,
`part_compatibility`. Esas tablas **no se crean** en el contenedor
porque `init_db.py` no las implementa. Son alcance documental del modelo
academico y se mencionan en la guia de defensa.

## Datos demo

El seed real esta en `scripts/database/seed_project_data.py`. Es
**idempotente**: antes de poblar consulta `has_operational_demo_data()`
y `has_purchase_demo_data()` y aborta si ya hay catalogos, ventas o
compras cargadas.

Carga:

- Usuario web `admin` con password `admin123`.
- Categorias de repuestos:
  - `Engine Parts`
  - `Transmission`
  - `Electrical`
  - `Suspension`
- Cinco repuestos iniciales con stock:
  - `Oxygen Sensor (Lambda Probe)`
  - `Spark Plug Standard`
  - `Clutch Kit 3-Piece`
  - `Iridium TT Spark Plug`
  - `Front Strut Mount`
- Cuatro clientes demo:
  - `Elena Rostova`
  - `Marcus Vance`
  - `Silvia Plath`
  - `Julian Black`
- Tres ventas historicas con pagos.
- Un proveedor demo y una orden de compra pendiente cuando todavia no
  existen compras demo.

## Flujo del entrypoint del contenedor `web`

`presentation/docker/entrypoint.sh` ejecuta, en orden:

1. Esperar a que MySQL responda (`wait_for_mysql.py`, polling con
   `mysql.connector.connect`, timeout configurable).
2. `python -m zarvent_repuestos.database.init_db` (idempotente via
   `CREATE TABLE IF NOT EXISTS`).
3. `python scripts/database/seed_project_data.py` (idempotente via
   chequeos previos).
4. `python -m flask --app zarvent_repuestos.web.app:app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload`.

`app.py` tambien llama a `crear_tablas()` al importarse. Es redundante
con el paso 2, pero inofensivo por la idempotencia y sirve como guion
de defensa: "primero la DB, despues el seed, despues la web".

## Requisito para DataGrip

El contenedor MySQL publica `127.0.0.1:3307` (configurable via
`MYSQL_HOST_PORT`).

Valores esperados para DataGrip:

| Campo | Valor |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3307` |
| User | `zarvent_app` |
| Password | `change_me` |
| Database | `sis122_zarvent_repuestos` |
| URL JDBC | `jdbc:mysql://127.0.0.1:3307/sis122_zarvent_repuestos` |

## Entregable

Todo queda dentro de `./presentation`. La estructura esperada es:

```text
presentation/
  docker-compose.yml
  Dockerfile.web
  .env.example
  .gitignore
  README.md
  source/                  # generado por build_docker_artifact.py
  docker/
    entrypoint.sh
    wait_for_mysql.py
    01-grants.sql          # init script para MySQL
```

El artefacto `presentation/source/` se regenera con:

```bash
uv run python scripts/presentation/build_docker_artifact.py
```

## Criterios de aceptacion

1. En una maquina limpia con Docker Desktop, el proyecto levanta desde
   `./presentation` sin instalar Python, `uv` ni MySQL en el sistema
   host.
2. La web abre en `http://127.0.0.1:5000` y permite iniciar sesion con
   `admin` / `admin123`.
3. La base `sis122_zarvent_repuestos` existe dentro del contenedor
   MySQL.
4. DataGrip puede conectarse al MySQL dockerizado en `127.0.0.1:3307`
   con los datos documentados.
5. Las 8 tablas minimas del prototipo (`users`, `part_category`,
   `part`, `inventory_stock`, `customer`, `sales_order`, `payment`,
   `purchase_order`) y sus datos demo aparecen en DataGrip.
6. El artefacto no depende de rutas absolutas de la maquina local.
7. El codigo fuente se puede abrir desde `presentation/source/`.
8. Si se edita un archivo `.py`, `docker compose restart web` toma el
   cambio. Si se edita un template, no hace falta reiniciar.
9. `docker compose down -v` resetea la base de datos y `docker compose
   up --build -d` la deja como recien instalada, gracias a la
   idempotencia del seed.

## Fuera de alcance

- Empaquetar el proyecto como imagen publica en Docker Hub.
- Construir un binario offline con todas las dependencias cacheadas.
- Crear las tablas del ERD extendido que la app no implementa.
- Cambiar la aplicacion Flask o la logica de CRUD.
