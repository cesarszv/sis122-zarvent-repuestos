# SPEC — Ventas

Contrato funcional y tecnico del modulo de Ventas de **Zarvent Repuestos**.
Cubre el registro POS de una venta, sus lineas, su cobro y el comprobante
asociado. Esta escrito como **contrato objetivo v1** y como base de defensa
para un estudiante de primer ano de Base de Datos I.

El modulo materializa la cadena:

`CUSTOMER -> SALES_ORDER -> SALES_ORDER_ITEM -> PART -> INVENTORY_STOCK`

mas el vinculo `SALES_ORDER -> PAYMENT` descritos en
[`docs/database/db_explanation.md`](../../docs/database/db_explanation.md).

---

## 1. Estado actual (reverse-engineered)

Lo que el codigo hace HOY, leido del repo. No es diseno, es evidencia.

### 1.1 Rutas Flask

Definidas en [`src/zarvent_repuestos/web/app.py`](../../src/zarvent_repuestos/web/app.py).

| Ruta | Metodo | Linea | Funcion que la implementa | Que hace |
| --- | --- | --- | --- | --- |
| `/sales` | `GET` | `app.py:186` | `sales()` | Lista ordenes de venta aplicando los filtros `status`, `start_date` y `end_date`. Carga `parts` y `customers` para alimentar el modal de registro. Renderiza `sales.html`. |
| `/sales` | `POST` | `app.py:186` | `sales()` | Procesa el formulario de nueva venta. Valida cliente (existente o nuevo), parsea `items_json`, llama a `sales_crud.crear_orden_venta`, hace `flash` y redirige a `/sales`. |
| `/sales/receipt/<int:sales_order_id>` | `GET` | `app.py:275` | `receipt()` | Devuelve el HTML del comprobante POS para la venta. Responde `404 "Venta no encontrada"` si la orden no existe. |

Las tres rutas usan `@login_required` (`app.py:69`).

### 1.2 Templates

- [`src/zarvent_repuestos/web/templates/sales.html`](../../src/zarvent_repuestos/web/templates/sales.html):
  cabecera con titulo "Ordenes de Venta" y boton "Nueva Venta"; sidebar de
  filtros con radios `All Orders`, `Paid`, `Pending`, `Cancelled` y rango
  `start_date` / `end_date`; tabla con columnas Codigo (`#ORD-{id}`), Cliente
  Facturacion, Fecha (`dd/mm/yyyy`), Estado (badge verde), Total Cobrado y
  boton "Ver Recibo"; modal `new-order-modal` con el formulario de registro;
  modal `receipt-modal` con contenido inyectado por AJAX.

  Bloque `extra_js` (`sales.html:277-437`): `addedItems` (arreglo en memoria),
  `toggleModal`, `toggleClientFields`, `addProductRow`, `removeProductRow`,
  `recalculateTotals`, `submitSalesOrder` y `viewReceipt`.

- [`src/zarvent_repuestos/web/templates/receipt.html`](../../src/zarvent_repuestos/web/templates/receipt.html):
  comprobante estilo POS con fuente monoespaciada y bordes discontinuos.
  Muestra numero de venta, fecha, cliente (`billing_name`), NIT/CI (`tax_id`),
  tabla de items (codigo, nombre, cantidad, precio unitario, subtotal),
  subtotal, descuento (solo si `discount_amount > 0`) y total. Se inyecta
  como fragmento HTML dentro de `receipt-modal`, no es una pagina navegable
  ni un PDF.

### 1.3 Funciones CRUD usadas

Definidas en
[`src/zarvent_repuestos/crud/sales_crud.py`](../../src/zarvent_repuestos/crud/sales_crud.py).

| Funcion | Responsabilidad |
| --- | --- |
| `crear_orden_venta(customer_id, items, payment_method)` | Crea la cabecera, los items, descuenta `inventory_stock` y registra el `payment` en una sola transaccion. Devuelve `sales_order_id` o lanza excepcion. |
| `listar_ordenes_venta(status, start_date, end_date)` | Lista ordenes con `JOIN` a `customer` y `person`. Aplica filtros opcionales. Ordena por `sales_order_id DESC`. |
| `obtener_detalles_orden(sales_order_id)` | Devuelve la cabecera mas la lista de items, con `JOIN` a `customer` y `person`. |
| `obtener_metricas_dashboard()` | Calcula metricas para `/dashboard`: ventas del dia, ordenes totales, ultimas 5 ordenes, items de stock bajo, etc. |

