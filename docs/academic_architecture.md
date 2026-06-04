# Guía de Defensa: Arquitectura Académica de Zarvent Repuestos

Esta guía explica detalladamente la arquitectura de software construida para **Zarvent Repuestos**. Está pensada para que un estudiante de primer año de **Base de Datos I (SIS-122)** pueda comprender el flujo de datos desde cero y defender las decisiones técnicas ante el docente.

---

## 1. Justificación de la Arquitectura por Capas

El docente ha solicitado una **Arquitectura de Separación por Capas** (Separation of Concerns). Esto significa separar el código técnico según su responsabilidad en lugar de mezclarlo todo en un solo archivo.

Las ventajas de este diseño que debes mencionar son:
1. **Mantenibilidad:** Si cambia el diseño visual (HTML), la base de datos no se ve afectada. Si cambia el motor de base de datos, el HTML no cambia.
2. **Reutilización:** Las funciones CRUD (de inserción y consulta) pueden ser utilizadas tanto por la aplicación web (Flask) como por un menú de consola (`main.py`) sin duplicar código.
3. **Seguridad relacional:** Evita acoplar la lógica de conexión directa con la visualización.

---

## 2. Mapa de Capas del Proyecto

El flujo de información sigue un camino de ida y vuelta:

```text
Usuario (Navegador) ⇄ Presentación (HTML/Jinja2) ⇄ Controlador (Flask app.py) ⇄ Operaciones (CRUD) ⇄ Conexión (MySQL Connector) ⇄ Base de Datos (MySQL Server)
```

A continuación se detalla qué hace cada archivo creado:

### Capa de Configuración
*   **`src/zarvent_repuestos/config/db_config.py`**
    *   *Qué hace:* Carga las credenciales del archivo local `.env` (que no se sube a Git por seguridad) y las organiza en un diccionario de configuración de Python (`DB_CONFIG`).
    *   *Defensa:* Centralizar la configuración evita escribir usuarios y contraseñas repetidamente en el código ("Hardcoding").

### Capa de Base de Datos
*   **`src/zarvent_repuestos/database/connection.py`**
    *   *Qué hace:* Provee la función `get_database_connection()` (y su alias `obtener_conexion()`) para abrir un canal de comunicación técnico con el servidor MySQL Server.
*   **`src/zarvent_repuestos/database/init_db.py`**
    *   *Qué hace:* Inicializa físicamente las tablas en MySQL en base al orden correcto de dependencias (para no violar restricciones de clave foránea al crearlas).
    *   *Defensa:* Las tablas se crean con el motor `InnoDB` para soportar **integridad referencial** (claves foráneas) y transacciones seguras.

### Capa de Modelos (Entidades de Dominio)
*   **`src/zarvent_repuestos/models/`** (`user.py`, `customer.py`, `part.py`, `sales_order.py`)
    *   *Qué hace:* Clases simples de Python (`User`, `Part`, `Customer`, etc.) que representan un registro de cada tabla de la base de datos en memoria. Tienen constructores `__init__` y métodos `__str__` para visualizar la entidad.
    *   *Defensa:* Permiten manejar los datos en la aplicación como objetos estructurados de negocio en lugar de simples tuplas o arreglos de texto plano.

### Capa CRUD (Lógica SQL Pura)
*   **`src/zarvent_repuestos/crud/`** (`user_crud.py`, `part_crud.py`, `customer_crud.py`, `sales_crud.py`)
    *   *Qué hace:* Contiene las funciones de base de datos (Crear, Leer, Actualizar, Borrar) utilizando **SQL puro parametrizado**.
    *   *Defensa (¡Muy Importante!):* 
        1. **Sin ORM:** No se utiliza ningún ORM avanzado (como SQLAlchemy) para demostrar dominio absoluto del lenguaje SQL.
        2. **Parámetros `%s`:** Las consultas usan placeholders `%s` en lugar de concatenar cadenas (evitando ataques de **Inyección SQL**).
        3. **Gestión de Recursos:** Cada función abre la conexión, ejecuta la consulta y asegura cerrar el `cursor` y la `conexion` en un bloque `finally` para no dejar conexiones colgadas en el servidor MySQL.

