# Deploy local en este dispositivo

Esta guia explica como dejar funcionando la aplicacion de Zarvent Repuestos en
este equipo de desarrollo.

No es un deploy de produccion en internet. Es un despliegue local para defensa,
pruebas y demostracion academica en Windows con MySQL local.

## Entorno esperado

Este dispositivo usa:

- Windows
- Python con entorno virtual local `venv`
- MySQL Server instalado como servicio `MySQL80`
- Flask como interfaz web simple
- Base de datos local en `127.0.0.1:3306`

La aplicacion se abre desde el navegador en:

```text
http://127.0.0.1:5000
```

## 1. Verificar MySQL

Primero revisa que el servicio de MySQL este encendido:

```powershell
Get-Service MySQL80
```

Si aparece `Running`, MySQL esta activo.

Si aparece detenido, inicia el servicio:

```powershell
Start-Service MySQL80
```

Si PowerShell pide permisos, abre la terminal como administrador.

## 2. Entrar al proyecto

Desde PowerShell, entra a la carpeta del repositorio:

```powershell
cd "C:\Users\Emanuel Justiniano\Documents\Python\zarvent\sis122-zarvent-repuestos"
```

## 3. Preparar Python

Si el entorno `venv` ya existe, no hace falta crearlo otra vez. Solo verifica
que Python y las librerias funcionen:

```powershell
.\venv\Scripts\python.exe scripts\check_environment.py
```

Debe mostrar `OK` para:

- `bcrypt`
- `flask`
- `mysql-connector-python`
- `python-dotenv`

Si falta alguna libreria, instala dependencias:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Revisar el archivo `.env`

El archivo `.env` guarda los datos de conexion local. Debe tener esta forma:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=cesarszv
DB_PASSWORD=cesarszv
```

La contrasena puede ser diferente si el usuario de MySQL fue creado con otra
clave. Lo importante es que coincida con un usuario real de MySQL que tenga
permiso sobre la base `sis122_zarvent_repuestos`.

No subas `.env` a Git. Ese archivo es local porque contiene credenciales.

## 5. Crear la base de datos y usuario de aplicacion

Ejecuta los scripts SQL en orden. Cada comando pedira la contrasena del usuario
administrador de MySQL, normalmente `root`.

```powershell
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\001_create_database.sql --admin-user root
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\002_users.sql --admin-user root
.\venv\Scripts\python.exe scripts\000_run_sql_file.py scripts\003_create_app_user.sql --admin-user root
```

Que hace cada script:

- `001_create_database.sql`: crea la base `sis122_zarvent_repuestos`.
- `002_users.sql`: crea la tabla `users`.
- `003_create_app_user.sql`: crea usuarios MySQL para conectarse desde Python.

## 6. Crear el usuario demo

Despues de crear la base y la tabla, registra el usuario demo:

```powershell
.\venv\Scripts\python.exe scripts\004_seed_demo_user.py
```

Credenciales demo:

```text
usuario: admin
contrasena: admin123
```

La contrasena se guarda con hash `bcrypt`, no como texto plano.

## 7. Verificar la base

Antes de iniciar Flask, confirma que Python puede conectarse a MySQL:

```powershell
.\venv\Scripts\python.exe scripts\005_check_database.py
```

Un resultado correcto se ve parecido a esto:

```text
Database: sis122_zarvent_repuestos
Table users: OK
Users registered: 1
```

Si aparece `Access denied`, el problema esta en el usuario o contrasena del
archivo `.env`.

## 8. Iniciar la aplicacion

Para desarrollo normal:

```powershell
.\venv\Scripts\python.exe app.py
```

Luego abre:

```text
http://127.0.0.1:5000
```

Para una demostracion local mas limpia, sin el recargador automatico de Flask:

```powershell
.\venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

Ambas formas sirven en este proyecto. La segunda evita que Flask cree procesos
extra durante la demostracion.

## 9. Reiniciar la aplicacion

Si el puerto `5000` ya esta ocupado, revisa que proceso lo usa:

```powershell
Get-NetTCPConnection -LocalPort 5000
```

Para cerrar procesos de esta aplicacion:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -and $_.CommandLine -like '*sis122-zarvent-repuestos*app.py*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

Despues vuelve a iniciar Flask con el comando del paso 8.

## Checklist rapido

Antes de defender o mostrar el sistema:

1. `Get-Service MySQL80` muestra `Running`.
2. `.env` tiene credenciales correctas.
3. `scripts\check_environment.py` muestra todas las dependencias en `OK`.
4. `scripts\005_check_database.py` muestra `Table users: OK`.
5. Flask responde en `http://127.0.0.1:5000`.
6. El login demo funciona con `admin` y `admin123`.

## Problemas comunes

| Problema | Causa probable | Solucion |
| --- | --- | --- |
| `Access denied` | Usuario o contrasena incorrectos en `.env`. | Revisar `.env` o ejecutar `003_create_app_user.sql` con `root`. |
| `Unknown database` | La base no fue creada. | Ejecutar `001_create_database.sql`. |
| `Table 'users' doesn't exist` | Falta la tabla de login. | Ejecutar `002_users.sql`. |
| Puerto `5000` ocupado | Ya hay otra instancia de Flask activa. | Cerrar procesos anteriores y reiniciar. |
| Login incorrecto | Usuario demo no fue creado o la clave cambio. | Ejecutar `004_seed_demo_user.py`. |

