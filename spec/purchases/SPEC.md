# SPEC — Compras

Este documento describe el modulo de **Compras a proveedores** de Zarvent
Repuestos tal como esta implementado hoy en el codigo. La intencion es que un
estudiante de primer ano pueda leerlo, ejecutarlo y defenderlo frente al
profesor sin tener que adivinar nada sobre rutas, funciones o tablas.

El modulo cubre el ciclo `SUPPLIER -> PURCHASE_ORDER -> PURCHASE_ORDER_ITEM ->
PART -> INVENTORY_STOCK` y la maquina de estados del header de la orden
(`Pending` -> `Partially Received` -> `Received`).

## Objetivo del modulo

El negocio de Zarvent Repuestos vende repuestos y, cuando el stock baja, tiene
que reponer mercaderia a proveedores. El modulo de **Compras** resuelve tres
problemas concretos:

1. **Registrar ordenes de reposicion.** Cuando un repuesto tiene stock bajo o
   se necesita ampliar el catalogo, el responsable de compras abre una orden
   contra un proveedor, con uno o varios repuestos, cantidades y costo
   unitario negociado.
2. **Hacer seguimiento del estado del pedido.** Una orden puede estar
   pendiente, recibirse por partes o recibirse por completo. Sin este control
   la empresa pierde pedidos o cree que ya llego algo que no llego.
3. **Actualizar el inventario al recibir mercaderia.** Cuando el almacen
   confirma la recepcion, el modulo debe subir el stock del repuesto en
   `inventory_stock` y recalcular el estado de la orden automaticamente.

En terminos de Base de Datos I, este modulo demuestra el uso correcto de:

- claves foraneas (`purchase_order` -> `supplier`, `purchase_order_item` ->
  `purchase_order` y a `part`);
- `UNIQUE` para evitar duplicados (`supplier.tax_id`);
- `CASCADE` en `purchase_order_item` para borrar lineas al borrar la orden;
- `FOR UPDATE` para que dos recepcionistas no rompan el stock al mismo
  tiempo;
- una transaccion pequena (header + items + stock + status) que se confirma
  o se deshace como un solo bloque.

## Estado actual reverse-engineered

### Rutas Flask

Todas las rutas viven en `src/zarvent_repuestos/web/app.py` (lineas 429-528)
y estan protegidas con `@login_required`.

| Ruta | Metodo | Funcion | Que hace |
| --- | --- | --- | --- |
| `/purchases` | `GET` | `purchases` | Lista ordenes de compra. Acepta `?status=...` para filtrar por estado. Carga proveedores activos y repuestos para alimentar el modal de nueva orden. |
| `/purchases` | `POST` | `purchases` | Recibe `supplier_id`, `expected_date` y `items_json` (un JSON serializado desde JavaScript). Llama a `purchase_crud.create_purchase_order`. |
| `/purchases/<int:purchase_order_id>` | `GET` | `purchase_detail` | Muestra la cabecera de la orden, los datos del proveedor y el formulario de recepcion. Devuelve `404` si la orden no existe. |
| `/purchases/<int:purchase_order_id>/receive` | `POST` | `receive_purchase` | Recibe `items_json` con cantidades recibidas acumuladas. Llama a `purchase_crud.receive_purchase_order`. |

### Templates Jinja2

- `src/zarvent_repuestos/web/templates/purchases.html`
  - Cabecera con titulo "Ordenes de Compra" y boton **Nueva Compra**.
  - Sidebar con filtro por estado: **Todas / Pendientes / Recibidas
    Parcialmente / Recibidas**. Es un `<form method="get">` con radios que
    se autoenvian al cambiar.
  - Tabla principal con columnas: Codigo, Proveedor, NIT, Fecha, Esperada,
    Estado, Total, Accion (icono de ojo para ver detalle).
  - Modal **Registrar Nueva Orden de Compra** (`#new-purchase-modal`) con:
    - selector de proveedor (obligatorio, viene de `purchase_crud.list_suppliers(active_only=True)`);
    - campo de fecha esperada (opcional, `type="date"`);
    - bloque "Agregar Repuestos" con selector de parte, cantidad, costo
      unitario y boton Agregar;
    - tabla de items agregados con subtotal y boton eliminar;
    - total general actualizado en vivo;
    - botones **Cancelar** y **Crear Orden**.
  - Bloque `extra_js` con la logica del modal:
    - `purchaseItems` (array en memoria con los items agregados);
    - `addItemRow()` valida cantidad > 0 y costo >= 0, evita duplicados;
    - `removeItemRow()` y `rebuildRows()` reindexan la tabla;
    - `recalculateTotals()` actualiza `#grand-total` y vuelca el JSON al
      `<input id="items_json">`;
    - `submitPurchaseOrder()` valida proveedor seleccionado y al menos un
      item antes de hacer `form.submit()`.

