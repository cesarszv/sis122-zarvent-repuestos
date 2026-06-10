# SPEC — Compras

Contrato funcional y tecnico del modulo de **Compras a proveedores** de
Zarvent Repuestos. Cubre el alta de proveedores, la creacion de ordenes
de compra, la maquina de estados del header y la recepcion parcial o
completa con actualizacion de stock. Pensado para que un estudiante de
primer ano de Base de Datos I pueda leerlo y defenderlo.

El modulo materializa la cadena:

`SUPPLIER -> PURCHASE_ORDER -> PURCHASE_ORDER_ITEM -> PART -> INVENTORY_STOCK`

y la maquina de estados del header documentada en la
[Seccion 2](#2-contrato-objetivo-v1).

---

## 1. Estado actual (reverse-engineered)

Lo que el codigo hace HOY, leido del repo. No es diseno, es evidencia.

### 1.1 Rutas Flask

Definidas en [`src/zarvent_repuestos/web/app.py`](../../src/zarvent_repuestos/web/app.py).

| Ruta | Metodo | Linea | Funcion que la implementa | Que hace |
| --- | --- | --- | --- | --- |
| `/purchases` | `GET` | `app.py:431` | `purchases()` | Lista ordenes de compra. Acepta `?status=...` para filtrar. Carga proveedores activos (`list_suppliers(active_only=True)`) y repuestos para alimentar el modal. |
| `/purchases` | `POST` | `app.py:431` | `purchases()` | Recibe `supplier_id`, `expected_date` y `items_json`. Llama a `purchase_crud.create_purchase_order`. |
| `/purchases/<int:purchase_order_id>` | `GET` | `app.py:486` | `purchase_detail()` | Muestra cabecera, datos del proveedor y formulario de recepcion. Responde `404` si la orden no existe. |
| `/purchases/<int:purchase_order_id>/receive` | `POST` | `app.py:500` | `receive_purchase()` | Recibe `items_json` con cantidades recibidas acumuladas. Llama a `purchase_crud.receive_purchase_order`. |

Las cuatro rutas usan `@login_required` (`app.py:69`).

### 1.2 Templates

- [`src/zarvent_repuestos/web/templates/purchases.html`](../../src/zarvent_repuestos/web/templates/purchases.html):
  cabecera con titulo "Ordenes de Compra" y boton "Nueva Compra"; sidebar
  con filtro por estado (`Todas`, `Pendientes`, `Recibidas Parcialmente`,
  `Recibidas`); tabla principal con columnas Codigo, Proveedor, NIT,
  Fecha, Esperada, Estado (badge), Total y Accion (icono de ojo); modal
  `new-purchase-modal` con selector de proveedor, fecha esperada y bloque
  "Agregar Repuestos" con tabla de items, total general en vivo y botones
  "Cancelar" y "Crear Orden".

  Bloque `extra_js`: `purchaseItems` (array en memoria), `addItemRow` con
  validacion de cantidad y costo, `removeItemRow` con reindexado,
  `rebuildRows`, `recalculateTotals` y `submitPurchaseOrder` que valida
  proveedor y al menos un item antes de hacer `form.submit()`.

- [`src/zarvent_repuestos/web/templates/purchase_detail.html`](../../src/zarvent_repuestos/web/templates/purchase_detail.html):
  breadcrumb `Compras > #PO-{id}` y boton "Volver"; tarjetas con datos
  del proveedor y de la orden; tabla de items con `internal_code`,
  `name`, `brand`, cantidad pedida, costo unitario, subtotal e input
  `quantity_received_{id}` precargado con el valor actual y con
  `max="{{ quantity_ordered }}"`; chip de estado por linea (Completa /
  Pendiente / Parcial); cuando la orden esta en `Received` los inputs
  quedan `disabled` y el boton "Registrar Recepcion" se reemplaza por el
  mensaje "Esta orden ya fue recibida por completo".

  Bloque `extra_js`: `collectReceivedItems` recorre los inputs
  `name^="quantity_received_"`, valida enteros entre 0 y `max`, arma el
  array `[{purchase_order_item_id, quantity_received}]` y lo serializa al
  `<input id="items_json">`; `submitReceiveForm` valida y envia el
  formulario por POST a `/purchases/<id>/receive`.

### 1.3 Funciones CRUD

Definidas en
[`src/zarvent_repuestos/crud/purchase_crud.py`](../../src/zarvent_repuestos/crud/purchase_crud.py).

**Proveedores:**

- `create_supplier(business_name, tax_id, phone, email, address)` -> `int | None`.
  Valida `business_name` y `tax_id` no vacios antes de tocar la base,
  inserta con `is_active = TRUE`, retorna `cursor.lastrowid` o `None`.
- `list_suppliers(active_only=True)` -> `list[dict]`. Selecciona y ordena
  por `business_name`. Acepta filtro opcional por `is_active`.
- `get_supplier(supplier_id)` -> `dict | None`. Por id o `None`.

**Ordenes de compra:**

- `create_purchase_order(supplier_id, expected_date, items)` -> `int | None`.
  `items` esperado: `[{"part_id", "quantity_ordered", "unit_cost"}]`. Valida
  lista no vacia, `quantity_ordered > 0` y `unit_cost >= 0`. Inserta la
  cabecera con `status = "Pending"` y luego cada item con
  `quantity_received = 0` en una sola transaccion.
- `list_purchase_orders(status=None)` -> `list[dict]`. JOIN con `supplier`.
  Acepta filtro opcional por `status`. Ordena por `purchase_order_id DESC`.
- `get_purchase_order_details(purchase_order_id)` -> `dict | None`. Devuelve
  header + `items` con JOIN a `part`.
- `receive_purchase_order(purchase_order_id, received_items)` -> `dict | None`.
  `received_items` esperado: `[{"purchase_order_item_id",
  "quantity_received"}]`. **El valor es acumulado, no delta.** Por cada
  item corre `SELECT ... FOR UPDATE`, rechaza si el nuevo valor es menor
  al ya recibido o mayor a `quantity_ordered`, calcula `delta = new -
  current`, hace `UPDATE purchase_order_item` y, si `delta > 0`, hace
  `UPDATE inventory_stock SET quantity_on_hand = quantity_on_hand +
  delta`. Al final recalcula el status del header.

### 1.4 Tablas relacionadas

Definidas en
[`src/zarvent_repuestos/database/init_db.py`](../../src/zarvent_repuestos/database/init_db.py).

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

### 1.5 Comportamiento visible HOY

- `create_supplier` existe y funciona, pero **no** hay ruta Flask ni
  template que la invoquen. Los proveedores del seed se cargan por
  `scripts/database/seed_project_data.py`.
- La maquina de estados en v1 cubre tres valores: `Pending`,
  `Partially Received`, `Received`. El valor `Cancelled` **no** se
  inserta desde ningun `create_purchase_order` ni `receive_purchase_order`.
- No hay endpoint para cancelar una orden.
- La recepcion acepta el **valor acumulado** (`quantity_received` total
  de la linea, no el delta). El `delta` se calcula internamente solo para
  `inventory_stock`.
- `purchase_order_item` registra `unit_cost` con el valor que envia la
  UI, no se recalcula desde `part.purchase_cost` (precio historico del
  costo de compra).

### 1.6 Mockup de diseno

No existe mockup dedicado en `.cszv/mockups/` para este modulo. La
pantalla real (`purchases.html` y `purchase_detail.html`) es la unica
referencia visual. Si en el futuro se quiere alinear la UI con un
diseno academico/mockup, primero se crea el mockup como tarea separada
y despues se actualiza este SPEC.

---

## 2. Contrato objetivo v1

Lo que el spec PROMETE en v1. Cualquier entrega que no cumpla esto queda
rechazada como contrato.

### 2.1 Alcance funcional

- Exponer UI para crear proveedores (ruta POST `/purchases/suppliers` que
  llama a `purchase_crud.create_supplier`).
- Crear ordenes de compra contra un proveedor existente, con N lineas de
  repuestos, cantidades y costos unitarios, fecha esperada opcional.
- Registrar la recepcion parcial o completa de una orden en una sola
  transaccion, con lock pesimista por linea y actualizacion del status
  del header.
- Cancelar SOLO ordenes en estado `Pending`, sin tocar stock y sin
  reversar recepciones.
- Mantener las constantes de estado (`Pending`, `Partially Received`,
  `Received`, `Cancelled`) en un modulo centralizado
  `src/zarvent_repuestos/constants.py` (compartido con el spec de
  [sales](../sales/SPEC.md)).

### 2.2 Estados y maquina del header

`purchase_order.status` toma exactamente uno de los cuatro valores
siguientes en v1:

```
                 create_purchase_order
                          |
                          v
                      +---------+
                      | Pending |
                      +----+----+
                           |
            +--------------+--------------+
            |                             |
    receive (>0, < ordered)        receive (todas = ordered)
            |                             |
            v                             v
   +---------------------+          +-----------+
   | Partially Received  |          | Received  |
   +---------------------+          +-----------+

   Solo desde Pending (sin recepciones):
            |
            v
      +-----------+
      | Cancelled |
      +-----------+
```

Reglas concretas en `receive_purchase_order`:

- Si `full_count == total_count` y `total_count > 0` -> `Received`.
- Si `any_count > 0` y `full_count < total_count` -> `Partially Received`.
- Si nadie recibio nada -> `Pending`.

Reglas concretas en `cancel_purchase_order` (nuevo en v1):

- Solo se puede cancelar una orden en `Pending` (sin recepciones).
- Si la orden ya tiene `quantity_received > 0` en alguna linea, se
  rechaza con `ValueError("Solo se pueden cancelar ordenes pendientes
  sin recepciones.")`.
- El nuevo status es `Cancelled` y queda persistido en la columna
  `purchase_order.status`.
- Cancelar una orden **no** decrementa `inventory_stock`: cuando se
  cancela una orden `Pending`, todavia no hubo movimiento de stock
  (el stock solo sube al recibir).

Una vez que el status es `Received` o `Cancelled`, el template no expone
controles de mutacion: los inputs de cantidad recibida quedan
`disabled` y la cancelacion no se ofrece desde la UI.

### 2.3 Rutas Flask v1

| Ruta | Metodo | Decorador | Que hace |
| --- | --- | --- | --- |
| `/purchases` | `GET` | `@login_required` | Lista ordenes con filtros. Carga proveedores activos y repuestos. |
| `/purchases` | `POST` | `@login_required` | Crea orden (`create_purchase_order`). |
| `/purchases/suppliers` | `POST` | `@login_required` | Crea proveedor (`create_supplier`). **Nueva en v1.** |
| `/purchases/<int:purchase_order_id>` | `GET` | `@login_required` | Muestra detalle y formulario de recepcion. |
| `/purchases/<int:purchase_order_id>/receive` | `POST` | `@login_required` | Registra recepcion (`receive_purchase_order`). |
| `/purchases/<int:purchase_order_id>/cancel` | `POST` | `@login_required` | Cancela una orden `Pending` (`cancel_purchase_order`). **Nueva en v1.** |

### 2.4 Validaciones

| Validacion | Donde | Mensaje al usuario |
| --- | --- | --- |
| `supplier_id` numerico positivo | ruta `/purchases` POST | `flash "Selecciona un proveedor."` |
| `items_json` parseable | ruta `/purchases` POST | `flash "Items de la orden estan mal formados."` |
| `expected_date` presente o vacio (opcional) | cliente | sin mensaje; se guarda `NULL` si viene vacio |
| Al menos un item al crear | `create_purchase_order` | `ValueError`: "La orden de compra debe tener al menos un item." |
| `quantity_ordered > 0` | `create_purchase_order` | `ValueError`: "La cantidad pedida del producto {id} debe ser mayor que cero." |
| `unit_cost >= 0` | `create_purchase_order` | `ValueError`: "El costo unitario del producto {id} no puede ser negativo." |
| Cantidad recibida no se reduce | `receive_purchase_order` | `ValueError`: "No puedes reducir la cantidad recibida de la linea {id}." |
| Cantidad recibida no excede lo pedido | `receive_purchase_order` | `ValueError`: "La linea {id} no puede recibir {n} unidades; solo se pidieron {m}." |
| Items recibidos en JSON | ruta `/purchases/<id>/receive` POST | `flash "Indica al menos una cantidad recibida."` |
| Entero entre 0 y `max` en cliente | `collectReceivedItems()` | `alert("Cantidad recibida invalida. Debe ser un numero entero entre 0 y {max}.")` |
| `business_name` y `tax_id` no vacios al crear proveedor | `create_supplier` | `ValueError`: "El nombre comercial del proveedor es obligatorio." / "El NIT del proveedor es obligatorio." |
| `tax_id` unico en BD al crear proveedor | MySQL UNIQUE constraint | `flash "No se pudo crear el proveedor (revisa datos duplicados o el log del servidor)."` (rutina generica) |
| Cancelar solo `Pending` | `cancel_purchase_order` | `ValueError`: "Solo se pueden cancelar ordenes pendientes sin recepciones." |

### 2.5 Mensajes flash

- `success`: `Orden de compra #{id} creada con exito.`,
  `Recepcion registrada con exito.`, `Orden de compra #{id} cancelada.`,
  `Proveedor '{razon_social}' creado con exito.`.
- `error`: mensajes de las validaciones listadas arriba, mas
  `Error al crear la orden de compra: ...`,
  `Error al recibir la orden: ...` y
  `Error al cancelar la orden: ...` como fallback.

### 2.6 Transaccion atomica de la recepcion

`receive_purchase_order` ejecuta todo dentro de una sola conexion MySQL:

1. Validar que `received_items` no este vacio.
2. Por cada item:
   1. `SELECT ... FOR UPDATE` sobre `purchase_order_item` para tomar el
      lock de la fila.
   2. Rechazar si `new_received < current_received` o
      `new_received > quantity_ordered`.
   3. `UPDATE purchase_order_item SET quantity_received = %s`.
   4. Si `delta > 0`, `UPDATE inventory_stock SET quantity_on_hand =
      quantity_on_hand + %s WHERE part_id = ?`.
3. `SELECT SUM(CASE ...)` para contar `full_count`, `any_count`,
   `total_count`.
4. Recalcular `status` (`Received` / `Partially Received` / `Pending`).
5. `UPDATE purchase_order SET status = %s`.
6. `conexion.commit()`. Ante `mysql.connector.Error` o `ValueError` se
   ejecuta `conexion.rollback()` y se re-lanza la excepcion.

### 2.7 Cancelacion atomica

`cancel_purchase_order` (nuevo en v1) ejecuta dentro de una sola
conexion:

1. `SELECT purchase_order_id, status FROM purchase_order WHERE
   purchase_order_id = %s FOR UPDATE`.
2. Si la orden no existe, `ValueError("La orden {id} no existe.")`.
3. Si `status != "Pending"`, `ValueError("Solo se pueden cancelar
   ordenes pendientes sin recepciones.")`.
4. `SELECT COUNT(*) FROM purchase_order_item WHERE purchase_order_id = %s
   AND quantity_received > 0`. Si `> 0`,
   `ValueError("Solo se pueden cancelar ordenes pendientes sin
   recepciones.")`.
5. `UPDATE purchase_order SET status = 'Cancelled' WHERE
   purchase_order_id = %s`.
6. `conexion.commit()`. No se toca `inventory_stock`.

### 2.8 Modulo de constantes centralizado

`src/zarvent_repuestos/constants.py` (nuevo en v1) expone:

- `SALES_STATUS_PAID = "Paid"` (compartido con
  [sales/SPEC.md](../sales/SPEC.md)).
- `PURCHASE_STATUS_PENDING = "Pending"`.
- `PURCHASE_STATUS_PARTIALLY_RECEIVED = "Partially Received"`.
- `PURCHASE_STATUS_RECEIVED = "Received"`.
- `PURCHASE_STATUS_CANCELLED = "Cancelled"` (nuevo en v1).

Las cadenas literales que el CRUD y los templates usan se reemplazan
por estas constantes. Esto es opcional en v1 para el path de datos
(los literales funcionan), pero la **existencia** del modulo y la
constante `PURCHASE_STATUS_CANCELLED` son obligatorias porque el nuevo
flujo de cancelacion no puede depender de un literal repetido.

---

## 3. Cambios requeridos v1

Lista concreta para pasar del estado actual al contrato de la
[Seccion 2](#2-contrato-objetivo-v1).

| # | Cambio | Archivo(s) | Tipo | Afecta spec vecino |
| --- | --- | --- | --- | --- |
| 1 | Crear `src/zarvent_repuestos/constants.py` con `PURCHASE_STATUS_PENDING`, `PURCHASE_STATUS_PARTIALLY_RECEIVED`, `PURCHASE_STATUS_RECEIVED`, `PURCHASE_STATUS_CANCELLED` y `SALES_STATUS_PAID`. | `src/zarvent_repuestos/constants.py` (nuevo) | codigo | [sales/SPEC.md](../sales/SPEC.md) |
| 2 | Implementar `cancel_purchase_order(purchase_order_id)` en `purchase_crud.py`: `SELECT ... FOR UPDATE` sobre el header, valida `status == "Pending"` y que `quantity_received = 0` en todas las lineas, hace `UPDATE purchase_order SET status = 'Cancelled'`, commit, rollback ante error. | `src/zarvent_repuestos/crud/purchase_crud.py` | codigo | este spec |
| 3 | Agregar ruta `POST /purchases/<int:purchase_order_id>/cancel` que llame a `cancel_purchase_order`, haga `flash` de exito o error y redirija al detalle. | `src/zarvent_repuestos/web/app.py` | codigo | este spec |
| 4 | Exponer en el template `purchases.html` (o en una seccion dedicada del mismo template) un formulario para crear proveedores que haga `POST` a `/purchases/suppliers` con `business_name`, `tax_id`, `phone`, `email`, `address`. | `src/zarvent_repuestos/web/templates/purchases.html` | UI | este spec |
| 5 | Agregar ruta `POST /purchases/suppliers` que parsee los campos, llame a `create_supplier` y haga `flash` de exito o error. Redirige a `/purchases`. | `src/zarvent_repuestos/web/app.py` | codigo | este spec |
| 6 | Mostrar en `purchase_detail.html` un boton "Cancelar Orden" SOLO cuando `order.status == "Pending"` y `order.items[].quantity_received == 0`. El boton hace `POST` a `/purchases/<id>/cancel`. | `src/zarvent_repuestos/web/templates/purchase_detail.html` | UI | este spec |
| 7 | Pintar en `purchases.html` y `purchase_detail.html` el badge "Cancelada" para `status == "Cancelled"`, en linea con la paleta del diseno actual (gris sobre `cold-white`). | `src/zarvent_repuestos/web/templates/purchases.html`, `src/zarvent_repuestos/web/templates/purchase_detail.html` | UI | este spec |
| 8 | Reemplazar los literales `"Pending"`, `"Partially Received"`, `"Received"` en `purchase_crud.py` por las constantes del modulo nuevo. | `src/zarvent_repuestos/crud/purchase_crud.py` | codigo | este spec |
| 9 | Cubrir `cancel_purchase_order` con tests: rechazo cuando `status != "Pending"`, rechazo cuando hay recepciones, transicion exitosa a `Cancelled`, `rollback` ante error. | `tests/test_purchase_crud.py` (extension) | test | este spec |
| 10 | Cubrir la ruta `POST /purchases/suppliers` con un test que verifique `200/302` y la llamada a `create_supplier`. | `tests/test_purchase_supplier_route.py` (nuevo) | test | este spec |

Ninguno de estos cambios rompe la transaccion atomica documentada en
las secciones 2.6 y 2.7.

---

## 4. Aceptacion automatizada

Tests en `tests/` que demuestran que el contrato se cumple.

### 4.1 Tests existentes

- [`tests/test_purchase_crud.py`](../../tests/test_purchase_crud.py) cubre
  las funciones de `purchase_crud.py` con la base de datos mockeada:
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
      `commit`, ningun `rollback`, `lastrowid = 42`, `status = "Pending"`,
      `total_amount = 100.0`.
  - `CreateSupplierValidationTest`:
    - `test_empty_business_name_raises_value_error_before_connection`.
    - `test_empty_tax_id_raises_value_error_before_connection`.
  - `ReceivePurchaseOrderTest`:
    - `test_full_reception_marks_header_received_and_increments_stock_by_delta`:
      con `ordered=5`, `current=0`, `new=5` -> `status = "Received"`,
      `UPDATE inventory_stock (5, part_id)`, commit unico.
    - `test_partial_reception_marks_header_partially_received_and_uses_partial_delta`:
      con `ordered=5`, `current=0`, `new=2` -> `status = "Partially
      Received"`, `UPDATE inventory_stock (2, part_id)`.
    - `test_reducing_received_is_rejected_with_value_error`: con
      `current=3`, `new=1` -> `ValueError`, rollback, sin updates a stock.
    - `test_over_receiving_is_rejected_with_value_error`: con `ordered=5`,
      `new=6` -> `ValueError`, rollback, sin updates a stock.

- [`tests/test_purchase_detail_route.py`](../../tests/test_purchase_detail_route.py)
  cubre la ruta `/purchases/<id>` con la app Flask real (cliente de
  test) y la base mockeada:
  - `test_purchase_detail_renders_200_with_preset_order`: la ruta
    devuelve 200 y muestra el codigo interno, el nombre del producto y el
    nombre del proveedor.
  - `test_purchase_detail_renders_with_no_items`: la ruta devuelve 200
    aun con `items = []` y no muestra el codigo interno esperado.
  - `test_purchase_detail_returns_404_when_order_missing`: si la orden
    no existe, devuelve 404.

### 4.2 Brechas a cerrar en v1 (tests a aniadir)

| Brecha | Test a aniadir | Archivo sugerido |
| --- | --- | --- |
| `cancel_purchase_order` exitoso transiciona `Pending -> Cancelled` con un solo `commit`, ningun `UPDATE inventory_stock`. | `test_cancel_pending_order_transitions_to_cancelled_without_touching_stock`. | `tests/test_purchase_crud.py` (extension) |
| `cancel_purchase_order` rechaza cuando la orden tiene `quantity_received > 0` en alguna linea. | `test_cancel_rejected_when_receptions_exist`. | `tests/test_purchase_crud.py` (extension) |
| `cancel_purchase_order` rechaza cuando la orden esta en `Received` o `Cancelled` o `Partially Received`. | `test_cancel_rejected_when_status_not_pending`. | `tests/test_purchase_crud.py` (extension) |
| `POST /purchases/<id>/cancel` redirige al detalle con flash de exito. | `test_cancel_route_redirects_with_success_flash`. | `tests/test_purchase_cancel_route.py` (nuevo) |
| `POST /purchases/suppliers` invoca `create_supplier` y redirige a `/purchases` con flash de exito. | `test_create_supplier_route_invokes_crud_and_redirects`. | `tests/test_purchase_supplier_route.py` (nuevo) |
| `create_supplier` con `tax_id` duplicado devuelve `None` y permite al caller mostrar el flash generico. | `test_create_supplier_returns_none_on_duplicate_tax_id` (mockear `mysql.connector.Error`). | `tests/test_purchase_crud.py` (extension) |

Comandos sugeridos:

```bash
uv run python -m unittest tests.test_purchase_crud
uv run python -m unittest tests.test_purchase_detail_route
uv run python -m unittest tests.test_purchase_cancel_route
uv run python -m unittest tests.test_purchase_supplier_route
```

---

## 5. Aceptacion manual en navegador / DataGrip

Pasos reproducibles que un estudiante junior puede correr para verificar el
contrato desde la UI o desde un cliente SQL.

### 5.1 En navegador

Prerequisito: estar logueado como `admin` / `admin123` y tener al menos
un proveedor y un repuesto cargados.

1. **Crear proveedor desde la UI.**
   - Ir a `/purchases`. En la seccion "Nuevo Proveedor" completar
     `business_name`, `tax_id` (unico), telefono, email, direccion.
   - Pulsar "Crear Proveedor". Verificar: flash de exito y el proveedor
     aparece en el dropdown del modal de nueva orden.
2. **Crear orden end-to-end.**
   - Pulsar "Nueva Compra". Seleccionar proveedor, dejar fecha esperada
     vacia, agregar dos repuestos con cantidad y costo validos.
   - Pulsar "Crear Orden". Verificar: redirige a `/purchases/<id>` con
     flash de exito, total correcto, ambos items con
     `quantity_received = 0`, badge "Pendiente".
3. **Recepcion parcial.**
   - En el detalle, modificar el primer input a 2 (sobre un pedido de 5)
     y pulsar "Registrar Recepcion". Verificar: flash de exito, badge
     "Recibida Parcialmente" (azul), chip "Parcial" en la fila,
     `inventory_stock` para ese repuesto aumento en 2.
4. **Recepcion completa.**
   - En el detalle, poner todos los inputs en el maximo y registrar.
     Verificar: badge "Recibida" (verde), inputs `disabled`, mensaje
     "Esta orden ya fue recibida por completo", stock incrementado en lo
     que faltaba.
5. **Cancelar orden `Pending`.**
   - En el detalle de una orden `Pending` SIN recepciones, pulsar
     "Cancelar Orden". Verificar: flash de exito, badge "Cancelada" en
     el detalle y en el listado, el stock de los repuestos de la orden
     NO cambio.
6. **Cancelar orden NO `Pending` debe estar bloqueado.**
   - En el detalle de una orden `Partially Received` o `Received`, el
     boton "Cancelar Orden" NO debe estar visible. Si se hace POST
     directo a `/purchases/<id>/cancel` con `id` de una orden no
     `Pending`, el flash debe ser de error y la base no debe cambiar.
7. **Validaciones de entrada en el cliente.**
   - Intentar `quantity = 0` o `unit_cost = -1` en el modal: el JS
     muestra `alert`.
   - Intentar registrar la orden sin proveedor o sin items: `alert`
     antes de enviar.
   - Intentar enviar una cantidad recibida mayor al maximo: `alert`
     desde `collectReceivedItems`.
8. **Validaciones del servidor.**
   - Forzar un POST directo a `/purchases` con `supplier_id = 0` o
     `items_json` invalido: flash de error, redirige a `/purchases`.
   - Forzar una recepcion con `quantity_received` menor al actual o
     mayor al `quantity_ordered`: flash "Error de validacion: ...",
     redirige al detalle sin cambiar stock ni status.
   - Forzar la creacion de dos proveedores con el mismo `tax_id`: el
     segundo flash debe ser de error.
9. **Filtros del sidebar.**
   - Pulsar cada radio del sidebar y comprobar que la URL lleva
     `?status=...` y la tabla solo muestra ordenes con ese estado.
   - Pulsar "Limpiar Filtros" y comprobar que vuelve a la lista
     completa.
   - Confirmar que el sidebar expone un filtro "Canceladas" en v1
     (nuevo) y que devuelve las ordenes canceladas.

### 5.2 En DataGrip / cliente SQL

Prerequisito: tener `mysql` CLI o DataGrip conectado a la base
`sis122_zarvent_repuestos`.

1. **Verificar que `supplier.tax_id` es unico.**
   ```sql
   INSERT INTO supplier (business_name, tax_id) VALUES ('Repetido SA', '9999999');
   INSERT INTO supplier (business_name, tax_id) VALUES ('Repetido SA 2', '9999999');
   ```
   La segunda insercion debe ser rechazada por MySQL.
2. **Verificar la maquina de estados del header.**
   ```sql
   SELECT status, COUNT(*) FROM purchase_order GROUP BY status;
   ```
   En v1 los valores posibles son exactamente cuatro: `Pending`,
   `Partially Received`, `Received`, `Cancelled`.
3. **Verificar que una cancelacion NO toca `inventory_stock`.**
   Antes y despues de cancelar una orden `Pending`, capturar el stock
   de cada `part_id` de la orden:
   ```sql
   SELECT s.part_id, s.quantity_on_hand
   FROM inventory_stock s
   WHERE s.part_id IN (1, 2);
   ```
   Ambos `SELECT` deben devolver los mismos valores.
4. **Verificar que `CASCADE` borra las lineas al borrar la cabecera.**
   ```sql
   SELECT COUNT(*) FROM purchase_order_item WHERE purchase_order_id = 999;
   DELETE FROM purchase_order WHERE purchase_order_id = 999;
   SELECT COUNT(*) FROM purchase_order_item WHERE purchase_order_id = 999;
   ```
   El segundo conteo debe ser 0.
5. **Verificar que `RESTRICT` impide borrar un proveedor con ordenes.**
   ```sql
   DELETE FROM supplier WHERE supplier_id = (SELECT supplier_id FROM purchase_order LIMIT 1);
   ```
   MySQL debe rechazar la operacion.
6. **Verificar que `unit_cost` guarda precio historico.**
   ```sql
   SELECT i.purchase_order_item_id, i.unit_cost, p.purchase_cost
   FROM purchase_order_item i
   JOIN part p ON i.part_id = p.part_id
   WHERE i.unit_cost <> p.purchase_cost;
   ```
   En el seed demo esta consulta puede devolver filas; eso valida que
   se guarda precio historico.
7. **Forzar una condicion de carrera sobre `purchase_order_item`.**
   Abrir dos sesiones MySQL concurrentes, correr en ambas
   `SELECT ... FROM purchase_order_item WHERE purchase_order_id = X AND
   purchase_order_item_id = Y FOR UPDATE;`. La segunda sesion debe
   quedar bloqueada hasta que la primera haga `COMMIT` o `ROLLBACK`.

---

## 6. Decisiones fuera de alcance

Lo que el analisis academico pedia y el equipo decidio NO entregar en
v1, con justificacion. Si quedan como objetivo futuro, se etiquetan
`backlog v2`.

| Tema | RF origen | Estado v1 | Justificacion |
| --- | --- | --- | --- |
| Devoluciones a proveedor (RF-08). | `docs/analysis/requirements.md` RF-08; `processes.md` (Devoluciones). | `fuera de alcance v1` (`backlog v2`) | RF-08 lo cubre el modulo de Ventas, no Compras. Las tablas `RETURN_ORDER` y `RETURN_ORDER_ITEM` no se crean en `init_db.py`. |
| Edicion de ordenes existentes. | (no documentado). | `fuera de alcance v1` (`backlog v2`) | No hay ruta `PUT`/`PATCH`. Una vez creada, la unica mutacion permitida es la recepcion o la cancelacion `Pending`. |
| `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM` (tabla separada para recepciones parciales). | `db_explanation.md` (Limitaciones aceptadas). | `fuera de alcance v1` (`backlog v2`) | La recepcion se aplica directamente sobre `purchase_order_item`. Esto significa que no hay un historial separado de recepciones (no se puede saber "quien recibio que dia"); solo queda el valor acumulado. |
| Alertas automaticas de atraso segun `expected_date`. | `processes.md` (Compras a proveedores). | `fuera de alcance v1` (`backlog v2`) | `expected_date` es opcional y se guarda como `NULL` si no se completa. No hay logica de notificacion asociada. |
| Autenticacion por actor (`actors.md`: Responsable de compras vs Encargado de almacen). | `actors.md`; `procedures.md` (Roles). | `fuera de alcance v1` (`backlog v2`) | La unica exigencia es `login_required`; no se diferencia que usuario puede crear ordenes, recibir o cancelar. El control de actor queda delegado a la convencion del equipo. |
| Cancelacion de ordenes con recepciones parciales (reversar el stock). | (no documentado). | `fuera de alcance v1` (`backlog v2`) | En v1 la cancelacion esta limitada a `Pending` con `quantity_received = 0` en todas las lineas. Reversar stock requiere reglas que exceden el alcance academico. |
| Mockup academico dedicado. | (no documentado). | `fuera de alcance v1` (`backlog v2`) | `.cszv/mockups/` no tiene `purchases_mockup.*`. La pantalla real es la unica referencia visual. |

`backlog v2` se usa **unicamente** en esta seccion y en la columna de
cambios de la matriz del `spec/README.md`. Nunca aparece como
`Estado v1` en la [Seccion 7](#7-trazabilidad-rf).

---

## 7. Trazabilidad RF

Tabla que cruza cada tema del modulo con su RF origen, su soporte de
datos y el codigo real que lo implementa, con un `Estado v1` por fila.

Los cuatro valores posibles para `Estado v1` son exactamente los definidos
en [`spec/README.md`](../README.md):

- `implementado v1`
- `parcial v1`
- `corregir UI/spec`
- `fuera de alcance v1`

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado v1 |
| --- | --- | --- | --- | --- |
| Entidad `SUPPLIER` con `tax_id` unico | `requirements.md` RF-07; `actors.md` (Proveedor); `processes.md` linea 49 | `erd.md` (SUPPLIER); `db_explanation.md` linea 21 | Tabla `supplier` en `init_db.py`; CRUD `create_supplier`, `list_suppliers`, `get_supplier` en `purchase_crud.py` | `implementado v1` |
| Crear proveedores desde la UI | `processes.md` linea 49; `procedures.md` (Registro de compra, paso 2) | (no modelado) | `create_supplier` existe; falta la ruta `POST /purchases/suppliers` y la seccion en `purchases.html` | `parcial v1` (ver [Seccion 3, cambios 4 y 5](#3-cambios-requeridos-v1)) |
| Entidad `PURCHASE_ORDER` con `status` y `expected_date` | `requirements.md` RF-07; `procedures.md` (Registro de compra) | `erd.md` (PURCHASE_ORDER); `db_explanation.md` linea 30 | Tabla `purchase_order` en `init_db.py`; CRUD `create_purchase_order`, `list_purchase_orders`, `get_purchase_order_details`; rutas `/purchases` GET/POST y `/purchases/<id>` GET | `implementado v1` |
| `expected_date` opcional | (no documentado) | `erd.md` `date expected_date` (sin `NOT NULL`) | `init_db.py` crea la columna sin `NOT NULL`; ruta `/purchases` POST acepta vacio y guarda `NULL` | `implementado v1` |
| Entidad `PURCHASE_ORDER_ITEM` con cantidad pedida, recibida y costo historico | `processes.md` linea 49; `procedures.md` (Registro de compra, paso 3) | `erd.md` (PURCHASE_ORDER_ITEM); `db_explanation.md` linea 31 | Tabla `purchase_order_item` en `init_db.py`; CRUD `create_purchase_order` y `receive_purchase_order` | `implementado v1` |
| Maquina de estados `Pending` / `Partially Received` / `Received` | (no modelado explicitamente) | (no modelado) | Implementada en `receive_purchase_order` (`full_count`, `any_count`, `total_count`) y reflejada en `purchases.html` y `purchase_detail.html` con badges | `implementado v1` |
| Transicion `Pending -> Cancelled` (nueva en v1) | (no documentado) | (no modelado) | `cancel_purchase_order` y ruta `POST /purchases/<id>/cancel` (pendientes: ver [Seccion 3, cambios 2 y 3](#3-cambios-requeridos-v1)) | `parcial v1` (cambios pendientes) |
| Recepcion parcial o completa | `procedures.md` (Registro de compra, pasos 5-6) | (no modelado) | `receive_purchase_order` con `FOR UPDATE`, validacion de no reducir y no exceder; UI en `purchase_detail.html` con `collectReceivedItems` | `implementado v1` |
| Incremento de `inventory_stock.quantity_on_hand` al recibir | `processes.md` linea 50; `procedures.md` (Control de inventario) | `db_explanation.md` linea 26 | `receive_purchase_order` hace `UPDATE inventory_stock SET quantity_on_hand = quantity_on_hand + delta` solo si `delta > 0` | `implementado v1` |
| Tabla separada de recepciones (`PURCHASE_RECEIPT_ITEM`) | (no nombrada) | `db_explanation.md` (Limitaciones aceptadas: `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM`) | No existe; la recepcion se hace directo sobre `purchase_order_item` | `fuera de alcance v1` |
| Edicion de ordenes de compra | (no documentado) | (no modelado) | No hay ruta `PUT`/`PATCH` ni template | `fuera de alcance v1` |
| Validacion de `quantity_ordered > 0` y `unit_cost >= 0` al crear | (regla implicita) | (no modelado) | `create_purchase_order` valida ambos y lanza `ValueError`; el cliente tambien valida en `addItemRow()` | `implementado v1` |
| Validacion de no reducir y no exceder al recibir | (regla implicita) | (no modelado) | `receive_purchase_order` valida ambos; el cliente valida el rango en `collectReceivedItems` | `implementado v1` |
| Lock pesimista `FOR UPDATE` sobre items | (no documentado) | (no modelado) | `SELECT ... FOR UPDATE` en `receive_purchase_order` por cada linea | `implementado v1` |
| `CASCADE` en items al borrar orden | (no documentado) | `init_db.py` define `ON DELETE CASCADE` para `purchase_order_item.purchase_order_id` | Esquema en `init_db.py` | `implementado v1` |
| `UNIQUE` en `supplier.tax_id` | (no documentado) | `db_explanation.md` (Reglas que deben defenderse) | `init_db.py`: `tax_id VARCHAR(50) UNIQUE NOT NULL` | `implementado v1` |
| Listar ordenes con filtro por estado | (no documentado) | (no modelado) | `purchases.html` sidebar + `list_purchase_orders(status=...)` | `implementado v1` |
| Filtro "Canceladas" en el sidebar | (no documentado) | (no modelado) | Sidebar hoy expone `Todas / Pendientes / Recibidas Parcialmente / Recibidas`; falta agregar `Canceladas` | `parcial v1` (ver [Seccion 3, cambio 7](#3-cambios-requeridos-v1)) |
| Constantes de estado centralizadas | (no documentado) | (no modelado) | Literales dispersos en `purchase_crud.py` y en templates | `parcial v1` (modulo `constants.py` a crear: ver [Seccion 3, cambio 1](#3-cambios-requeridos-v1)) |
| Mockup academico del modulo de compras | (no documentado) | (no modelado) | No existe `purchases_mockup.*` en `.cszv/mockups/` | `fuera de alcance v1` |
