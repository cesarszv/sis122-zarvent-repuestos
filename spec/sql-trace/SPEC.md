# SPEC — SQL Trace

El modulo **SQL Trace** es una herramienta didactica y de diagnostico en vivo
que envuelve los cursores de `mysql-connector-python` para registrar cada
`execute()` y `executemany()` sin tocar el codigo CRUD del negocio. Esta pensado
para defender el proyecto en clase, NO para alimentar tablas propias ni
persistir informacion.

## Objetivo del modulo

SQL Trace **NO es un modulo CRUD del negocio**. No crea tablas, no recibe
formularios y no expone endpoints de escritura contra la base de datos.

Su unico objetivo es servir como **herramienta de defensa y diagnostico en
vivo** dentro de la aplicacion Flask de Zarvent Repuestos. Concretamente:

- Mostrar en una pantalla web los ultimos `SELECT`, `INSERT`, `UPDATE` y
  `DELETE` que `mysql-connector-python` envia al servidor MySQL, con su
  `method` + `route` Flask, parametros resumidos, duracion y estado
  (`OK` / `ERROR`).
- Permitir durante la defensa explicar como cada caso de uso del negocio
  (RF-01 a RF-09) termina en sentencias SQL concretas, sin tener que abrir
  DataGrip ni los logs de MySQL.
- Aislar errores SQL en vivo (parametros mal enviados, constraints violados,
  consultas lentas) y verlos en pantalla con la ruta que los provoco.

El modulo **interviene de forma transversal**: no aparece en los `docs/analysis`
ni en el `docs/database/erd.md` como entidad propia. Existe solo como
`src/zarvent_repuestos/database/sql_trace.py` y se inyecta en
`src/zarvent_repuestos/database/connection.py` cuando la variable de entorno
`SQL_TRACE_ENABLED` esta prendida.

## Estado actual reverse-engineered

Esta seccion documenta lo que **hoy existe en el repositorio** (no lo que
deberia existir). Sirve como punto de partida antes de cualquier cambio.

### Rutas Flask

Definidas en `src/zarvent_repuestos/web/app.py`:

| Ruta | Metodo | Linea | Decoradores | Proposito |
| --- | --- | --- | --- | --- |
| `/sql-trace` | `GET` | `app.py:287` | `@login_required` | Renderiza `sql_trace.html` con el flag `trace_enabled`. |
| `/api/sql-trace` | `GET` | `app.py:298` | `@login_required` | Devuelve `{"entries": [...], "summary": {...}}` en JSON. |
| `/api/sql-trace/clear` | `POST` | `app.py:306` | `@login_required` | Llama a `clear_sql_trace_entries()` y responde `{"status": "ok"}`. |

Las tres rutas requieren login (`@login_required` en `app.py:69`), igual que
el resto de modulos privados. El banner amarillo solo aparece en la pantalla
HTML; las APIs JSON siempre devuelven datos cuando el trace esta encendido.

### Hooks de request

En `app.py:55-66` se conectan dos hooks que **solo corren si el trace esta
habilitado**:

- `before_request` -> `capture_sql_trace_request_context`:
  llama a `set_request_context(request.method, request.path)` y guarda los
  labels en `ContextVar`.
- `teardown_request` -> `release_sql_trace_request_context`:
  llama a `clear_request_context()` y restaura los labels a `"-"`.

Esto significa que cada entry nueva queda automaticamente etiquetada con el
`METHOD` y la `route` Flask que la origino (por ejemplo `GET /dashboard`).

### Modulo Python: `src/zarvent_repuestos/database/sql_trace.py`

Constantes y estado en memoria:

- `MAX_TRACE_ENTRIES = 80` (linea 14). Ring buffer de los ultimos 80
  statements.
- `SQL_TRACE_ENABLED = os.getenv("SQL_TRACE_ENABLED", "").lower() in {"1", "true", "yes", "on"}`
  (linea 15). Booleano resuelto **al momento de importar el modulo**; cambiar
  la variable en runtime no tiene efecto hasta reiniciar.