- `src/zarvent_repuestos/web/templates/purchase_detail.html`
  - Breadcrumb `Compras > #PO-{id}` y boton **Volver**.
  - Tarjeta con datos del proveedor (razon social, NIT, telefono, email,
    direccion).
  - Tarjeta con datos de la orden (fecha de emision, fecha esperada, total,
    badge de estado).
  - Tabla de items con: codigo, producto, marca, cant. pedida, costo unit.,
    subtotal y un input numerico `quantity_received_{id}` precargado con el
    valor actual y con `max="{quantity_ordered}"`.
  - Cada fila muestra un chip segun el estado de la linea: **Completa /
    Pendiente / Parcial**.
  - Cuando la orden esta en `Received` los inputs quedan `disabled` y el
    boton **Registrar Recepcion** se reemplaza por un mensaje de "ya fue
    recibida por completo".
  - Bloque `extra_js`:
    - `collectReceivedItems()` recorre los inputs `name^="quantity_received_"`,
      valida que sean enteros entre 0 y `max`, y arma el array
      `[{purchase_order_item_id, quantity_received}]`;
    - `submitReceiveForm()` valida con `collectReceivedItems()` y envia el
      formulario por POST a `/purchases/<id>/receive`.

### Funciones CRUD

Todas viven en `src/zarvent_repuestos/crud/purchase_crud.py`.

**Proveedores**

- `create_supplier(business_name, tax_id, phone, email, address)` -> `int | None`
  - Valida `business_name` y `tax_id` no vacios antes de tocar la base.
  - Inserta con `is_active = TRUE`.
  - Devuelve `cursor.lastrowid` o `None` si MySQL falla.
- `list_suppliers(active_only=True)` -> `list[dict]`
  - Selecciona `supplier_id, business_name, tax_id, phone, email, address,
    is_active`, ordena por `business_name`.
- `get_supplier(supplier_id)` -> `dict | None`
  - Devuelve un proveedor por id o `None`.

**Ordenes de compra**

- `create_purchase_order(supplier_id, expected_date, items)` -> `int | None`
  - `items` esperado: `[{"part_id", "quantity_ordered", "unit_cost"}]`.
  - Valida lista no vacia, `quantity_ordered > 0` y `unit_cost >= 0`.
  - Calcula `total_amount` en Python redondeado a 2 decimales.
  - Inserta el header con `status = "Pending"` y luego cada item con
    `quantity_received = 0`, todo en una sola transaccion.
- `list_purchase_orders(status=None)` -> `list[dict]`
  - JOIN con `supplier` para mostrar nombre y NIT.
  - Acepta filtro opcional por `status`.
  - Ordena por `purchase_order_id DESC`.
- `get_purchase_order_details(purchase_order_id)` -> `dict | None`
  - Devuelve el header + `items` (JOIN con `part` para sacar codigo interno,
    nombre y marca).
  - Es la fuente de verdad del template `purchase_detail.html`.
- `receive_purchase_order(purchase_order_id, received_items)` -> `dict | None`
  - `received_items` esperado: `[{"purchase_order_item_id",
    "quantity_received"}]`. **El valor es acumulado, no delta.**
  - Por cada item:
    1. `SELECT ... FOR UPDATE` para tomar el lock de la fila;
    2. rechaza si el nuevo valor es menor al ya recibido;
    3. rechaza si el nuevo valor es mayor a `quantity_ordered`;
    4. calcula `delta = new - current`, hace `UPDATE purchase_order_item`
       y, si `delta > 0`, hace `UPDATE inventory_stock SET quantity_on_hand
       = quantity_on_hand + delta`;
  - Despues de procesar todos los items, recalcula el status del header
    contando cuantos items llegaron completos y cuantos recibieron algo.

