# Deploy local en Linux

Esta guia resume el deploy local en Linux. El flujo oficial usa `uv`.

## 1. Verificar UV

```bash
uv --version
```

Si falta:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 2. Verificar MySQL

```bash
sudo systemctl status mysql
```

Si esta detenido:

```bash
sudo systemctl start mysql
```

## 3. Preparar el proyecto

```bash
uv python install 3.14
uv sync
uv run python scripts/development/check_python_environment.py
```

## 4. Crear `.env`

```bash
cp .env.example .env
```

Edita `.env` con el usuario MySQL del proyecto.

## 5. Crear base y tabla de login

```bash
uv run python scripts/database/run_mysql_script.py scripts/database/001_create_project_database.sql --admin-user root
uv run python scripts/database/run_mysql_script.py scripts/database/002_create_login_users_table.sql --admin-user root
uv run python scripts/database/run_mysql_script.py scripts/database/003_create_mysql_app_users.sql --admin-user root
uv run python scripts/database/seed_demo_login_user.py
uv run python scripts/database/check_login_database.py
```

## 6. Iniciar Flask

```bash
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

Abre:

```text
http://127.0.0.1:5000
```
