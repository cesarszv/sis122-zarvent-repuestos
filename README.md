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

El proyecto se puede usar de dos formas:

- con Python nativo y `pip`;
- con `uv`, que lee `pyproject.toml` y `uv.lock`.

Las dependencias externas son pocas:

- `mysql-connector-python`: permite conectar Python con MySQL Server.
- `python-dotenv`: permite leer las credenciales desde `.env`.
- `bcrypt`: permite trabajar contrasenas con hash.
- `flask`: permite mostrar una pantalla web simple para el login.

La interfaz actual usa Flask porque permite separar de forma simple:

- `app.py`: rutas de la aplicacion.
- `templates/`: pantallas HTML.
- `static/`: CSS, imagenes y archivos publicos.

Estructura recomendada para el prototipo web:

```text
sis122-zarvent-repuestos/
|-- app.py
|-- db.py
|-- user_service.py
|-- templates/
|   `-- login.html
|-- static/
|   |-- css/
|   |   `-- style.css
|   `-- img/
`-- venv/
```

`db.py` y `user_service.py` no reemplazan la estructura del profesor. Solo
separan la conexion MySQL y la logica de usuarios para que `app.py` no quede
mezclado con todo.

### Opcion A: Python nativo

El profesor recomienda crear un entorno virtual local llamado `venv`.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\check_environment.py
python app.py
```

Si Windows no reconoce `python`, usa `py` en el primer comando:

```powershell
py -m venv venv
```

Despues de activar `venv`, `python` debe apuntar al entorno virtual.

### Opcion B: UV

Primero instala `uv` una sola vez si el equipo no lo tiene:

```powershell
py -m pip install --user uv
```

Si despues de instalar aparece el mensaje `uv no se reconoce`, abre una nueva
terminal o usa `py -m uv` en lugar de `uv`.

Luego, dentro del repo:

```powershell
uv sync
uv run python scripts\check_environment.py
uv run python app.py
```

Comandos equivalentes si la terminal todavia no reconoce `uv`:

```powershell
py -m uv sync
py -m uv run python scripts\check_environment.py
py -m uv run python app.py
```

### Ejecutar la pantalla de login

Cuando `app.py` este corriendo, abre:

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
|-- 001_create_database.sql
|-- 002_users.sql
|-- 003_create_app_user.sql
|-- 004_seed_demo_user.py
`-- 005_check_database.py
```

Como el comando `mysql` puede no estar en el `PATH`, el repo incluye un
ejecutor pequeno que usa `mysql-connector-python` y pide la contrasena del
usuario administrador sin guardarla:

```powershell
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\001_create_database.sql --admin-user root
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\002_users.sql --admin-user root
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\003_create_app_user.sql --admin-user root
.\venv\Scripts\python.exe scripts\004_seed_demo_user.py
.\venv\Scripts\python.exe scripts\005_check_database.py
```

Si prefieres MySQL Workbench, ejecuta estos SQL en el mismo orden:

```sql
SOURCE scripts/001_create_database.sql;
SOURCE scripts/002_users.sql;
SOURCE scripts/003_create_app_user.sql;
```

El usuario demo queda asi si no pasas argumentos:

```text
usuario: admin
contrasena: admin123
```

Despues levanta la app:

```powershell
.\venv\Scripts\python.exe app.py
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
- [`database/schema.sql`](database/schema.sql): borrador manual del esquema SQL
  a completar en MySQL.

## Como trabajar este repo

1. Lee primero `docs/analysis`.
2. Estudia el ERD en `docs/database/erd.md`.
3. Revisa la explicacion tabla por tabla.
4. Escribe el SQL manualmente en `database/schema.sql`.
5. Valida cada tabla entendiendo que regla del negocio protege.

La regla es simple: si no puedes explicar una tabla, no la metas.