### Tablas usadas

Definidas en `src/zarvent_repuestos/database/init_db.py` y explicadas en
`docs/database/erd.md` y `docs/database/db_explanation.md`.

- `supplier` (`supplier_id`, `business_name`, `tax_id` UNIQUE, `phone`,
  `email`, `address`, `is_active`).
- `purchase_order` (`purchase_order_id`, `supplier_id` FK, `order_date`,
  `expected_date`, `status` default `'Pending'`, `total_amount`).
- `purchase_order_item` (`purchase_order_item_id`, `purchase_order_id` FK
  CASCADE, `part_id` FK RESTRICT, `quantity_ordered`,
  `quantity_received` default 0, `unit_cost`).
- `inventory_stock` (`inventory_stock_id`, `part_id` UNIQUE FK CASCADE,
  `location_name`, `quantity_on_hand` default 0, `reorder_level` default
  10).

### Mockup de diseno

**Mockup de diseno:** No existe un mockup dedicado en `.cszv/mockups` para
este modulo. La pantalla real es la unica referencia visual. Si en el futuro
se quiere alinear la UI con un diseno academico/mockup, se debera crear
primero el mockup como tarea separada y recien despues actualizar este
SPEC.

Verificacion realizada: `ls .cszv/mockups/` muestra unicamente
`dashboard_mockup.*`, `inventory_mockup.*` y `sales_mockup.*`. No existe
`purchases_mockup.*`.

## Contrato funcional

### Crear orden de compra

1. El usuario hace clic en **Nueva Compra** en `purchases.html`.
2. Se abre el modal `#new-purchase-modal`.
3. El usuario selecciona un proveedor del `<select id="supplier_id">`. El
   campo es obligatorio.
4. Opcionalmente completa `expected_date` (input `type="date"`).
5. Para cada repuesto:
   - selecciona un item del catalogo (`#part_selector`),
   - indica `quantity` (entero, minimo 1),
   - indica `unit_cost` (decimal, minimo 0; se pre-rellena con
     `part.purchase_cost` al elegir el repuesto),
   - pulsa **Agregar** (`addItemRow()`).
6. `recalculateTotals()` actualiza el gran total y serializa el array
   `purchaseItems` al `<input id="items_json">`.
7. Al pulsar **Crear Orden** (`submitPurchaseOrder()`), el form hace POST a
   `/purchases`.
8. La ruta `purchases` (POST) llama a `purchase_crud.create_purchase_order`
   y, si todo sale bien, redirige a `/purchases/<id>` mostrando la orden
   recien creada con un flash de exito.

### Listar ordenes de compra

- La tabla principal muestra todas las ordenes en orden descendente por id.
- El sidebar permite filtrar por estado:
  - vacio = todas,
  - `Pending` = pendientes,
  - `Partially Received` = recibidas parcialmente,
  - `Received` = recibidas.
- El filtro se envia por GET (`?status=...`) y recarga la pagina.

### Ver detalle de una orden

- La ruta GET `/purchases/<id>` carga la orden con sus items y la pinta con
  `purchase_detail.html`.
- Si la orden no existe devuelve `404`.

### Registrar recepcion (parcial o completa)

1. En `purchase_detail.html` cada item tiene un input
   `quantity_received_{id}` precargado con el valor actual
   (`{{ item.quantity_received }}`) y con `max="{{ item.quantity_ordered }}"`.
2. El usuario modifica los inputs que necesite y pulsa **Registrar
   Recepcion**.
3. `collectReceivedItems()` valida en el cliente que cada valor sea entero
   entre 0 y el maximo, y arma el array de items.
4. El form hace POST a `/purchases/<id>/receive`.
5. La ruta llama a `receive_purchase_order`, que:
   - actualiza `purchase_order_item.quantity_received` por linea,
   - incrementa `inventory_stock.quantity_on_hand` con el delta real
     (`nuevo - actual`),
   - recalcula el `status` del header,
   - hace `commit` o `rollback` segun corresponda.