- `_TRACE_ENTRIES: deque[dict[str, Any]] = deque(maxlen=MAX_TRACE_ENTRIES)`
  (linea 21). Buffer FIFO de entradas.
- `_CURRENT_ROUTE: ContextVar[str]` y `_CURRENT_METHOD: ContextVar[str]`
  (lineas 22-23). ContextVar separadas con default `"-"`, una por Flask
  request concurrente.

API publica (funciones puras o helpers):

- `is_sql_trace_enabled()` -> `bool` (linea 26).
- `get_sql_trace_entries()` -> `list[dict]` (linea 31). Devuelve
  `list(reversed(_TRACE_ENTRIES))` para que la UI reciba el mas nuevo primero.
- `clear_sql_trace_entries()` -> `None` (linea 36). `deque.clear()`.
- `set_request_context(method, route)` y `clear_request_context()` (lineas 41
  y 47). Set / reset de los `ContextVar`.
- `compact_sql(statement)` (linea 53). Colapsa cualquier whitespace
  (`re.sub(r"\s+", " ", statement).strip()`).
- `summarize_params(statement, params)` (linea 58). Devuelve:
  - `"-"` si `params is None`.
  - `"[redacted password fields]"` si la palabra `password` aparece en el
    SQL (case-insensitive). Esto oculta el password del login.
  - `repr(params)` truncado a 180 caracteres si el resto.
- `operation_name(statement)` (linea 72). Devuelve la primera keyword
  (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, etc.) en mayusculas.
- `operation_concept(operation)` (linea 78). Mapea la keyword a una etiqueta
  academica corta en Latam Spanish: `SELECT -> "Consulta datos"`,
  `INSERT -> "Crea registros"`, `UPDATE -> "Modifica registros"`,
  `DELETE -> "Elimina registros"`, resto -> `"Ejecuta SQL"`.
- `extract_tables(statement)` (linea 89). Regex para `FROM`, `JOIN`, `INTO`,
  `UPDATE`. Devuelve la lista de tablas en orden, sin duplicados, en
  minusculas.
- `build_summary(entries)` (linea 107). Funcion **pura** (sin side effects)
  que devuelve `{"total", "errors", "operations", "tables"}`. `tables` es un
  dict con las 8 tablas mas frecuentes, ordenadas por conteo descendente.
- `build_trace_entry(...)` (linea 141). Construye el dict que se guarda en el
  deque. No toca estado global, solo lee los `ContextVar`.

Clases envoltorio:

- `TracedCursor` (linea 165). Recibe un cursor real de
  `mysql-connector-python` y envuelve `execute()` y `executemany()`. Mide
  duracion con `time.perf_counter()`, captura `status` (`OK` / `ERROR`) y el
  mensaje de error. En el `finally`:
  1. Hace `append` del entry al deque.
  2. Imprime por stdout una linea con prefijo `[SQL TRACE]` (importante: el
     trace sale **tambien en la consola del servidor**, no solo en la UI).
  Para `executemany` agrega el sufijo ` MANY` al campo `operation` para
  distinguirlo. `__getattr__` delega cualquier otro metodo al cursor real, asi
  `fetchone`, `fetchall`, `rowcount`, etc. funcionan sin reescribirse.
- `TracedConnection` (linea 220). Envoltorio delgado: solo sobreescribe
  `cursor()` para devolver `TracedCursor`. El resto se delega a la conexion
  real con `__getattr__`.

### Inyeccion en `connection.py`

En `src/zarvent_repuestos/database/connection.py:13-22`,
`get_database_connection()` decide el tipo de conexion que devuelve:

```python
conexion = mysql.connector.connect(**DB_CONFIG)
if is_sql_trace_enabled():
    return TracedConnection(conexion)
return conexion
```

