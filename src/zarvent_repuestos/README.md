# Guia simple de `src/`

Esta carpeta guarda el codigo Python real de la aplicacion.

La idea no es tener una arquitectura complicada. La idea es separar el codigo
en partes faciles de explicar:

- `access/`: login y usuarios.
- `config/`: datos de configuracion.
- `crud/`: consultas SQL y operaciones con MySQL.
- `database/`: conexion, creacion de tablas y trazador SQL.
- `models/`: clases simples que representan datos del negocio.
- `web/`: Flask, pantallas HTML, CSS e imagenes.

## Mapa rapido

```text
src/
|-- README.md
+-- zarvent_repuestos/
    |-- __init__.py
    |-- access/
    |-- config/
    |-- crud/
    |-- database/
    |-- models/
    +-- web/
```

## Flujo principal de la app

```text
1. El usuario entra a una pantalla en web/.
2. Flask recibe la accion en web/app.py.
3. app.py llama una funcion de crud/.
4. crud/ usa database/connection.py.
5. MySQL guarda o devuelve datos.
6. Flask muestra el resultado con templates/.
```

Ese es el camino principal del sistema.

## `zarvent_repuestos/`

```text
zarvent_repuestos/
|-- __init__.py
|-- access/
|-- config/
|-- crud/
|-- database/
|-- models/
+-- web/
```

Esta es la carpeta principal del paquete Python.

Se llama `zarvent_repuestos` porque todo el codigo pertenece al sistema
academico de Zarvent Repuestos.

### `__init__.py`

```text
zarvent_repuestos/
+-- __init__.py
```

Marca la carpeta como un paquete de Python.

En simple: permite importar codigo usando rutas como esta:

```python
from zarvent_repuestos.web.app import app
```

No tiene reglas del negocio. Solo ayuda a organizar el proyecto.

## `access/`

```text
access/
|-- __init__.py
+-- user_service.py
```

Esta carpeta maneja el acceso al sistema.

Aqui vive la logica del login: crear usuarios, validar contrasenas y buscar
usuarios en la tabla `users`.

### `access/__init__.py`

```text
access/
+-- __init__.py
```

Marca `access/` como una parte importable del proyecto.

No tiene logica importante.

### `access/user_service.py`

```text
access/
+-- user_service.py
```

Trabaja con los usuarios del sistema.

Hace estas tareas:

- protege contrasenas con `bcrypt`;
- compara la contrasena escrita en el login con la contrasena guardada;
- crea usuarios;
- autentica usuarios;
- lista usuarios;
- busca usuarios por ID;
- actualiza usuarios;
- elimina usuarios.

La funcion mas importante para la demo es `authenticate_user()`.

Esa funcion se usa cuando alguien intenta iniciar sesion desde la pantalla de
login.

## `config/`

```text
config/
+-- db_config.py
```

Esta carpeta guarda configuracion.

Por ahora solo tiene la configuracion para conectarse a MySQL.

### `config/db_config.py`

```text
config/
+-- db_config.py
```

Lee las variables del archivo `.env`.

Ejemplo:

```text
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sis122_zarvent_repuestos
DB_USER=zarvent_app
DB_PASSWORD=change_me
```

Despues arma un diccionario llamado `DB_CONFIG`.

Ese diccionario se usa cuando Python necesita abrir una conexion con MySQL.

## `crud/`

```text
crud/
|-- customer_crud.py
|-- part_crud.py
+-- sales_crud.py
```

Esta carpeta contiene funciones que hablan directamente con la base de datos.

`CRUD` significa:

- `Create`: crear datos.
- `Read`: leer datos.
- `Update`: actualizar datos.
- `Delete`: eliminar datos.

En este proyecto, los archivos de `crud/` tienen consultas SQL con
`cursor.execute(...)`.

La app Flask no escribe todo el SQL directamente. Flask llama a estas funciones.

### `crud/customer_crud.py`

```text
crud/
+-- customer_crud.py
```

Maneja clientes y personas.

Sirve para:

- registrar un cliente nuevo;
- guardar primero los datos personales en `person`;
- guardar despues el cliente en `customer`;
- listar clientes;
- buscar clientes por documento de identidad.

Idea importante:

```text
PERSON != CUSTOMER
```

