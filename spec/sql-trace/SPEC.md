# SPEC — SQL Trace

Contrato tecnico y de uso del modulo **SQL Trace** de Zarvent Repuestos.
Es una herramienta didactica y de diagnostico en vivo: envuelve los
cursores de `mysql-connector-python` para registrar cada `execute()` y
`executemany()` sin tocar el codigo CRUD del negocio. Esta pensada para
defender el proyecto en clase, NO para alimentar tablas propias ni
persistir informacion.

SQL Trace **no** es un modulo CRUD del negocio. No aparece en
`docs/analysis/requirements.md` como RF propio, no es una entidad del
ERD y no implementa ningun requerimiento funcional: hace visibles, en
vivo y con etiquetas `method + route`, las consultas que el resto de
los modulos ya disparan contra MySQL.

---

## 1. Estado actual (reverse-engineered)

Lo que el codigo hace HOY, leido del repo. No es diseno, es evidencia.

### 1.1 Rutas Flask

Definidas en [`src/zarvent_repuestos/web/app.py`](../../src/zarvent_repuestos/web/app.py).

| Ruta | Metodo | Linea | Decoradores | Proposito |
| --- | --- | --- | --- | --- |
| `/sql-trace` | `GET` | `app.py:287` | `@login_required` | Renderiza `sql_trace.html` con el flag `trace_enabled`. |
| `/api/sql-trace` | `GET` | `app.py:298` | `@login_required` | Devuelve `{"entries": [...], "summary": {...}}` en JSON. |
| `/api/sql-trace/clear` | `POST` | `app.py:306` | `@login_required` | Llama a `clear_sql_trace_entries()` y responde `{"status": "ok"}`. |

Las tres rutas requieren login (`@login_required` en `app.py:69`), igual
que el resto de modulos privados.

### 1.2 Hooks de request

En `app.py:55-66` se conectan dos hooks que **solo corren si el trace
esta habilitado**:

- `before_request` -> `capture_sql_trace_request_context`:
  llama a `set_request_context(request.method, request.path)` y guarda
  los labels en `ContextVar`.
- `teardown_request` -> `release_sql_trace_request_context`:
  llama a `clear_request_context()` y restaura los labels a `"-"`.

Esto significa que cada entry nueva queda automaticamente etiquetada con
el `METHOD` y la `route` Flask que la origino (por ejemplo
`GET /dashboard`).

### 1.3 Modulo Python

[`src/zarvent_repuestos/database/sql_trace.py`](../../src/zarvent_repuestos/database/sql_trace.py).

Constantes y estado en memoria:

- `MAX_TRACE_ENTRIES = 80` (linea 14). Ring buffer de los ultimos 80
  statements.
- `SQL_TRACE_ENABLED = os.getenv("SQL_TRACE_ENABLED", "").lower() in
  {"1", "true", "yes", "on"}` (linea 15). Booleano resuelto al momento
  de importar el modulo; cambiar la variable en runtime no tiene efecto
  hasta reiniciar.
- `_TRACE_ENTRIES: deque[dict[str, Any]] = deque(maxlen=MAX_TRACE_ENTRIES)`
  (linea 21). Buffer FIFO de entradas.
- `_CURRENT_ROUTE: ContextVar[str]` y `_CURRENT_METHOD: ContextVar[str]`
  (lineas 22-23). `ContextVar` con default `"-"`, una por Flask request
  concurrente.

API publica:

- `is_sql_trace_enabled()` -> `bool` (linea 26).
- `get_sql_trace_entries()` -> `list[dict]` (linea 31). Devuelve
  `list(reversed(_TRACE_ENTRIES))` para que la UI reciba el mas nuevo
  primero.
- `clear_sql_trace_entries()` -> `None` (linea 36). `deque.clear()`.
- `set_request_context(method, route)` y `clear_request_context()`
  (lineas 41 y 47). Set / reset de los `ContextVar`.
- `compact_sql(statement)` (linea 53). Colapsa whitespace
  (`re.sub(r"\s+", " ", statement).strip()`).
