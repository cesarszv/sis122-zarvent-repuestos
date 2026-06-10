# SPEC — Inventario

El modulo de Inventario es la pantalla `/inventory` de Zarvent Repuestos.
Permite buscar, filtrar, registrar, editar, activar y desactivar repuestos
del catalogo, y crear categorias, a partir de las tablas `part`,
`part_category` e `inventory_stock` de MySQL. La lista de stock bajo se
sirve desde la vista `vw_low_stock_parts`. Cubre parcialmente los
requerimientos `RF-02` y `RF-04` de
[`docs/analysis/requirements.md`](../../docs/analysis/requirements.md).

> Mockup de diseno: `spec/inventory/inventory_mockup.html` y
> `spec/inventory/inventory_mockup.png`. Pantalla real implementada:
> `src/zarvent_repuestos/web/templates/inventory.html`.

## 1. Estado actual (reverse-engineered)

### Rutas Flask

- `src/zarvent_repuestos/web/app.py:121` define la ruta unica
  `/inventory`, con `methods=["GET", "POST"]` y decorada con
  `@login_required`. GET lista y filtra; POST registra un repuesto nuevo.

Las rutas para editar un repuesto (`/inventory/<id>/edit`) y para crear categorías (`/inventory/categories`) están implementadas e integradas en la UI.

### Templates

`src/zarvent_repuestos/web/templates/inventory.html` (190 lineas):

- Encabezado con titulo "Catalogo de Repuestos" y boton "Anadir Producto"
  que abre un modal (`#add-product-modal`).
- Formulario GET de filtros: input `search`, select `category_id`, select
  `brand`. Los `select` se autoenvian con `onchange="this.form.submit()"`.
  El boton "Limpiar" aparece solo si hay algun filtro aplicado.
- Tabla de resultados con columnas: codigo interno, codigo OEM, nombre,
  marca, categoria, precio de venta, stock y ubicacion. Las filas con
  `quantity_on_hand <= reorder_level` se pintan en rojo
  (`text-zarvent-red`); el resto en verde (`text-green-700`).
- Modal `#add-product-modal` con el formulario POST.

### Funciones CRUD usadas

Llamadas desde `app.py:inventory()`:

- `part_crud.crear_producto(part, initial_stock, location)` en POST
  (`src/zarvent_repuestos/crud/part_crud.py:56`).
- `part_crud.listar_productos(search, category_id, brand)` en GET
  (`part_crud.py:101`).
- `part_crud.listar_categorias()` en GET (`part_crud.py:33`).
- `part_crud.obtener_marcas()` en GET (`part_crud.py:147`).

Las funciones `part_crud.crear_categoria`, `part_crud.get_part`, `part_crud.update_part`, `part_crud.deactivate_part` y `part_crud.reactivate_part` están completamente implementadas y conectadas a sus respectivas rutas en Flask.

### Modelos

- `src/zarvent_repuestos/models/part.py:9` define `PartCategory` (PK
  `part_category_id`, `name`, `description`).
- `src/zarvent_repuestos/models/part.py:19` define `Part` con campos
  `part_id`, `part_category_id`, `internal_code`, `oem_code`, `name`,
  `brand`, `unit` (default `pcs`), `sale_price`, `purchase_cost`,
  `warranty_days` (default `0`), `status` (default `active`) y `category`
  (relacion).

### Tablas relacionadas (esquema real en `init_db.py`)

- `part_category` (`part_category_id` PK, `name` UNIQUE, `description`).
- `part` (`part_id` PK, `part_category_id` FK a `part_category` con
  `ON DELETE RESTRICT`, `internal_code` UNIQUE, `oem_code`, `name`,
  `brand`, `unit`, `sale_price`, `purchase_cost`, `warranty_days`,
  `status`).
- `inventory_stock` (`inventory_stock_id` PK, `part_id` UNIQUE FK a `part`
  con `ON DELETE CASCADE`, `location_name`, `quantity_on_hand` default `0`,
  `reorder_level` default `10`).

### Comportamiento visible

- GET con `search`, `category_id` o `brand` aplica filtros en
  `listar_productos`. Si los tres vienen vacios, lista todo.