Una persona guarda datos personales. Un cliente es esa persona dentro del flujo
comercial.

### `crud/part_crud.py`

```text
crud/
+-- part_crud.py
```

Maneja el catalogo de repuestos.

Sirve para:

- crear categorias de repuestos;
- listar categorias;
- crear repuestos;
- guardar stock inicial;
- actualizar repuestos;
- listar repuestos con filtros;
- obtener marcas;
- ver alertas de stock bajo.

Relacion principal:

```text
part_category -> part -> inventory_stock
```

En simple:

- una categoria ordena los repuestos;
- un repuesto guarda codigo, nombre, marca y precio;
- el inventario guarda cantidad disponible y ubicacion.

### `crud/sales_crud.py`

```text
crud/
+-- sales_crud.py
```

Maneja ventas, pagos y metricas del dashboard.

Sirve para:

- crear una venta;
- registrar varias lineas de venta;
- descontar stock;
- registrar el pago;
- listar ventas;
- obtener el detalle de un recibo;
- calcular metricas del dashboard.

La funcion mas importante es `crear_orden_venta()`.

Esa funcion usa una transaccion. Eso significa que la venta, los items, el
descuento de stock y el pago se guardan como una sola operacion.

Si algo falla, se hace `rollback()` y la base de datos no queda a medias.

## `database/`

```text
database/
|-- __init__.py
|-- connection.py
|-- init_db.py
+-- sql_trace.py
```

Esta carpeta contiene codigo relacionado con MySQL.

No guarda la logica del negocio. Ayuda a conectar, preparar y observar la base
de datos.

### `database/__init__.py`

```text
database/
+-- __init__.py
```

Marca `database/` como una parte importable del proyecto.

No tiene logica de negocio.

### `database/connection.py`

```text
database/
+-- connection.py
```

Abre la conexion con MySQL.

La funcion principal es `get_database_connection()`.

Los archivos de `crud/` llaman a esa funcion cada vez que necesitan consultar o
modificar datos.

Si `SQL_TRACE_ENABLED=1` esta activado, la conexion se envuelve con el trazador
SQL para mostrar consultas en vivo durante la defensa.

### `database/init_db.py`

```text
database/
+-- init_db.py
```

Ayuda a crear la base y las tablas necesarias para la demo.

Incluye funciones como:

- `initialize_database()`: crea la base de datos si falta;
- `crear_tablas()`: crea las tablas principales que necesita la app.

Sirve para levantar el prototipo local sin crear todo manualmente cada vez.

### `database/sql_trace.py`

```text
database/
+-- sql_trace.py
```

Existe para apoyar la defensa.

Registra las consultas SQL que ejecuta la app con `mysql-connector-python`.

Muestra:

- hora de la consulta;
- ruta de Flask, por ejemplo `POST /sales`;
- tipo de operacion: `SELECT`, `INSERT`, `UPDATE`, `DELETE`;
- tablas probables usadas por la consulta;
- parametros enviados;
- tiempo de ejecucion;
- estado `OK` o `ERROR`.

Esto ayuda a mostrar que la pagina no simula datos. La app llama funciones
Python, esas funciones ejecutan SQL, y MySQL responde.

## `models/`

```text
models/
|-- customer.py
|-- part.py
+-- sales_order.py
```

Esta carpeta contiene clases simples del negocio.

Una clase de modelo representa un objeto importante en Python.

No son tablas por si solas. Solo ayudan a ordenar datos antes de guardarlos o
mostrarlos.

### `models/customer.py`

```text
models/
+-- customer.py
```

Define:

- `Person`: persona con nombre, apellido, documento, telefono, correo y
  direccion.
- `Customer`: persona registrada como cliente del negocio.

Idea importante:

```text
persona != cliente
```

Una persona guarda datos personales. Un cliente participa en ventas.

### `models/part.py`

```text
models/
+-- part.py
```

Define:

- `PartCategory`: categoria del repuesto.
- `Part`: repuesto del catalogo.
- `InventoryStock`: cantidad y ubicacion del repuesto.

Relacion principal:

```text
categoria -> repuesto -> stock
```

La categoria ordena productos. El stock se separa porque una cosa es el
repuesto y otra cosa es cuantas unidades hay.

### `models/sales_order.py`

```text
models/
+-- sales_order.py
```

