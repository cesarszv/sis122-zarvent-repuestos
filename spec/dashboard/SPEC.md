# SPEC — Dashboard

El modulo Dashboard es la pantalla de inicio del sistema despues del login.
Muestra indicadores operativos de ventas del dia, total de ordenes, compras
pendientes, pagos del dia por metodo, alertas de stock y categorias activas, y
lista las ultimas cinco ordenes de venta. Es un modulo de **solo lectura**:
recibe `GET` y no modifica la base de datos. Cubre parcialmente el
requerimiento `RF-09` de [`docs/analysis/requirements.md`](../../docs/analysis/requirements.md).

## 1. Estado actual (reverse-engineered)

### Rutas Flask

- `GET /dashboard` declarada en `src/zarvent_repuestos/web/app.py:113-118`,
  decorada con `@login_required` (`app.py:69-77`). Si la sesion no tiene
  `user_id`, redirige a `/` con un `flash` de error. Llama a
  `sales_crud.obtener_metricas_dashboard()` y renderiza
  `templates/dashboard.html` con `active_page="dashboard"` y `metrics`.

### Templates

- `src/zarvent_repuestos/web/templates/dashboard.html` (152 lineas). Extiende
  `layout.html`. Composicion:
  - Encabezado "Resumen General" + subtitulo "Estado operacional y alertas en
    tiempo real".
  - Grilla bento declarada como `md:grid-cols-4` (`dashboard.html:17`) pero
    con **3** tarjetas hijas: Ventas de Hoy, Alertas de Stock, Categorias
    Activas.
  - Bloque "Ultimas Ordenes de Venta": tabla con hasta 5 ordenes
    (`#ORD-{id}`, `billing_name`, fecha `dd/mm/yyyy`, monto, estado). Si la
    lista viene vacia, muestra el texto literal
    `"No hay ventas registradas hoy."` (`dashboard.html:103`).
  - Bloque "Alertas de Reabastecimiento": hasta 5 productos con
    `quantity_on_hand <= reorder_level`. Si esta vacia, muestra
    `"Todo el stock esta en niveles optimos!"` (`dashboard.html:140`).
  - Enlace `Ver todas las ventas ->` apunta a `/sales`.
  - Enlace `Ir al catalogo ->` apunta a `/inventory`.
- `templates/layout.html:99-101` resalta la opcion "Dashboard" del menu
  lateral cuando `active_page == 'dashboard'`.

### Funcion CRUD usada

- `sales_crud.obtener_metricas_dashboard()` en
  `src/zarvent_repuestos/crud/sales_crud.py:206-276`. Devuelve un diccionario
  con **6** claves (`today_sales_amount`, `categories_count`,
  `low_stock_count`, `total_orders_count`, `recent_orders`, `low_stock_items`).
  Usa dos cursores: el primero (cursor por defecto) para agregaciones, luego
  lo cierra y abre `cursor(dictionary=True)` para las dos listas. No usa
  transaccion porque es solo lectura.

### Tablas relacionadas (consultadas en tiempo real)

| Tabla | Uso actual en el dashboard |
| --- | --- |
| `sales_order` | `today_sales_amount`, `total_orders_count`, `recent_orders` (JOIN con `customer`) |
| `customer` | `recent_orders.billing_name` |
| `inventory_stock` | `low_stock_count`, `low_stock_items` (JOIN con `part`) |
| `part` | `low_stock_items.internal_code`, `name`, `brand` |
| `part_category` | `categories_count` |

Las tablas se crean en `src/zarvent_repuestos/database/init_db.py` mediante
`CREATE TABLE IF NOT EXISTS`. El borrador academico en
[`database/schema.sql`](../../database/schema.sql) no las contiene todavia.

### Comportamiento visible

- Sin login, `GET /dashboard` redirige a `/` con un mensaje en `flash`.
- Con login, devuelve codigo `200` y el HTML renderizado de `dashboard.html`.
- Las metricas se calculan al vuelo en cada request. No hay cache, no hay
  `?refresh=`, no hay parametro de fecha.
