# Getting Started

Esta guia deja el proyecto listo para una presentacion local. El flujo oficial
del repositorio usa **UV** para Python. No usamos `pip` manual ni `python -m
venv` como pasos del proyecto.

La meta es dejar funcionando:

- MySQL Server con la base `sis122_zarvent_repuestos`.
- El entorno Python creado por `uv`.
- La tabla `users` del prototipo de login.
- Un usuario demo para entrar a la pantalla web.
- Flask en `http://127.0.0.1:5000`.

El modelo relacional completo se defiende desde `docs/database`. La app Flask
actual solo demuestra conexion a MySQL, login y contrasenas con `bcrypt`.

## 1. Instalar UV

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Si no tienes `curl`:

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
uv --version
```

### MacOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv --version
```

Si usas Homebrew:

```bash
brew install uv
uv --version
```

### Windows

En PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv --version
```

Si `uv` no se reconoce despues de instalarlo, cierra y abre la terminal.

## 2. Instalar y encender MySQL Server

Si MySQL ya esta instalado, solo verifica que este encendido.

### Linux

En Ubuntu o Debian:

```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl status mysql
```

Si el servicio esta detenido:

```bash
sudo systemctl start mysql
```

### MacOS

Con Homebrew:

```bash
brew install mysql
brew services start mysql
brew services list
```

### Windows

Instala **MySQL Installer** o **MySQL Server** desde el sitio oficial de MySQL.
Luego verifica el servicio:

```powershell
Get-Service MySQL80
```

Si aparece detenido:

```powershell
Start-Service MySQL80
```

Si PowerShell pide permisos, abre la terminal como administrador.

## 3. Entrar al proyecto

### Linux

```bash
cd /ruta/al/proyecto/sis122-zarvent-repuestos
```

### MacOS

```bash
cd /ruta/al/proyecto/sis122-zarvent-repuestos
```

### Windows

```powershell
cd "C:\ruta\al\proyecto\sis122-zarvent-repuestos"
```

Todos los comandos siguientes se ejecutan desde la raiz del repositorio.

## 4. Preparar Python con UV

`uv sync` lee `pyproject.toml` y `uv.lock`, crea o actualiza `.venv`, instala
las dependencias y deja el proyecto listo para ejecutar.

### Linux

```bash
uv python install 3.14
uv sync
uv run python scripts/development/check_python_environment.py
```

### MacOS

```bash
uv python install 3.14
uv sync
uv run python scripts/development/check_python_environment.py
```

### Windows

```powershell
uv python install 3.14
uv sync
uv run python scripts\development\check_python_environment.py
```

Debe aparecer `OK` para:

- `bcrypt`
- `flask`
- `mysql-connector-python`
- `python-dotenv`

## 5. Crear el archivo `.env`

El archivo `.env` contiene las credenciales locales de MySQL. No se sube a
Git.

### Linux

```bash
cp .env.example .env
```

### MacOS

```bash
cp .env.example .env
```

### Windows

```powershell
Copy-Item .env.example .env
```

Luego edita `.env` con un usuario creado para el proyecto:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=zarvent_app
DB_PASSWORD=change_me
```

Lo importante es que `DB_USER` y `DB_PASSWORD` coincidan con un usuario real de
MySQL. El script `003_create_mysql_app_users.sql` crea `zarvent_app` para el
prototipo.

## 6. Probar el acceso administrador a MySQL

Este paso solo verifica que conoces la contrasena del usuario administrador,
normalmente `root`.

### Linux

```bash
uv run python scripts/development/check_mysql_admin_connection.py
```

### MacOS

```bash
uv run python scripts/development/check_mysql_admin_connection.py
```

### Windows

```powershell
uv run python scripts\development\check_mysql_admin_connection.py
```

El script pide la contrasena de `root` y no la guarda.

## 7. Configuración unificada de Base de Datos y Datos de Prueba

Esta es la forma recomendada y más rápida. Ejecuta el script unificado de configuración de base de datos de Python:

### Linux / MacOS

```bash
uv run python scripts/database/setup_database.py
```

### Windows

```powershell
uv run python scripts\database\setup_database.py
```

Este script unificado automatiza los siguientes pasos:
1. Te pide la contraseña de `root` (u otro usuario administrador) de tu MySQL local.
2. Crea la base de datos `sis122_zarvent_repuestos`.
3. Crea el usuario local de la aplicación (indicado en tu `.env`, ej. `cesarszv` con contraseña `cesarszv`) y le otorga privilegios.
4. Genera físicamente todas las tablas del esquema relacional del proyecto.
5. Puebla las tablas de repuestos, categorías, clientes y ventas históricas para coincidir con tus mockups.

*(Opcional: Si deseas ejecutar manualmente los scripts SQL individuales con un usuario administrador, puedes seguir el paso 8)*.

| Script | Resultado |
| --- | --- |
| `001_create_project_database.sql` | Crea la base `sis122_zarvent_repuestos`. |
| `002_create_login_users_table.sql` | Crea la tabla `users` del login demo. |
| `003_create_mysql_app_users.sql` | Crea el usuario MySQL para conectarse desde Python. |