### Capa de Controladores y Vistas
*   **`src/zarvent_repuestos/web/app.py`**
    *   *Qué hace:* Define el ruteo web de Flask, procesa formularios `POST` y variables de sesión para el inicio de sesión. Coordina la llamada al CRUD correspondiente para pasar los datos a las plantillas HTML.
*   **`src/zarvent_repuestos/web/templates/`** (`layout.html`, `dashboard.html`, `inventory.html`, `sales.html`, `receipt.html`)
    *   *Qué hace:* Archivos HTML con sintaxis Jinja2 para renderizar dinámicamente las tablas operativas de repuestos y ventas de forma interactiva y premium.

---

## 3. Ejemplo práctico de flujo: Registrar una Venta

Cuando el usuario da click en "Confirmar Venta":

1.  **Vista (`sales.html`):** Captura mediante JavaScript los repuestos agregados al carrito de compras, arma un JSON de ítems y lo envía mediante `POST` al servidor.
2.  **Controlador (`app.py`):** Recibe la solicitud `/sales`, valida la sesión, y llama a la función del CRUD: `sales_crud.crear_orden_venta(customer_id, items, payment_method)`.
3.  **CRUD (`sales_crud.py`):**
    *   Inicia una transacción en MySQL.
    *   Ejecuta un `SELECT ... FOR UPDATE` en `inventory_stock` para bloquear temporalmente las filas del stock y verificar que haya suficiente cantidad. Si no hay stock, lanza un error y ejecuta `rollback()`.
    *   Inserta la cabecera en `sales_order` y obtiene el ID generado.
    *   Por cada producto del detalle, realiza un `INSERT` en `sales_order_item` y ejecuta un `UPDATE` en `inventory_stock` restando la cantidad vendida (`quantity_on_hand = quantity_on_hand - %s`).
    *   Inserta el recibo en la tabla `payment`.
    *   Si todo sale bien, ejecuta `commit()` para guardar definitivamente.
4.  **MySQL Server:** Registra los cambios y actualiza el stock físico de forma segura.
5.  **Controlador y Vista:** Notifica éxito al usuario mediante un Flash Message y refresca la pantalla mostrando el saldo actualizado.

---

## 4. Preguntas Frecuentes del Docente y Cómo Responderlas

*   **P: ¿Por qué no guardas el precio de venta final directamente calculándolo del precio actual del repuesto?**
    *   *R:* Porque el precio de `PART` puede cambiar mañana (debido a inflación o cambio de proveedor). Si no guardamos la columna `unit_price` histórica en `SALES_ORDER_ITEM`, al modificar el precio de un repuesto alteraríamos el historial financiero de ventas pasadas, lo cual es un grave error de diseño relacional.
*   **P: ¿Qué pasa si ocurre un corte de energía en medio del bucle de inserción de detalles de venta?**
    *   *R:* Al utilizar transacciones (`InnoDB`), los cambios intermedios quedan en un estado temporal. Si la conexión se interrumpe o falla la inserción de algún ítem, la cláusula `except` captura el error y ejecuta `conexion.rollback()`. De este modo, la base de datos vuelve a su estado inicial, garantizando la propiedad **ACID** de **Atomicidad**.
*   **P: ¿Por qué separaste las tablas `PERSON` y `CUSTOMER`?**
    *   *R:* Para cumplir con la normalización y evitar redundancia. Una entidad `PERSON` guarda datos generales de identidad civil (nombres, teléfono, dirección). La entidad `CUSTOMER` solo añade datos comerciales (NIT, nombre de facturación). De esta manera, si en el futuro registramos proveedores u operarios, todos pueden referenciar a `PERSON` sin duplicar datos personales básicos.