Define:

- `SalesOrder`: cabecera de la venta.
- `SalesOrderItem`: linea o detalle de la venta.
- `Payment`: pago asociado a la venta.

Relacion principal:

```text
venta -> items de venta -> pago
```

Una venta puede tener varios repuestos. Por eso los items van separados de la
cabecera de la venta.

## `web/`

```text
web/
|-- __init__.py
|-- app.py
|-- static/
+-- templates/
```

Esta carpeta contiene la aplicacion web.

Aqui vive Flask, las rutas, las pantallas HTML, los estilos y las imagenes.

### `web/__init__.py`

```text
web/
+-- __init__.py
```

Marca `web/` como una parte importable del proyecto.

No tiene logica principal.

### `web/app.py`

```text
web/
+-- app.py
```

Es el archivo principal de Flask.

Define las rutas:

- `/`: pantalla de login;
- `/logout`: cierra sesion;
- `/dashboard`: muestra indicadores;
- `/inventory`: muestra y registra repuestos;
- `/sales`: muestra y registra ventas;
- `/sales/receipt/<id>`: muestra un recibo;
- `/sql-trace`: muestra consultas SQL en vivo para la defensa;
- `/api/sql-trace`: entrega los datos del trazador SQL;
- `/api/sql-trace/clear`: limpia el trazador SQL.

## `web/templates/`

```text
templates/
|-- dashboard.html
|-- inventory.html
|-- layout.html
|-- login.html
|-- receipt.html
|-- sales.html
+-- sql_trace.html
```

Esta carpeta guarda las pantallas HTML.

Flask usa estos archivos para mostrar la aplicacion en el navegador.

### `templates/layout.html`

Es la base visual de las pantallas internas.

Tiene la barra lateral, el encabezado, los estilos generales y el espacio donde
se carga cada pagina.

### `templates/login.html`

Muestra el formulario de inicio de sesion.

El usuario escribe su usuario y contrasena. Flask valida esos datos usando
`access/user_service.py`.

### `templates/dashboard.html`

Muestra indicadores generales del negocio:

- ventas del dia;
- cantidad de categorias;
- productos con stock bajo;
- ventas recientes.

Los datos vienen de `sales_crud.obtener_metricas_dashboard()`.

### `templates/inventory.html`

Muestra el catalogo de repuestos.

Tambien permite registrar nuevos repuestos con stock inicial.

Usa datos de `part_crud.py`.

### `templates/sales.html`

Muestra la pantalla de ventas.

Permite seleccionar cliente, repuestos, cantidades, metodo de pago y registrar
una venta.

Usa principalmente `sales_crud.py`, `customer_crud.py` y `part_crud.py`.

### `templates/receipt.html`

Muestra un recibo simple de una venta.

Sirve para demostrar que una venta guardada se puede consultar despues con sus
items.

### `templates/sql_trace.html`

Muestra las consultas SQL en vivo.

Es una pantalla de apoyo para la defensa. Ayuda a explicar que cada accion de
la app genera consultas reales a MySQL.

## `web/static/`

```text
static/
|-- assets/
|-- css/
+-- img/
```

Esta carpeta guarda archivos estaticos.

Un archivo estatico es algo que el navegador descarga tal como esta: imagenes,
CSS, iconos, etc.

### `static/assets/`

```text
assets/
|-- banner.jpg
+-- logo.png
```

Guarda imagenes principales de la marca visual.

- `banner.jpg`: imagen usada como fondo o apoyo visual.
- `logo.png`: logo de Zarvent Repuestos.

### `static/css/`

```text
css/
+-- style.css
```

Guarda estilos CSS propios del proyecto.

La app tambien usa Tailwind desde las plantillas, pero este archivo mantiene
estilos adicionales del proyecto.

### `static/img/`

```text
img/
+-- .gitkeep
```

Carpeta preparada para imagenes futuras.

`.gitkeep` solo existe para que Git conserve la carpeta aunque todavia este
vacia.

## Carpetas generadas por Python

```text
__pycache__/
```

Estas carpetas aparecen cuando Python ejecuta el proyecto.

Guardan archivos temporales que ayudan a Python a cargar mas rapido.

No son parte del modelo, no son parte de Flask y no se defienden como codigo
del proyecto.