- `summarize_params(statement, params)` (linea 58). Devuelve:
  - `"-"` si `params is None`.
  - `"[redacted password fields]"` si la palabra `password` aparece en
    el SQL (`statement.lower()`). Esto oculta el password del login.
  - `repr(params)` truncado a 180 caracteres si el resto.
- `operation_name(statement)` (linea 72). Devuelve la primera keyword
  (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, etc.) en mayusculas.
- `operation_concept(operation)` (linea 78). Mapea la keyword a una
  etiqueta academica corta en Latam Spanish: `SELECT -> "Consulta
  datos"`, `INSERT -> "Crea registros"`, `UPDATE -> "Modifica
  registros"`, `DELETE -> "Elimina registros"`, resto -> `"Ejecuta
  SQL"`.
- `extract_tables(statement)` (linea 89). Regex para `FROM`, `JOIN`,
  `INTO`, `UPDATE`. Devuelve la lista de tablas en orden, sin duplicados,
  en minusculas.
- `build_summary(entries)` (linea 107). Funcion pura (sin side effects)
  que devuelve `{"total", "errors", "operations", "tables"}`. `tables`
  es un dict con las 8 tablas mas frecuentes, ordenadas por conteo
  descendente.
- `build_trace_entry(...)` (linea 141). Construye el dict que se guarda
  en el deque. No toca estado global, solo lee los `ContextVar`.

Clases envoltorio:

- `TracedCursor` (linea 165). Recibe un cursor real de
  `mysql-connector-python` y envuelve `execute()` y `executemany()`.
  Mide duracion con `time.perf_counter()`, captura `status` (`OK` /
  `ERROR`) y el mensaje de error. En el `finally`:
  1. Hace `append` del entry al deque.
  2. Imprime por stdout una linea con prefijo `[SQL TRACE]`
     (importante: el trace sale **tambien** en la consola del servidor,
     no solo en la UI).
  Para `executemany` agrega el sufijo ` MANY` al campo `operation` para
  distinguirlo. `__getattr__` delega cualquier otro metodo al cursor
  real, asi `fetchone`, `fetchall`, `rowcount`, etc. funcionan sin
  reescribirse.
- `TracedConnection` (linea 220). Envoltorio delgado: solo sobreescribe
  `cursor()` para devolver `TracedCursor`. El resto se delega a la
  conexion real con `__getattr__`.

### 1.4 Inyeccion en `connection.py`

[`src/zarvent_repuestos/database/connection.py`](../../src/zarvent_repuestos/database/connection.py:13-22)
decide el tipo de conexion que devuelve:

```python
conexion = mysql.connector.connect(**DB_CONFIG)
if is_sql_trace_enabled():
    return TracedConnection(conexion)
return conexion
```

Si `SQL_TRACE_ENABLED` esta apagado, **toda la infraestructura de
trace se bypasea** y la aplicacion usa cursores nativos. Por eso el
modulo es opt-in y no agrega overhead en produccion / demo normal.

### 1.5 Template

[`src/zarvent_repuestos/web/templates/sql_trace.html`](../../src/zarvent_repuestos/web/templates/sql_trace.html)
tiene la siguiente estructura:

- Header con titulo "Consultas SQL en vivo", badge de estado
  (`En vivo` / `Pausado` / `Sin conexion`) y botones `Pausar` /
  `Limpiar`.
- Banner amarillo `{% if not trace_enabled %}` que aparece solo cuando
  `SQL_TRACE_ENABLED` esta apagado, recomendando arrancar con
  `SQL_TRACE_ENABLED=1`.
- Fila de 5 metricas en vivo: `Consultas`, `Ultima`, `Promedio`,
  `Ruta`, `Tablas`.
- Aside lateral con 4 bloques: `Resumen` (total + errores + tablas mas
  usadas), `Operaciones` (barras horizontales SELECT/INSERT/UPDATE/
  DELETE), `Filtro` (botones `ALL`, `SELECT`, `INSERT`, `UPDATE`,
  `DELETE`, `ERROR`), `Lectura para defensa` (una sola frase con la
  entry mas reciente).
