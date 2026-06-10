# SPEC — Dashboard

El modulo Dashboard es la pantalla de inicio del sistema despues de iniciar
sesion. Muestra indicadores operativos de ventas del dia, alertas de stock bajo
y categorias activas, y lista las ultimas cinco ordenes de venta. Es de solo
lectura: no recibe parametros en `GET` y no modifica la base de datos.

## Objetivo del modulo

Resolver la necesidad del item 11 de `docs/analysis/processes.md`: la gerencia
necesita consultar de un vistazo el estado operativo del negocio (ventas del
dia, stock bajo, ultimas ordenes) sin correr reportes manuales ni abrir Excel.
Tambien cumple de forma minima el requerimiento `RF-09` de
`docs/analysis/requirements.md` (reportes basicos), aunque solo sobre datos de
ventas, stock y categorias, sin pagos ni devoluciones.

Esta pensado para ser la primera vista del usuario logueado y para funcionar
como punto de entrada a los modulos `/sales`, `/inventory` y `/customers` desde
los enlaces `Ver todas las ventas ->` e `Ir al catalogo ->` que renderiza el
template.

## Estado actual reverse-engineered

### Rutas Flask

- `GET /dashboard` declarada en `src/zarvent_repuestos/web/app.py:113-118`.
  Decorada con `@login_required` (definido en `app.py:69-77`). Si la sesion no
  tiene `user_id`, redirige a `/` con un `flash` de error.
  Llama a `sales_crud.obtener_metricas_dashboard()` y renderiza
  `templates/dashboard.html` pasando `active_page="dashboard"` y `metrics`.

### Templates

- `src/zarvent_repuestos/web/templates/dashboard.html` (152 lineas). Extiende
  `layout.html`. No define bloques personalizados mas alla de `title` y
  `content`. Se compone de:
  - Encabezado "Resumen General" + subtitulo "Estado operacional y alertas en
    tiempo real".
  - Grilla bento de 3 tarjetas KPI (no 4, pese a que la clase es
    `md:grid-cols-4`): Ventas de Hoy, Alertas de Stock, Categorias Activas.
  - Bloque "Ultimas Ordenes de Venta": tabla con las ultimas 5 ordenes
    (codigo `#ORD-{id}`, cliente `billing_name`, fecha, monto, estado). Si la
    lista viene vacia, muestra "No hay ventas registradas hoy." (mensaje
    literal del template, aunque la consulta no filtra por fecha).
  - Bloque "Alertas de Reabastecimiento": lista de hasta 5 productos con
    `quantity_on_hand <= reorder_level`. Si esta vacia, muestra
    "Todo el stock esta en niveles optimos!".
  - Enlace `Ver todas las ventas ->` apunta a `/sales`.
  - Enlace `Ir al catalogo ->` apunta a `/inventory`.
- `src/zarvent_repuestos/web/templates/layout.html:99-101` resalta la opcion
  "Dashboard" del menu lateral cuando `active_page == 'dashboard'`.

### Funcion CRUD usada

- `sales_crud.obtener_metricas_dashboard()` en
  `src/zarvent_repuestos/crud/sales_crud.py:206-276`. Devuelve un diccionario
  con seis claves. Usa dos cursores: el primero (cursor por defecto) para los
  `SELECT` de agregacion, y luego lo cierra y abre un nuevo `cursor(dictionary=True)`
  para devolver las dos listas. No usa transaccion porque es solo lectura.

### Tablas relacionadas (consultadas en tiempo real)

| Tabla | Uso en el dashboard |
| --- | --- |
| `sales_order` | `today_sales_amount`, `total_orders_count`, `recent_orders` (join con `customer`) |
| `customer` | `recent_orders.billing_name` |
| `inventory_stock` | `low_stock_count`, `low_stock_items` (join con `part`) |
| `part` | `low_stock_items.internal_code`, `name`, `brand` |
| `part_category` | `categories_count` |

Las tablas se crean en `src/zarvent_repuestos/database/init_db.py` mediante
`CREATE TABLE IF NOT EXISTS` (sin esquema en `database/schema.sql` aparte del
borrador academico).

### Comportamiento visible

- Sin login, `GET /dashboard` redirige a `/` con un mensaje en `flash`.
- Con login, devuelve codigo `200` y el HTML renderizado de `dashboard.html`.
- Las metricas se calculan al vuelo en cada request. No hay cache, no hay
  `?refresh=`, no hay parametro de fecha.