6. La vista redirige al mismo detalle con un flash de exito o de error.

### Validaciones explicitas

| Validacion | Donde | Mensaje al usuario |
| --- | --- | --- |
| `supplier_id` numerico positivo | ruta `/purchases` POST | flash `Selecciona un proveedor.` |
| `items_json` parseable | ruta `/purchases` POST | flash `Items de la orden estan mal formados.` |
| `expected_date` presente o vacio (opcional) | cliente | sin mensaje; se guarda `NULL` si viene vacio |
| Al menos un item al crear | `create_purchase_order` | `ValueError`: "La orden de compra debe tener al menos un item." |
| Cantidad pedida > 0 | `create_purchase_order` | `ValueError`: "La cantidad pedida del producto {id} debe ser mayor que cero." |
| Costo unitario >= 0 | `create_purchase_order` | `ValueError`: "El costo unitario del producto {id} no puede ser negativo." |
| Cantidad recibida no se reduce | `receive_purchase_order` | `ValueError`: "No puedes reducir la cantidad recibida de la linea {id}." |
| Cantidad recibida no excede lo pedido | `receive_purchase_order` | `ValueError`: "La linea {id} no puede recibir {n} unidades; solo se pidieron {m}." |
| Items recibidos en JSON | ruta `/purchases/<id>/receive` POST | flash `Indica al menos una cantidad recibida.` |
| Entero entre 0 y `max` en cliente | `collectReceivedItems()` | `alert("Cantidad recibida invalida. Debe ser un numero entero entre 0 y {max}.")` |

### Mensajes flash

- `success`: `Orden de compra #{id} creada con exito.`,
  `Recepcion registrada con exito.`
- `error`: mensajes de las validaciones listadas arriba, mas
  `Error al crear la orden de compra: ...` y `Error al recibir la orden:
  ...` como fallback.

## Contrato de datos

### Tablas y relaciones

| Tabla | Columnas relevantes | Reglas |
| --- | --- | --- |
| `supplier` | `supplier_id` PK, `business_name` NOT NULL, `tax_id` UNIQUE NOT NULL, `phone`, `email`, `address`, `is_active` DEFAULT TRUE | `tax_id` debe ser unico. |
| `purchase_order` | `purchase_order_id` PK, `supplier_id` FK -> `supplier` ON DELETE RESTRICT, `order_date` NOT NULL, `expected_date` (opcional), `status` DEFAULT 'Pending', `total_amount` NOT NULL | Cabecera. |
| `purchase_order_item` | `purchase_order_item_id` PK, `purchase_order_id` FK -> `purchase_order` ON DELETE CASCADE, `part_id` FK -> `part` ON DELETE RESTRICT, `quantity_ordered` NOT NULL, `quantity_received` DEFAULT 0, `unit_cost` NOT NULL | Linea. Al borrar la cabecera, se borran sus lineas. |
| `inventory_stock` | `inventory_stock_id` PK, `part_id` UNIQUE FK -> `part` ON DELETE CASCADE, `location_name`, `quantity_on_hand` DEFAULT 0, `reorder_level` DEFAULT 10 | Stock actual por repuesto. Se incrementa con cada recepcion. |

Relaciones en terminos del ERD:

- `SUPPLIER 1 -- N PURCHASE_ORDER`: un proveedor puede recibir muchas
  ordenes.
- `PURCHASE_ORDER 1 -- N PURCHASE_ORDER_ITEM`: una orden debe tener al
  menos una linea.
- `PART 1 -- N PURCHASE_ORDER_ITEM`: un repuesto puede comprarse en muchas
  ordenes.
- `PART 1 -- 1 INVENTORY_STOCK`: cada repuesto tiene una fila de stock
  (relacion uno-a-uno por el `UNIQUE` sobre `part_id`).

### Maquina de estados del header

`purchase_order.status` solo toma tres valores en este modulo:

```
                create_purchase_order
                       |
                       v
                   +---------+
                   | Pending |
                   +----+----+
                        |
       +----------------+----------------+
       |                                 |
 receive (>0, < ordered)        receive (todas = ordered)
       |                                 |
       v                                 v
+---------------------+             +-----------+
| Partially Received  |             | Received |
+---------------------+             +-----------+
       ^                                 |
       |                                 |
       +------ receive (alguna < ordered) +
```

Reglas concretas en `receive_purchase_order`:

- Si `full_count == total_count` y `total_count > 0` -> `Received`.
- Si `any_count > 0` y `full_count < total_count` -> `Partially Received`.
- Si nadie recibio nada -> `Pending`.

Importante: una vez que el status es `Received`, el template muestra los
inputs como `disabled` y no permite registrar mas recepciones.

### Lock pesimista con `FOR UPDATE`

`receive_purchase_order` hace, por cada item del payload:

```sql
SELECT purchase_order_item_id, part_id, quantity_ordered, quantity_received
FROM purchase_order_item
WHERE purchase_order_id = %s AND purchase_order_item_id = %s
FOR UPDATE
```

Esto toma un lock de fila en `purchase_order_item` para esa linea, de modo
que dos recepciones concurrentes contra el mismo `purchase_order_id` se
serializan y no se pisan al:

- calcular el delta sobre `quantity_received`,
- incrementar `inventory_stock.quantity_on_hand`,
- reescribir el status del header.

Sin este lock, dos llamadas simultaneas podrian leer la misma
`quantity_received` previa, calcular el mismo delta, y duplicar el aumento
de stock.

### Side effects de `receive_purchase_order`

| Tabla afectada | Columna | Operacion |
| --- | --- | --- |
| `purchase_order_item` | `quantity_received` | `UPDATE` al valor acumulado nuevo. |
| `inventory_stock` | `quantity_on_hand` | `UPDATE quantity_on_hand = quantity_on_hand + delta WHERE part_id = ?`. Solo cuando `delta > 0`. |
| `purchase_order` | `status` | `UPDATE` al estado recalculado (Pending / Partially Received / Received). |

Todo esto ocurre dentro de una sola transaccion (`conexion.commit()` al
finalizar, `conexion.rollback()` si algo lanza `ValueError` o
`mysql.connector.Error`).

### Reglas de integridad relevantes

- `supplier.tax_id` es `UNIQUE NOT NULL`: dos proveedores no pueden
  compartir NIT.
- `purchase_order.supplier_id` es `ON DELETE RESTRICT`: no se puede borrar
  un proveedor con ordenes abiertas.
- `purchase_order_item.purchase_order_id` es `ON DELETE CASCADE`: borrar
  una orden limpia sus lineas.
- `purchase_order_item.part_id` es `ON DELETE RESTRICT`: no se puede borrar
  un repuesto que figure como item de compra.
- `inventory_stock.part_id` es `UNIQUE` y `ON DELETE CASCADE`: cada
  repuesto tiene una unica fila de stock; si se borra el repuesto, se
  borra su stock.

## Trazabilidad SDD

Esta matriz cruza lo que dicen los docs, lo que esta en la base de datos y
lo que esta en el codigo real. **No se inventa nada**: si la columna viene
vacia, significa que el tema no se nombra en esa fuente.

Estados posibles:

- `implementado` = existe en el codigo real y ademas esta documentado.
- `parcial` = existe en el codigo pero con diferencias respecto al doc, o
  existe en el doc pero no en el codigo.
- `faltante` = deberia estar segun el proceso, pero no esta implementado.
- `fuera de alcance` = no aplica a este modulo o se decidio no hacerlo.