- POST siempre hace `redirect(url_for("inventory"))`. El resultado del
  POST llega como `flash` en el GET siguiente.
- El stock se descuenta y se repone desde otros modulos: Ventas descuenta
  en `sales_crud.crear_orden_venta` y Compras suma en
  `purchase_crud.receive_purchase_order`. Este modulo no altera el stock
  por si mismo, salvo en la creacion inicial.
- `listar_productos` no distingue entre repuestos activos e inactivos:
  devuelve todas las filas, sin importar `part.status`. La columna
  `status` no se proyecta en la grilla.

## 2. Contrato objetivo v1

### Flujos permitidos

1. **Listar catalogo (GET sin filtros, `?status=active` por defecto).**
   Muestra los repuestos con `status='active'` ordenados por
   `internal_code`.
2. **Buscar por texto (GET `?search=...`).** Coincidencia parcial en
   `internal_code`, `oem_code`, `name` o `brand`.
3. **Filtrar por categoria (GET `?category_id=...`).** Solo repuestos de
   esa categoria. El combo se autoenvia al cambiar.
4. **Filtrar por marca (GET `?brand=...`).** Solo repuestos de esa marca.
5. **Filtrar por estado (GET `?status=active|inactive|all`).** Default
   `active`. `all` muestra todos.
6. **Combinar filtros.** Los parametros se aplican con `AND`.
7. **Limpiar filtros.** El boton "Limpiar" lleva a `/inventory` sin query
   string.
8. **Registrar repuesto nuevo (POST `/inventory`).** Abre el modal,
   completa el formulario y crea el repuesto con su stock inicial en una
   sola transaccion.
9. **Editar repuesto (POST `/inventory/<part_id>/edit`).** Carga el
   repuesto, actualiza campos editables, persiste.
10. **Desactivar repuesto (POST `/inventory/<part_id>/deactivate`).**
    Cambia `part.status` a `'inactive'`. El repuesto deja de aparecer en
    la lista por defecto.
11. **Reactivar repuesto (POST `/inventory/<part_id>/reactivate`).**
    Cambia `part.status` a `'active'`.
12. **Crear categoria (POST `/inventory/categories`).** Inserta una
    categoria nueva en `part_category`. Disponible inmediatamente en los
    combos.

### Campos del formulario POST (`/inventory`)

| Campo en form | Destino en BD | Validacion visible en HTML |
| --- | --- | --- |
| `name` | `part.name` | `required` |
| `internal_code` | `part.internal_code` | `required` |
| `oem_code` | `part.oem_code` (NULL si vacio) | opcional |
| `brand` | `part.brand` (NULL si vacio) | `required` |
| `part_category_id` | `part.part_category_id` | `required`, `<select>` |
| `unit` | `part.unit` | `required`, default `pcs` |
| `sale_price` | `part.sale_price` | `required`, `min="0.01"`, `step="0.01"` |
| `purchase_cost` | `part.purchase_cost` | `required`, `min="0.01"`, `step="0.01"` |
| `warranty_days` | `part.warranty_days` | `required`, `min="0"`, default `0` |
| `status` | `part.status` | `required`, `select active/inactive`, default `active` |
| `initial_stock` | `inventory_stock.quantity_on_hand` | `required`, `min="0"` |
| `reorder_level` | `inventory_stock.reorder_level` | `required`, `min="0"`, default `10` |
| `location_name` | `inventory_stock.location_name` | `required` |

### Validaciones del lado servidor

- Conversion a tipos: `int(part_category_id)`, `float(sale_price)`,
  `float(purchase_cost)`, `int(initial_stock)`, `int(reorder_level)`,
  `int(warranty_days)`. Si MySQL rechaza los valores, se captura como
  excepcion y se muestra flash de error.
- `internal_code` duplicado: lo bloquea la restriccion `UNIQUE` de la
  tabla `part`. El CRUD devuelve `False` y la ruta muestra flash de
  error.
- `part_category_id` debe existir: lo valida la FK a `part_category`. Si
  no existe, la insercion falla.