- La fecha de las ordenes se formatea con `order_date.strftime('%d/%m/%Y')` en
  el template, pero `today_sales_amount` SI filtra por `order_date = CURDATE()`.
  El mensaje "No hay ventas registradas hoy" es estatico del template y no
  distingue "hoy" de "siempre".

### SQL trace indirecto

El modulo `src/zarvent_repuestos/database/sql_trace.py` envuelve los cursores
con `TracedCursor` y `TracedConnection`. Cuando `SQL_TRACE_ENABLED=1`, cada
query que dispara `obtener_metricas_dashboard()` queda registrada con
`method=GET` y `route=/dashboard`. La pagina `/sql-trace` los muestra. Los
hooks `before_request` y `teardown_request` en `app.py:55-66` etiquetan la
ruta actual antes de cada peticion y la limpian al terminar. El dashboard no
participa en el trace de forma explicita, pero las consultas que ejecuta si
quedan registradas.

## Contrato funcional

### Flujos permitidos

1. Usuario autenticado entra a `/dashboard`. El sistema calcula seis metricas
   y renderiza la pagina.
2. Usuario autenticado hace click en `Ver todas las ventas ->` y navega a
   `/sales`.
3. Usuario autenticado hace click en `Ir al catalogo ->` y navega a
   `/inventory`.
4. Usuario no autenticado intenta `/dashboard` y es redirigido a `/` con
   `flash("Por favor, inicia sesion para acceder al sistema.", "error")`.

### Campos visibles (en orden de renderizado)

| Bloque | Campo | Tipo template | Origen |
| --- | --- | --- | --- |
| KPI 1 | Ventas de Hoy | `metrics.today_sales_amount` formateado `$1,234.56` | `SUM(sales_order.total_amount) WHERE order_date=CURDATE() AND status<>'Cancelled'` |
| KPI 2 | Alertas de Stock | `metrics.low_stock_count` (entero) | `COUNT(inventory_stock) WHERE quantity_on_hand <= reorder_level` |
| KPI 3 | Categorias Activas | `metrics.categories_count` (entero) | `COUNT(part_category)` |
| Tabla ordenes | `sales_order_id` | `metrics.recent_orders[].sales_order_id` | `ORDER BY sales_order_id DESC LIMIT 5` |
| Tabla ordenes | cliente | `metrics.recent_orders[].billing_name` | JOIN `customer` |
| Tabla ordenes | fecha | `metrics.recent_orders[].order_date` | `sales_order.order_date` |
| Tabla ordenes | monto | `metrics.recent_orders[].total_amount` | `sales_order.total_amount` |
| Tabla ordenes | estado | `metrics.recent_orders[].status` | `sales_order.status` |
| Lista stock | codigo, nombre, marca | `metrics.low_stock_items[].{internal_code,name,brand}` | JOIN `part` |
| Lista stock | stock actual | `metrics.low_stock_items[].quantity_on_hand` | `inventory_stock.quantity_on_hand` |
| Lista stock | minimo | `metrics.low_stock_items[].reorder_level` | `inventory_stock.reorder_level` |

El diccionario `metrics` siempre trae las seis claves, aunque algunas sean
lista vacia o `0.0` / `0` si la funcion captura una excepcion
(`sales_crud.py:270-274` loguea y devuelve el diccionario con valores por
defecto, no propaga el error a Flask).

### Validaciones

- No hay validaciones de entrada: el endpoint solo acepta `GET` y no lee
  parametros de query string ni de formulario.
- El filtro de fecha para "Ventas de Hoy" es siempre `CURDATE()` y no se
  puede ajustar.

### Mensajes visibles

- Sin stock bajo: "Todo el stock esta en niveles optimos!" (literal del
  template `dashboard.html:140`).
- Sin ordenes: "No hay ventas registradas hoy." (literal del template
  `dashboard.html:103`). El texto no se ajusta si la base no tiene ordenes
  nunca o si solo no hay ventas del dia.
- Sin sesion: `flash("Por favor, inicia sesion para acceder al sistema.",
  "error")` y redirect a `/`.

### Estados y efectos esperados

- 200 OK con HTML renderizado cuando el usuario esta autenticado.
- 302 redirect a `/` cuando no hay sesion.
- Si MySQL falla durante `obtener_metricas_dashboard()`, la funcion loguea
  `Error al obtener metricas del dashboard: <err>` (`sales_crud.py:271`) y
  devuelve el diccionario con ceros y listas vacias. Flask no recibe
  excepcion, asi que la pagina se renderiza con valores en cero en lugar de
  mostrar un 500.
- No hay efecto colateral en la base de datos: el modulo es 100% lectura.

## Contrato de datos

### Tablas y relaciones utilizadas