- La fecha de las ordenes se formatea con `order_date.strftime('%d/%m/%Y')`
  en el template, pero la consulta de `recent_orders` **no filtra** por fecha
  (`sales_crud.py:250-255`). El mensaje "No hay ventas registradas hoy." es
  estatico y no distingue "hoy" de "siempre".
- `total_orders_count` se calcula (`sales_crud.py:242-244`) y se devuelve en
  el diccionario, pero el template **no lo renderiza** en ninguna tarjeta.
- `sales_crud.py:223-225` filtra `today_sales_amount` con
  `status != 'Cancelled'`, pero en la practica `sales_crud.crear_orden_venta`
  inserta siempre `status='Paid'` (`sales_crud.py:76`). El filtro es
  redundante y se debe quitar.

### SQL trace indirecto

El modulo `src/zarvent_repuestos/database/sql_trace.py` envuelve los cursores
con `TracedCursor` y `TracedConnection`. Cuando `SQL_TRACE_ENABLED=1`, cada
query que dispara `obtener_metricas_dashboard()` queda registrada con
`method=GET` y `route=/dashboard`. La pagina `/sql-trace` los muestra. Los
hooks `before_request` y `teardown_request` en `app.py:55-66` etiquetan la
ruta actual antes de cada peticion y la limpian al terminar.

## 2. Contrato objetivo v1

### Flujos permitidos

1. Usuario autenticado entra a `GET /dashboard`. El sistema calcula 6
   metricas + 1 lista y renderiza la pagina.
2. Usuario autenticado hace click en `Ver todas las ventas ->` y navega a
   `/sales` (codigo 200).
3. Usuario autenticado hace click en `Ir al catalogo ->` y navega a
   `/inventory` (codigo 200).
4. Usuario no autenticado intenta `/dashboard` y es redirigido a `/` con
   `flash("Por favor, inicia sesion para acceder al sistema.", "error")`.

### Bloques visibles (orden de renderizado)

| Bloque | Contenido | Origen de datos |
| --- | --- | --- |
| KPI 1 | Ventas de Hoy (`$X,XXX.XX`) | `SUM(sales_order.total_amount) WHERE order_date = CURDATE()` |
| KPI 2 | Total Ordenes (entero) | `COUNT(sales_order)` |
| KPI 3 | Alertas de Stock (entero, en rojo si > 0) | `SELECT COUNT(*) FROM vw_low_stock_parts` |
| KPI 4 | Categorias Activas (entero) | `SELECT COUNT(*) FROM part_category` |
| Seccion compras + pagos | `pending_purchase_count` (entero) + lista `payments_by_method` | `purchase_order WHERE status='Pending'` y `payment WHERE payment_date = CURDATE() GROUP BY method` |
| Tabla ordenes | hasta 5 filas con `#ORD-{id}`, `billing_name`, `dd/mm/yyyy`, monto, badge de estado | `sales_order` JOIN `customer` `ORDER BY sales_order_id DESC LIMIT 5` |
| Lista stock | hasta 5 items con codigo, nombre, marca, stock, minimo | `SELECT * FROM vw_low_stock_parts ORDER BY quantity_on_hand ASC LIMIT 5` |

### Validaciones

- El endpoint solo acepta `GET`. No lee `query string` ni `form`.
- El filtro de fecha para "Ventas de Hoy" es siempre `CURDATE()` y no se
  puede ajustar desde la UI.
- `pending_purchase_count` no filtra por fecha (es conteo actual).
- `payments_by_method` filtra por `payment_date = CURDATE()` (pagos del dia).

### Mensajes visibles

| Caso | Texto literal |
| --- | --- |
| Sin sesion | `flash("Por favor, inicia sesion para acceder al sistema.", "error")` y redirect a `/` |
| Sin ordenes recientes | `"No hay ventas registradas."` (sin la palabra "hoy") |
| Sin stock bajo | `"Todo el stock esta en niveles optimos!"` |
| Sin compras pendientes | `0` mostrado en la tarjeta |
| Sin pagos del dia | `"No hay pagos registrados hoy."` |

### Estados y efectos esperados

