# Deploy local en Windows

Esta guia resume el deploy local en Windows. El flujo oficial usa `uv`.

No es un deploy de produccion en internet. Es un despliegue local para defensa,
pruebas y demostracion academica con MySQL local.

## 1. Verificar UV

```powershell
uv --version
```

Si falta:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y abre PowerShell si el comando `uv` no aparece inmediatamente.

## 2. Verificar MySQL

```powershell
Get-Service MySQL80
```

Si aparece detenido:

```powershell
Start-Service MySQL80
```

Si PowerShell pide permisos, abre la terminal como administrador.

## 3. Preparar el proyecto

```powershell
uv python install 3.14
uv sync
uv run python scripts\development\check_python_environment.py
```

## 4. Crear `.env`

```powershell
Copy-Item .env.example .env
```

El archivo debe quedar parecido a esto:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=cesarszv
DB_PASSWORD=cesarszv
```

## 5. Crear base y tabla de login

Cada comando pedira la contrasena del usuario administrador de MySQL.

```powershell
uv run python scripts\database\run_sql_file.py scripts\database\001_create_database.sql --admin-user root
uv run python scripts\database\run_sql_file.py scripts\database\002_create_users_table.sql --admin-user root
uv run python scripts\database\run_sql_file.py scripts\database\003_create_app_user.sql --admin-user root
uv run python scripts\database\seed_demo_user.py
uv run python scripts\database\check_database.py
```

## 6. Iniciar Flask

```powershell
uv run python -m flask --app zarvent_repuestos.interfaces.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

Abre:

```text
http://127.0.0.1:5000
```

Usuario demo:

```text
usuario: admin
contrasena: admin123
```