- `sales_order (customer_id) -> customer (customer_id) -> person (person_id)`.
  Solo se proyecta `customer.billing_name` para mostrar nombre comercial en la
  tabla de ultimas ordenes.
- `sales_order` se consulta directo (sin JOIN) para `today_sales_amount` y
  `total_orders_count`.
- `inventory_stock (part_id) -> part (part_id) -> part_category
  (part_category_id)`. La lista de stock bajo hace JOIN con `part` para
  mostrar `internal_code`, `name` y `brand`. `categories_count` cuenta
  categorias de forma independiente.

### Queries reales (extraidas de `sales_crud.py:222-268`)

1. Ventas de hoy:
   `SELECT COALESCE(SUM(total_amount), 0.0) FROM sales_order WHERE order_date =
   CURDATE() AND status != 'Cancelled'`
2. Conteo de categorias: `SELECT COUNT(*) FROM part_category`
3. Conteo de stock bajo: `SELECT COUNT(*) FROM inventory_stock WHERE
   quantity_on_hand <= reorder_level`
4. Conteo de ordenes: `SELECT COUNT(*) FROM sales_order`
5. Ultimas 5 ordenes: `SELECT o.sales_order_id, o.order_date, o.status,
   o.total_amount, c.billing_name FROM sales_order o JOIN customer c ON
   o.customer_id = c.customer_id ORDER BY o.sales_order_id DESC LIMIT 5`
6. Stock bajo top 5: `SELECT p.internal_code, p.name, p.brand, s.quantity_on_hand,
   s.reorder_level FROM part p JOIN inventory_stock s ON p.part_id = s.part_id
   WHERE s.quantity_on_hand <= s.reorder_level ORDER BY s.quantity_on_hand ASC
   LIMIT 5`

### Side effects

- Ninguno. No se hace `INSERT`, `UPDATE` ni `DELETE` desde
  `obtener_metricas_dashboard` ni desde la ruta.
- `obtener_metricas_dashboard` abre y cierra una conexion por request usando
  `get_database_connection()` (`zarvent_repuestos.database.connection`).

### Reglas de integridad que se aprovechan

- `sales_order.customer_id` y `sales_order_item.sales_order_id` permiten los
  JOIN sin logica adicional.
- `inventory_stock.part_id` es `UNIQUE NOT NULL` (`init_db.py:128`), por lo
  que la relacion 1 a 1 entre parte y stock es segura para el JOIN.
- `part_category.name` es `UNIQUE` (`init_db.py:101`), por lo que el conteo
  representa categorias reales y no duplicados.

## Trazabilidad SDD

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Reportes de supervision para gerencia | `processes.md` item 11: "Gerencia consulta reportes de ventas, compras, pagos, stock y devoluciones." | `db_explanation.md` y `erd.md` solo dejan la consulta libre sobre tablas operativas | `GET /dashboard` + `obtener_metricas_dashboard()` muestra ventas del dia, stock bajo y categorias | parcial |
| Reportes basicos (RF-09) | `requirements.md` RF-09: ventas, pagos, stock bajo, compras pendientes, devoluciones | No define vistas, son consultas SQL | Implementa ventas del dia, stock bajo, categorias, ultimas 5 ordenes. NO incluye pagos, compras pendientes ni devoluciones | parcial |
| Ventas por dia | Proceso 11 (ventas) | `sales_order.total_amount`, `order_date`, `status` | `SUM(total_amount) WHERE order_date=CURDATE() AND status<>'Cancelled'` | implementado |
| Stock bajo | Proceso "Consulta y control de stock" | `inventory_stock.quantity_on_hand`, `reorder_level` | `COUNT` y `SELECT` con `quantity_on_hand <= reorder_level` | implementado |
| Conteo de categorias | Proceso "Gestion del catalogo de repuestos" | `part_category` | `COUNT(*) FROM part_category` | implementado |
| Ultimas N ordenes | No especificado en analisis | `sales_order` + `customer` | `ORDER BY sales_order_id DESC LIMIT 5` (limite arbitrario, no configurable) | implementado |
| Reporte de pagos | Proceso 7 (registrar pago) | `payment.amount`, `payment.status` | NO se consulta en `obtener_metricas_dashboard` | faltante |
| Compras pendientes | Proceso 8 (compras) | `purchase_order.status='Pending'` | NO se consulta en el dashboard | faltante |
| Devoluciones | Proceso 10 (devoluciones) | `RETURN_ORDER`, `RETURN_ORDER_ITEM` | NO se consulta en el dashboard. Ademas, las tablas no existen en `init_db.py` | faltante |
| Compatibilidad vehicular (RF-03) | `requirements.md` RF-03 | `VEHICLE_MODEL`, `PART_COMPATIBILITY` | Tablas no creadas en `init_db.py`. No es parte del dashboard, pero figura en la trazabilidad general | fuera de alcance |
| Historial de movimientos de stock | `db_explanation.md` "Limitaciones aceptadas" menciona `INVENTORY_MOVEMENT` | No implementado | No se usa en el dashboard (segun el contrato actual solo se muestra stock actual) | fuera de alcance |
| Autenticacion previa al dashboard | Implícito: la gerencia es un actor identificado | `users` (`init_db.py:206`) | `@login_required` en `app.py:114` valida `session["user_id"]` | implementado |
| Trazabilidad SQL de la consulta | No mencionado en `docs/analysis` | No mencionado en `docs/database` | Hooks en `app.py:55-66` + `sql_trace.py` registran la ruta `/dashboard` cuando `SQL_TRACE_ENABLED=1` | parcial (es opt-in via env var) |