- `200 OK` con HTML renderizado cuando el usuario esta autenticado.
- `302 redirect` a `/` cuando no hay sesion.
- Si MySQL falla durante `obtener_metricas_dashboard()`, la funcion loguea
  el error y devuelve el diccionario con ceros y listas vacias. Flask no
  recibe excepcion, asi que la pagina se renderiza con valores en cero en
  lugar de mostrar un 500.
- No hay efecto colateral en la base de datos: el modulo es 100% lectura.

## 3. Cambios requeridos v1

| # | Cambio | Archivo / linea actual | Afecta spec vecino |
| --- | --- | --- | --- |
| 1 | Crear la vista `vw_low_stock_parts` con `CREATE OR REPLACE VIEW` (columnas: `part_id`, `internal_code`, `name`, `brand`, `quantity_on_hand`, `reorder_level`; filtro `quantity_on_hand <= reorder_level`). | nuevo en `src/zarvent_repuestos/database/init_db.py` (o `database/schema.sql`) | [inventory/SPEC.md](inventory/SPEC.md) (tambien la consume) |
| 2 | Quitar `AND status != 'Cancelled'` del `WHERE` de `today_sales_amount` en `obtener_metricas_dashboard`. | `src/zarvent_repuestos/crud/sales_crud.py:222-225` | [sales/SPEC.md](sales/SPEC.md) |
| 3 | Reemplazar `SELECT COUNT(*) FROM inventory_stock WHERE quantity_on_hand <= reorder_level` por `SELECT COUNT(*) FROM vw_low_stock_parts`. | `src/zarvent_repuestos/crud/sales_crud.py:235-239` | [inventory/SPEC.md](inventory/SPEC.md) |
| 4 | Reemplazar el `SELECT` ad-hoc de `low_stock_items` (con JOIN a `part`) por `SELECT * FROM vw_low_stock_parts ORDER BY quantity_on_hand ASC LIMIT 5`. | `src/zarvent_repuestos/crud/sales_crud.py:260-268` | [inventory/SPEC.md](inventory/SPEC.md) |
| 5 | Anadir la metrica `pending_purchase_count` (`SELECT COUNT(*) FROM purchase_order WHERE status = 'Pending'`) al diccionario devuelto. | `src/zarvent_repuestos/crud/sales_crud.py` (despues de `total_orders_count`) | [purchases/SPEC.md](purchases/SPEC.md) |
| 6 | Anadir la metrica `payments_by_method` (`SELECT method, SUM(amount) AS total FROM payment WHERE payment_date = CURDATE() GROUP BY method`) al diccionario. | `src/zarvent_repuestos/crud/sales_crud.py` | [sales/SPEC.md](sales/SPEC.md) |
| 7 | Renderizar `total_orders_count` como una nueva tarjeta KPI en la grilla bento (`dashboard.html`). La grilla pasa de 3 a 4 tarjetas y la clase `md:grid-cols-4` pasa a estar usada al maximo. | `src/zarvent_repuestos/web/templates/dashboard.html:17-65` | — |
| 8 | Anadir una seccion visible debajo de la grilla de KPIs que muestre `pending_purchase_count` (numero) y la lista `payments_by_method` (etiqueta por metodo + monto). Si la lista viene vacia, mostrar el texto "No hay pagos registrados hoy." | `src/zarvent_repuestos/web/templates/dashboard.html` | — |
| 9 | Corregir el texto vacio de la tabla de ordenes: cambiar `"No hay ventas registradas hoy."` a `"No hay ventas registradas."`. | `src/zarvent_repuestos/web/templates/dashboard.html:103` | — |

## 4. Aceptacion automatizada

| Test | Cubre | Detalle |
| --- | --- | --- |
| `tests/test_login_flow.py:24` | redirect al dashboard | Verifica que `POST /` con credenciales validas redirige a `/dashboard`. |
| `tests/test_sql_trace.py` | modulo SQL trace (no dashboard) | Cubre el mecanismo de captura de queries; el dashboard se beneficia del mismo cuando `SQL_TRACE_ENABLED=1`. |
| `tests/test_setup_database.py` | creacion de tablas | Pre-requisito: si las tablas no existen, el dashboard falla. |

### Brechas de cobertura

