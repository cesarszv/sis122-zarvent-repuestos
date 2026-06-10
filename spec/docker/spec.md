# Especificacion Docker

## Objetivo

Dockerizar **Zarvent Repuestos** y dejar un artefacto listo para copiar a USB
desde Ubuntu Linux y ejecutar en computadoras Windows de la universidad con
Docker instalado.

El objetivo no es cambiar la aplicacion. El objetivo es empacar el proyecto
actual para que Flask, MySQL y los datos demo funcionen de forma reproducible en
la defensa.

## Requisitos

1. Al finalizar, debe existir un artefacto dentro de `./presentation` que pueda
   copiar a un USB. Ese artefacto se genera localmente en Ubuntu Linux.
2. En Windows, con Docker Desktop instalado, debe poder ejecutarse todo el
   proyecto usando solamente el contenido copiado desde `./presentation`.
3. El artefacto debe incluir instrucciones cortas para arrancar, detener y
   reiniciar el entorno.
4. Una vez en ejecucion, debe ser posible inspeccionar la base de datos desde
   JetBrains DataGrip conectandose al contenedor de MySQL por un puerto publicado
   en `localhost`.
5. El proyecto debe conservar el flujo real del repositorio: aplicacion Flask en
   Python, base de datos MySQL y seed de datos demo.
6. Durante la presentacion debe poder abrirse el codigo fuente del proyecto
   desde la carpeta copiada al USB. Si se edita el codigo, el contenedor web debe
   poder reiniciarse y tomar esos cambios.

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
- Base por defecto: `sis122_zarvent_repuestos`.
- Usuario MySQL de la aplicacion: `zarvent_app`.
- Password demo por defecto: `change_me`.
- Puerto MySQL por defecto: `3306`.
- Variable de clave Flask: `FLASK_SECRET_KEY`.

## Aplicacion web

- Modulo Flask principal: `zarvent_repuestos.web.app`.
- Comando local actual:

```bash
uv run python -m zarvent_repuestos.web.app
```

- Comando equivalente para ejecucion controlada:

```bash
uv run python -m flask --app zarvent_repuestos.web.app:app run --host 0.0.0.0 --port 5000 --no-debugger --no-reload
```

- El contenedor web debe exponer la aplicacion en `localhost:5000` o documentar
  claramente el puerto final si se elige otro.

## Codigo fuente en la defensa

Docker no reemplaza al codigo fuente. Docker solo crea el entorno donde se
ejecuta la aplicacion.

Para la defensa, el artefacto debe incluir una copia del repositorio fuente
dentro de `./presentation`, por ejemplo en:

```text
presentation/
  source/
    pyproject.toml
    uv.lock
    .python-version
    src/
    scripts/
    database/
    docs/
```

El contenedor web debe usar ese codigo de una de estas dos formas:

1. Montando `./source` como volumen dentro del contenedor. Esta opcion es mejor
   para la defensa porque permite abrir y editar archivos desde Windows, luego
   reiniciar el contenedor web y ver los cambios.
2. Copiando `./source` dentro de la imagen Docker. Esta opcion es mas cerrada:
   sirve para ejecutar, pero no es comoda si necesito editar codigo durante la
   presentacion.

La opcion preferida para este proyecto es montar `./source` como volumen, porque
permite explicar y modificar el codigo sin reconstruir toda la imagen.

## Base de datos

La configuracion actual se lee desde `.env` o variables de entorno:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=zarvent_app
DB_PASSWORD=change_me
FLASK_SECRET_KEY=zarvent-academic-secret-key-122
```

En Docker, `DB_HOST` no debe apuntar a `127.0.0.1` desde el contenedor web.
Debe apuntar al nombre del servicio MySQL definido en `docker-compose.yml`.

Tablas creadas por la aplicacion:

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

## Datos demo

El seed real esta en `scripts/database/seed_project_data.py`.

Debe cargar:

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
- Un proveedor demo y una orden de compra pendiente cuando todavia no existen
  compras demo.

## Requisito para DataGrip

El contenedor MySQL debe publicar un puerto accesible desde Windows para que
DataGrip pueda conectarse.

Valores esperados para DataGrip, salvo que el artefacto final documente otro
puerto:

| Campo | Valor |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3306` |
| User | `zarvent_app` |
| Password | `change_me` |
| Database | `sis122_zarvent_repuestos` |
| URL JDBC | `jdbc:mysql://127.0.0.1:3306/sis122_zarvent_repuestos` |

## Entregable

- Todo debe quedar dentro de `./presentation`, de modo que esa carpeta pueda
  copiarse al USB y tambien conservarse localmente en el proyecto.
- El artefacto debe incluir, como minimo:
  - una copia del repositorio fuente en `presentation/source`;
  - archivos Docker necesarios para levantar Flask y MySQL;
  - instrucciones de ejecucion para Windows;
  - instrucciones de conexion desde DataGrip;
  - datos de acceso demo (`admin` / `admin123`);
  - una forma clara de reiniciar desde cero los contenedores y volumenes.

## Criterios de aceptacion

1. En una maquina limpia con Docker, el proyecto levanta desde `./presentation`
   sin instalar Python, `uv` ni MySQL en el sistema host.
2. La web abre en el navegador y permite iniciar sesion con `admin` /
   `admin123`.
3. La base `sis122_zarvent_repuestos` existe dentro del contenedor MySQL.
4. DataGrip puede conectarse al MySQL dockerizado usando los datos documentados.
5. Las tablas y datos demo aparecen en DataGrip.
6. El artefacto no depende de rutas absolutas de la maquina local.
7. El codigo fuente se puede abrir desde `presentation/source`.
8. Si se edita codigo fuente, se puede reiniciar el contenedor web para ejecutar
   la version editada.
