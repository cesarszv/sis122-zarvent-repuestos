# Guía de Defensa: Arquitectura Académica de Zarvent Repuestos

Esta guía explica la arquitectura de software construida para **Zarvent
Repuestos**. Está pensada para que un estudiante de primer año de **Base de
Datos I (SIS-122)** pueda comprender el flujo de datos desde cero y defender
las decisiones técnicas ante el docente.

---

## 1. Justificación de la Arquitectura por Capas

El docente ha solicitado una **Arquitectura de Separación por Capas**
(*Separation of Concerns*). Esto significa separar el código técnico según su
responsabilidad en lugar de mezclarlo todo en un solo archivo.

Las ventajas de este diseño que debes mencionar son:

1. **Mantenibilidad:** si cambia el diseño visual, la base de datos no se ve
   afectada. Si cambia una consulta SQL, el HTML no debería cambiar.
2. **Reutilización:** las funciones de inserción y consulta pueden ser usadas
   por Flask o por scripts sin duplicar código.
3. **Seguridad relacional:** evita mezclar conexión, consultas, validación y
   presentación en un solo lugar.

---

## 2. Mapa de Capas del Proyecto

El flujo de información sigue este camino:

```text
Usuario (navegador)
  -> Presentación (HTML/Jinja2)
  -> Controlador (Flask app.py)
  -> Operaciones SQL (crud/)
  -> Conexión (mysql-connector-python)
  -> Base de datos (MySQL Server)
```

### Capa de Configuración

- **`src/zarvent_repuestos/config/db_config.py`**
  - Carga las credenciales del archivo local `.env`.
  - Centraliza la configuración para no repetir host, usuario, contraseña y
    nombre de base de datos en varios archivos.

### Capa de Acceso

- **`src/zarvent_repuestos/access/user_service.py`**
  - Maneja usuarios, login y contraseñas con `bcrypt`.
  - Es la única fuente de verdad para autenticación.

### Capa de Base de Datos

- **`src/zarvent_repuestos/database/connection.py`**
  - Provee `get_database_connection()` para abrir una conexión con MySQL.
- **`src/zarvent_repuestos/database/init_db.py`**
  - Crea las tablas físicas en el orden correcto para no romper claves
    foráneas.
  - Usa `InnoDB` para soportar integridad referencial y transacciones.

### Capa de Modelos

- **`src/zarvent_repuestos/models/`** (`customer.py`, `part.py`,
  `sales_order.py`)
  - Contiene clases simples de Python para representar entidades usadas por la
    aplicación.
  - No reemplaza al modelo relacional. Solo ayuda a pasar datos dentro del
    código.

### Capa CRUD

- **`src/zarvent_repuestos/crud/`** (`part_crud.py`, `customer_crud.py`,
  `sales_crud.py`)
  - Contiene operaciones SQL para inventario, clientes y ventas.
  - Usa SQL parametrizado con `%s`, no concatenación de valores del usuario.
  - Cada función abre conexión, ejecuta, confirma o revierte, y cierra recursos.

### Capa de Controladores y Vistas

- **`src/zarvent_repuestos/web/app.py`**
  - Define rutas de Flask, procesa formularios y coordina llamadas a servicios
    o CRUD.
- **`src/zarvent_repuestos/web/templates/`**
  - Renderiza dashboard, inventario, ventas y recibos con HTML/Jinja2.

---

## 3. Ejemplo práctico de flujo: Registrar una Venta

Cuando el usuario confirma una venta:

1. **Vista (`sales.html`):** captura los repuestos agregados al carrito y envía
   un JSON de ítems por `POST`.
2. **Controlador (`app.py`):** valida que haya sesión, lee cliente, pago e
   ítems, y llama a `sales_crud.crear_orden_venta(...)`.
3. **CRUD (`sales_crud.py`):**
   - valida cantidades, precios y descuentos;
   - inicia una transacción;
   - bloquea stock con `SELECT ... FOR UPDATE`;
   - inserta `sales_order`;
   - inserta `sales_order_item`;
   - descuenta `inventory_stock`;
   - inserta `payment`;
   - confirma con `commit()` o revierte con `rollback()`.
4. **MySQL Server:** guarda los cambios de forma atómica.
5. **Vista:** muestra un mensaje y actualiza la información visible.

---

## 4. Preguntas Frecuentes del Docente

- **¿Por qué guardar `unit_price` en `SALES_ORDER_ITEM`?**

  Porque el precio del repuesto puede cambiar después. Si una venta antigua
  dependiera del precio actual de `PART`, el historial financiero quedaría mal.

- **¿Qué pasa si falla una venta a la mitad?**

  La operación usa transacción. Si ocurre un error, `rollback()` revierte los
  cambios y evita una venta parcial.

- **¿Por qué separar `PERSON` y `CUSTOMER`?**

  Para evitar duplicar datos personales. `PERSON` guarda identidad y contacto;
  `CUSTOMER` agrega datos comerciales como facturación o NIT.