- **No existe `tests/test_dashboard.py`.** Las 6 metricas del diccionario, el
  filtro `order_date = CURDATE()`, el uso de la vista `vw_low_stock_parts`,
  las dos nuevas metricas `pending_purchase_count` y `payments_by_method`, y
  el renderizado de las 4 tarjetas KPI no tienen asserts dedicados.
- **No existe test para la creacion de `vw_low_stock_parts`.** El test deberia
  verificar que la vista existe y devuelve al menos una fila cuando hay
  stock bajo.
- El fallo controlado de MySQL (pagina con ceros, no 500) tampoco esta
  cubierto por un test automatico.

## 5. Aceptacion manual en navegador / DataGrip

### Pasos en navegador (estudiante junior)

1. Levantar el servidor: `uv run python -m zarvent_repuestos.web.app` desde
   la raiz del repo.
2. Cargar el seed academico: `uv run python scripts/database/seed_project_data.py`
   (credencial `admin / admin123`).
3. Abrir `http://localhost:5000/`, iniciar sesion con `admin / admin123`. La
   aplicacion redirige a `/dashboard`.
4. Verificar que la grilla de KPIs tiene **4** tarjetas: Ventas de Hoy, Total
   Ordenes, Alertas de Stock, Categorias Activas. La tarjeta "Total Ordenes"
   muestra el conteo total de filas en `sales_order`.
5. Verificar que la seccion de compras + pagos muestra el conteo de compras
   en estado `Pending` y la lista de pagos del dia agrupados por metodo.
6. Verificar que la tabla "Ultimas Ordenes de Venta" muestra hasta 5 filas
   con codigo `#ORD-{id}`, `billing_name` del cliente, fecha `dd/mm/yyyy`,
   monto formateado y badge con el `status`.
7. Si la tabla de ordenes esta vacia, debe verse el texto
   `"No hay ventas registradas."` (sin "hoy").
8. Si la lista de stock bajo esta vacia, debe verse
   `"Todo el stock esta en niveles optimos!"`.
9. Visitar `http://localhost:5000/dashboard` sin haber iniciado sesion.
   Resultado esperado: redirect `302` a `/` y mensaje en flash.
10. Click en `Ver todas las ventas ->` debe llevar a `/sales` con `200`.
11. Click en `Ir al catalogo ->` debe llevar a `/inventory` con `200`.
12. **Fallo controlado**: detener MySQL, recargar `/dashboard` autenticado.
    La pagina debe renderizar con valores en cero y listas vacias, no
    devolver `500`.

### Pasos en DataGrip (cliente SQL)

1. Conectarse a la base `sis122_zarvent_repuestos`.
2. Verificar que la vista existe:
   `SHOW CREATE VIEW vw_low_stock_parts;`
   Debe devolver el `CREATE OR REPLACE VIEW` que la define.
3. Consultar la vista:
   `SELECT * FROM vw_low_stock_parts ORDER BY quantity_on_hand ASC LIMIT 5;`
   El resultado debe coincidir con los items renderizados en la lista
   lateral del dashboard.
4. Verificar el conteo de compras pendientes:
   `SELECT COUNT(*) FROM purchase_order WHERE status = 'Pending';`
   El numero debe coincidir con la tarjeta "Compras Pendientes".
5. Verificar el desglose de pagos del dia:
   `SELECT method, SUM(amount) FROM payment WHERE payment_date = CURDATE() GROUP BY method;`
   El resultado debe coincidir con la lista "Pagos del Dia".
6. Verificar el conteo total de ordenes:
   `SELECT COUNT(*) FROM sales_order;`
   El numero debe coincidir con la tarjeta "Total Ordenes".

## 6. Decisiones fuera de alcance

1. **Reporte de devoluciones (RF-08)**: las tablas `return_order` y
   `return_order_item` aparecen en [`docs/database/erd.md`](../../docs/database/erd.md) pero
   `init_db.py` no las crea. No se puede consultar el dato. Marcado como
   `fuera de alcance v1`, `backlog v2`.
2. **Compatibilidad vehicular (RF-03)**: las tablas `vehicle_model` y
   `part_compatibility` tampoco se crean. No es un reporte del dashboard,
   pero figura en la trazabilidad general. `fuera de alcance v1`,
   `backlog v2`.
