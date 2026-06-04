# Conectar MySQL de Zarvent Repuestos a JetBrains DataGrip

Esta guia explica como conectar **JetBrains DataGrip** a la base de datos local
del proyecto `Zarvent Repuestos`.

El objetivo no es cambiar la base desde DataGrip sin entenderla. El objetivo es
usar DataGrip como una herramienta visual para revisar tablas, datos,
relaciones y consultas SQL del proyecto.

## Datos de conexion del proyecto

La app Flask lee estos datos desde el archivo `.env`:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=zarvent_app
DB_PASSWORD=change_me
```

En DataGrip se cargan asi:

| Campo en DataGrip | Valor para este proyecto |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `zarvent_app` |
| Password | `change_me` |
| Database | `sis122_zarvent_repuestos` |
| URL | `jdbc:mysql://127.0.0.1:3306/sis122_zarvent_repuestos` |

Si tu `.env` tiene otro usuario o contrasena, usa los valores de tu `.env`, no
los de esta guia.

## 1. Verificar que MySQL este encendido

DataGrip no crea el servidor MySQL. Primero MySQL Server debe estar instalado y
encendido en tu computadora.

En Linux:

```bash
sudo systemctl status mysql
```

Si esta detenido:

```bash
sudo systemctl start mysql
```

En MacOS con Homebrew:

```bash
brew services list
brew services start mysql
```

En Windows PowerShell:

```powershell
Get-Service MySQL80
Start-Service MySQL80
```

## 2. Verificar que la base ya exista desde el proyecto

Antes de abrir DataGrip, revisa que el proyecto pueda conectarse a MySQL.

Desde la raiz del repositorio:

```bash
cd /home/cszv/Documents/UCB-LIA/sis122/assignments/final_project
uv sync
uv run python scripts/database/check_login_database.py
```

Resultado esperado:

```text
Database: sis122_zarvent_repuestos
Table users: OK
Users registered: 1
```

Si aparece `Access denied`, `Unknown database` o `Table users doesn't exist`,
primero prepara la base:

```bash
uv run python scripts/database/setup_database.py
```

En Linux, si `root` de MySQL funciona con `sudo mysql` y no con contrasena:

```bash
uv run python scripts/database/setup_database.py --admin-mode sudo-mysql
```

Ese script crea:

- la base `sis122_zarvent_repuestos`;
- el usuario MySQL `zarvent_app`;
- las tablas fisicas del prototipo;
- datos demo para login, inventario, clientes, ventas y pagos.

## 3. Crear la conexion en DataGrip

Abre DataGrip y sigue estos pasos:

1. En el panel izquierdo, haz clic en `+`.
2. Selecciona `Data Source`.
3. Selecciona `MySQL`.
4. Si DataGrip pide descargar el driver, acepta `Download Driver Files`.
5. Completa los campos de conexion:

```text
Name: Zarvent Repuestos Local
Host: 127.0.0.1
Port: 3306
User: zarvent_app
Password: change_me
Database: sis122_zarvent_repuestos
```

Tambien puedes revisar que la URL quede asi:

```text
jdbc:mysql://127.0.0.1:3306/sis122_zarvent_repuestos
```

Luego haz clic en `Test Connection`.

Si DataGrip muestra un mensaje de conexion exitosa, haz clic en `OK` o
`Apply`.

## 4. Seleccionar el esquema correcto

Despues de conectar, DataGrip puede mostrar el servidor MySQL pero no siempre
muestra todas las tablas inmediatamente.

En la conexion `Zarvent Repuestos Local`:

1. Abre la configuracion de la conexion.
2. Entra a la pestana `Schemas`.
3. Marca `sis122_zarvent_repuestos`.
4. Guarda con `Apply`.
5. En el panel izquierdo, haz clic derecho sobre la conexion.
6. Selecciona `Refresh`.

Ahora deberias ver tablas como:

```text
users
person
customer
part_category
part
inventory_stock
sales_order
sales_order_item
payment
```

El ERD documentado es mas amplio que el prototipo web actual. Por eso algunas
tablas del modelo completo pueden estar documentadas como mejora futura aunque
la demo Flask se enfoque en login, inventario, clientes, ventas y pagos.

## 5. Probar consultas simples

Para comprobar que DataGrip esta leyendo la misma base que usa Flask, abre una
consola SQL sobre la conexion y ejecuta:

```sql
SELECT DATABASE();
```

Debe devolver:

```text
sis122_zarvent_repuestos
```

Luego revisa el usuario demo:

```sql
SELECT id, username
FROM users;
```

No consultes ni copies hashes de contrasenas en una presentacion. Solo muestra
que el usuario existe.

Tambien puedes revisar categorias de repuestos:

```sql
SELECT part_category_id, name, description
FROM part_category
ORDER BY name;
```

Y stock disponible:

```sql
SELECT
  p.internal_code,
  p.name,
  p.brand,
  s.quantity_on_hand,
  s.location_name
FROM part AS p
JOIN inventory_stock AS s ON s.part_id = p.part_id
ORDER BY p.name;
```

## 6. Que explicar si lo muestras en la defensa

La explicacion simple es:

```text
Flask no guarda datos en memoria.
Flask lee .env.
Python usa mysql-connector-python.
Python se conecta a MySQL con zarvent_app.
MySQL guarda los datos en sis122_zarvent_repuestos.
DataGrip se conecta a la misma base para verla y consultar SQL.
```

La idea importante es que DataGrip no reemplaza al modelo relacional. Solo ayuda
a observarlo.

Puedes explicar estas separaciones:

- `person` guarda datos personales.
- `customer` representa a una persona dentro del flujo comercial.
- `part` guarda el repuesto.
- `inventory_stock` guarda la cantidad disponible del repuesto.
- `sales_order` guarda la cabecera de la venta.
- `sales_order_item` guarda cada linea de la venta.
- `payment` guarda el pago asociado a la venta.

## 7. Problemas comunes

| Problema en DataGrip | Causa probable | Solucion |
| --- | --- | --- |
| `Connection refused` | MySQL Server esta apagado. | Enciende MySQL y vuelve a probar. |
| `Access denied for user 'zarvent_app'` | El usuario o la contrasena no coinciden con MySQL. | Revisa `.env` y ejecuta `setup_database.py`. |
| `Unknown database 'sis122_zarvent_repuestos'` | La base todavia no fue creada. | Ejecuta `uv run python scripts/database/setup_database.py`. |
| No aparecen tablas | El esquema no esta marcado en DataGrip. | Marca `sis122_zarvent_repuestos` en `Schemas` y haz `Refresh`. |
| Aparece otra base | DataGrip se conecto con otro `Database`. | Corrige el campo `Database` o la URL JDBC. |
| El proyecto funciona pero DataGrip no | DataGrip usa otros datos de conexion. | Copia exactamente `host`, `port`, `user`, `password` y `database` desde `.env`. |

## 8. Checklist final

Antes de presentar, confirma:

1. MySQL Server esta encendido.
2. `.env` existe en la raiz del proyecto.
3. `.env` apunta a `sis122_zarvent_repuestos`.
4. `uv run python scripts/database/check_login_database.py` funciona.
5. DataGrip tiene host `127.0.0.1` y puerto `3306`.
6. DataGrip usa el usuario `zarvent_app`.
7. El esquema `sis122_zarvent_repuestos` esta seleccionado.
8. Puedes ejecutar `SELECT DATABASE();` desde DataGrip.

Si esos puntos funcionan, DataGrip ya esta conectado al mismo entorno de base
de datos que usa la aplicacion Flask.