## Criterios de aceptacion

### Pruebas manuales

1. **Sin sesion**: con el servidor levantado (`uv run python -m
   zarvent_repuestos.web.app`), abrir `http://localhost:5000/dashboard` sin
   haber iniciado sesion. Resultado esperado: redirect 302 a `/` y mensaje
   "Por favor, inicia sesion para acceder al sistema." visible tras hacer
   login.
2. **Login redirige al dashboard**: tras autenticarse con `admin` / `admin123`
   (credencial sembrada en `scripts/database/seed_project_data.py`, no
   generada por el modulo Dashboard), la aplicacion redirige a `/dashboard`.
   Caso ya cubierto por `tests/test_login_flow.py:24`.
3. **KPI Ventas de Hoy con base sembrada**: con el seed cargado y al menos
   una venta con `order_date = CURDATE()` y `status != 'Cancelled'`, el KPI
   debe mostrar un monto `$X,XXX.XX` con dos decimales y separador de miles.
4. **KPI Ventas de Hoy sin ventas del dia**: con todas las ventas en
   `order_date < CURDATE()`, el KPI debe mostrar `$0.00` (gracias a
   `COALESCE(SUM(...), 0.0)` en `sales_crud.py:223`).
5. **KPI Alertas de Stock en cero**: si ningun `inventory_stock` cumple
   `quantity_on_hand <= reorder_level`, el numero debe ser `0` y la lista
   debe mostrar "Todo el stock esta en niveles optimos!".
6. **KPI Alertas de Stock > 0**: si hay productos bajo el minimo, el numero
   debe verse en rojo (`text-zarvent-red` en `dashboard.html:41`) y la lista
   lateral debe mostrar hasta 5 productos ordenados por
   `quantity_on_hand ASC`.
7. **Tabla de ultimas ordenes vacia**: con `sales_order` sin registros, la
   tabla debe mostrar la fila "No hay ventas registradas hoy." y no romper.
8. **Tabla con ordenes**: con `sales_order` cargada, deben verse hasta 5
   filas con codigo `#ORD-{id}`, `billing_name` del cliente, fecha en formato
   `dd/mm/yyyy`, monto formateado y badge con el `status` actual.
9. **Enlaces internos**: `Ver todas las ventas ->` lleva a `/sales` con
   codigo 200. `Ir al catalogo ->` lleva a `/inventory` con codigo 200.
10. **Fallo de MySQL controlado**: si se baja el servidor MySQL y se hace
    `GET /dashboard` autenticado, la pagina no debe devolver 500: debe
    renderizar KPIs en cero y la lista de stock bajo vacia. Esto valida que
    `obtener_metricas_dashboard()` captura `mysql.connector.Error` en
    `sales_crud.py:270-274`.
11. **Trazabilidad SQL**: con `SQL_TRACE_ENABLED=1`, abrir
    `http://localhost:5000/sql-trace` despues de visitar `/dashboard`. Las
    consultas de `obtener_metricas_dashboard()` deben aparecer con
    `method=GET` y `route=/dashboard`. Caso cubierto conceptualmente por
    `tests/test_sql_trace.py` (el test prueba el modulo, no el dashboard
    puntual).

### Pruebas automatizadas existentes

- `tests/test_login_flow.py:24` verifica que el login redirige a
  `/dashboard`. Es la unica cobertura automatica que toca al dashboard de
  forma directa.
- `tests/test_sql_trace.py` cubre el modulo de trace, no el dashboard, pero
  el dashboard se beneficia del mismo mecanismo cuando la env var esta
  activa.