- `status` aceptado: `active` o `inactive` (la ruta debe validar el valor
  antes de persistir).

### Mensajes flash

| Caso | Texto |
| --- | --- |
| Exito al crear | `flash("Producto '<name>' creado con exito.", "success")` |
| Falla del CRUD al crear | `flash("Error al registrar el producto en la base de datos.", "error")` |
| Excepcion tecnica | `flash("Error tecnico: <e>", "error")` |
| Exito al editar | `flash("Producto '<name>' actualizado con exito.", "success")` |
| Falla al editar | `flash("No se pudo actualizar el producto.", "error")` |
| Exito al desactivar | `flash("Producto '<name>' desactivado.", "success")` |
| Exito al reactivar | `flash("Producto '<name>' reactivado.", "success")` |
| Exito al crear categoria | `flash("Categoria '<name>' creada con exito.", "success")` |
| Falla al crear categoria | `flash("No se pudo crear la categoria.", "error")` |

En todos los casos, el POST termina en `redirect(url_for("inventory"))` (o
la ruta apropiada), asi que los mensajes se ven en el siguiente GET.

### Estados y efectos esperados

- Al registrar un repuesto: existe una fila nueva en `part` y una fila
  nueva en `inventory_stock` con el mismo `part_id`, `location_name`,
  `quantity_on_hand = initial_stock` y `reorder_level = reorder_level`
  (proveniente del form, no hardcoded).
- Al editar: se actualizan los campos permitidos en `part` (no se toca
  `inventory_stock` desde esta ruta).
- Al desactivar: `part.status = 'inactive'`. El repuesto desaparece de la
  lista por defecto y aparece en `?status=inactive` o `?status=all`.
- Al reactivar: `part.status = 'active'`.
- Al crear una categoria: existe una fila nueva en `part_category`.
- Al filtrar por `status=active`: la tabla refleja el resultado de
  `listar_productos(...)` con `AND p.status = 'active'`.
- El stock visible en la tabla se mantiene coherente con
  `inventory_stock.quantity_on_hand` aunque cambie desde Ventas o
  Compras.
- Las filas con `quantity_on_hand <= reorder_level` se pintan en rojo. La
  comparacion se hace en el template sobre `part.quantity_on_hand` y
  `part.reorder_level` (los alias `quantity_on_hand` y `reorder_level`
  vienen del `LEFT JOIN` con `inventory_stock` en `listar_productos`,
  `part_crud.py:101-144`).

## 3. Cambios requeridos v1

### Cambios en `part_crud.py`

| # | Cambio | Detalle |
| --- | --- | --- |
| 1 | Anadir `get_part(part_id) -> Optional[Dict]` | Devuelve una fila de `part` (JOIN `part_category`) por `part_id`, o `None`. |
| 2 | Anadir `update_part(part_id, **campos) -> bool` | Hace `UPDATE part SET ...` con los campos editables. No toca `inventory_stock`. Devuelve `True`/`False`. |
| 3 | Anadir `deactivate_part(part_id) -> bool` | `UPDATE part SET status = 'inactive' WHERE part_id = %s`. |
| 4 | Anadir `reactivate_part(part_id) -> bool` | `UPDATE part SET status = 'active' WHERE part_id = %s`. |
| 5 | Modificar `listar_productos(...)` para aceptar `status: str = 'active'` | Default `'active'` aplica `AND p.status = 'active'`. `'inactive'` aplica `AND p.status = 'inactive'`. `'all'` no filtra por `status`. |
| 6 | Modificar `crear_producto(...)` para aceptar `reorder_level` del form | Reemplazar el `10` hardcoded de `part_crud.py:88` por el parametro. |
| 7 | Conectar `crear_categoria(...)` a Flask | La funcion ya existe; falta la ruta y la vista. |

### Cambios en `app.py`