| Tema | docs/analysis | docs/database | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Entidad `SUPPLIER` con `tax_id` unico | `requirements.md` RF-07, `actors.md` Proveedor, `processes.md` linea 49 | `erd.md` SUPPLIER, `db_explanation.md` linea 21 | Tabla `supplier` en `init_db.py`; CRUD `create_supplier`/`list_suppliers`/`get_supplier` | implementado |
| Crear proveedores desde la UI | `processes.md` linea 49, `procedures.md` "Registro de compra" paso 2 | n/a | No hay ruta Flask ni template para crear proveedores. `create_supplier` existe pero no se expone. | parcial |
| Entidad `PURCHASE_ORDER` con `status` y `expected_date` | `requirements.md` RF-07, `procedures.md` "Registro de compra" | `erd.md` PURCHASE_ORDER, `db_explanation.md` linea 30 | Tabla `purchase_order` en `init_db.py`; CRUD `create_purchase_order`, `list_purchase_orders`, `get_purchase_order_details`; rutas `/purchases` GET/POST y `/purchases/<id>` GET | implementado |
| `expected_date` opcional | n/a | `erd.md` `date expected_date` (sin NOT NULL) | `init_db.py` crea la columna sin `NOT NULL`; ruta `/purchases` POST acepta vacio y guarda `NULL` | implementado |
| Entidad `PURCHASE_ORDER_ITEM` con cantidad pedida, recibida y costo historico | `processes.md` linea 49, `procedures.md` "Registro de compra" paso 3 | `erd.md` PURCHASE_ORDER_ITEM, `db_explanation.md` linea 31 | Tabla `purchase_order_item` en `init_db.py`; CRUD `create_purchase_order` y `receive_purchase_order` | implementado |
| Maquina de estados Pending / Partially Received / Received | n/a (no se modela explicitamente) | n/a | Implementada en `receive_purchase_order` (`full_count`, `any_count`, `total_count`) y reflejada en `purchases.html` y `purchase_detail.html` con badges | implementado |
| Recepcion parcial o completa | `procedures.md` "Registro de compra" pasos 5-6 | n/a | `receive_purchase_order` con `FOR UPDATE`, validacion de no reducir y no exceder; UI en `purchase_detail.html` con `collectReceivedItems` | implementado |
| Incremento de `inventory_stock.quantity_on_hand` al recibir | `processes.md` linea 50, `procedures.md` "Control de inventario" | `db_explanation.md` linea 26 | `receive_purchase_order` hace `UPDATE inventory_stock SET quantity_on_hand = quantity_on_hand + delta` solo si `delta > 0` | implementado |
| Tabla separada de recepciones (`PURCHASE_RECEIPT_ITEM`) | n/a (no nombrada) | `db_explanation.md` "Limitaciones aceptadas": `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM` quedan como mejora futura | No existe. La recepcion se hace directo sobre `purchase_order_item` | fuera de alcance |
| Cancelacion de ordenes de compra | n/a | n/a | No implementada. No hay ruta, no hay columna `cancelled` | faltante |
| Edicion de ordenes de compra | n/a | n/a | No implementada. No hay ruta PUT/PATCH ni template | faltante |
| Validacion de `quantity > 0` y `unit_cost >= 0` al crear | n/a (regla de negocio implicita) | n/a | `create_purchase_order` valida ambos y lanza `ValueError`; el cliente tambien valida en `addItemRow()` | implementado |
| Validacion de no reducir y no exceder al recibir | n/a (regla de negocio implicita) | n/a | `receive_purchase_order` valida ambos; el cliente valida el rango en `collectReceivedItems` | implementado |
| Lock pesimista `FOR UPDATE` sobre items | n/a | n/a | `SELECT ... FOR UPDATE` en `receive_purchase_order` por cada linea | implementado |
| CASCADE en items al borrar orden | n/a | `init_db.py` define `ON DELETE CASCADE` para `purchase_order_item.purchase_order_id` | Esquema en `init_db.py` | implementado |
| UNIQUE en `supplier.tax_id` | n/a | `db_explanation.md` "Reglas que deben defenderse" | `init_db.py`: `tax_id VARCHAR(50) UNIQUE NOT NULL` | implementado |
| Listar ordenes con filtro por estado | n/a | n/a | `purchases.html` sidebar + `list_purchase_orders(status=...)` | implementado |
| Mockup academico del modulo de compras | n/a | n/a | No existe `purchases_mockup.*` en `.cszv/mockups/` | faltante |

## Criterios de aceptacion

### Pruebas automatizadas

Las pruebas viven en `tests/`. Los modulos relevantes son:

