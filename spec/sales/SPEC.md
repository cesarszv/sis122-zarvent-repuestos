# SPEC — Ventas

Especificacion funcional y tecnica del modulo de Ventas de **Zarvent Repuestos**.
Cubre el registro de ordenes de venta, la gestion de su detalle, la relacion con
pagos, y la emision del comprobante POS. Documenta lo que el codigo hace hoy
y las brechas detectadas respecto al diseno academico.

## Objetivo del modulo

El modulo de Ventas resuelve el problema central del negocio: registrar de forma
confiable una transaccion comercial entre un cliente y la casa de repuestos.

Para Zarvent Repuestos eso significa:

- Identificar al cliente que compra, ya sea uno existente o uno nuevo registrado
  en el momento.
- Cargar el detalle del repuesto vendido, con cantidad, precio unitario
  historico y descuento.
- Validar que el stock disponible alcance para cubrir la venta.
- Registrar el cobro asociado a la venta y emitir un comprobante legible para
  el cliente.

El modulo reduce los tres problemas clasicos del flujo manual descritos en
[`docs/analysis/processes.md`](../../docs/analysis/processes.md):

- ventas sin detalle confiable,
- pagos separados de la venta,
- stock que no coincide con la realidad.

A nivel de base de datos, el modulo materializa la relacion

`CUSTOMER -> SALES_ORDER -> SALES_ORDER_ITEM -> PART -> INVENTORY_STOCK`

y el vinculo `SALES_ORDER -> PAYMENT` descritos en
[`docs/database/db_explanation.md`](../../docs/database/db_explanation.md).

## Estado actual reverse-engineered

Esta seccion describe lo que el codigo hace hoy, sin presuponer diseno. Sirve
como base para entender el contrato real y las brechas mas adelante.

### Rutas Flask

Las rutas viven en
[`src/zarvent_repuestos/web/app.py`](../../src/zarvent_repuestos/web/app.py).

| Ruta | Metodo | Decorador | Que hace |
| --- | --- | --- | --- |
| `/sales` | GET | `@login_required` | Lista ordenes de venta aplicando filtros por estado y rango de fechas. Renderiza `sales.html`. |
| `/sales` | POST | `@login_required` | Procesa el formulario de nueva venta: valida cliente, parsea `items_json`, llama a `crear_orden_venta`, hace `flash` del resultado y redirige a la misma ruta. |
| `/sales/receipt/<int:sales_order_id>` | GET | `@login_required` | Devuelve el HTML del comprobante POS para una venta existente. Si la venta no existe responde 404. |

Ambas rutas usan `@login_required` (`src/zarvent_repuestos/web/app.py:69`), por
lo que requieren sesion activa.

### Templates

#### `sales.html`

Render principal del modulo. Contiene cuatro bloques visibles:

- Cabecera con el titulo "Ordenes de Venta" y el boton "Nueva Venta" que abre
  el modal de registro.
- Sidebar de filtros dentro de un `<form method="get" action="/sales">`:
  - Estado de Venta con radios: `All Orders`, `Paid`, `Pending`, `Cancelled`.
  - Rango de fechas con inputs `start_date` y `end_date` que disparan
    `this.form.submit()` al cambiar.
  - Boton "Limpiar Filtros" visible solo si hay algun filtro aplicado.
- Tabla de resultados con columnas Codigo (`#ORD-{id}`), Cliente Facturacion,
  Fecha (`dd/mm/yyyy`), Estado, Total Cobrado y boton "Ver Recibo".