| # | Cambio | Ruta | Detalle |
| --- | --- | --- | --- |
| 8 | Anadir ruta POST edicion | `POST /inventory/<int:part_id>/edit` | Lee los campos del form, llama a `part_crud.update_part`, hace redirect a `/inventory`. |
| 9 | Anadir ruta POST desactivar | `POST /inventory/<int:part_id>/deactivate` | Llama a `part_crud.deactivate_part`, hace redirect. |
| 10 | Anadir ruta POST reactivar | `POST /inventory/<int:part_id>/reactivate` | Llama a `part_crud.reactivate_part`, hace redirect. |
| 11 | Anadir ruta POST crear categoria | `POST /inventory/categories` | Recibe `name` y `description`, llama a `part_crud.crear_categoria`. |
| 12 | Anadir lectura del parametro `?status=...` en GET | `GET /inventory` | Default `active`. Pasa a `listar_productos(status=...)`. |
| 13 | Pasar `reorder_level`, `warranty_days`, `unit` y `status` al handler POST de `/inventory` | `POST /inventory` | Hoy se ignoran o se hardcodean. |

### Cambios en `templates/inventory.html`

| # | Cambio | Detalle |
| --- | --- | --- |
| 14 | Anadir campos al modal "Anadir Producto" | `unit` (text, default `pcs`), `warranty_days` (number, min 0, default 0), `reorder_level` (number, min 0, default 10), `status` (select `active`/`inactive`, default `active`). |
| 15 | Anadir columna "Estado" a la tabla | Badge verde `Activo` o gris `Inactivo` segun `part.status`. |
| 16 | Anadir columna "Acciones" por fila | Iconos para Editar, Desactivar/Activar. El form de cada accion envia `POST` a la ruta correspondiente. |
| 17 | Anadir combo `Estado` al formulario de filtros | Opciones `Activos` (default), `Inactivos`, `Todos`. Autoenvia al cambiar. |
| 18 | Anadir boton "Nueva Categoria" junto a "Anadir Producto" | Abre un mini modal con `name` (required) y `description` (opcional). |
| 19 | Anadir vista de edicion inline o panel | Cuando el handler de edicion devuelve el form prellenado, se renderiza sobre la lista (mismo patron que `customers.html` con `{% if editing %}`). |

### Cambios en la base de datos

| # | Cambio | Archivo | Afecta spec vecino |
| --- | --- | --- | --- |
| 20 | Crear vista `vw_low_stock_parts` | nuevo en `src/zarvent_repuestos/database/init_db.py` (o `database/schema.sql`) | [dashboard/SPEC.md](../dashboard/SPEC.md) (tambien la consume) |
| 21 | Reemplazar el coloreo ad-hoc del template por una consulta a `vw_low_stock_parts` para mostrar un badge "Stock bajo" en la lista | `templates/inventory.html` | [dashboard/SPEC.md](../dashboard/SPEC.md) |

### RF fuera de alcance

- **RF-03 Compatibilidad vehicular**: las tablas `vehicle_model` y
  `part_compatibility` no se crean. No hay CRUD, ni ruta, ni campos en el
  form. Marcado como `fuera de alcance v1`, `backlog v2` (la
  documentacion academica de `processes.md` lo menciona, pero el alcance
  del modulo no lo cubre).

## 4. Aceptacion automatizada

| Test | Cubre | Detalle |
| --- | --- | --- |
| `tests/unit/test_part_crud.py` | Métricas y CRUD | Cobertura unitaria para las funciones de edición y borrado lógico (`update_part`, `deactivate_part`, `reactivate_part`), así como la lógica de consulta de stock bajo con fallback. |

### Cobertura de Tests

Las adiciones v1 están testeadas en `tests/unit/test_part_crud.py` y los flujos de integración en `tests/integration/test_integration_flows.py`.

## 5. Aceptacion manual en navegador / DataGrip

### Pasos en navegador (estudiante junior)

1. Login con `admin / admin123`. Ir a `/inventory`. Ver tabla con los
   repuestos demo del seed.
2. Verificar que la columna "Estado" muestra badge `Activo` para todos.
3. Cambiar el filtro de estado a `Inactivos`. La tabla debe quedar
   vacia. Cambiar a `Todos`. Deben verse todos los repuestos.
4. Buscar por texto en la barra superior. Verificar que filtra por
   `internal_code`, `oem_code`, `name` o `brand`.
5. Filtrar por categoria. Verificar que solo aparecen los repuestos de
   esa categoria.