- Lista de entries (`#trace-list`) con scroll vertical
  (`max-h-[68vh]`). Cada card muestra: hora, badge de operacion, badge
  `METHOD route`, badge de status, `<pre>` con el SQL, panel lateral
  con `Concepto` / `Tablas` / `Tiempo`, y los parametros en una
  franja inferior.

Logica JS inline (en `{% block extra_js %}`):

- `loadTrace()`: `fetch("/api/sql-trace")` cada 1 segundo
  (`setInterval(loadTrace, 1000)`). Llama a `renderTrace(cachedEntries)`
  y `renderSummary(summary)`. Si `paused === true`, sale sin hacer
  nada. Si falla el `fetch`, pone el badge en rojo `"Sin conexion"`.
- `pauseTrace` click: alterna `paused`, cambia el texto del boton
  entre `Pausar` / `Reanudar` y el badge entre `En vivo` (verde) /
  `Pausado` (ambar).
- `clearTrace` click: `POST /api/sql-trace/clear`, vacia
  `cachedEntries`, y re-renderiza con resumen en cero. Si no estaba
  pausado, vuelve a llamar a `loadTrace()` para refrescar.
- `renderTrace(entries)`: actualiza contadores, promedio de duracion,
  ultima ruta, ultimas tablas, conteo de visibles, barras de
  operaciones y la frase de defensa. Dibuja cada card con
  `escapeHtml` para evitar XSS.
- `renderSummary(summary)`: muestra/oculta `#trace-summary` segun haya
  datos y renderiza los chips de tablas con su conteo.
- Filtros: `data-filter="ALL|SELECT|INSERT|UPDATE|DELETE|ERROR"` en
  cada boton. `ALL` muestra todo, `ERROR` filtra por `status ===
  "ERROR"`, los demas filtran por la primera keyword de
  `entry.operation`.

### 1.6 Archivo `.env.example` HOY