3. **Auto-refresh / AJAX / WebSockets**: el dashboard se recalcula solo en
   cada `GET`. No hay polling. Coherente con alcance academico.
4. **Control de roles**: cualquier usuario autenticado
   (`session["user_id"]` presente) ve las mismas metricas. El modulo de
   usuarios del proyecto no implementa roles todavia.
5. **Historial de movimientos de stock**: `inventory_movement` no existe.
   No es un reporte del dashboard; queda como `fuera de alcance v1`.
6. **Procedimientos almacenados y triggers**: el dashboard no los usa.
   Documentado como `fuera de alcance v1` en
   [spec/README.md](../README.md) (fila 6 de la matriz).
7. **Mockup academico**: existen `spec/dashboard/dashboard_mockup.html` y
   `spec/dashboard/dashboard_mockup.png`. La pantalla real usa nombres de
   clases CSS distintos pero conserva la misma estructura semantica. No
   requiere cambios para v1.

## 7. Trazabilidad RF

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado v1 |
| --- | --- | --- | --- | --- |
| Reportes de supervision para gerencia | [`processes.md`](../../docs/analysis/processes.md) item 11 | [`db_explanation.md`](../../docs/database/db_explanation.md) (consulta libre) | `GET /dashboard` + `obtener_metricas_dashboard()` | parcial v1 |
| RF-09 ventas del dia | `processes.md` item 11 | `sales_order.total_amount`, `order_date` | `SUM(total_amount) WHERE order_date = CURDATE()` (cambio v1: quitar `status != 'Cancelled'`) | implementado v1 |
| RF-09 total de ordenes | `processes.md` item 11 | `sales_order` | calculado en `sales_crud.py:242-244`, no renderizado (cambio v1: anadir tarjeta KPI) | parcial v1 |
| RF-09 stock bajo | `processes.md` control de inventario | `inventory_stock.quantity_on_hand`, `reorder_level` | SELECT ad-hoc (cambio v1: usar `vw_low_stock_parts`) | parcial v1 |
| RF-09 compras pendientes | `processes.md` item 8 | `purchase_order.status='Pending'` | NO consultado (cambio v1: anadir `pending_purchase_count`) | parcial v1 |
| RF-09 pagos del dia | `processes.md` item 7 | `payment.method`, `payment.amount`, `payment_date` | NO consultado (cambio v1: anadir `payments_by_method`) | parcial v1 |
| RF-09 devoluciones | `processes.md` item 10 | `return_order`, `return_order_item` | Tablas no creadas en `init_db.py` | fuera de alcance v1 |
| RF-02 conteo de categorias | `processes.md` gestion catalogo | `part_category` | `COUNT(*) FROM part_category` | implementado v1 |
| RF-04 stock bajo por repuesto | `requirements.md` RF-04 | `INVENTORY_STOCK` | mismo cambio v1: `vw_low_stock_parts` | parcial v1 |
| RF-05 ultimas N ordenes | derivado del proceso 11 | `sales_order` + `customer` | `ORDER BY sales_order_id DESC LIMIT 5` | implementado v1 |
| RF-06 pagos por metodo | `processes.md` item 7 | `payment` | NO consultado en v1 (cambio v1: `payments_by_method`) | parcial v1 |
| RF-03 compatibilidad vehicular | `requirements.md` RF-03 | `VEHICLE_MODEL`, `PART_COMPATIBILITY` | No aplica al dashboard; tablas no creadas | fuera de alcance v1 |
| Autenticacion previa | actores `actors.md` | `users` (`init_db.py:206`) | `@login_required` en `app.py:114` | implementado v1 |
| Trazabilidad SQL | — | — | `sql_trace.py` + hooks en `app.py:55-66` (opt-in `SQL_TRACE_ENABLED=1`) | implementado v1 |
| Vistas (`vw_low_stock_parts`) | derivado de RF-04 y RF-09 | nueva vista en `database/schema.sql` o `init_db.py` | NO existe en codigo (cambio v1: crearla) | parcial v1 |