6. Filtrar por marca. Verificar que solo aparecen los repuestos de esa
   marca.
7. Abrir el modal "Anadir Producto". Llenar todos los campos
   (incluyendo `unit`, `warranty_days`, `reorder_level`, `status`).
   Guardar. Verificar que aparece en la tabla como `Activo`.
8. Click en el icono "Editar" de un repuesto. Modificar `sale_price`.
   Guardar. Verificar que el cambio se refleja en la tabla.
9. Click en el icono "Desactivar" de un repuesto. Verificar que
   desaparece de la lista por defecto y aparece en
   `?status=inactive`.
10. Click en el icono "Reactivar" del mismo repuesto. Verificar que
    vuelve a aparecer en la lista por defecto.
11. Click en "Nueva Categoria". Llenar `name`. Guardar. Verificar que la
    nueva categoria aparece en el combo de filtro y en el modal de
    creacion.
12. Intentar crear dos categorias con el mismo `name`. La segunda debe
    fallar por la `UNIQUE` de `part_category.name` y mostrar flash de
    error.
13. Intentar crear un repuesto con un `internal_code` ya existente. La
    base rechaza el `INSERT`, la ruta muestra flash de error, y no queda
    fila huera en `inventory_stock` (rollback de la transaccion).
14. Visitar `/inventory` sin sesion. Debe redirigir a `/` con flash de
    error.
15. Visitar `/inventory` con un repuesto con `quantity_on_hand <=
    reorder_level`. La fila debe pintarse en rojo y la lista lateral de
    stock bajo del dashboard debe incluirlo.

### Pasos en DataGrip (cliente SQL)

1. Conectarse a `sis122_zarvent_repuestos`.
2. Verificar que la vista existe:
   `SHOW CREATE VIEW vw_low_stock_parts;`
3. Consultar la vista:
   `SELECT * FROM vw_low_stock_parts ORDER BY quantity_on_hand ASC LIMIT 5;`
   El resultado debe coincidir con la lista lateral del dashboard.
4. Verificar el contenido de `part`:
   `SELECT part_id, internal_code, name, status, unit, warranty_days
   FROM part ORDER BY part_id;`
   Las columnas `unit`, `warranty_days` y `status` deben estar pobladas
   para los repuestos creados desde la UI.
5. Verificar el contenido de `inventory_stock`:
   `SELECT part_id, location_name, quantity_on_hand, reorder_level
   FROM inventory_stock;`
   `reorder_level` debe respetar el valor enviado desde el form (no ser
   siempre `10`).
6. Verificar la unicidad:
   `SHOW CREATE TABLE part;` debe incluir
   `UNIQUE KEY internal_code (internal_code)`.
7. `SHOW CREATE TABLE part_category;` debe incluir
   `UNIQUE KEY name (name)`.
8. `SHOW CREATE TABLE inventory_stock;` debe incluir
   `UNIQUE KEY part_id (part_id)`.
9. Probar soft-delete via SQL:
   `UPDATE part SET status = 'inactive' WHERE part_id = 1;`
   `SELECT * FROM part WHERE part_id = 1;` debe mostrar `status =
   'inactive'`.

## 6. Decisiones fuera de alcance

1. **RF-03 Compatibilidad vehicular** (`fuera de alcance v1`, `backlog v2`):
   las tablas `vehicle_model` y `part_compatibility` no se crean. El form
   no captura `make`, `model`, `year`, `engine_code`. La busqueda no
   acepta filtro por vehiculo. Es la principal diferencia entre el
   analisis academico y el modulo actual.
2. **Stock multi-ubicacion**: el ERD admite 1 a N entre `PART` e
   `INVENTORY_STOCK`, pero la columna `inventory_stock.part_id` es
   `UNIQUE NOT NULL`. El modulo sigue tratando stock como 1 a 1.
   `parcial v1`.
3. **Paginacion**: `listar_productos` no usa `LIMIT/OFFSET` y la tabla
   no muestra controles de paginacion. Aceptable para el tamano del
   dataset academico. `fuera de alcance v1`.