[`../../.env.example`](../../.env.example) NO incluye la variable
`SQL_TRACE_ENABLED`. En v1 se agrega como documentacion explicita
del default (ver [Seccion 3, cambio 1](#3-cambios-requeridos-v1)).

### 1.7 Mockup de diseno

No existe mockup dedicado en `.cszv/mockups/` para este modulo. La
pantalla real (`sql_trace.html`) es la unica referencia visual.

---

## 2. Contrato objetivo v1

Lo que el spec PROMETE en v1. Cualquier entrega que no cumpla esto queda
rechazada como contrato.

### 2.1 Naturaleza y alcance

- SQL Trace es una **herramienta didactica transversal**: no agrega
  tablas, no agrega columnas, no implementa RF-01..RF-09, no aparece en
  el ERD. Existe solo para hacer visibles las consultas que el resto
  de los modulos ya emiten.
- Es **opt-in**: el default en v1 es `SQL_TRACE_ENABLED=0` (apagado).
  Cualquier entrega academica que no levante Flask con la variable
  prendida tendra el modulo presente pero inerte.
- Es **no persistente**: vive en un `deque` en memoria del proceso
  Flask. No hay archivo, no hay tabla, no hay log externo mas alla
  del `print` a stdout.
- Es **no contaminante del flujo CRUD**: si la variable esta apagada,
  `get_database_connection()` devuelve la conexion nativa y los CRUD
  usan cursores nativos sin overhead.

### 2.2 Activacion

- Variable de entorno: `SQL_TRACE_ENABLED`.
- Valores validos (case-insensitive): `1`, `true`, `yes`, `on`.
  Cualquier otro valor (incluido vacio) desactiva el modulo.
- Se lee **una sola vez** al importar `sql_trace.py`. Cambiar la
  variable sin reiniciar Flask **no** prende/apaga el trace en
  runtime.
- Si esta desactivado:
  - `get_database_connection()` devuelve la conexion nativa de
    `mysql-connector-python`.
  - La pantalla `/sql-trace` renderiza un **banner amarillo** de
    aviso en lugar de un trace vacio silencioso. El resto de la UI
    sigue renderizando (botones y filtros visibles), pero las APIs
    devuelven datos vacios persistentes y el polling no captura
    nada.

### 2.3 Rutas Flask v1

| Ruta | Metodo | Decorador | Que hace |
| --- | --- | --- | --- |
| `/sql-trace` | `GET` | `@login_required` | Renderiza `sql_trace.html` con el flag `trace_enabled`. |
| `/api/sql-trace` | `GET` | `@login_required` | Devuelve `{"entries": [...], "summary": {...}}` en JSON. |
| `/api/sql-trace/clear` | `POST` | `@login_required` | Llama a `clear_sql_trace_entries()` y responde `{"status": "ok"}`. |

### 2.4 Side effects garantizados por cada `execute()` / `executemany()`

Cuando `SQL_TRACE_ENABLED` esta prendido, `TracedCursor.execute` y
`TracedCursor.executemany`:

1. Miden duracion con `time.perf_counter()`.
2. Capturan `status` (`OK` / `ERROR`) y `error` (string vacio si no
   fallo).
3. Agregan un entry al ring buffer (FIFO, maximo 80) con la forma
   documentada en la [Seccion 2.6](#26-forma-de-cada-entry).
4. Imprimen una linea con prefijo `[SQL TRACE]` en stdout (visible
   en la terminal del servidor y en cualquier log redirigido).

Para `executemany`, el campo `operation` se construye como
`f"{base} MANY"`. Eso distingue un batch de un statement individual
mientras mantiene el filtro por keyword (`data-filter="INSERT"`
sigue considerando el batch como `INSERT`).

### 2.5 Redaction de passwords

`summarize_params(statement, params)` aplica la siguiente regla, en
este orden:

1. Si `params is None`, devuelve `"-"`.
2. Si `"password" in statement.lower()`, devuelve
   `"[redacted password fields]"`. La comparacion es
   case-insensitive.
3. En otro caso, devuelve `repr(params)`, truncado a 180 caracteres.

El password real del login **nunca** aparece en la UI ni en stdout.

### 2.6 Forma de cada entry

`build_trace_entry(...)` produce un `dict` con esta forma:

| Campo | Tipo | Origen |
| --- | --- | --- |
| `time` | `str` (`"HH:MM:SS"`) | `datetime.now().strftime("%H:%M:%S")` |
| `method` | `str` | `_CURRENT_METHOD.get()` |
| `route` | `str` | `_CURRENT_ROUTE.get()` |
| `operation` | `str` | `operation_name(operation)` (+ `" MANY"` si es `executemany`) |
| `concept` | `str` | `operation_concept(operation)` (etiqueta academica Latam Spanish) |
| `tables` | `list[str]` | `extract_tables(operation)` (regex sobre el SQL) |
| `sql` | `str` | `compact_sql(operation)` (whitespace colapsado) |
| `params` | `str` | `summarize_params(operation, params)` (con redaction de password) |
| `duration_ms` | `float` | `(perf_counter delta) * 1000`, redondeado a 2 decimales |
| `status` | `"OK" \| "ERROR"` | Resultado del `execute` / `executemany` |
| `error` | `str` | `str(error)` solo si hubo excepcion; vacio si no |

### 2.7 Persistencia y limites

- No hay export a disco, ni a archivo de log, ni a tabla.
- No hay persistencia entre reinicios: al levantar Flask de nuevo, el
  `deque` arranca vacio.
- No hay paginacion historica: solo se ve lo que esta en memoria
  (maximo 80 entries). Lo que se fue del ring buffer se pierde.
- El unico sink externo es el `print` a stdout con prefijo
  `[SQL TRACE]`, que sigue en pie aunque Flask no este corriendo
  (por ejemplo, en un script que importe `connection.py`).

### 2.8 Flujos del usuario

1. **Ver la pagina.** Ir a `/sql-trace` (requiere login). Ver
   header con badge de estado, fila de 5 metricas y la lista de
   entries en vivo. Ver panel lateral: `Resumen`, barras por
   operacion, `Filtro`, `Lectura para defensa` con la entry mas
   reciente. Cada entry nueva aparece arriba de la lista (`deque`
   con orden invertido). Auto-refresh cada 1 segundo via `fetch`.
2. **Pausar el auto-refresh.** Click en `Pausar`. El JS marca
   `paused = true` y deja de llamar a `/api/sql-trace`. Las entries
   **no se borran**, solo deja de refrescar la vista. El badge
   cambia a `Pausado` (ambar). El boton pasa a `Reanudar`.
   Click en `Reanudar`: vuelve a hacer polling cada segundo.
3. **Limpiar el buffer.** Click en `Limpiar`. Hace `POST
   /api/sql-trace/clear`, lo que llama a `clear_sql_trace_entries()`
   (`deque.clear()`). La UI limpia `cachedEntries` y repinta
   contadores en cero. Si no esta pausado, hace un `loadTrace()`
   inmediato para mostrar la realidad post-clear.
4. **Filtrar por operacion.** Botones `ALL`, `SELECT`, `INSERT`,
   `UPDATE`, `DELETE`, `ERROR`. `ALL` -> sin filtro. `ERROR` ->
   entries con `status === "ERROR"`. Resto -> entries cuya primera
   keyword (`operationBase`) coincide. El filtro solo afecta lo
   que se **muestra**; el `deque` siempre tiene los ultimos 80
   reales. El boton activo se pinta de negro; los demas quedan en
   blanco con borde gris.
5. **Defender el proyecto.** Con el trace prendido, navegar a
   `/dashboard`, `/inventory`, `/sales`, `/customers`,
   `/purchases`. Cada vista dispara una serie de `SELECT` que se
   ven llegar al panel. Crear una venta o un cliente: aparecen
   `INSERT` sobre `customer`, `sales_order`,
   `sales_order_item`, `payment`, etc. Provocar un error (por
   ejemplo, eliminar un cliente con ventas): se ve la entry con
   `status=ERROR` y el mensaje de MySQL.

---

## 3. Cambios requeridos v1

Lista concreta para pasar del estado actual al contrato de la
[Seccion 2](#2-contrato-objetivo-v1).

| # | Cambio | Archivo(s) | Tipo | Afecta spec vecino |
| --- | --- | --- | --- | --- |
| 1 | Documentar `SQL_TRACE_ENABLED=0` en `.env.example` como default explicito. NO implementar la feature (ya esta); solo dejar el knob documentado. | `.env.example` | docs | este spec |
| 2 | Mantener la redaccion de passwords en `summarize_params` (ya esta en `sql_trace.py:58-69`); documentar el contrato en este spec. | (sin cambio de codigo) | spec | este spec |
| 3 | Mantener el modulo opcional y sin contaminar el flujo CRUD principal: si `SQL_TRACE_ENABLED` esta apagado, `get_database_connection` devuelve la conexion nativa (ya esta en `connection.py:13-22`). | (sin cambio de codigo) | spec | transversal a todos los specs de modulos |
| 4 | Cubrir el helper `extract_tables` con un caso de `INTO` (`INSERT INTO table_name`) para reforzar la lista de tablas que aparecen en el panel. | `tests/test_sql_trace.py` (extension) | test | este spec |
| 5 | Cubrir `summarize_params` con un caso de `params` que no es tupla (por ejemplo `dict` o `list`) para garantizar que `repr()` funciona sin explotar. | `tests/test_sql_trace.py` (extension) | test | este spec |

Ninguno de estos cambios introduce una nueva ruta, una nueva tabla o
un nuevo campo. SQL Trace sigue siendo una herramienta opt-in y
transversal.

---

## 4. Aceptacion automatizada

Tests en `tests/` que demuestran que el contrato se cumple.

### 4.1 Tests existentes

[`tests/test_sql_trace.py`](../../tests/test_sql_trace.py) cubre los
helpers puros del modulo:

- `ExtractTablesTest`:
  - `test_returns_joined_tables_in_order_without_duplicates`: caso
    `FROM` + `JOIN` (sin duplicados, en orden).
  - `test_returns_table_name_for_update_statement`: caso `UPDATE`.
- `SummarizeParamsTest`:
  - `test_redacts_when_password_keyword_is_in_sql`.
  - `test_redaction_is_case_insensitive` (PASSWORD mayusculas).
  - `test_returns_short_repr_when_password_keyword_is_absent`.
  - `test_returns_dash_when_params_is_none`.
- `CompactSqlTest`:
  - `test_collapses_multiple_whitespace_into_single_spaces`.
- `OperationNameTest`:
  - `test_returns_select_keyword`.
  - `test_returns_insert_keyword`.
- `BuildSummaryTest`:
  - `test_counts_total_errors_and_operations`.

Comando sugerido:

```bash
uv run python -m unittest tests.test_sql_trace
```

### 4.2 Brechas a cerrar en v1 (tests a aniadir)

| Brecha | Test a aniadir | Archivo sugerido |
| --- | --- | --- |
| `extract_tables` detecta tablas en `INSERT INTO table_name ...` ademas de `FROM` / `JOIN` / `UPDATE`. | `test_extract_tables_handles_insert_into_keyword`. | `tests/test_sql_trace.py` (extension) |
| `summarize_params` no falla con `params` que es `dict` o `list`. | `test_summarize_params_handles_dict_and_list`. | `tests/test_sql_trace.py` (extension) |
| `summarize_params` con password y params vacios devuelve el placeholder, no una cadena vacia. | `test_summarize_params_with_empty_params_and_password_keyword`. | `tests/test_sql_trace.py` (extension) |
| `build_summary` cuenta correctamente las operations con sufijo ` MANY` (un `INSERT MANY` cuenta como `INSERT`). | `test_build_summary_counts_many_suffix_as_base_operation`. | `tests/test_sql_trace.py` (extension) |

No se aniaden tests de integracion contra MySQL real: el modulo es
un envoltorio delgado sobre `mysql-connector-python` y la cobertura
unitaria de los helpers cubre la logica defendible. Las pruebas
manuales de la [Seccion 5](#5-aceptacion-manual-en-navegador--datagrip)
cubren la captura end-to-end.

---

## 5. Aceptacion manual en navegador / DataGrip

Pasos reproducibles que un estudiante junior puede correr para
verificar el contrato desde la UI o desde un cliente SQL.

### 5.1 En navegador

Prerequisito: estar logueado como `admin` / `admin123`.

1. **Apagado por default.**
   - Levantar Flask sin la variable:
     ```bash
     uv run python -m zarvent_repuestos.web.app
     ```
   - Ir a `/sql-trace` logueado. Debe verse el **banner amarillo**
     "SQL Trace esta desactivado. Inicia Flask con
     `SQL_TRACE_ENABLED=1` para registrar consultas." Las barras,
     los filtros y la lista se renderizan vacios, y el `GET
     /api/sql-trace` devuelve `{"entries": [], "summary":
     {...vacio...}}`.
2. **Prendido.**
   - Levantar con la variable prendida:
     ```bash
     SQL_TRACE_ENABLED=1 uv run python -m zarvent_repuestos.web.app
     ```
     (o exportar la variable y arrancar igual).
   - Ir a `/sql-trace`. **No** debe verse el banner amarillo. Las
     metricas arrancan en cero.
3. **Captura de lecturas.**
   - Navegar a `/dashboard`. Deben aparecer entries `SELECT` sobre
     las tablas del dashboard, con la ruta `GET /dashboard` en el
     badge.
   - Navegar a `/inventory`. Aparecen entries `SELECT` y la lista
     crece.
4. **Captura de escrituras.**
   - Ir a `/sales` y registrar una venta. Aparecen `INSERT` sobre
     `sales_order`, `sales_order_item`, `payment`, `customer` (si
     se registro un cliente nuevo), ademas de `UPDATE` sobre
     `inventory_stock` para descontar stock.
5. **Captura de errores.**
   - Forzar un error conocido (por ejemplo, intentar eliminar un
     cliente con ventas via `POST /customers/<id>/delete`). La
     entry aparece con `status: ERROR` y el mensaje de MySQL en
     el campo `error`.
6. **Redaction de password.**
   - Loguearse (`/`) con `admin` / `admin123`. El `POST /` dispara
     una consulta contra `users`. El campo `params` de esa entry
     debe ser `"[redacted password fields]"`, **no** debe verse el
     password en ningun momento de la UI ni en el stdout.
7. **Ver el trace tambien en consola.**
   - En la terminal donde corre Flask, durante cualquiera de los
     pasos anteriores, deben aparecer lineas con prefijo
     `[SQL TRACE]` por cada `execute()` / `executemany()`.
8. **Pausar y limpiar.**
   - Click en `Pausar`: la UI deja de actualizarse, el badge pasa
     a `Pausado` (ambar), el boton a `Reanudar`. La base de datos
     sigue funcionando normal; solo se congela la vista.
   - Click en `Reanudar`: el polling se restaura.
   - Click en `Limpiar`: contadores a cero, lista vacia. El
     `deque` queda vacio en el servidor.
9. **Filtros.**
   - Click en `SELECT`: solo se ven entries de tipo SELECT.
   - Click en `ERROR`: solo las que fallaron.
   - Click en `ALL`: vuelve a verse todo.
10. **Anillo de 80.**
    - Provocar mas de 80 statements rapidos (por ejemplo, recargar
      `/inventory` muchas veces). La lista mostrada no debe crecer
      mas alla de 80 entradas; las viejas se descartan en orden
      FIFO.

### 5.2 En DataGrip / cliente SQL

Prerequisito: tener `mysql` CLI o DataGrip conectado a la base
`sis122_zarvent_repuestos`. El modulo no toca la base, asi que las
validaciones SQL se limitan a confirmar que ninguna tabla auxiliar se
creo.

1. **Listar las tablas existentes.**
   ```sql
   SHOW TABLES;
   ```
   El resultado debe ser exactamente el conjunto declarado en
   `init_db.py`: `person`, `customer`, `supplier`, `part_category`,
   `part`, `inventory_stock`, `sales_order`, `sales_order_item`,
   `payment`, `purchase_order`, `purchase_order_item`, `users`. No
   debe haber tablas auxiliares como `sql_trace_entry` o similar.
2. **Confirmar que el modulo no migro nada.**
   ```sql
   SELECT TABLE_NAME FROM information_schema.TABLES
   WHERE TABLE_SCHEMA = DATABASE()
   AND TABLE_NAME LIKE '%trace%';
   ```
   El resultado debe ser vacio.
3. **Confirmar que ninguna vista/funcion auxiliar fue creada.**
   ```sql
   SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES
   WHERE TABLE_SCHEMA = DATABASE();
   ```
   El conjunto debe ser solo `BASE TABLE` (mas las vistas
   preexistentes `vw_low_stock_parts` y `vw_daily_sales_summary`
   declaradas en `database/schema.sql`).

---

## 6. Decisiones fuera de alcance

Lo que el modulo NO entrega en v1, con justificacion. Si quedan como
objetivo futuro, se etiquetan `backlog v2`.

| Tema | Estado v1 | Justificacion |
| --- | --- | --- |
| Persistencia del trace (archivo, tabla, SQLite, JSON). | `fuera de alcance v1` (`backlog v2`) | Es un modulo didactico. La salida oficial es la UI + stdout. Persistir cambia la naturaleza de la herramienta. |
| Paginacion historica del anillo de 80. | `fuera de alcance v1` (`backlog v2`) | En defensa se navega la app para generar statements frescos; no se necesita historial. |
| Export del trace a CSV / PDF / reporte academico. | `fuera de alcance v1` (`backlog v2`) | El material defendible es la UI en vivo + el `print` a stdout. |
| Reemplazo de literales en `sql_trace.py` por constantes en `constants.py`. | `fuera de alcance v1` (`backlog v2`) | Los strings `"OK"`, `"ERROR"`, `"-"`, `"[redacted password fields]"` y los prefijos son parte del contrato del modulo y no se duplican en otros CRUDs. No justifica un modulo de constantes compartido. |
| Mockup academico dedicado en `.cszv/mockups/`. | `fuera de alcance v1` (`backlog v2`) | No existe `sql_trace_mockup.*`. La pantalla real es la unica referencia visual. |
| Trace por nivel de log configurable (DEBUG / INFO). | `fuera de alcance v1` (`backlog v2`) | El modulo es opt-in. Apagado = sin overhead, prendido = captura todo. Un nivel intermedio no aporta a la defensa. |
| Captura de sentencias que no pasan por `mysql-connector-python` (por ejemplo, `SQLAlchemy` si se aniade en v2). | `fuera de alcance v1` (`backlog v2`) | La envoltura es especifica al driver actual. Migrar de driver requeriria reescribir el envoltorio. |

`backlog v2` se usa **unicamente** en esta seccion y en la columna de
cambios de la matriz del `spec/README.md`. Nunca aparece como
`Estado v1` en la [Seccion 7](#7-trazabilidad-rf).

---

## 7. Trazabilidad RF

Tabla que cruza cada tema del modulo con su origen analitico, su
soporte de datos y el codigo real, con un `Estado v1` por fila.

SQL Trace es **transversal** a todos los modulos CRUD: no aparece en
`docs/analysis` ni en `docs/database/erd.md` como entidad o
requerimiento formal, porque no es parte del modelo relacional. La
matriz de RF es por lo tanto mas corta que en otros specs y
predominan los estados `implementado v1` con la justificacion de
"herramienta didactica".

Los cuatro valores posibles para `Estado v1` son exactamente los
definidos en [`spec/README.md`](../README.md):

- `implementado v1`
- `parcial v1`
- `corregir UI/spec`
- `fuera de alcance v1`

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado v1 |
| --- | --- | --- | --- | --- |
| Modulo SQL Trace en si | (no mencionado) | (no mencionado; no es parte del ERD) | `database/sql_trace.py`; `web/app.py` (rutas + hooks); `web/templates/sql_trace.html`; inyeccion en `database/connection.py` | `implementado v1` (herramienta didactica transversal) |
| Captura de las queries que disparan los CRUD de RF-01..RF-09 | `requirements.md` RF-01..RF-09; `processes.md`; `procedures.md` | Tablas operativas referenciadas en el ERD | `TracedCursor` envuelve cada `execute()` / `executemany()`; el trace captura las queries que `customer_crud`, `sales_crud`, `purchase_crud`, `part_crud`, `customer_crud.delete_customer` (uso de `rowcount`), etc. emiten | `implementado v1` (cubierto por el envoltorio, no por un modulo propio) |
| `dashboard` (RF-09) y sus queries de metricas | `requirements.md` RF-09; `processes.md` (Reportes) | Tablas operativas referenciadas | `sales_crud.obtener_metricas_dashboard()` y similares; el trace captura las queries que estos disparan | `implementado v1` (el trace no implementa RF-09, solo lo hace visible para defenderlo) |
| Redaction de passwords en `summarize_params` | (no documentado) | (no aplica: es capa de aplicacion) | `summarize_params` en `sql_trace.py:58-69` | `implementado v1` |
| `print` a stdout con prefijo `[SQL TRACE]` | (no documentado) | (no aplica) | `TracedCursor.execute` y `executemany` en `sql_trace.py:186-191` y `sql_trace.py:209-214` | `implementado v1` |
| Anillo de 80 (`MAX_TRACE_ENTRIES`) | (no documentado) | (no aplica) | `deque(maxlen=80)` en `sql_trace.py:21` | `implementado v1` |
| `SQL_TRACE_ENABLED=0` documentado en `.env.example` | (no documentado) | (no aplica) | `.env.example` incluye la variable y documentación de uso | `implementado v1` |
| Persistencia / export del trace | (no requerida) | (no requerida: no toca el modelo) | No implementado (intencional) | `fuera de alcance v1` |
| Mockup academico para la UI del trace | (no aplica) | (no aplica) | No existe mockup en `.cszv/mockups/` para este modulo | `fuera de alcance v1` |