- `tests/test_setup_database.py` cubre la creacion de tablas
  (`init_db.py`), pre-requisito para que el dashboard funcione.

### Brecha de cobertura

- No existe `tests/test_dashboard.py` ni un test equivalente. Las metricas
  `today_sales_amount`, `low_stock_count`, `categories_count`,
  `total_orders_count`, `recent_orders` y `low_stock_items` no tienen
  asserts dedicados. Esto debe documentarse como gap academico antes de
  defender el modulo.

## Brechas y decisiones

1. **Pagos no aparecen en el dashboard**. El analisis (`processes.md` item
   11) menciona "pagos" y `requirements.md` RF-06 + RF-09 los listan, pero
   `obtener_metricas_dashboard` no consulta la tabla `payment`. Decision:
   el alcance actual prioriza "ventas cobradas" como una sola unidad
   (`sales_order.status='Paid'` ya implica pago), pero no hay metrica
   explicita de pagos por metodo o por dia.

2. **Compras pendientes no aparecen**. RF-07 cubre compras pero el dashboard
   no las muestra. No hay `count(purchase_order WHERE status='Pending')` ni
   similar. Decision: el modulo actual se centra en venta y stock; las
   compras se revisan desde `/purchases`.

3. **Devoluciones no existen en la base de datos**. `RETURN_ORDER` y
   `RETURN_ORDER_ITEM` aparecen en `docs/database/erd.md` y en
   `db_explanation.md` como piezas del modelo, pero `init_db.py` no las
   crea. Por lo tanto, no pueden consultarse desde el dashboard. Marcadas
   como `fuera de alcance` en la matriz de trazabilidad.

4. **El mensaje "No hay ventas registradas hoy" es estatico**. El template
   `dashboard.html:103` muestra ese mensaje cuando `metrics.recent_orders`
   esta vacia, pero la consulta no filtra por fecha (`recent_orders` trae
   las ultimas 5 sin importar `order_date`). Si la base esta vacia, se
   muestra el mismo mensaje que si solo no hay ventas del dia. Decision
   documentada en este SPEC: no se corrige para no introducir cambios
   funcionales fuera del contrato.

5. **`total_orders_count` no se renderiza**. La funcion lo calcula
   (`sales_crud.py:242-244`) y lo devuelve en `metrics["total_orders_count"]`,
   pero el template `dashboard.html` no lo muestra en ninguna tarjeta. Es un
   campo fantasma. Mantenerlo no rompe nada; quitarlo requiere editar
   `sales_crud.py` y el contrato, y esta fuera de alcance de este SPEC.

6. **Filtros del dashboard son hardcodeados**. `order_date = CURDATE()` y
   `LIMIT 5` no son configurables por query string ni por variables de
   entorno. Si se necesita "ventas de ayer" o "ultimas 10", hay que tocar
   la funcion.

7. **Cobertura de tests es nula para el dashboard**. Solo
   `test_login_flow.py:24` valida el redirect al dashboard. Las seis
   metricas calculadas no tienen asserts dedicados. Marcado como brecha en
   la seccion de Criterios de aceptacion.

8. **El dashboard no es reactivo**. La pagina se recalcula solo en cada
   request. No hay AJAX, no hay auto-refresh, no hay long-polling. Esto es
   coherente con el alcance academico y no es un defecto, pero conviene
   declararlo para evitar preguntas en la defensa.

9. **No hay control de roles para ver el dashboard**. Cualquier usuario
   autenticado (`session["user_id"]` presente) ve las mismas seis metricas.
   `processes.md` distingue Gerente / Vendedor / Almacen / Compras como
   actores, pero el modulo de usuarios del proyecto no tiene roles todavia
   (`init_db.py:206-212` define `users` solo con `id`, `username`,
   `password`). Decision documentada: el alcance del dashboard es
   "vista unica para todos los usuarios logueados".

10. **El mockup visual existe pero no es codigo de produccion**. Los archivos
    `spec/dashboard/dashboard_mockup.html` y `spec/dashboard/dashboard_mockup.png`
    son material de diseno. La implementacion real esta en
    `src/zarvent_repuestos/web/templates/dashboard.html`. Ambos coinciden en
    bloques (KPI Ventas de Hoy, KPI Alertas, KPI Categorias, tabla de
    ultimas ordenes, lista lateral de stock bajo), pero el mockup usa clases
    de Tailwind propias (`gap-gutter`, `font-body-md`) y el template
    real usa las del layout institucional (`bg-pure-white`, `text-zarvent-red`,
    etc.). La diferencia es solo de naming; la estructura semantica es la
    misma.