4. **Auditoria de cambios**: no hay `part_audit` ni triggers. Cada
   `UPDATE` sobrescribe el valor anterior sin dejar rastro.
   `fuera de alcance v1`.
5. **Validacion de imagen / fotografia del repuesto**: el modulo no
   maneja archivos. `fuera de alcance v1`.
6. **Borrado fisico de repuestos**: no se permite desde la UI. Solo se
   puede desactivar. Si se necesita borrar fisicamente, hay que hacerlo
   directo en SQL. Razon: `sales_order_item` y `purchase_order_item`
   referencian a `part` con `ON DELETE RESTRICT`, asi que un borrado
   fisico requiere borrar antes las dependencias. `fuera de alcance v1`.
7. **Auto-generacion de codigo interno**: el `internal_code` se ingresa a
   mano. No hay secuencia automatica. `fuera de alcance v1`.

## 7. Trazabilidad RF

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado v1 |
| --- | --- | --- | --- | --- |
| RF-02 catalogo de repuestos (alta y listado) | [`requirements.md`](../../docs/analysis/requirements.md) RF-02; `processes.md` gestion catalogo | `erd.md` `PART`, `PART_CATEGORY` | `app.py:inventory` GET+POST, `part_crud.crear_producto`, `listar_productos` | implementado v1 |
| RF-02 administracion del catalogo (editar, activar, desactivar) | `processes.md` "Revisa que la informacion este actualizada" | `erd.md` `PART` actualizable | Rutas GET/POST y funciones CRUD implementadas | implementado v1 |
| RF-02 creacion de categorias desde la UI | `processes.md` gestion catalogo | `erd.md` `PART_CATEGORY` | Ruta `/inventory/categories` y modal implementados | implementado v1 |
| RF-02 campos `warranty_days`, `unit`, `status` | `requirements.md` RF-02 los pide explicitamente | `erd.md` `PART.warranty_days`, `PART.unit`, `PART.status` | Campos expuestos en formularios y tablas de la UI | implementado v1 |
| RF-04 stock inicial al crear repuesto | `requirements.md` RF-04; `processes.md` control inventario | `erd.md` `INVENTORY_STOCK` | `crear_producto` inserta en `inventory_stock` | implementado v1 |
| RF-04 umbral de reorden configurable | `processes.md` "Reporta productos con stock bajo a compras" | `db_explanation.md` `reorder_level` | Leído desde el formulario e insertado en la base de datos | implementado v1 |
| RF-04 stock bajo via vista | derivado de RF-04 y RF-09 | nueva vista `vw_low_stock_parts` | Vista `vw_low_stock_parts` creada y consumida | implementado v1 |
| RF-04 alertas visuales de stock bajo | `processes.md` paso 5 control inventario | `inventory_stock.quantity_on_hand` <= `reorder_level` | `inventory.html` pinta en rojo | implementado v1 |
| RF-02 estado del repuesto (`active`/`inactive`) | `requirements.md` RF-02 lo pide | `erd.md` `PART.status` | Estado expuesto y filtrable en la UI | implementado v1 |
| RF-03 compatibilidad vehicular | `requirements.md` RF-03; `processes.md` fila compatibilidad | `erd.md` `VEHICLE_MODEL`, `PART_COMPATIBILITY` | Tablas no creadas; no hay CRUD, ni ruta, ni form | fuera de alcance v1 |
| Busqueda por texto, categoria, marca | `procedures.md` busqueda de repuesto | `db_explanation.md` `internal_code`, `oem_code`, `brand`, `name` | `listar_productos` con `LIKE` y filtros | implementado v1 |
| Edicion de repuestos | `processes.md` revisa informacion | `erd.md` `PART` actualizable | Ruta `/inventory/<id>/edit` y función `update_part` implementadas | implementado v1 |
| Eliminacion fisica de repuestos | derivado de `ON DELETE RESTRICT` | `erd.md` `ON DELETE RESTRICT` desde `sales_order_item`, `purchase_order_item` | NO se permite desde la UI (cambio v1: solo desactivar) | fuera de alcance v1 |
| Paginacion del listado | — | — | NO implementado | fuera de alcance v1 |