- `tests/test_purchase_crud.py` cubre las funciones de `purchase_crud.py`
  con la base de datos mockeada:
  - `CreatePurchaseOrderValidationTest`:
    - `test_empty_items_raises_value_error_before_connection`: items
      vacios no abren conexion.
    - `test_zero_quantity_raises_value_error_before_connection`:
      `quantity_ordered = 0` no abre conexion.
    - `test_negative_unit_cost_raises_value_error_before_connection`:
      `unit_cost < 0` no abre conexion.
  - `CreatePurchaseOrderHappyPathTest`:
    - `test_header_and_item_inserts_happen_in_a_single_transaction`:
      confirma un `INSERT` al header, un `INSERT` por cada item, un solo
      `commit`, ningun `rollback`, `lastrowid = 42`, status `Pending`,
      `total_amount = 100.0`.
  - `CreateSupplierValidationTest`:
    - `test_empty_business_name_raises_value_error_before_connection`.
    - `test_empty_tax_id_raises_value_error_before_connection`.
  - `ReceivePurchaseOrderTest`:
    - `test_full_reception_marks_header_received_and_increments_stock_by_delta`:
      con `ordered=5`, `current=0`, `new=5` -> status `Received`,
      `UPDATE inventory_stock (5, part_id)`, commit unico.
    - `test_partial_reception_marks_header_partially_received_and_uses_partial_delta`:
      con `ordered=5`, `current=0`, `new=2` -> status
      `Partially Received`, `UPDATE inventory_stock (2, part_id)`.
    - `test_reducing_received_is_rejected_with_value_error`: con
      `current=3`, `new=1` -> `ValueError`, rollback, sin updates a
      stock.
    - `test_over_receiving_is_rejected_with_value_error`: con
      `ordered=5`, `new=6` -> `ValueError`, rollback, sin updates a
      stock.

- `tests/test_purchase_detail_route.py` cubre la ruta `/purchases/<id>`
  con la app Flask real (cliente de test) y la base mockeada:
  - `test_purchase_detail_renders_200_with_preset_order`: la ruta
    devuelve 200 y muestra el codigo interno, el nombre del producto y el
    nombre del proveedor.
  - `test_purchase_detail_renders_with_no_items`: la ruta devuelve 200
    aun con `items = []` y no muestra el codigo interno esperado.
  - `test_purchase_detail_returns_404_when_order_missing`: si la orden
    no existe, devuelve 404.

Comandos sugeridos (sin asumir nada sobre el framework):

```bash
python -m unittest tests.test_purchase_crud
python -m unittest tests.test_purchase_detail_route
```

### Pruebas manuales sugeridas

1. **Crear orden end-to-end.**
   - Login con `admin` / `admin123`.
   - Ir a `/purchases`. Pulsar **Nueva Compra**.
   - Seleccionar proveedor, dejar fecha vacia, agregar dos repuestos con
     cantidad y costo validos, pulsar **Crear Orden**.
   - Verificar: redirige a `/purchases/<id>`, flash de exito, total
     correcto, ambos items con `quantity_received = 0`.
2. **Recepcion parcial.**
   - En el detalle, modificar el primer input a 2 (sobre un pedido de 5)
     y pulsar **Registrar Recepcion**.
   - Verificar: flash de exito, status `Partially Received` (badge
     azul), chip **Parcial** en la fila, `inventory_stock` para ese
     repuesto aumento en 2.
3. **Recepcion completa.**
   - En el detalle, poner todos los inputs en el maximo y registrar.
   - Verificar: status `Received` (badge verde), inputs `disabled`,
     mensaje "Esta orden ya fue recibida por completo.", stock
     incrementado en lo que faltaba.
4. **Validaciones de entrada en el cliente.**
   - Intentar `quantity = 0` o `unit_cost = -1` en el modal: el JS
     muestra `alert`.
   - Intentar registrar la orden sin proveedor o sin items: `alert`
     antes de enviar.
   - Intentar enviar una cantidad recibida mayor al maximo: `alert`
     desde `collectReceivedItems`.