- Modal `new-order-modal` con el formulario de registro (ver
  [Contrato funcional](#contrato-funcional)).
- Modal `receipt-modal` cuyo contenido se inyecta por AJAX desde
  `/sales/receipt/<id>`.

El bloque `extra_js` define el estado del lado cliente y los handlers
(`src/zarvent_repuestos/web/templates/sales.html:277-437`):

- `let addedItems = []`: arreglo en memoria con los items de la orden actual.
- `toggleModal(modalId, show)`: muestra u oculta modales.
- `toggleClientFields(value)`: alterna entre cliente existente y registro
  rapido; ajusta atributos `required`.
- `addProductRow()`: lee el selector de repuesto y la cantidad, valida stock
  leido desde `data-stock`, evita duplicados por `part_id`, agrega a
  `addedItems` y redibuja la tabla.
- `removeProductRow(partId)`: quita un item del carrito y de la tabla.
- `recalculateTotals()`: suma `unit_price * quantity` para todos los items y
  actualiza el label "Total a Pagar" y el input oculto `items_json`.
- `submitSalesOrder()`: valida cliente y al menos un item, y hace `submit()`.
- `viewReceipt(orderId)`: hace `fetch("/sales/receipt/${orderId}")` y coloca
  la respuesta en `#receipt-content`.

#### `receipt.html`

Template minimalista que renderiza un comprobante estilo POS usando fuente
monoespaciada y bordes discontinuos. Muestra:

- Cabecera con el nombre del autoservicio y ubicacion.
- Numero de venta, fecha, cliente (`billing_name`) y NIT/CI (`tax_id`).
- Tabla con cada item vendido: codigo, nombre, cantidad, precio unitario y
  subtotal calculado como `unit_price * quantity`.
- Totales: subtotal, descuento (solo si `discount_amount > 0`) y total.
- Pie de comprobante con el agradecimiento.

Importante: este template se devuelve como fragmento HTML dentro del modal
`receipt-modal`, **no se emite PDF**.

### Funciones CRUD relevantes

Definidas en
[`src/zarvent_repuestos/crud/sales_crud.py`](../../src/zarvent_repuestos/crud/sales_crud.py).

| Funcion | Responsabilidad |
| --- | --- |
| `crear_orden_venta(customer_id, items, payment_method)` | Crea la orden, sus items, descuenta stock y registra el pago, todo en una sola transaccion atomica. Devuelve el `sales_order_id` o lanza excepcion. |
| `listar_ordenes_venta(status, start_date, end_date)` | Lista ordenes con datos de cliente y facturacion. Aplica filtros opcionales. Ordena por `sales_order_id DESC`. |
| `obtener_detalles_orden(sales_order_id)` | Devuelve la cabecera de la orden mas su lista de items, haciendo `JOIN` con `customer` y `person`. |
| `obtener_metricas_dashboard()` | Calcula metricas usadas por la ruta `/dashboard`: ventas del dia, conteo de ordenes, ultimas ordenes, stock bajo, etc. |

### Tablas relacionadas en la base de datos

El modulo toca directamente las siguientes tablas del esquema real definido en
[`src/zarvent_repuestos/database/init_db.py`](../../src/zarvent_repuestos/database/init_db.py):

- `sales_order` (cabecera: `sales_order_id`, `customer_id`, `order_date`,
  `status`, `subtotal`, `discount_amount`, `total_amount`).
- `sales_order_item` (lineas: `sales_order_item_id`, `sales_order_id`,
  `part_id`, `quantity`, `unit_price`, `discount_amount`).
- `payment` (`payment_id`, `sales_order_id`, `payment_date`, `method`,
  `amount`, `reference_number`, `status`).
- `inventory_stock` (`inventory_stock_id`, `part_id`, `quantity_on_hand`,
  `reorder_level`): se valida y se decrementa.
- `customer` y `person`: para identificar al cliente y mostrar nombre fiscal.
- `part`: para precio historico y descripcion del item vendido.

### Comportamiento visible

- Una venta se crea siempre con `status = "Paid"`. No hay flujo para crear
  ventas en estado `Pending` o `Cancelled` desde la UI actual.
- Por cada venta se inserta exactamente un `payment` por el total completo.
- El comprobante se muestra dentro de un modal de la misma pagina, no en una
  ruta dedicada navegable.
- El sidebar permite filtrar por estado, pero en la practica solo aparecen
  ordenes con `status = "Paid"` porque el codigo nunca inserta otros valores.

## Contrato funcional

Esta seccion describe los flujos visibles para el usuario final del modulo.

### Pantalla principal `/sales`

1. El usuario autenticado entra a `/sales`.
2. El servidor responde con el listado completo de ordenes (orden descendente
   por id) y los catalogos necesarios para el modal de registro:
   - `parts` para el selector de repuestos.
   - `customers` para el selector de cliente existente.
3. El usuario puede filtrar por:
   - Estado (`All Orders` por defecto, `Paid`, `Pending`, `Cancelled`).
   - Rango de fechas (`start_date`, `end_date`).
4. Cada fila expone un boton "Ver Recibo" que abre el modal del comprobante.

### Crear venta (cliente existente)

1. El usuario hace clic en "Nueva Venta" y se abre `new-order-modal`.
2. En el selector "Tipo de Cliente" deja la opcion por defecto
   `Cliente Registrado` y elige un cliente del dropdown `customer_id`.
3. Agrega uno o mas repuestos con el selector `part_selector` y la cantidad
   `part_quantity`. La suma `unit_price * quantity` se acumula en
   `recalculateTotals()` y se muestra como "Total a Pagar".
4. Elige el metodo de pago en `payment_method`.
5. Confirma con "Confirmar Venta". El frontend valida cliente y al menos un
   item, serializa `addedItems` a JSON y lo envia como `items_json` en el
   `POST /sales`.

### Crear venta (cliente nuevo)

1. Cambia el selector a `Registrar Nuevo Cliente`.
2. Se muestran los campos `new_first_name`, `new_last_name`,
   `new_identity_number`, todos `required`.
3. Al confirmar, el backend:
   - Busca primero si el cliente ya existe por documento de identidad
     (`customer_crud.buscar_cliente_por_doc`).
   - Si existe, reutiliza su `customer_id`.
   - Si no existe, llama a `customer_crud.crear_cliente` y luego recupera el
     id del cliente recien creado.
4. Continua con el mismo flujo que cliente existente.

### Seleccion de items

- El selector lista cada repuesto como
  `[internal_code] name (Stock: quantity_on_hand - $sale_price)`.
- El campo de cantidad empieza en `1` y acepta minimo `1` (validacion HTML).
- El JS no permite agregar el mismo `part_id` dos veces; si se intenta,
  muestra un `alert("Este producto ya fue agregado...")`.
- El JS tampoco permite superar el stock disponible; en ese caso muestra
  `alert("Stock insuficiente. Solo quedan X unidades disponibles.")`.

### Validaciones de negocio

Las validaciones se aplican en dos capas:

#### En el cliente (`sales.html`)

- `payment_method` es obligatorio por estar en un `<select>`.
- `customer_id` se vuelve `required` cuando el modo es "Cliente Registrado".
- `new_first_name`, `new_last_name` y `new_identity_number` se vuelven
  `required` cuando el modo es "Registrar Nuevo Cliente".
- `items_json` se llena siempre desde `recalculateTotals()` antes del submit.
- `submitSalesOrder()` valida cliente y al menos un item, y bloquea el submit
  con `alert` si falta algo.

#### En el servidor (`crear_orden_venta`)

Antes de abrir la transaccion con la base de datos:

- `quantity` debe ser `> 0`.
- `unit_price` debe ser `> 0`.
- `discount_amount` debe ser `>= 0`.
- `discount_amount` no puede ser mayor que `unit_price`.
- La lista `items` no puede estar vacia.

Si alguna validacion falla se lanza `ValueError` y la operacion no toca la
base de datos. Esto esta cubierto por
[`tests/test_sales_validation.py`](../../tests/test_sales_validation.py).

### Pago

El selector `payment_method` ofrece cuatro valores exactos en Latam Spanish:

- `Efectivo`
- `Tarjeta de Débito`
- `Tarjeta de Crédito`
- `Transferencia` (etiquetada en UI como "Transferencia QR")

Estos valores se persisten tal cual en la columna `payment.method`. No hay
catalogo separado de metodos de pago en la base de datos.

### Recibo (`/sales/receipt/<id>`)

1. El usuario hace clic en el icono de recibo de una fila.
2. El JS llama a `fetch('/sales/receipt/${orderId}')` y abre el modal
   `receipt-modal`.
3. El servidor renderiza `receipt.html` con la orden recuperada por
   `obtener_detalles_orden`.
4. Si la orden no existe, el servidor responde 404 con el texto
   `"Venta no encontrada"`.
5. El modal expone el boton "Imprimir Comprobante" que dispara
   `window.print()` sobre el comprobante ya cargado.

El comprobante es HTML preformateado, no un PDF. Ver
[Brechas y decisiones](#brechas-y-decisiones) para el detalle.

### Mensajes flash

Los `flash()` se disparan desde la ruta `/sales` POST en tres casos:

| Caso | Origen del mensaje | Categoria |
| --- | --- | --- |
| Exito al crear venta | `f"Venta #{sales_order_id} registrada correctamente."` | `success` |
| Falla al crear venta (devuelve `None`) | `"Error al registrar la venta."` | `error` |
| Excepcion atrapada | `f"Error al procesar venta: {e}"` | `error` |

En el caso de excepcion, la causa comun es la validacion de stock. El
`ValueError("Stock insuficiente para el producto ID X. Disponible: A,
Solicitado: B.")` se propaga desde `crear_orden_venta` y se muestra al usuario
en el flash.

### Comportamiento del cliente AJAX

- `viewReceipt(orderId)` es la unica llamada AJAX del modulo. Muestra primero
  el texto "Cargando comprobante..." y luego reemplaza el contenido por el
  HTML del comprobante.
- Si la peticion falla (`!res.ok`), se inyecta un parrafo con
  `text-zarvent-red` y el mensaje del error.
- No hay timeout explicito ni reintentos: la peticion depende de la sesion
  activa y del 404 que devuelve el backend si la orden no existe.

## Contrato de datos

### Tablas involucradas

Origen del esquema: `init_db.py` (declaraciones `CREATE TABLE`).

| Tabla | Rol en el modulo | Columnas relevantes |
| --- | --- | --- |
| `customer` | Cliente que compra. | `customer_id`, `person_id`, `billing_name`, `tax_id` |
| `person` | Datos civiles del cliente. | `person_id`, `first_name`, `last_name`, `identity_number`, `phone`, `email`, `address` |
| `part` | Repuesto vendido. | `part_id`, `part_category_id`, `internal_code`, `name`, `brand`, `sale_price` |
| `inventory_stock` | Stock actual del repuesto. | `inventory_stock_id`, `part_id`, `quantity_on_hand`, `reorder_level` |
| `sales_order` | Cabecera de la venta. | `sales_order_id`, `customer_id`, `order_date`, `status`, `subtotal`, `discount_amount`, `total_amount` |
| `sales_order_item` | Lineas de la venta. | `sales_order_item_id`, `sales_order_id`, `part_id`, `quantity`, `unit_price`, `discount_amount` |
| `payment` | Cobro de la venta. | `payment_id`, `sales_order_id`, `payment_date`, `method`, `amount`, `reference_number`, `status` |

### Relaciones usadas

- `CUSTOMER (1) -> SALES_ORDER (0..N)`: cada venta pertenece a un unico
  cliente; `customer_id` es la foranea.
- `SALES_ORDER (1) -> SALES_ORDER_ITEM (1..N)`: una venta tiene al menos una
  linea (validado por `crear_orden_venta` antes de tocar la base de datos).
- `PART (1) -> SALES_ORDER_ITEM (0..N)`: cada linea referencia un repuesto.
- `SALES_ORDER (1) -> PAYMENT (0..N)`: una venta puede tener uno o varios
  pagos, aunque la UI solo crea siempre un solo pago por el total.
- `PART (1) -> INVENTORY_STOCK (1)`: la relacion es uno-a-uno en el esquema
  actual porque `inventory_stock.part_id` es `UNIQUE`.

Las reglas de integridad declaradas por el esquema (claves primarias,
foraneas, `UNIQUE`) estan en
[`docs/database/db_explanation.md`](../../docs/database/db_explanation.md).
Las que toca defender en la creacion de una venta son:

- `PART.internal_code` es unico.
- `PERSON.identity_number` es unico.
- `SALES_ORDER.customer_id` debe existir.
- `SALES_ORDER_ITEM.part_id` debe existir (`ON DELETE RESTRICT`).
- `INVENTORY_STOCK.part_id` es `UNIQUE`, por lo que un repuesto tiene un
  unico registro de stock en el esquema actual.

### Transaccion atomica

`crear_orden_venta` ejecuta toda la operacion dentro de una sola transaccion
sobre una conexion MySQL. Los pasos, en orden, son:

1. Validar los datos del cliente (`quantity`, `unit_price`, `discount_amount`,
   `items` no vacio) sin abrir conexion.
2. Calcular `subtotal`, `discount_total` y `total_amount` en Python.
3. Abrir conexion y cursor.
4. Para cada item, ejecutar
   `SELECT quantity_on_hand FROM inventory_stock WHERE part_id = %s FOR UPDATE`
   para tomar un lock de fila.
   - Esto bloquea el registro de stock del repuesto hasta el `COMMIT`,
     evitando que dos ventas concurrentes vendan la misma unidad.
   - Si el repuesto no tiene fila en `inventory_stock`, lanza
     `ValueError("El producto con ID X no esta registrado en el inventario.")`.
   - Si `quantity_on_hand < qty_needed`, lanza
     `ValueError("Stock insuficiente...")`.
5. Insertar la cabecera en `sales_order` con `status = "Paid"`,
   `subtotal`, `discount_amount` y `total_amount`.
6. Por cada item, insertar `sales_order_item` y ejecutar
   `UPDATE inventory_stock SET quantity_on_hand = quantity_on_hand - %s
   WHERE part_id = %s`.
7. Insertar el `payment` con `status = "Completed"`, `method = payment_method`,
   `amount = total_amount`, `payment_date = order_date`, y
   `reference_number = f"PAY-{sales_order_id}-{datetime.now().strftime('%M%S')}"`.
8. `conexion.commit()`. Si en cualquier punto se lanza
   `mysql.connector.Error` o `ValueError`, se ejecuta
   `conexion.rollback()` y se re-lanza la excepcion.

El `FOR UPDATE` es importante para la defensa academica: es la unica proteccion
contra una condicion de carrera en la que dos ventas concurrentes leen stock
suficiente antes de descontar.

### Side effects garantizados

Si `crear_orden_venta` retorna un `sales_order_id`, el caller puede asumir que
se ejecutaron, en el mismo commit, todas estas operaciones:

- 1 insercion en `sales_order`.
- N inserciones en `sales_order_item` (una por item).
- N updates en `inventory_stock` (descuento de stock).
- 1 insercion en `payment` con `amount = total_amount`.

Si retorna `None` o lanza excepcion, ningun cambio persiste (rollback).

### Reglas de integridad y consistencia

- El `status` de la cabecera siempre se inserta como `"Paid"`. El default de
  la columna es `"pending"`, pero la capa de aplicacion lo sobreescribe.
- `payment.amount` siempre coincide con `sales_order.total_amount`. No hay
  pagos parciales ni multiples pagos.
- `sales_order.subtotal` se calcula como `sum(unit_price * quantity)`.
- `sales_order.discount_amount` se calcula como
  `sum(item.discount_amount * item.quantity)`.
- `sales_order.total_amount` se calcula como `subtotal - discount_amount`.
- `sales_order_item.unit_price` y `sales_order_item.discount_amount`
  persisten lo que el cliente envio, **no** se recalculan desde `PART.sale_price`
  ni desde `PART.purchase_cost`. Esto cumple la regla de
  "precio historico" del ERD.
- El `order_date` se toma con `datetime.date.today()` en el servidor. La
  aplicacion no permite registrar ventas con fecha manual.
- `order_date` y `payment_date` quedan iguales al insertar.

### Formula de subtotal, descuento y total

Para una orden con items `i_1, i_2, ..., i_n`, donde cada item tiene
`quantity = q_j`, `unit_price = p_j`, `discount_amount = d_j` (descuento por
unidad):

- `subtotal = sum(p_j * q_j)`
- `discount_total = sum(d_j * q_j)`
- `total_amount = subtotal - discount_total`

Restricciones por item aplicadas antes de calcular los totales:

- `q_j > 0`
- `p_j > 0`
- `0 <= d_j <= p_j`

El JS del modal recalcula el "Total a Pagar" en pantalla usando solo
`unit_price * quantity` (sin descuento), porque el formulario no captura
descuento por unidad. El descuento por linea siempre se envia como `0.0`
desde la UI, aunque el backend lo soporte si viniera con valor.

## Trazabilidad SDD

Esta matriz cruza los temas clave del modulo contra los documentos de
analisis, los documentos de base de datos, el codigo actual y el estado
real. Las etiquetas son `implementado`, `parcial`, `faltante` o
`fuera de alcance`.

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Registrar cliente en el momento de la venta | `processes.md` (Registro de clientes), `requirements.md` (RF-01) | `db_explanation.md` (PERSON, CUSTOMER) | `sales` POST + `customer_crud.buscar_cliente_por_doc` y `crear_cliente` | `implementado` |
| Seleccionar cliente existente y asociarlo a la venta | `procedures.md` (Registro de venta) | `db_explanation.md` (relacion CUSTOMER -> SALES_ORDER) | `sales` POST rama `client_mode == "existing"` + FK `sales_order.customer_id` | `implementado` |
| Lineas de venta con cantidad, precio historico y descuento | `requirements.md` (RF-05), `procedures.md` (Registro de venta) | `erd.md` (SALES_ORDER_ITEM), `db_explanation.md` (regla de precio historico) | `crear_orden_venta` inserta `sales_order_item` con `quantity`, `unit_price`, `discount_amount` | `implementado` |
| Validacion de stock antes de vender | `processes.md` (reglas), `procedures.md` (Registro de venta) | `db_explanation.md` (regla: "Una venta confirmada no debe vender mas que el stock disponible") | `SELECT ... FOR UPDATE` + comparacion en `crear_orden_venta` | `implementado` |
| Transaccion atomica (orden + items + stock + pago) | `procedures.md` (Registro de venta) | no documentado como tal | `try / except / commit / rollback` en `crear_orden_venta` | `implementado` |
| Pago asociado a la venta | `requirements.md` (RF-06) | `erd.md` (PAYMENT), `db_explanation.md` (pagos parciales o multiples metodos) | `crear_orden_venta` inserta un `payment` por el total | `parcial` (solo un pago por el total, no multiples ni parciales) |
| Listado de ventas con filtros | `processes.md` (Reportes) | no documentado | `listar_ordenes_venta` + filtros en `sales.html` | `implementado` |
| Comprobante / recibo de la venta | `procedures.md` (paso 7), `processes.md` (documentos) | no modelado | `receipt.html` renderizado por `/sales/receipt/<id>` | `parcial` (es HTML preformateado, no PDF ni factura formal) |
| Compatibilidad vehicular al vender | `requirements.md` (RF-03), `processes.md` (Compatibilidad vehicular) | `erd.md` (VEHICLE_MODEL, PART_COMPATIBILITY), `db_explanation.md` | no implementado en el flujo de venta | `faltante` |
| Devoluciones o garantias | `requirements.md` (RF-08), `processes.md` (Devoluciones) | `erd.md` (RETURN_ORDER, RETURN_ORDER_ITEM) | no hay rutas ni CRUD de devoluciones | `faltante` |
| Estados de venta Pending y Cancelled | `processes.md` (ciclo de vida) | `erd.md` (status de SALES_ORDER), `init_db.py` (default "pending") | UI los ofrece como filtro, pero `crear_orden_venta` siempre inserta "Paid" | `parcial` |
| Cancelacion o anulacion de venta | no documentado como procedimiento | no modelado | no implementado | `faltante` |
| Edicion de venta existente | no documentado | no modelado | no hay ruta `PUT`/`PATCH` ni formulario de edicion | `faltante` |
| Metricas de ventas en dashboard | `processes.md` (Reportes), `requirements.md` (RF-09) | no modelado | `obtener_metricas_dashboard` (ventas del dia, ultimas ordenes, etc.) | `implementado` |
| Generar reporte fiscal formal | `processes.md` (comprobantes) | `db_explanation.md` ("Limitaciones aceptadas": SALES_INVOICE) | no implementado | `fuera de alcance` (es un proyecto academico) |
| Historial de movimientos de stock | `processes.md` (reglas), `db_explanation.md` (mejora futura) | `db_explanation.md` (INVENTORY_MOVEMENT) | no implementado; solo se descuenta `inventory_stock.quantity_on_hand` | `fuera de alcance` |

## Criterios de aceptacion

### Pruebas automatizadas existentes

Las pruebas que respaldan este modulo viven en
[`tests/`](../../tests/).

- `tests/test_sales_validation.py`
  - Verifica que un `quantity` invalido (`-2`) se rechaza con `ValueError` y
    que el codigo de conexion no se invoca. Esto protege la regla de
    "validar antes de abrir transaccion" del backend.
- `tests/test_receipt_route.py`
  - Verifica que `/sales/receipt/<id>`:
    - Responde 200 con la sesion autenticada y la orden mockeada.
    - Renderiza datos del comprobante (`ZR-0001`, `Filtro Demo`,
      `Cliente Demo`).
    - Responde 200 incluso con `items = []`.
    - Responde 404 cuando `obtener_detalles_orden` retorna `None`.
  - Ademas cubre que la sesion requiere login (`authenticate_user` mockeado
    en `_login`).

### Pruebas manuales recomendadas

1. Listado inicial
   - Entrar a `/sales` autenticado.
   - Confirmar que la tabla muestra las ordenes existentes, ordenadas por id
     descendente.
   - Cambiar el filtro de estado a "Pendientes" o "Canceladas" y confirmar que
     la lista queda vacia (no hay ventas con ese status).
2. Filtro por fechas
   - Escoger `start_date` y `end_date` conocidos.
   - Confirmar que solo aparecen ordenes dentro del rango.
3. Crear venta con cliente existente
   - Abrir el modal, elegir un cliente del dropdown.
   - Agregar dos repuestos distintos y confirmar la suma en "Total a Pagar".
   - Confirmar con "Efectivo" como metodo de pago.
   - Verificar que la pagina redirige a `/sales` con un flash de exito y la
     nueva orden aparece arriba.
4. Crear venta con cliente nuevo
   - Cambiar a "Registrar Nuevo Cliente", llenar los tres campos.
   - Si el documento de identidad ya existe, confirmar que el sistema lo
     reutiliza en vez de duplicarlo.
5. Stock insuficiente
   - Intentar vender una cantidad mayor al stock visible.
   - En la UI debe bloquearse con `alert("Stock insuficiente...")`.
   - Saltandose la UI (con POST directo) la transaccion debe hacer rollback
     y el flash debe mostrar el `ValueError` capturado.
6. Cantidad invalida
   - Forzar un POST con `quantity <= 0` o `unit_price <= 0` o descuento
     negativo. Debe responder con flash de error y la base de datos no debe
     modificarse.
7. Pago y recibo
   - Abrir el recibo de una venta recien creada.
   - Verificar que aparecen: numero, fecha, cliente, NIT/CI, lineas, subtotal,
     descuento (si aplica) y total.
   - Probar "Imprimir Comprobante" y confirmar que abre el dialogo de
     impresion del navegador sobre el HTML preformateado.
8. Recibo inexistente
   - Visitar `/sales/receipt/999999`. Debe responder 404.
9. Sesion requerida
   - Visitar `/sales` sin iniciar sesion. Debe redirigir a `/`.

### Criterios de aceptacion resumidos

- `tests/test_sales_validation.py` pasa.
- `tests/test_receipt_route.py` pasa.
- El flujo manual de "crear venta con cliente existente" completa los nueve
  pasos anteriores sin errores.
- Ninguna operacion del modulo deja la base de datos en estado inconsistente
  (transaccion atómica).

## Brechas y decisiones

Esta seccion enumera las diferencias entre lo propuesto en los documentos
academicos y lo que el codigo implementa hoy. Algunas son limitaciones
aceptadas del alcance academico; otras son puntos debiles que conviene
explicar en la defensa.

### Status de venta siempre "Paid"

El `init_db.py` define `sales_order.status` con default `"pending"`, lo que
sugiere un ciclo de vida `pending -> paid -> cancelled`. Sin embargo, el
codigo de `crear_orden_venta` inserta siempre `status = "Paid"`. Por lo
tanto:

- No existe en el codigo un flujo para vender "al fiado" o dejar la orden
  abierta.
- No existe un flujo para cancelar o anular una venta.
- La UI filtra por "Pending" y "Cancelled" pero en la practica esas opciones
  siempre devuelven listas vacias.
- El modulo `obtener_metricas_dashboard` calcula "ventas del dia" usando
  `status != 'Cancelled'`. Esa condicion existe a nivel SQL pero no tiene
  contraparte en la insercion.

### Un solo pago por venta, siempre por el total

`db_explanation.md` describe la relacion
`SALES_ORDER (1) -> PAYMENT (0..N)` como soporte para "pagos parciales o
multiples metodos". El codigo no lo aprovecha:

- Por cada venta se inserta un unico `payment`.
- El `amount` es siempre igual a `sales_order.total_amount`.
- No hay UI para dividir el pago entre varios metodos ni para registrar
  abonos.

Esto es coherente con el modelo POS estilo "todo o nada" que se ve en el
formulario, pero conviene reconocerlo como simplificacion academica.

### Ventas no cancelables ni editables

- No existe ruta `PUT`/`PATCH` ni vista de edicion de venta.
- No existe endpoint para cancelar: no hay `sales_order.status = "Cancelled"`
  en ningun `UPDATE`.
- El `dashboard` filtra `status != 'Cancelled'` pero, como el codigo nunca
  cancela ventas, esa exclusion nunca quita filas reales.

### Comprobante como HTML, no PDF

`receipt.html` produce un comprobante visual estilo POS con fuente
monoespaciada y bordes discontinuos, pensado para imprimirse con
`window.print()`. Decisiones implicitas:

- No se genera un PDF del lado servidor.
- No hay layout A4 con datos fiscales, no hay numero de autorizacion, ni
  regimen fiscal.
- La ruta `/sales/receipt/<id>` no es navegable como pagina completa: se
  devuelve como fragmento HTML y se inyecta en el modal `receipt-modal`.

El mockup visual de diseno esta en
[`spec/sales/sales_mockup.html`](./sales_mockup.html) y
[`spec/sales/sales_mockup.png`](./sales_mockup.png).

### Modo "cliente nuevo" acoplado al formulario de venta

El alta rapida de cliente se hace en el mismo `POST /sales` que registra la
venta. Esto evita un viaje extra al servidor pero mezcla dos operaciones
logicas. Si el alta de cliente falla por validacion interna, se devuelve
`ValueError("No se pudo registrar al nuevo cliente.")` y la venta tampoco se
crea. No hay un endpoint dedicado de creacion de cliente invocado desde el
modal de venta, aunque `customer_crud.crear_cliente` si existe.

### Validaciones de stock en dos capas

- En el cliente: la UI ya no permite pasar el stock visible.
- En el servidor: la regla de negocio real se aplica con
  `SELECT ... FOR UPDATE` dentro de la transaccion.

La doble validacion es deliberada: la UI es una guia, pero la verdad
definitiva la tiene la base de datos. Para la defensa es importante senalar
que el `FOR UPDATE` evita que dos ventas concurrentes vendan la misma
unidad cuando ambas leen stock suficiente antes de descontar.

### Descuentos por linea: soportados en backend, no en UI

`crear_orden_venta` valida y persiste `discount_amount` por linea, pero el
modal de venta no captura ese valor. La UI envia siempre
`discount_amount: 0.0` por item. Por eso:

- `sales_order.discount_amount` casi siempre vale `0` en la practica.
- `sales_order.subtotal == sales_order.total_amount` salvo casos manuales.
- El comprobante muestra la linea de descuento solo si
  `order.discount_amount > 0`.

### Compatibilidad vehicular y devoluciones: fuera del alcance

- `VEHICLE_MODEL` y `PART_COMPATIBILITY` existen en el ERD pero no se
  consultan ni se persisten desde el modulo de Ventas.
- `RETURN_ORDER` y `RETURN_ORDER_ITEM` tampoco tienen rutas ni CRUD en la
  aplicacion actual. Esto es coherente con el listado de "mejoras futuras"
  en `db_explanation.md` y debe presentarse como trabajo futuro, no como
  bug.

### Inventario sin historial de movimientos

Solo se descuenta `inventory_stock.quantity_on_hand`. No hay
`INVENTORY_MOVEMENT`, asi que auditar por que bajo el stock desde la base de
datos requiere revisar las ventas (`SALES_ORDER_ITEM`).

### Decisiones que conviene defender

- `sales_order.status` se mantiene como `VARCHAR` aunque en la practica
  solo se use "Paid"; eso deja la puerta abierta a los otros valores
  documentados.
- `payment.reference_number` se genera con el id de la orden y los minutos
  y segundos (`MMSS`); no es un identificador formal.
- `order_date` y `payment_date` son siempre `today()` del servidor; el modulo
  no permite registrar ventas con fecha manual.
- El `FOR UPDATE` sobre `inventory_stock` es la unica proteccion contra
  condicion de carrera y debe ser mencionado explicitamente en la defensa.