Es decir: si `SQL_TRACE_ENABLED` esta apagado, **toda la infraestructura de
trace se bypasea** y la aplicacion usa cursores nativos. Por eso el modulo es
opt-in y no agrega overhead en produccion / demo normal.

### Template `sql_trace.html`

Estructura actual:

- Header con titulo "Consultas SQL en vivo", badge de estado (`En vivo` /
  `Pausado` / `Sin conexion`) y botones `Pausar` / `Limpiar`.
- Banner amarillo `{% if not trace_enabled %}` que aparece solo cuando
  `SQL_TRACE_ENABLED` esta apagado, recomendando arrancar con
  `SQL_TRACE_ENABLED=1`.
- Fila de **5 metricas en vivo**: `Consultas`, `Ultima`, `Promedio`, `Ruta`,
  `Tablas`.
- Aside lateral con 4 bloques: `Resumen` (total + errores + tablas mas
  usadas), `Operaciones` (barras horizontales SELECT/INSERT/UPDATE/DELETE),
  `Filtro` (botones `ALL`, `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `ERROR`),
  `Lectura para defensa` (una sola frase con la entry mas reciente).
- Lista de entries (`#trace-list`) con scroll vertical (`max-h-[68vh]`). Cada
  card muestra: hora, badge de operacion, badge `METHOD route`, badge de
  status, `<pre>` con el SQL, panel lateral con `Concepto` / `Tablas` /
  `Tiempo`, y los parametros en una franja inferior.

Logica JS inline (en `{% block extra_js %}`):

- `loadTrace()`: `fetch("/api/sql-trace")` cada 1 segundo (al final
  `setInterval(loadTrace, 1000)`). Llama a `renderTrace(cachedEntries)` y
  `renderSummary(summary)`. Si `paused === true`, sale sin hacer nada. Si
  falla el `fetch`, pone el badge en rojo `"Sin conexion"`.
- `pauseTrace` click: alterna `paused`, cambia el texto del boton entre
  `Pausar` / `Reanudar` y el badge entre `En vivo` (verde) / `Pausado`
  (ambar).
- `clearTrace` click: `POST /api/sql-trace/clear`, vacia `cachedEntries`, y
  re-renderiza con resumen en cero. Si no estaba pausado, vuelve a llamar a
  `loadTrace()` para refrescar.
- `renderTrace(entries)`: actualiza contadores, promedio de duracion, ultima
  ruta, ultimas tablas, conteo de visibles, barras de operaciones y la
  frase de defensa. Dibuja cada card con `escapeHtml` para evitar XSS.
- `renderSummary(summary)`: muestra/oculta `#trace-summary` segun haya datos y
  renderiza los chips de tablas con su conteo.
- Filtros: `data-filter="ALL|SELECT|INSERT|UPDATE|DELETE|ERROR"` en cada
  boton. `ALL` muestra todo, `ERROR` filtra por `status === "ERROR"`, los
  demas filtran por la primera keyword de `entry.operation`.

> **Mockup de diseno:** No existe un mockup dedicado en `.cszv/mockups` para
> este modulo. La pantalla real (`sql_trace.html`) es la unica referencia
> visual. Si en el futuro se quiere alinear la UI con un diseno
> academico/mockup, se debera crear primero el mockup como tarea separada y
> recien despues actualizar este SPEC.

## Contrato funcional

### Activacion

- Variable de entorno: `SQL_TRACE_ENABLED`.
- Valores validos (case-insensitive): `1`, `true`, `yes`, `on`. Cualquier
  otro valor (incluido vacio) desactiva el modulo.
- Se lee **una sola vez** al importar `sql_trace.py`. Cambiar la variable sin
  reiniciar Flask **no** prende/apaga el trace en runtime.
- Si esta desactivado:
  - `get_database_connection()` devuelve la conexion nativa de
    `mysql-connector-python`.
  - La pantalla `/sql-trace` renderiza un **banner amarillo** de aviso en
    lugar de un trace vacio silencioso. El resto de la UI sigue renderizando
    (botones y filtros visibles, pero las APIs devuelven datos vacios
    persistentes).

### Flujos del usuario

1. **Ver la pagina**
   - Ir a `/sql-trace` (requiere login).
   - Ver header con badge de estado, fila de 5 metricas (`Consultas`,
     `Ultima`, `Promedio`, `Ruta`, `Tablas`) y la lista de entries en vivo.
   - Ver panel lateral: `Resumen`, barras por operacion (`SELECT`, `INSERT`,
     `UPDATE`, `DELETE`), `Filtro`, `Lectura para defensa` con la entry mas
     reciente.
   - Cada entry nueva aparece arriba de la lista (`deque` con orden
     invertido). Auto-refresh cada 1 segundo via `fetch`.

2. **Pausar el auto-refresh**
   - Click en `Pausar`. El JS marca `paused = true` y deja de llamar a
     `/api/sql-trace`. Las entries **no se borran**, solo deja de refrescar
     la vista. El badge cambia a `Pausado` (ambar). El boton pasa a
     `Reanudar`.
   - Click en `Reanudar`: vuelve a hacer polling cada segundo.

3. **Limpiar el buffer**
   - Click en `Limpiar`. Hace `POST /api/sql-trace/clear`, lo que llama a
     `clear_sql_trace_entries()` (`deque.clear()`). La UI limpia
     `cachedEntries` y repinta contadores en cero. Si no esta pausado, hace
     un `loadTrace()` inmediato para mostrar la realidad post-clear.

4. **Filtrar por operacion**
   - Botones `ALL`, `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `ERROR`.
   - `ALL` -> sin filtro.
   - `ERROR` -> entries con `status === "ERROR"`.
   - Resto -> entries cuya primera keyword (`operationBase`) coincide.
   - El filtro solo afecta lo que se **muestra**; el `deque` siempre tiene
     los ultimos 80 reales.
   - El boton activo se pinta de negro; los demas quedan en blanco con borde
     gris.

5. **Defender el proyecto**
   - Con el trace prendido, navegar a `/dashboard`, `/inventory`, `/sales`,
     `/customers`, `/purchases`. Cada vista dispara una serie de `SELECT`
     que se ven llegar al panel.
   - Crear una venta o un cliente: aparecen `INSERT` sobre `customer`,
     `sales_order`, `sales_order_item`, `payment`, etc.
   - Provocar un error (por ejemplo, eliminar un cliente con ventas): se ve
     la entry con `status=ERROR` y el mensaje de MySQL.

## Contrato de datos

**SQL Trace NO persiste en base de datos.** Es 100% in-memory.

### Estructuras en memoria

- `_TRACE_ENTRIES: deque[dict[str, Any]]` con `maxlen=80` (variable
  `MAX_TRACE_ENTRIES`). FIFO: cuando se llena, las entries mas viejas se
  descartan automaticamente.
- `_CURRENT_ROUTE: ContextVar[str]` con default `"-"`.
- `_CURRENT_METHOD: ContextVar[str]` con default `"-"`.

### Forma de cada entry

`build_trace_entry(...)` produce este dict:

| Campo | Tipo | Origen |
| --- | --- | --- |
| `time` | `str` (`"HH:MM:SS"`) | `datetime.now().strftime("%H:%M:%S")` |
| `method` | `str` | `_CURRENT_METHOD.get()` |
| `route` | `str` | `_CURRENT_ROUTE.get()` |
| `operation` | `str` | `operation_name(operation)` (+`" MANY"` si es `executemany`) |
| `concept` | `str` | `operation_concept(operation)` (etiqueta academica Latam Spanish) |
| `tables` | `list[str]` | `extract_tables(operation)` (regex sobre el SQL) |
| `sql` | `str` | `compact_sql(operation)` (whitespace colapsado) |
| `params` | `str` | `summarize_params(operation, params)` (con redaction de password) |
| `duration_ms` | `float` | `(perf_counter delta) * 1000`, redondeado a 2 decimales |
| `status` | `"OK" \| "ERROR"` | Resultado del `execute` / `executemany` |
| `error` | `str` | `str(error)` solo si hubo excepcion; vacio si no |

### Tablas del modelo que apareceran en los traces

Como `TracedConnection` envuelve **cada** `cursor.execute()` y
`cursor.executemany()` que se ejecute, los traces pueden incluir
sentencias sobre **todas las tablas del modelo** definidas en
`docs/database/erd.md` y en `database/schema.sql`:

- `person`, `customer`
- `supplier`
- `part_category`, `part`, `vehicle_model`, `part_compatibility`,
  `inventory_stock`
- `sales_order`, `sales_order_item`, `payment`
- `purchase_order`, `purchase_order_item`
- `return_order`, `return_order_item`
- `users` (tabla operativa de autenticacion, no listada en `erd.md` pero
  presente en `database/schema.sql` y en el seed demo)

`extract_tables` se basa en regex sobre `FROM`, `JOIN`, `INTO`, `UPDATE`, asi
que si MySQL recibe SQL que referencie cualquier otra tabla, tambien
aparecera listada.

### Persistencia

- **No hay export a disco**, ni a archivo de log, ni a tabla.
- **No hay persistencia entre reinicios**: al levantar Flask de nuevo, el
  `deque` arranca vacio.
- **No hay paginacion historica**: solo se ve lo que esta en memoria
  (maximo 80 entries). Lo que se fue del ring buffer se pierde.
- El unico sink externo es el `print` a stdout con prefijo `[SQL TRACE]`,
  que sigue en pie aunque Flask no este corriendo (por ejemplo, en un script
  que importe `connection.py`).

## Trazabilidad SDD

SQL Trace es **transversal** a todos los modulos CRUD. No aparece en
`docs/analysis` ni en `docs/database/erd.md` como entidad o requerimiento
formal, porque no es parte del modelo relacional: no agrega tablas, no agrega
columnas, no toca los RF-01..RF-09 en si. Es una herramienta auxiliar para
**defenderlos mejor en vivo**.

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Modulo SQL Trace en si | No mencionado | No mencionado (no es parte del ERD) | `database/sql_trace.py`, `web/app.py` (rutas + hooks), `web/templates/sql_trace.html`, inyeccion en `database/connection.py` | implementado |
| RF-09 Reportes (ventas, pagos, stock bajo, compras pendientes, devoluciones) | Listado en `requirements.md` como RF-09 | Tablas operativas referenciadas (no es modulo SQL Trace) | CRUD en `sales_crud.obtener_metricas_dashboard()` y similares; el trace captura las queries que estos disparan | implementado (como **fuera del flujo CRUD principal**: el trace no implementa RF-09, solo lo hace visible para defenderlo) |
| Otras tablas (`person`, `customer`, `supplier`, `part`, `inventory_stock`, `sales_order*`, `payment`, `purchase_order*`, `return_order*`, `users`) | RF-01 a RF-08 | Diagrama completo en `erd.md` | Esquema en `database/schema.sql`; el trace las cubre via `TracedCursor` | implementado (cubierto por el envoltorio, no por un modulo propio) |
| Mockup academico para la UI del trace | No aplica | No aplica | **No existe** mockup en `.cszv/mockups/` para este modulo | faltante |
| Persistencia / export del trace | No requerida | No requerida (no toca el modelo) | No implementado (intencional, ver `Brechas y decisiones`) | fuera de alcance |
| Redaction de passwords en `summarize_params` | No documentado | No aplica (es capa de aplicacion) | `summarize_params` en `sql_trace.py:58-69` | implementado |
| `print` a stdout con prefijo `[SQL TRACE]` | No documentado | No aplica | `TracedCursor.execute` y `executemany` en `sql_trace.py:186-191` y `sql_trace.py:209-214` | implementado |

## Criterios de aceptacion

### Pruebas automatizadas

- Existe `tests/test_sql_trace.py` con casos unitarios para los helpers
  puros del modulo. Cubre, como minimo:
  - `extract_tables`: caso `FROM` + `JOIN` (sin duplicados, en orden) y caso
    `UPDATE`.
  - `summarize_params`: redaction cuando aparece `password` (case-sensitive
    e insensitive), redaction con `PASSWORD` mayusculas, repr corto cuando
    no hay password, `"-"` cuando `params is None`.
  - `compact_sql`: colapso de multiples espacios, saltos de linea y tabs a
    un solo espacio.
  - `operation_name`: `SELECT` y `INSERT` con whitespace inicial.
  - `build_summary`: conteo de total, errores y operaciones.
- Comando sugerido para correrlos (alineado con el resto del repo, no
  escrito en piedra):

  ```bash
  uv run python -m unittest tests.test_sql_trace
  ```

### Pruebas manuales

1. **Apagado por defecto**:
   - Levantar Flask sin la variable: `uv run python -m zarvent_repuestos.web.app`.
   - Ir a `/sql-trace` logueado. Debe verse el **banner amarillo**
     "SQL Trace esta desactivado. Inicia Flask con `SQL_TRACE_ENABLED=1`
     para registrar consultas." Las barras, los filtros y la lista se
     renderizan vacios, y el `GET /api/sql-trace` devuelve `{"entries": [],
     "summary": {...vacio...}}`.
2. **Prendido**:
   - Levantar con `SQL_TRACE_ENABLED=1 uv run python -m zarvent_repuestos.web.app`
     (o exportar la variable y arrancar igual).
   - Ir a `/sql-trace`. **No** debe verse el banner amarillo. Las metricas
     arrancan en cero.
3. **Captura de lecturas**:
   - Navegar a `/dashboard`. Deben aparecer entries `SELECT` sobre las
     tablas del dashboard, con la ruta `GET /dashboard` en el badge.
   - Navegar a `/inventory`. Aparecen entries `SELECT` y la lista crece.
4. **Captura de escrituras**:
   - Ir a `/sales` y registrar una venta. Aparecen `INSERT` sobre
     `sales_order`, `sales_order_item`, `payment`, `customer` (si se
     registro un cliente nuevo), ademas de `UPDATE` sobre
     `inventory_stock` para descontar stock.
5. **Captura de errores**:
   - Forzar un error conocido (por ejemplo, intentar eliminar un cliente
     con ventas). La entry aparece con `status: ERROR` y el mensaje de
     MySQL en el campo `error`.
6. **Redaction de password**:
   - Loguearse (`/`) con `admin` / `admin123`. El `POST /` dispara un
     `SELECT` (o `UPDATE`, segun el flujo de `authenticate_user`) sobre
     `users`. El campo `params` de esa entry debe ser
     `"[redacted password fields]"`, **no** debe verse el password en
     ningun momento de la UI ni en el stdout.
7. **Ver el trace tambien en consola**:
   - En la terminal donde corre Flask, durante cualquiera de los pasos
     anteriores, deben aparecer lineas con prefijo `[SQL TRACE]` por cada
     `execute()` / `executemany()`.
8. **Pausar y limpiar**:
   - Click en `Pausar`: la UI deja de actualizarse, el badge pasa a
     `Pausado` (ambar), el boton a `Reanudar`. La base de datos sigue
     funcionando normal; solo se congela la vista.
   - Click en `Reanudar`: el polling se restaura.
   - Click en `Limpiar`: contadores a cero, lista vacia. El `deque` queda
     vacio en el servidor.
9. **Filtros**:
   - Click en `SELECT`: solo se ven entries de tipo SELECT.
   - Click en `ERROR`: solo las que fallaron.
   - Click en `ALL`: vuelve a verse todo.
10. **Anillo de 80**:
    - Provocar mas de 80 statements rapidos (por ejemplo, recargar
      `/inventory` muchas veces). La lista mostrada no debe crecer mas
      alla de 80 entradas; las viejas se descartan en orden FIFO.

## Brechas y decisiones

Diferencias explícitas entre lo que un observador podria esperar y lo que
el codigo hace hoy:

- **El trace NO incluye el query del login con la password real**.
  `summarize_params` revisa si la palabra `password` aparece en el SQL
  (`statement.lower()`) y, si esta, devuelve `"[redacted password fields]"`
  sin importar el valor de `params`. Esto esta hecho a proposito: el
  endpoint de login es uno de los pocos lugares donde la app recibe
  passwords en texto claro, y la pantalla del trace es visible a cualquier
  usuario logueado. Es una decision defensiva por defecto.

- **El `deque` es de tamano fijo 80 (`MAX_TRACE_ENTRIES = 80`)**. No hay
  export a archivo, ni a tabla, ni a stdout persistente. La unica salida
  distinta al UI es la linea `[SQL TRACE]` por `execute()`. Si se
  reinicia Flask, se pierde todo.

- **No hay paginacion historica**. Solo se ve lo que esta actualmente en
  memoria. Lo que sale del anillo de 80 no es recuperable desde la UI. Si
  en la defensa se necesita "ir atras" mas alla de 80 statements, hay que
  recargar la pagina y volver a navegar (lo que vuelve a generar
  statements).

- **No hay persistencia entre reinicios**. El estado vive en
  `_TRACE_ENTRIES`, un `deque` en memoria del proceso Flask. No hay SQLite,
  no hay tabla MySQL auxiliar, no hay archivo JSON.

- **`connection.py` solo retorna `TracedConnection` cuando
  `SQL_TRACE_ENABLED` esta prendido**. Esto esta confirmado en
  `src/zarvent_repuestos/database/connection.py:20-22`:

  ```python
  if is_sql_trace_enabled():
      return TracedConnection(conexion)
  return conexion
  ```

  Si la variable esta apagada, los CRUD usan cursores nativos sin
  overhead.

- **El `print` a stdout con prefijo `[SQL TRACE]` es un canal paralelo a la
  UI**. No es ruido decorativo: es lo que permite ver el trace tambien en
  la terminal del servidor (y en archivos de log redirigidos) sin abrir
  `/sql-trace`. Vale la pena dejarlo documentado porque es la unica forma
  de auditar el trace cuando la UI no esta abierta.

- **`executemany` agrega el sufijo ` MANY` al campo `operation`**. En la
  UI aparece como `INSERT MANY`, `UPDATE MANY`, etc. Esto distingue un
  batch de statements de uno individual y permite que el filtro
  `data-filter="INSERT"` siga considerando el batch como `INSERT`.

- **Los `ContextVar` se setean en `before_request` y se limpian en
  `teardown_request`**, no en `after_request`. Esto cubre incluso requests
  que fallen con excepcion, evitando que una entry quede etiquetada con la
  ruta equivocada.

- **El modulo es transversal y queda fuera del flujo CRUD principal**. No
  aparece en `docs/analysis/requirements.md` ni en `docs/database/erd.md`,
  y no debe aparecer: no es una entidad del modelo de Zarvent, no es un
  requerimiento funcional, y meterlo ahi distorsionaria el ERD academico
  que se defiende en clase. La trazabilidad hacia los RF-01..RF-09 es
  indirecta: el trace captura las queries que esos RF disparan.

- **No existe mockup en `.cszv/mockups/` para este modulo**. La carpeta
  solo tiene mockups para `dashboard`, `inventory` y `sales`. La pantalla
  real `sql_trace.html` es la unica referencia visual. Si en algun
  momento se quiere alinear la UI con un diseno academico/mockup, primero
  se debe crear el mockup como tarea separada y recien despues actualizar
  este SPEC.