## 8. Alternativa con MySQL Shell

Usa esta opcion si quieres mostrar exactamente que SQL se ejecuta.

### Linux

```text
\sql
\connect root@localhost
\source scripts/database/001_create_project_database.sql
\source scripts/database/002_create_login_users_table.sql
\source scripts/database/003_create_mysql_app_users.sql
```

### MacOS

```text
\sql
\connect root@localhost
\source scripts/database/001_create_project_database.sql
\source scripts/database/002_create_login_users_table.sql
\source scripts/database/003_create_mysql_app_users.sql
```

### Windows

```text
\sql
\connect root@localhost
\source scripts\database\001_create_project_database.sql
\source scripts\database\002_create_login_users_table.sql
\source scripts\database\003_create_mysql_app_users.sql
```

El SQL esencial es:

```sql
CREATE DATABASE IF NOT EXISTS sis122_zarvent_repuestos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sis122_zarvent_repuestos;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL
);

CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me';
CREATE USER IF NOT EXISTS 'zarvent_app'@'%' IDENTIFIED BY 'change_me';

GRANT SELECT, INSERT, UPDATE, DELETE
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE
ON sis122_zarvent_repuestos.*
TO 'zarvent_app'@'%';

FLUSH PRIVILEGES;
```

## 9. Poblar la base de datos con datos de prueba (Recomendado)

Para que la aplicación muestre toda la información operativa (catálogo de repuestos, categorías, clientes y transacciones de ventas) de forma idéntica a los mockups de diseño, ejecuta el script de población completo:

### Linux / MacOS

```bash
uv run python scripts/database/seed_project_data.py
```

### Windows

```powershell
uv run python scripts\database\seed_project_data.py
```

Esto creará de forma automática en la base de datos:
- El usuario administrativo `admin` con la contraseña `admin123` (encriptada con bcrypt).
- Las categorías iniciales: *Engine Parts*, *Transmission*, *Electrical*, *Suspension*.
- Los repuestos iniciales con sus códigos internos, OEM, costos y cantidades en stock.
- Clientes de ejemplo registrados.
- Historial de transacciones de ventas y pagos asociados.

*(Si solo deseas crear el usuario administrativo básico vacío, puedes correr opcionalmente `uv run python scripts/database/seed_demo_login_user.py`)*.

## 10. Verificar la base de datos

### Linux

```bash
uv run python scripts/database/check_login_database.py
```

### MacOS

```bash
uv run python scripts/database/check_login_database.py
```

### Windows

```powershell
uv run python scripts\database\check_login_database.py
```

Resultado esperado:

```text
Database: sis122_zarvent_repuestos
Table users: OK
Users registered: 1
```

## 11. Iniciar Flask

Para desarrollo normal:

### Linux

```bash
uv run python -m zarvent_repuestos.web.app
```

### MacOS

```bash
uv run python -m zarvent_repuestos.web.app
```

### Windows

```powershell
uv run python -m zarvent_repuestos.web.app
```

Luego abre:

```text
http://127.0.0.1:5000
```

Para presentacion, usa el comando sin recargador automatico:

### Linux

```bash
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

### MacOS

```bash
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

### Windows

```powershell
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

En el login:

```text
usuario: admin
contrasena: admin123
```

## 12. Checklist antes de presentar

1. `uv --version` funciona.
2. MySQL Server esta encendido.
3. `uv sync` ya fue ejecutado.
4. `.env` existe y apunta a `sis122_zarvent_repuestos`.
5. Los tres scripts SQL ya fueron ejecutados.
6. `seed_demo_login_user.py` ya creo el usuario `admin`.
7. `check_login_database.py` muestra `Table users: OK`.
8. Flask abre en `http://127.0.0.1:5000`.
9. El login funciona con `admin` y `admin123`.

## 13. Problemas comunes

| Problema | Causa probable | Solucion |
| --- | --- | --- |
| `uv` no se reconoce | La terminal no actualizo el `PATH`. | Cierra y abre la terminal. |
| `Access denied` | Usuario o contrasena incorrectos en `.env`. | Revisa `.env` o ejecuta `003_create_mysql_app_users.sql`. |
| `Unknown database` | La base no fue creada. | Ejecuta `001_create_project_database.sql`. |
| `Table 'users' doesn't exist` | Falta la tabla del login. | Ejecuta `002_create_login_users_table.sql`. |
| Login incorrecto | Falta el usuario demo o la clave cambio. | Ejecuta `seed_demo_login_user.py`. |
| Puerto `5000` ocupado | Ya hay otra app usando ese puerto. | Cierra la app anterior o usa otro puerto. |

## 14. Que explicar en la defensa

Para no confundir el alcance:

- El ERD completo esta en `docs/database/erd.md`.
- La explicacion tabla por tabla esta en `docs/database/db_explanation.md`.
- La defensa tecnica esta en `docs/database/erd_explanation.md`.
- El borrador del esquema completo esta en `database/schema.sql`.
- La app Flask actual solo demuestra conexion, tabla `users`, login y hash de
  contrasena.

La idea importante es simple: `uv` facilita ejecutar el proyecto, pero la
defensa principal sigue siendo el modelo relacional.
