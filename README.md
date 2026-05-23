# Zarvent Repuestos

Proyecto academico para la asignatura `SIS-122` (Base de Datos I) con el
profesor *Ismael Antonio Delgado Huanca*.

Realizado por:

- Cesar Sebastian Zambrana Ventura
- Emanuel Justiniano Peralta

## Objetivo

Zarvent Repuestos modela una empresa ficticia de venta de repuestos de
vehiculos.

El objetivo actual del repositorio es **defender el modelo de base de datos**:
entidades, atributos, claves primarias, claves foraneas, relaciones,
normalizacion y consultas posibles.

No estamos intentando demostrar arquitectura de software avanzada. Eso seria
ruido para este punto del proyecto.

## Alcance actual

El modelo cubre:

- clientes
- proveedores
- catalogo de repuestos
- compatibilidad de repuestos con vehiculos
- stock actual
- ventas
- pagos
- compras
- devoluciones y garantias
- reportes derivados de las tablas operativas

## Stack academico

Por exigencia del curso, el gestor elegido es **MySQL Server**.

Por ahora el foco sigue siendo la base de datos. Primero se entiende el modelo;
despues se escribe cualquier codigo de aplicacion.

## Entorno de Python

El proyecto usa **UV** como flujo oficial de Python.

`uv` lee `pyproject.toml` y `uv.lock`, crea o actualiza `.venv/` y ejecuta los
comandos dentro del entorno del proyecto. No usamos `pip` manual ni `python -m
venv` como pasos de trabajo del repositorio.

Las dependencias externas son pocas:

- `mysql-connector-python`: permite conectar Python con MySQL Server.
- `python-dotenv`: permite leer las credenciales desde `.env`.
- `bcrypt`: permite trabajar contrasenas con hash.
- `flask`: permite mostrar una pantalla web simple para el login.

La aplicacion usa una arquitectura modular simple. La idea es que las carpetas
principales muestren responsabilidades claras:

- `modules`: reglas del negocio por area.
- `infrastructure`: detalles tecnicos externos, como MySQL.
- `interfaces`: formas de usar el sistema, como Flask.

Estructura actual del prototipo:

```text
sis122-zarvent-repuestos/
|-- src/
|   `-- zarvent_repuestos/
|       |-- infrastructure/
|       |   `-- mysql/
|       |       `-- connection.py
|       |-- interfaces/
|       |   `-- web/
|       |       |-- app.py
|       |       |-- templates/
|       |       `-- static/
|       `-- modules/
|           `-- access/
|               `-- service.py
|-- scripts/
|   |-- database/
|   `-- development/
|-- database/
|-- docs/
`-- .venv/
```

`access` contiene login, usuarios y contrasenas. `mysql` contiene la conexion a
la base de datos. `web` contiene la interfaz Flask.

### Setup rapido con UV

```powershell
uv python install 3.14
uv sync
uv run python scripts\development\check_python_environment.py
uv run python -m zarvent_repuestos.interfaces.web.app
```

### Ejecutar la pantalla de login

Cuando la aplicacion Flask este corriendo, abre:

- `http://127.0.0.1:5000`
- `http://localhost:5000`

### Archivo `.env`

Crea una copia local de ejemplo:

```powershell
Copy-Item .env.example .env
```

Despues edita `.env` con las credenciales reales de MySQL del equipo.

### Preparar MySQL

La base de datos del proyecto debe llamarse exactamente:

```text
sis122_zarvent_repuestos
```

Los scripts estan numerados para poder repetir el proceso paso por paso:

```text
scripts/
|-- database/
|   |-- run_sql_file.py
|   |-- 001_create_database.sql
|   |-- 002_create_users_table.sql
|   |-- 003_create_app_user.sql
|   |-- seed_demo_user.py
|   `-- check_database.py
`-- development/
    `-- check_python_environment.py
```

Como el comando `mysql` puede no estar en el `PATH`, el repo incluye un
ejecutor pequeno que usa `mysql-connector-python` y pide la contrasena del
usuario administrador sin guardarla:

```powershell
uv run python scripts\database\run_sql_file.py scripts\database\001_create_database.sql --admin-user root
uv run python scripts\database\run_sql_file.py scripts\database\002_create_users_table.sql --admin-user root
uv run python scripts\database\run_sql_file.py scripts\database\003_create_app_user.sql --admin-user root
uv run python scripts\database\seed_demo_user.py
uv run python scripts\database\check_database.py
```

Si prefieres MySQL Workbench, ejecuta estos SQL en el mismo orden:

```sql
SOURCE scripts/database/001_create_database.sql;
SOURCE scripts/database/002_create_users_table.sql;
SOURCE scripts/database/003_create_app_user.sql;
```

El usuario demo queda asi si no pasas argumentos:

```text
usuario: admin
contrasena: admin123
```

Despues levanta la app:

```powershell
uv run python -m zarvent_repuestos.interfaces.web.app
```

## Documentos principales

- [`docs/database/erd.md`](docs/database/erd.md): diagrama ERD compacto.
- [`docs/database/db_explanation.md`](docs/database/db_explanation.md):
  explicacion tabla por tabla.
- [`docs/database/erd_explanation.md`](docs/database/erd_explanation.md):
  defensa profunda del modelo.
- [`docs/database/erd_business_research.md`](docs/database/erd_business_research.md):
  justificacion del ERD desde el negocio.
- [`docs/analysis`](docs/analysis): actores, procesos, procedimientos,
  requerimientos y recursos.
- [`docs/getting-started.md`](docs/getting-started.md): guia paso a paso para
  levantar el proyecto en Linux, MacOS y Windows.
- [`docs/uv.md`](docs/uv.md): explicacion de como usamos `uv` en el proyecto.
- [`docs/deployment`](docs/deployment): guias cortas por sistema operativo.
- [`database/schema.sql`](database/schema.sql): borrador manual del esquema SQL
  a completar en MySQL.

## Como trabajar este repo

1. Lee primero `docs/analysis`.
2. Estudia el ERD en `docs/database/erd.md`.
3. Revisa la explicacion tabla por tabla.
4. Escribe el SQL manualmente en `database/schema.sql`.
5. Valida cada tabla entendiendo que regla del negocio protege.

La regla es simple: si no puedes explicar una tabla, no la metas.