5. **Validaciones del servidor.**
   - Forzar un POST directo a `/purchases` con `supplier_id = 0` o
     `items_json` invalido: flash de error, redirige a `/purchases`.
   - Forzar una recepcion con `quantity_received` menor al actual o
     mayor al `quantity_ordered`: flash `Error de validacion: ...`,
     redirige al detalle sin cambiar stock ni status.
6. **Filtros del sidebar.**
   - Pulsar cada radio del sidebar y comprobar que la URL lleva
     `?status=...` y la tabla solo muestra ordenes con ese estado.
   - Pulsar **Limpiar Filtros** y comprobar que vuelve a la lista
     completa.
7. **Integridad de base de datos.**
   - Con DataGrip o `mysql` CLI, intentar insertar dos `supplier` con
     el mismo `tax_id`: MySQL debe rechazarlo.
   - Borrar una `purchase_order` con items: las lineas deben
     desaparecer por la `CASCADE`.

## Brechas y decisiones

Estas son las diferencias entre lo que proponen los documentos de analisis y
lo que el codigo implementa hoy. Sirven para que la defensa sea honesta.

1. **No hay UI para crear proveedores.** La funcion `create_supplier`
   existe en `purchase_crud.py` (con validacion de `business_name` y
   `tax_id` no vacios, insercion con `is_active = TRUE`), pero ninguna
   ruta Flask la expone y ningun template la usa. Los proveedores
   necesarios en demo se cargan por `scripts/database/seed_project_data.py`.
   Esto es coherente con el alcance academico (no se queria invertir
   tiempo en CRUD de proveedores), pero es una brecha visible respecto a
   `procedures.md` "Registro de compra" paso 2.

2. **No existe tabla `PURCHASE_RECEIPT_ITEM`.** El ERD compacto no la
   incluye y `db_explanation.md` la lista como mejora futura bajo
   "Limitaciones aceptadas". En el codigo, la recepcion se aplica
   directamente sobre `purchase_order_item` con `UPDATE
   quantity_received`. Esto es valido para el alcance, pero significa
   que no hay un historial separado de recepciones (no se puede saber
   "quien recibio que dia"); solo queda el valor acumulado.

3. **`expected_date` es opcional.** La columna no tiene `NOT NULL` en
   `init_db.py`, la ruta acepta vacio y guarda `NULL`, y el template
   muestra `—` cuando esta vacia. El procedimiento `procedures.md`
   "Registro de compra" no exige fecha esperada, asi que esto es
   coherente, pero conviene saber que el sistema no alerta cuando se
   atrasa una entrega esperada.

4. **No hay cancelacion de ordenes de compra.** No existe una columna
   `cancelled` ni un endpoint para marcar la orden como cancelada. La
   unica forma de "sacarla" del flujo es recibirla por completo.

5. **No hay edicion de ordenes de compra.** Una vez creada la orden con
   `create_purchase_order`, no se puede modificar ni el proveedor, ni
   los items, ni el costo unitario. La unica mutacion permitida es la
   recepcion (que solo sube `quantity_received`).

6. **El endpoint de recepcion recibe el valor acumulado, no el delta.**
   Esto se verifica en el codigo (`receive_purchase_order` recalcula
   `delta = new_received - current_received` y hace `UPDATE` con el
   valor nuevo, no con el delta) y en el template (`value="{{
   item.quantity_received }}"` precarga el valor actual y
   `collectReceivedItems` envia ese mismo valor). El CRUD usa `delta`
   solo para `inventory_stock`. Es importante tenerlo claro en la
   defensa: si la UI enviara el delta, el backend lo rechazaria porque
   "reduciria" el valor.

7. **No hay mockup academico del modulo.** `.cszv/mockups/` solo
   contiene `dashboard_mockup.*`, `inventory_mockup.*` y
   `sales_mockup.*`. El presente SPEC no se puede alinear con un
   mockup que no existe; la pantalla real (los templates Jinja2
   actuales) es la unica referencia visual.

8. **No hay autenticacion por actor en la UI.** `actors.md` distingue
   entre Responsable de compras y Encargado de almacen, pero el
   codigo solo exige `login_required` y no diferencia que usuario
   puede crear ordenes o registrar recepciones. El control de actor
   queda delegado a la convencion del equipo.