### 1.4 Tablas relacionadas

Definidas en
[`src/zarvent_repuestos/database/init_db.py`](../../src/zarvent_repuestos/database/init_db.py).

- `sales_order` (`sales_order_id`, `customer_id`, `order_date`, `status`,
  `subtotal`, `discount_amount`, `total_amount`).
- `sales_order_item` (`sales_order_item_id`, `sales_order_id`, `part_id`,
  `quantity`, `unit_price`, `discount_amount`).
- `payment` (`payment_id`, `sales_order_id`, `payment_date`, `method`,
  `amount`, `reference_number`, `status`).
- `inventory_stock` (`inventory_stock_id`, `part_id` UNIQUE, `quantity_on_hand`,
  `reorder_level`): se valida y se decrementa.
- `customer` y `person`: para identificar al cliente y mostrar nombre fiscal.
- `part`: para precio historico y descripcion del item vendido.

### 1.5 Comportamiento visible HOY

- Toda venta se crea con `status = "Paid"`. La capa CRUD no expone ningun
  flujo que inserte `Pending` o `Cancelled` (`sales_crud.py:76`).
- Por cada venta se inserta exactamente un `payment` por el total completo
  (`sales_crud.py:101-107`).
- El comprobante se carga dentro de `receipt-modal` via `fetch`, no en una
  pagina dedicada navegable.
- El sidebar de `sales.html` ofrece los filtros `Pending` y `Cancelled` como
  radios, pero esos filtros SIEMPRE devuelven lista vacia porque el codigo
  nunca inserta otros valores (`sales.html:35-42`).
- El dashboard calcula `today_sales_amount` con
  `WHERE order_date = CURDATE() AND status != 'Cancelled'`
  (`sales_crud.py:222-225`). La condicion `status != 'Cancelled'` no tiene
  contraparte en la insercion: nunca se descartan filas.
- La UI de venta no captura descuento por linea; el JS siempre envia
  `discount_amount: 0.0` por item (`sales.html:346`). El backend si lo
  soporta y lo valida.
- `obtener_metricas_dashboard` no expone hoy el reparto de pagos por metodo
  (`payments_by_method`); esa metrica NO esta calculada en
  `sales_crud.py:206-275`.

---

## 2. Contrato objetivo v1

Lo que el spec PROMETE en v1. Cualquier entrega que no cumpla esto queda
rechazada como contrato.

### 2.1 Alcance funcional

- Registrar una venta POS en una sola transaccion atomica, con N lineas de
  repuestos, descuento opcional por linea, un unico pago por el total y
  comprobante HTML imprimible.
- Listar ventas con filtros por estado y rango de fechas.
- Consultar el comprobante de una venta existente desde la misma pantalla.
- Exponer la metrica "ventas del dia" en el dashboard consumiendo `Paid`.
- Exponer el reparto de pagos del dia por metodo en el dashboard
  (`payments_by_method`).

### 2.2 Estados y reglas de la venta

- Toda venta creada por el flujo v1 se inserta con `sales_order.status =
  "Paid"`. La columna admite otros valores por el `VARCHAR(50)`, pero el
  CRUD v1 **no** expone el camino para crearlas en `Pending` o `Cancelled`.
- El filtro `All Orders` (default) y `Paid` son los unicos que devuelven
  datos en v1. Los radios `Pending` y `Cancelled` se retiran del sidebar
  de `sales.html` (ver [Seccion 3](#3-cambios-requeridos-v1)).
- `payment.status` siempre se inserta como `"Completed"`
  (`sales_crud.py:107`).
- `payment.amount` siempre coincide con `sales_order.total_amount`. No hay
  pagos parciales ni multiples pagos en v1.
- `order_date` y `payment_date` son siempre `datetime.date.today()` del
  servidor. La app no permite registrar ventas con fecha manual.

### 2.3 Validaciones de entrada

#### Cliente (cliente nuevo en el mismo POST)

- `new_first_name`, `new_last_name` y `new_identity_number` son obligatorios
  cuando el modo es `new`.
- Antes de crear el cliente nuevo, el backend busca por documento de
  identidad (`customer_crud.buscar_cliente_por_doc`). Si existe, reutiliza
  el `customer_id`; si no, llama a `customer_crud.crear_cliente`.
- Si el alta de cliente nuevo lanza excepcion, se muestra
  `"No se pudo registrar al nuevo cliente."` como `flash` de error y la
  venta no se crea.

#### Cliente (cliente existente)

- `customer_id` es obligatorio cuando el modo es `existing`.
- Si no llega, se muestra `"No se selecciono ningun cliente."` como `flash`
  de error.

#### Items

- `items_json` debe parsear como JSON no vacio.
- Si la lista es vacia, se lanza `ValueError("La orden de venta debe tener
  al menos un item.")` y se traduce a `flash` de error.
- Por cada item: `quantity > 0`, `unit_price > 0`, `0 <= discount_amount <=
  unit_price`. Si falla, `ValueError` y la transaccion no abre conexion
  (`test_sales_validation.py:10-17`).

#### Stock

- Antes de tocar la base, `crear_orden_venta` corre
  `SELECT quantity_on_hand FROM inventory_stock WHERE part_id = %s FOR UPDATE`
  por cada item. Si `quantity_on_hand < qty_needed`, lanza
  `ValueError("Stock insuficiente para el producto ID X. Disponible: A,
  Solicitado: B.")`. La UI ademas bloquea con `alert` antes de enviar.

#### Metodo de pago

- El selector `payment_method` de `sales.html` expone exactamente cuatro
  valores persistidos en `payment.method`:
  - `Efectivo`
  - `Tarjeta de Debito`
  - `Tarjeta de Credito`
  - `Transferencia` (etiquetada en UI como "Transferencia QR")
- Cualquier otro valor que llegue al backend se persiste tal cual; la UI no
  deberia permitirlo.

### 2.4 Transaccion atomica (side effects garantizados)

`crear_orden_venta` ejecuta todo dentro de una sola conexion MySQL:

1. Validar `quantity`, `unit_price`, `discount_amount` por item sin abrir
   conexion.
2. Calcular `subtotal`, `discount_total` y `total_amount` en Python.
3. Abrir conexion y cursor.
4. Por cada item, `SELECT ... FOR UPDATE` sobre `inventory_stock.part_id`.
   Si el repuesto no esta registrado en inventario, lanza
   `ValueError("El producto con ID X no esta registrado en el inventario.")`.
5. Insertar cabecera en `sales_order` con `status = "Paid"`.
6. Por cada item, insertar `sales_order_item` y ejecutar
   `UPDATE inventory_stock SET quantity_on_hand = quantity_on_hand - %s
   WHERE part_id = %s`.
7. Insertar `payment` con `status = "Completed"`, `method = payment_method`,
   `amount = total_amount`, `payment_date = order_date` y
   `reference_number = f"PAY-{sales_order_id}-{datetime.now().strftime('%M%S')}"`.
8. `conexion.commit()`. Ante `mysql.connector.Error` o `ValueError` se
   ejecuta `conexion.rollback()` y se re-lanza la excepcion.

### 2.5 Mensajes flash

| Caso | Mensaje | Categoria |
| --- | --- | --- |
| Venta creada | `Venta #{sales_order_id} registrada correctamente.` | `success` |
| Error al crear (id devuelto `None`) | `Error al registrar la venta.` | `error` |
| Excepcion atrapada | `Error al procesar venta: {e}` | `error` |

### 2.6 Comprobante (`/sales/receipt/<id>`)

- Responde `200` con `receipt.html` renderizado cuando la orden existe.
- Responde `404 "Venta no encontrada"` cuando
  `obtener_detalles_orden` retorna `None`.
- El comprobante expone los datos del cliente (`billing_name`, `tax_id`),
  los items con `internal_code`, `name`, `quantity`, `unit_price`,
  subtotal (`unit_price * quantity`), el subtotal, el descuento (solo si
  `discount_amount > 0`) y el total. El boton "Imprimir Comprobante" del
  modal dispara `window.print()` sobre el HTML preformateado.

### 2.7 Dashboard

- `obtener_metricas_dashboard` retorna ademas de las metricas actuales una
  nueva entrada `payments_by_method: list[dict]` con el reparto de pagos
  del dia actual, agrupado por `payment.method`. Cada elemento expone
  `method` y `amount` (`SUM(payment.amount)`), ordenado por monto
  descendente. La consulta base es
  `SELECT method, SUM(amount) FROM payment WHERE payment_date = CURDATE()
  AND sales_order_id IN (SELECT sales_order_id FROM sales_order WHERE
  status != 'Cancelled' AND order_date = CURDATE()) GROUP BY method`.
- `metrics.today_sales_amount` se calcula con la misma condicion
  `status != 'Cancelled'` que ya existe en el codigo (la exclusion queda
  como defensa academica: aunque hoy nunca se inserta otra cosa, deja la
  puerta abierta al valor `Cancelled` si v2 lo introduce).
- `dashboard.html` no consume `payments_by_method` en v1: la metrica se
  calcula y queda disponible para un consumo futuro. **No** se agrega UI
  nueva en v1 (ver [Seccion 3](#3-cambios-requeridos-v1)).

### 2.8 Comportamiento del cliente AJAX

- `viewReceipt(orderId)` es la unica llamada AJAX del modulo. Muestra
  "Cargando comprobante..." y luego reemplaza por el HTML del comprobante.
- Si la peticion falla (`!res.ok`), inyecta un parrafo `text-zarvent-red`
  con el mensaje del error.
- No hay timeout explicito ni reintentos: depende de la sesion activa.

---

## 3. Cambios requeridos v1

Lista concreta para pasar del estado actual al contrato de la
[Seccion 2](#2-contrato-objetivo-v1).

| # | Cambio | Archivo(s) | Tipo | Afecta spec vecino |
| --- | --- | --- | --- | --- |
| 1 | Quitar los radios `Pending` y `Cancelled` del sidebar de filtros de `sales.html` (dejan de existir radios que siempre devuelven vacio). | `src/zarvent_repuestos/web/templates/sales.html` | UI | este spec |
| 2 | Aceptar y persistir los cuatro valores de `payment_method` (`Efectivo`, `Tarjeta de Debito`, `Tarjeta de Credito`, `Transferencia`). **No** requiere cambio de codigo: el valor llega como `string` y se inserta tal cual. Verificar que el `<select>` en `sales.html` ya los expone y que `payment.method` es `VARCHAR(50)`. | `src/zarvent_repuestos/crud/sales_crud.py`, `src/zarvent_repuestos/web/templates/sales.html` | codigo/UI | este spec |
| 3 | Corregir la metrica `today_sales_amount` para que no dependa de un filtro que no tiene contraparte: el contrato v1 la documenta con `status != 'Cancelled'`. **No** requiere cambio de SQL: la condicion ya esta en `sales_crud.py:222-225`. | `src/zarvent_repuestos/crud/sales_crud.py` | spec/codigo | [dashboard/SPEC.md](../dashboard/SPEC.md) |
| 4 | Exponer `payments_by_method` desde `obtener_metricas_dashboard`. La query es nueva: `SELECT method, SUM(amount) FROM payment WHERE payment_date = CURDATE() AND sales_order_id IN (SELECT sales_order_id FROM sales_order WHERE status != 'Cancelled' AND order_date = CURDATE()) GROUP BY method ORDER BY SUM(amount) DESC`. La salida es `list[dict]` con llaves `method` y `amount`. | `src/zarvent_repuestos/crud/sales_crud.py` | codigo | [dashboard/SPEC.md](../dashboard/SPEC.md) |
| 5 | Mover las constantes de estado de venta a `src/zarvent_repuestos/constants.py` (modulo centralizado: `SALES_STATUS_PAID = "Paid"`). Reemplazar el literal `"Paid"` en `sales_crud.py:76` por la constante. | `src/zarvent_repuestos/constants.py` (nuevo), `src/zarvent_repuestos/crud/sales_crud.py` | codigo | [purchases/SPEC.md](../purchases/SPEC.md) (el mismo modulo reune estados de compra) |
| 6 | Cubrir el caso de stock insuficiente en `crear_orden_venta` con un test que verifique el rollback. | `tests/test_sales_validation.py` (nuevo caso) | test | este spec |
| 7 | Cubrir el caso de pago (`payment`) insertado con `amount = total_amount` y `status = "Completed"` con un test mockeado. | `tests/test_sales_payment.py` (nuevo) | test | este spec |

Ninguno de los cambios rompe la transaccion atomica documentada en
`[Seccion 2.4](#24-transaccion-atomica-side-effects-garantizados)`.

---

## 4. Aceptacion automatizada

Tests en `tests/` que demuestran que el contrato se cumple.

### 4.1 Tests existentes

- [`tests/test_sales_validation.py`](../../tests/test_sales_validation.py)
  cubre `SalesValidationTest::test_invalid_quantity_is_rejected_before_database_connection`:
  con `quantity = -2` se espera `ValueError` y
  `get_database_connection` no debe invocarse. Este test protege la regla
  "validar antes de abrir transaccion" del backend.
- [`tests/test_receipt_route.py`](../../tests/test_receipt_route.py) cubre la
  ruta `/sales/receipt/<id>` con la app Flask real y la base mockeada:
  - `test_receipt_renders_200_with_preset_order`: 200 con sesion
    autenticada y orden mockeada; verifica que el HTML contiene `ZR-0001`,
    `Filtro Demo` y `Cliente Demo`.
  - `test_receipt_renders_with_no_items`: 200 con `items = []`; no aparece
    el codigo interno esperado.
  - `test_receipt_returns_404_when_order_missing`: 404 cuando
    `obtener_detalles_orden` retorna `None`.

### 4.2 Brechas a cerrar en v1 (tests a aniadir)

| Brecha | Test a aniadir | Archivo sugerido |
| --- | --- | --- |
| Stock insuficiente dispara `rollback` y `flash` de error. | `test_stock_insufficient_raises_value_error_and_triggers_rollback` con conexion mockeada. | `tests/test_sales_validation.py` |
| `payment` se inserta con `amount = total_amount` y `status = "Completed"` exactamente una vez. | `test_payment_insert_uses_total_amount_and_completed_status`. | `tests/test_sales_payment.py` (nuevo) |
| `obtener_metricas_dashboard` retorna `payments_by_method` con `method` y `amount` por metodo, ordenado por monto descendente. | `test_dashboard_metrics_include_payments_by_method_for_today`. | `tests/test_sales_dashboard.py` (nuevo) |
| `crear_orden_venta` con `payment_method = "Efectivo"` persiste ese mismo literal en `payment.method`. | `test_payment_method_value_is_persisted_verbatim`. | `tests/test_sales_payment.py` |

Comandos sugeridos (alineados con el resto del repo):

```bash
uv run python -m unittest tests.test_sales_validation
uv run python -m unittest tests.test_receipt_route
uv run python -m unittest tests.test_sales_payment
uv run python -m unittest tests.test_sales_dashboard
```

---

## 5. Aceptacion manual en navegador / DataGrip

Pasos reproducibles que un estudiante junior puede correr para verificar el
contrato desde la UI o desde un cliente SQL.

### 5.1 En navegador

Prerequisito: estar logueado como `admin` / `admin123` y tener al menos un
cliente y un repuesto con stock cargados.

1. **Listado inicial.**
   - Ir a `/sales`. Confirmar que la tabla muestra las ordenes existentes,
     ordenadas por id descendente.
2. **Filtros por fecha.**
   - Escoger `start_date` y `end_date` conocidos.
   - Confirmar que solo aparecen ordenes dentro del rango.
3. **Sidebar reducido.**
   - Confirmar que en v1 el sidebar **no** muestra radios `Pendientes` ni
     `Canceladas`; solo `Todas` y `Pagadas`.
4. **Crear venta con cliente existente.**
   - Pulsar "Nueva Venta", elegir un cliente del dropdown.
   - Agregar dos repuestos distintos y confirmar la suma en
     "Total a Pagar".
   - Elegir `Tarjeta de Debito` como metodo de pago.
   - Pulsar "Confirmar Venta".
   - Verificar: la pagina redirige a `/sales` con un flash de exito y la
     nueva orden aparece arriba.
5. **Crear venta con cliente nuevo.**
   - Cambiar a "Registrar Nuevo Cliente", llenar los tres campos.
   - Si el documento ya existe, confirmar que el sistema lo reutiliza en
     vez de duplicarlo.
6. **Stock insuficiente.**
   - Intentar vender una cantidad mayor al stock visible.
   - En la UI debe bloquearse con `alert("Stock insuficiente...")`.
   - Saltandose la UI (POST directo) la transaccion debe hacer rollback y
     el flash debe mostrar el `ValueError` capturado.
7. **Recibo.**
   - Pulsar el icono de recibo de una fila.
   - Verificar: aparece el modal con numero, fecha, cliente, NIT/CI,
     lineas, subtotal, descuento (si aplica) y total.
   - Pulsar "Imprimir Comprobante" y confirmar que abre el dialogo de
     impresion del navegador sobre el HTML preformateado.
8. **Recibo inexistente.**
   - Visitar `/sales/receipt/999999` logueado. Debe responder 404.
9. **Sesion requerida.**
   - Visitar `/sales` sin iniciar sesion. Debe redirigir a `/` con flash
     de error.

### 5.2 En DataGrip / cliente SQL

Prerequisito: tener `mysql` CLI o DataGrip conectado a la base
`sis122_zarvent_repuestos`.

1. **Verificar que toda venta tiene `status = 'Paid'`.**
   ```sql
   SELECT status, COUNT(*) FROM sales_order GROUP BY status;
   ```
   En v1, el resultado esperado es una sola fila: `Paid` con todas las
   ordenes.
2. **Verificar que existe exactamente un `payment` por venta.**
   ```sql
   SELECT sales_order_id, COUNT(*) AS pagos
   FROM payment
   GROUP BY sales_order_id
   HAVING COUNT(*) > 1;
   ```
   El resultado debe ser vacio.
3. **Verificar que `payment.amount` coincide con `sales_order.total_amount`.**
   ```sql
   SELECT p.sales_order_id, p.amount, o.total_amount
   FROM payment p
   JOIN sales_order o ON p.sales_order_id = o.sales_order_id
   WHERE p.amount <> o.total_amount;
   ```
   El resultado debe ser vacio.
4. **Verificar que `sales_order_item.unit_price` y `discount_amount`
   persisten el precio historico enviado por la UI (no se recalculan desde
   `part.sale_price`).**
   ```sql
   SELECT i.sales_order_item_id, i.unit_price, p.sale_price
   FROM sales_order_item i
   JOIN part p ON i.part_id = p.part_id
   WHERE i.unit_price <> p.sale_price;
   ```
   En el seed demo esta consulta puede devolver filas (los `sale_price`
   cambiaron despues de la venta). Eso valida que se guarda precio
   historico.
5. **Verificar que el dashboard expone `payments_by_method` para la fecha
   actual.**
   ```sql
   SELECT method, SUM(amount) AS total
   FROM payment
   WHERE payment_date = CURDATE()
   GROUP BY method
   ORDER BY total DESC;
   ```
   El resultado debe coincidir con `metrics.payments_by_method` devuelto
   por `obtener_metricas_dashboard`.
6. **Forzar una condicion de carrera para validar el `FOR UPDATE`.**
   Abrir dos sesiones MySQL concurrentes, correr en ambas
   `SELECT quantity_on_hand FROM inventory_stock WHERE part_id = X FOR
   UPDATE;`. La segunda sesion debe quedar bloqueada hasta que la primera
   haga `COMMIT` o `ROLLBACK`.

---

## 6. Decisiones fuera de alcance

Lo que el analisis academico pedia y el equipo decidio NO entregar en v1,
con justificacion. Si quedan como objetivo futuro, se etiquetan
`backlog v2`.

| Tema | RF origen | Estado v1 | Justificacion |
| --- | --- | --- | --- |
| Devoluciones y garantias (RF-08). | `docs/analysis/requirements.md` RF-08; `processes.md` linea 51. | `fuera de alcance v1` (`backlog v2`) | Las tablas `RETURN_ORDER` y `RETURN_ORDER_ITEM` no se crean en `init_db.py`. Toda la cadena de devolucion queda diferida para una iteracion posterior. |
| Anulacion de venta. | `procedures.md` (no documentado como procedimiento explicito). | `fuera de alcance v1` (`backlog v2`) | El CRUD no expone `UPDATE sales_order SET status = 'Cancelled'`. El dashboard filtra `status != 'Cancelled'` por defensa, pero el camino para insertar ese valor no existe en v1. |
| Edicion de venta existente. | (no documentado). | `fuera de alcance v1` (`backlog v2`) | No hay ruta `PUT`/`PATCH` ni vista de edicion. El precio historico se congela al registrar la venta. |
| Compatibilidad vehicular (RF-03). | `requirements.md` RF-03; `processes.md` linea 45. | `fuera de alcance v1` (`backlog v2`) | Las tablas `VEHICLE_MODEL` y `PART_COMPATIBILITY` existen en el ERD pero no se crean en `init_db.py` y el flujo de venta no las consulta. |
| Pagos multiples o parciales. | `db_explanation.md` (linea 29); `procedures.md` paso 6. | `fuera de alcance v1` (`backlog v2`) | El codigo inserta siempre un unico `payment` por el total. La relacion `SALES_ORDER 1..N PAYMENT` esta prevista en el modelo y la columna `amount` lo permite, pero la UI no lo expone. |
| Descuentos por linea desde la UI. | (no documentado como requerimiento formal). | `fuera de alcance v1` (`backlog v2`) | El backend valida y persiste `discount_amount` por linea, pero `sales.html` no captura ese valor y siempre envia `0.0`. |
| Comprobante PDF / factura formal. | `db_explanation.md` (Limitaciones: `SALES_INVOICE`). | `fuera de alcance v1` (`backlog v2`) | El comprobante actual es HTML preformateado; no hay layout A4 con datos fiscales. Es coherente con el alcance academico. |
| Generar UI para `payments_by_method` en el dashboard. | (no documentado). | `fuera de alcance v1` (`backlog v2`) | En v1 la metrica se calcula y se expone via `obtener_metricas_dashboard`, pero `dashboard.html` no la consume todavia. La UI del dashboard queda intacta en v1. |
| `INVENTORY_MOVEMENT` (historial de movimientos de stock). | `db_explanation.md` (Limitaciones). | `fuera de alcance v1` (`backlog v2`) | Solo se descuenta `inventory_stock.quantity_on_hand`. Auditar la razon historica del stock requiere revisar `sales_order_item` y `purchase_order_item`. |

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
| Registrar cliente en el momento de la venta | `processes.md` (Registro de clientes); `requirements.md` RF-01 | `db_explanation.md` (`PERSON`, `CUSTOMER`); `erd.md` (PERSON, CUSTOMER) | `/sales` POST + `customer_crud.buscar_cliente_por_doc` y `customer_crud.crear_cliente` en `app.py:198-218` | `implementado v1` |
| Seleccionar cliente existente y asociarlo a la venta | `procedures.md` (Registro de venta, paso 1) | `db_explanation.md` (relacion `CUSTOMER -> SALES_ORDER`); `erd.md` | `/sales` POST rama `client_mode == "existing"` + FK `sales_order.customer_id` (`ON DELETE RESTRICT` en `init_db.py:147`) | `implementado v1` |
| Lineas de venta con cantidad, precio historico y descuento | `requirements.md` RF-05; `procedures.md` (Registro de venta, pasos 2-3) | `erd.md` (`SALES_ORDER_ITEM`); `db_explanation.md` (regla de precio historico) | `crear_orden_venta` inserta `sales_order_item` con `quantity`, `unit_price`, `discount_amount` (`sales_crud.py:79-99`) | `implementado v1` |
| Validacion de stock antes de vender | `processes.md` (reglas); `procedures.md` (Registro de venta, paso 4) | `db_explanation.md` ("Una venta confirmada no debe vender mas que el stock disponible") | `SELECT ... FOR UPDATE` + comparacion en `crear_orden_venta` (`sales_crud.py:51-69`) | `implementado v1` |
| Transaccion atomica (orden + items + stock + pago) | `procedures.md` (Registro de venta, pasos 5-8) | (no documentado como tal) | `try / except / commit / rollback` en `crear_orden_venta` (`sales_crud.py:50-119`) | `implementado v1` |
| Pago unico por el total | `requirements.md` RF-06; `procedures.md` (Registro de venta, paso 6) | `db_explanation.md` (columna `payment.amount`); `erd.md` (PAYMENT) | `crear_orden_venta` inserta un `payment` con `amount = total_amount`, `status = "Completed"` y `method` verbatim (`sales_crud.py:101-107`) | `implementado v1` |
| Metodo de pago con cuatro valores definidos | `processes.md` (Registro de pagos) | `db_explanation.md` (columna `payment.method` `VARCHAR(50)`) | `<select id="payment_method">` en `sales.html:229-234` + `payment_method` recibido en `/sales` POST (`app.py:193`) | `implementado v1` |
| Listado de ventas con filtros | `processes.md` (Reportes) | (no documentado) | `listar_ordenes_venta` + filtros en `sales.html` | `parcial v1` (filtros `Pending` y `Cancelled` son ruido: ver [Seccion 3, cambio 1](#3-cambios-requeridos-v1)) |
| Comprobante / recibo de la venta | `procedures.md` (Registro de venta, paso 7) | (no modelado) | `receipt.html` renderizado por `/sales/receipt/<id>` (`app.py:275-284`) | `implementado v1` (HTML preformateado, no PDF) |
| Compatibilidad vehicular al vender | `requirements.md` RF-03; `processes.md` (Compatibilidad vehicular) | `erd.md` (`VEHICLE_MODEL`, `PART_COMPATIBILITY`) | (no implementado en el flujo de venta) | `fuera de alcance v1` |
| Devoluciones o garantias | `requirements.md` RF-08; `processes.md` (Devoluciones) | `erd.md` (`RETURN_ORDER`, `RETURN_ORDER_ITEM`) | (no hay rutas ni CRUD de devoluciones) | `fuera de alcance v1` |
| Estados de venta `Pending` y `Cancelled` con flujo real | `processes.md` (ciclo de vida) | `erd.md` (`status` de `SALES_ORDER`); `init_db.py` (default `'pending'`) | UI los ofrece como filtro, pero `crear_orden_venta` siempre inserta `"Paid"` | `corregir UI/spec` (filtros muertos a retirar; ver [Seccion 3, cambio 1](#3-cambios-requeridos-v1)) |
| Cancelacion o anulacion de venta | (no documentado como procedimiento) | (no modelado) | (no implementado) | `fuera de alcance v1` |
| Edicion de venta existente | (no documentado) | (no modelado) | (no hay ruta `PUT`/`PATCH` ni formulario de edicion) | `fuera de alcance v1` |
| Metricas de ventas en dashboard | `processes.md` (Reportes); `requirements.md` RF-09 | (no modelado) | `obtener_metricas_dashboard` (`sales_crud.py:206-275`); `dashboard.html` | `parcial v1` (la condicion `status != 'Cancelled'` en `today_sales_amount` queda como defensa; el `payments_by_method` se calcula y queda disponible pero `dashboard.html` no lo consume en v1: ver [Seccion 3, cambios 3 y 4](#3-cambios-requeridos-v1)) |
| Generar reporte fiscal formal (PDF) | `processes.md` (comprobantes) | `db_explanation.md` ("Limitaciones aceptadas": `SALES_INVOICE`) | (no implementado) | `fuera de alcance v1` |
| Historial de movimientos de stock | `processes.md` (reglas); `db_explanation.md` (mejora futura) | `db_explanation.md` (`INVENTORY_MOVEMENT`) | (no implementado) | `fuera de alcance v1` |
