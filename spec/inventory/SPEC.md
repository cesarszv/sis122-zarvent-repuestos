# SPEC — Inventario

Resumen ejecutivo: el modulo de Inventario es la pantalla `/inventory` de
Zarvent Repuestos. Permite buscar, filtrar y registrar repuestos en el
catalogo a partir de las tablas `part`, `part_category` e `inventory_stock`
de MySQL, y queda alineado parcialmente con el ERD academico descrito en
`docs/database/erd.md`.

> Mockup de diseno: `spec/inventory/inventory_mockup.html` y
> `spec/inventory/inventory_mockup.png`. Pantalla real implementada:
> `src/zarvent_repuestos/web/templates/inventory.html`.

## Objetivo del modulo

El modulo de Inventario resuelve un problema operativo basico de Zarvent
Repuestos: hoy el negocio anota repuestos, precios y stock en papel, Excel
y WhatsApp. Eso produce piezas escritas de varias formas, precios
desactualizados y stock fantasma.

Este modulo centraliza tres cosas:

1. El **catalogo de repuestos** (codigo interno, codigo OEM, nombre, marca,
   categoria, precio de venta, costo de compra, garantia, estado).
2. La **primera linea de stock** por repuesto y ubicacion fisica, con un
   umbral minimo de reorden.
3. La **busqueda y filtrado** de repuestos por texto, categoria y marca,
   para que Ventas pueda cotizar rapido.

Con eso, Ventas, Almacen y Compras comparten la misma fuente de verdad
antes de vender, reponer o devolver.

## Estado actual reverse-engineered

### Rutas Flask

- `src/zarvent_repuestos/web/app.py:121` define la ruta unica
  `/inventory`, con `methods=["GET", "POST"]` y decorada con
  `@login_required`. GET lista y filtra; POST registra un repuesto
  nuevo.

No existen rutas separadas para editar, eliminar, ver detalle de un
repuesto, ni para crear categorias.

### Templates

- `src/zarvent_repuestos/web/templates/inventory.html`:
  - Encabezado con titulo "Catalogo de Repuestos" y boton "Anadir
    Producto" que abre un modal.
  - Formulario GET de filtros: input de busqueda libre (`search`),
    select de categoria (`category_id`) y select de marca (`brand`).
    Los select filtran en cliente y se autoenvian con
    `onchange="this.form.submit()"`.
  - Boton "Limpiar" visible solo si hay algun filtro aplicado.
  - Tabla de resultados con columnas: codigo interno, codigo OEM,
    nombre, marca, categoria, precio de venta, stock y ubicacion.
    Resalta en rojo las filas con `quantity_on_hand <= reorder_level`.
  - Modal `#add-product-modal` con el formulario POST.

### Funciones CRUD usadas

Llamadas desde `app.py:inventory()`:

- `part_crud.crear_producto(part, initial_stock, location)` en POST
  (`src/zarvent_repuestos/crud/part_crud.py:56`).
- `part_crud.listar_productos(search, category_id, brand)` en GET
  (`src/zarvent_repuestos/crud/part_crud.py:101`).
- `part_crud.listar_categorias()` en GET
  (`src/zarvent_repuestos/crud/part_crud.py:33`).
- `part_crud.obtener_marcas()` en GET
  (`src/zarvent_repuestos/crud/part_crud.py:147`).

Funciones definidas pero no conectadas a ninguna ruta Flask:

- `part_crud.crear_categoria(name, description)`
  (`src/zarvent_repuestos/crud/part_crud.py:16`). Existe el helper,
  pero no hay UI ni endpoint que la invoque.

### Modelos

- `src/zarvent_repuestos/models/part.py:9` define `PartCategory` (PK
  `part_category_id`, `name`, `description`).
- `src/zarvent_repuestos/models/part.py:19` define `Part` con campos
  `part_id`, `part_category_id`, `internal_code`, `oem_code`, `name`,
  `brand`, `unit` (default `pcs`), `sale_price`, `purchase_cost`,
  `warranty_days` (default 0), `status` (default `active`) y
  `category` (relacion).

### Tablas relacionadas (esquema real)

Creadas en `src/zarvent_repuestos/database/init_db.py`:

- `part_category` (`part_category_id` PK, `name` UNIQUE, `description`).
- `part` (`part_id` PK, `part_category_id` FK a `part_category` con
  `ON DELETE RESTRICT`, `internal_code` UNIQUE, `oem_code`, `name`,
  `brand`, `unit`, `sale_price`, `purchase_cost`, `warranty_days`,
  `status`).
- `inventory_stock` (`inventory_stock_id` PK, `part_id` UNIQUE FK a
  `part` con `ON DELETE CASCADE`, `location_name`, `quantity_on_hand`
  default 0, `reorder_level` default 10).

### Comportamiento visible

- GET con `search`, `category_id` o `brand` aplica filtros en
  `listar_productos`. Si los tres vienen vacios, lista todo.
- POST siempre hace `redirect(url_for("inventory"))`. El resultado del
  POST no se ve en la misma peticion: llega como `flash` en el GET
  siguiente.
- En el template, las filas con `quantity_on_hand <= reorder_level` se
  pintan en rojo (`text-zarvent-red`). El resto en verde
  (`text-green-700`).
- El stock se descuenta y se repone desde otros modulos: Ventas
  descuenta en `sales_crud.crear_orden_venta` y Compras suma en
  `purchase_crud.receive_purchase_order`. Este modulo no altera el
  stock por si mismo, salvo en la creacion inicial.

## Contrato funcional

### Flujos permitidos

1. **Listar catalogo (GET sin filtros).** Muestra todos los repuestos
   ordenados por `internal_code` con su categoria, marca, precio,
   stock y ubicacion.
2. **Buscar por texto (GET `?search=...`).** Filtra por coincidencia
   parcial en `internal_code`, `oem_code`, `name` o `brand`.
3. **Filtrar por categoria (GET `?category_id=...`).** Muestra solo
   repuestos de esa categoria. El combo se autoenvia al cambiar.
4. **Filtrar por marca (GET `?brand=...`).** Muestra solo repuestos de
   esa marca. El combo se autoenvia al cambiar.
5. **Combinar filtros.** Los tres parametros se aplican con `AND`.
6. **Limpiar filtros.** El boton "Limpiar" lleva a `/inventory` sin
   query string.
7. **Registrar repuesto nuevo (POST).** Abre el modal, completa el
   formulario y crea el repuesto con su stock inicial en una sola
   transaccion.

### Campos del formulario POST

| Campo en form | Destino en BD | Validacion visible en HTML |
| --- | --- | --- |
| `name` | `part.name` | `required`, texto libre |
| `internal_code` | `part.internal_code` | `required`, texto libre |
| `oem_code` | `part.oem_code` (NULL si vacio) | opcional |
| `brand` | `part.brand` (NULL si vacio) | `required` |
| `part_category_id` | `part.part_category_id` | `required`, `<select>` |
| `sale_price` | `part.sale_price` | `required`, `min="0.01"`, `step="0.01"` |
| `purchase_cost` | `part.purchase_cost` | `required`, `min="0.01"`, `step="0.01"` |
| `initial_stock` | `inventory_stock.quantity_on_hand` | `required`, `min="0"` |
| `location_name` | `inventory_stock.location_name` | `required`, default `"Aisle 1"` si se envia vacio en el server |

Campos del modelo que el form **no expone**:

- `unit`: se guarda con el default del modelo (`'pcs'`).
- `warranty_days`: se guarda con el default del modelo (`0`).
- `status`: el handler de la ruta lo fuerza a `"active"`.

### Validaciones del lado servidor

- Conversion a tipos: `int(part_category_id)`, `float(sale_price)`,
  `float(purchase_cost)`, `int(initial_stock)`. Si MySQL rechaza los
  valores (por ejemplo, `sale_price` negativo) se captura como
  excepcion y se muestra flash de error.
- Codigo interno duplicado: lo bloquea la restriccion `UNIQUE` de la
  tabla `part`. El CRUD devuelve `False` y la ruta muestra flash de
  error.
- `reorder_level` no se recibe del form: queda fijado en `10` por el
  CRUD.
- `part_category_id` debe existir: lo valida la FK a
  `part_category`. Si no existe, la insercion falla.

### Mensajes flash

- Exito: `flash(f"Producto '{name}' creado con éxito.", "success")`.
- Falla del CRUD: `flash("Error al registrar el producto en la base
  de datos.", "error")`.
- Excepcion tecnica: `flash(f"Error técnico: {e}", "error")`.

En todos los casos, el POST termina en
`redirect(url_for("inventory"))`, asi que los mensajes se ven en el
siguiente GET.

### Estados y efectos esperados

- Al registrar un repuesto: existe una fila nueva en `part` y una fila
  nueva en `inventory_stock` con el mismo `part_id`, `location_name`,
  `quantity_on_hand = initial_stock` y `reorder_level = 10`.
- Al filtrar: la tabla refleja exactamente el resultado del `SELECT`
  con `LIKE` y `WHERE` aplicados.
- El stock visible en la tabla se mantiene coherente con
  `inventory_stock.quantity_on_hand` aunque cambie desde Ventas o
  Compras, porque cada GET relee la base.

## Contrato de datos

### Tablas involucradas

| Tabla | Rol en el modulo | Origen |
| --- | --- | --- |
| `part_category` | Catalogo de categorias (combos y filtro). | `init_db.py:99` |
| `part` | Repuestos vendibles (catalogo, filtros, insercion). | `init_db.py:108` |
| `inventory_stock` | Stock actual y umbral de reorden por repuesto. | `init_db.py:126` |

Tablas del ERD academico que **no** se usan en este modulo:

- `VEHICLE_MODEL` y `PART_COMPATIBILITY`: el modulo de Inventario no
  expone ni crea compatibilidades. `part_crud` no las toca.
- `SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM`, `PAYMENT`,
  `RETURN_ORDER`, `RETURN_ORDER_ITEM`: son responsabilidad de otros
  modulos y se documentan en sus propios SPEC.

### Relaciones relevantes

- `part_category` 1 a N `part`. `part.part_category_id` referencia a
  `part_category.part_category_id` con `ON DELETE RESTRICT`.
- `part` 1 a 1 `inventory_stock` en la implementacion actual: la
  columna `part_id` de `inventory_stock` es `UNIQUE`, asi que solo
  puede existir una fila de stock por repuesto. El ERD academico
  admite 1 a N, pero el esquema fisico y `crear_producto` lo tratan
  como 1 a 1.
- `part` 1 a N `sales_order_item` y 1 a N `purchase_order_item` (no
  usados aqui, pero existen en el modelo).

### Funciones CRUD y su responsabilidad

| Funcion | Ubicacion | Que hace |
| --- | --- | --- |
| `crear_producto(part, initial_stock, location)` | `part_crud.py:56` | Inserta el repuesto en `part` y su stock en `inventory_stock` en una sola transaccion. Devuelve `True`/`False`. |
| `listar_productos(search, category_id, brand)` | `part_crud.py:101` | `SELECT` con `JOIN` a `part_category` y `LEFT JOIN` a `inventory_stock`. Aplica filtros opcionales y ordena por `internal_code`. |
| `listar_categorias()` | `part_crud.py:33` | Devuelve `List[PartCategory]` ordenada por nombre. |
| `obtener_marcas()` | `part_crud.py:147` | `SELECT DISTINCT brand` no nulos y no vacios, ordenados. |
| `crear_categoria(name, description)` | `part_crud.py:16` | Inserta una categoria. **No se usa desde Flask.** |

### Side effects (efectos colaterales)

- `crear_producto` realiza dos `INSERT` (`part` y `inventory_stock`)
  en una sola transaccion. Si MySQL falla en cualquier paso, ejecuta
  `conexion.rollback()` y devuelve `False`. El commit se hace solo si
  ambos `INSERT` salieron bien.
- El `reorder_level` que se guarda en `inventory_stock` es siempre
  `10`. Esta hardcodeado en `part_crud.py:88` y no se puede cambiar
  desde la UI.
- El `status` de `part` se setea siempre a `"active"` desde
  `app.py:145`. No se puede elegir desde el form.
- `inventory_stock.quantity_on_hand` se inicializa con el valor de
  `initial_stock` enviado por el form.

### Reglas de integridad involucradas

- `part.internal_code` UNIQUE: no se puede registrar dos repuestos con
  el mismo codigo interno.
- `part.part_category_id` FK a `part_category` con
  `ON DELETE RESTRICT`: no se puede borrar una categoria que tenga
  repuestos asociados.
- `inventory_stock.part_id` UNIQUE y FK a `part` con
  `ON DELETE CASCADE`: borrar un repuesto borra su stock.
- `part_category.name` UNIQUE: no se duplican categorias.

## Trazabilidad SDD

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Catalogo de repuestos (RF-02) | `requirements.md` RF-02; `processes.md` gestion del catalogo | `erd.md` tabla `PART` y `PART_CATEGORY`; `db_explanation.md` fila `PART` | `app.py:inventory` GET+POST, `part_crud.crear_producto`, `listar_productos`, template `inventory.html` | `implementado` |
| Busqueda por texto, categoria y marca | `procedures.md` busqueda de repuesto (paso 3) | `db_explanation.md` atributos `internal_code`, `oem_code`, `brand`, `name` | `listar_productos` con `LIKE` y filtros; filtros GET en `inventory.html` | `implementado` |
| Stock inicial al crear repuesto (RF-04) | `requirements.md` RF-04; `processes.md` control de inventario | `erd.md` `INVENTORY_STOCK`; `db_explanation.md` fila `INVENTORY_STOCK` | `crear_producto` inserta fila en `inventory_stock` con `initial_stock` y `reorder_level=10` | `parcial` (ver Brechas: umbral hardcoded) |
| Umbral de reorden configurable | `processes.md` "Reporta productos con stock bajo a compras" | `db_explanation.md` `reorder_level` | No existe UI ni parametro. Valor fijo en `part_crud.py:88` | `faltante` |
| Compatibilidad vehicular (RF-03) | `requirements.md` RF-03; `processes.md` fila "Compatibilidad vehicular" | `erd.md` `VEHICLE_MODEL` y `PART_COMPATIBILITY`; `db_explanation.md` filas correspondientes | Tablas no creadas en `init_db.py`; no hay CRUD, ni ruta, ni campos en el form | `faltante` |
| Edicion de repuestos | `processes.md` "Revisa que la informacion este actualizada" (cliente); el ERD lo permite al ser `part` actualizable | `erd.md` no exige historico en `PART` | No hay ruta `/inventory/<id>/edit`. `part_crud` no expone `update`. | `faltante` |
| Eliminacion (baja) de repuestos | No esta exigido por un RF, pero `ON DELETE CASCADE` lo permite desde `inventory_stock` y `RESTRICT` lo bloquea si hay ventas/compras | `erd.md` `ON DELETE RESTRICT` desde `sales_order_item` y `purchase_order_item` | No hay ruta `/inventory/<id>/delete`. `part_crud` no expone `delete`. | `faltante` |
| Creacion de categorias desde la UI | `processes.md` gestion del catalogo (categoria como dato) | `erd.md` `PART_CATEGORY`; `db_explanation.md` `name` UNIQUE | `part_crud.crear_categoria` existe. No hay ruta Flask ni formulario. | `faltante` |
| Alertas visuales de stock bajo | `processes.md` paso 5 de control de inventario | No especificado a nivel BD | `inventory.html` pinta en rojo `quantity_on_hand <= reorder_level` | `implementado` |
| Garantia y estado del repuesto | `requirements.md` RF-02 menciona "garantia y estado" | `erd.md` `PART.warranty_days`, `PART.status`; `db_explanation.md` mismos campos | `part.warranty_days` y `part.status` existen en BD pero **no se exponen** en el form. `status` se fuerza a `"active"`. | `parcial` |
| Gestion de ubicaciones multiples por repuesto | `processes.md` "Actualiza ubicaciones si cambia la posicion fisica" | `db_explanation.md` admite 1 a N entre `PART` e `INVENTORY_STOCK` | Esquema fisico define `inventory_stock.part_id` como `UNIQUE`. Una sola ubicacion por repuesto. | `parcial` |
| Paginacion y "Mostrando X de Y entradas" | No esta en `requirements.md` | No aplica | No implementado. `listar_productos` no usa `LIMIT/OFFSET`. El mockup `inventory_mockup.html` si la muestra. | `faltante` |
| Busqueda por compatibilidad vehiculo | `procedures.md` paso 2 y 3 de busqueda de repuesto | `erd.md` `PART_COMPATIBILITY` | No hay UI ni consulta por vehiculo | `fuera de alcance` (las tablas no existen en el esquema) |

## Criterios de aceptacion

### Pruebas manuales

1. **Listado vacio.** Con la base recien creada y sin repuestos, la
   pantalla muestra la fila "No se encontraron productos registrados
   con los filtros aplicados.".
2. **Listado con datos.** Despues de correr el seed
   `scripts/database/seed_project_data.py`, la tabla muestra los cinco
   repuestos demo en orden por `internal_code`.
3. **Busqueda por texto.** GET `/inventory?search=Spark` lista solo los
   repuestos cuyo nombre, codigo interno, OEM o marca contenga
   "Spark".
4. **Filtro por categoria.** GET `/inventory?category_id=<id>` lista
   solo los repuestos de esa categoria. El select queda con esa
   opcion marcada.
5. **Filtro por marca.** GET `/inventory?brand=Bosch` lista solo
   repuestos con esa marca. El select queda con esa opcion marcada.
6. **Filtros combinados.** Los tres parametros se aplican con `AND`.
7. **Alerta de stock bajo.** Un repuesto con
   `quantity_on_hand <= 10` aparece con el numero de stock en rojo.
8. **Registrar repuesto nuevo.** Completar el modal con datos
   validos y enviar. Resultado: nueva fila en `part` y nueva fila en
   `inventory_stock` con `reorder_level=10`. Aparece flash de exito.
9. **Codigo interno duplicado.** Intentar registrar un repuesto con un
   `internal_code` ya existente. Resultado: la base rechaza el
   `INSERT`, la ruta muestra flash de error, y no queda fila huera
   en `inventory_stock` (rollback de la transaccion).
10. **Categoria inexistente.** Si se manipula el `part_category_id`
    para apuntar a un id que no existe, el `INSERT` falla por la FK y
    se muestra flash de error.
11. **Acceso sin login.** Visitar `/inventory` sin sesion redirige a
    `home` con flash "Por favor, inicia sesion para acceder al
    sistema.".

### Pruebas automatizadas

- **No existen tests automatizados para este modulo.** El directorio
  `tests/` cubre otros CRUDs (`test_purchase_crud.py`,
  `test_customer_crud.py`, `test_login_flow.py`,
  `test_purchase_detail_route.py`, `test_receipt_route.py`,
  `test_sales_validation.py`, `test_setup_database.py`,
  `test_sql_trace.py`), pero ninguno apunta a `part_crud`,
  `listar_productos`, `crear_producto` ni a la ruta `/inventory`.
  `test_purchase_crud.py` si toca `inventory_stock`, pero solo para
  verificar incrementos de stock durante la recepcion de compras, no
  el modulo de Inventario.
- Esto se documenta como brecha en la seccion siguiente.

## Brechas y decisiones

1. **No hay edicion ni eliminacion de repuestos en la UI.**
   El modulo solo permite crear y listar. No existen rutas
   `/inventory/<id>/edit` ni `/inventory/<id>/delete`, y
   `part_crud` no expone `update_part` ni `delete_part`. Para
   corregir un codigo, una marca o un precio hay que tocar la base
   directamente. **Brecha: faltante.** Esto rompe RF-02 en su
   dimension de "administrar", no solo "registrar".
2. **`crear_categoria` no esta conectado a Flask.** La funcion existe
   en `part_crud.py:16` y la tabla `part_category` admite inserciones
   (`name` UNIQUE, `description` opcional), pero la ruta
   `/inventory` solo lee categorias. El alta de categorias nuevas
   depende del seed o de inserts manuales. **Brecha: faltante.**
3. **El umbral de reorden esta hardcoded a `10`.** Tanto el esquema
   (`init_db.py:131` define `reorder_level INT NOT NULL DEFAULT 10`)
   como el `INSERT` de `crear_producto` (`part_crud.py:88` pasa el
   literal `10`) lo dejan fijo. No es configurable por categoria, por
   repuesto ni desde la UI. **Brecha: parcial.** Decision: se mantiene
   el `10` porque el alcance academico prioriza mostrar el JOIN y la
   alerta visual, no parametrizar el umbral.
4. **Compatibilidad vehicular (RF-03) no se implementa.** Las tablas
   `VEHICLE_MODEL` y `PART_COMPATIBILITY` del ERD academico no estan
   creadas en `init_db.py`, no hay modelos Python, no hay CRUD y la
   busqueda del modulo no acepta marca/modelo/anio del vehiculo. El
   procedimiento "Busqueda de repuesto" en
   `docs/analysis/procedures.md` menciona compatibilidad, pero la
   pantalla real no la expone. **Brecha: faltante / fuera de alcance
   para el modulo de Inventario.** Es una de las principales
   diferencias entre el diseno y la implementacion.
5. **Stock de una sola ubicacion por repuesto.** El ERD academico
   admite 1 a N entre `PART` e `INVENTORY_STOCK`, pero la columna
   `inventory_stock.part_id` es `UNIQUE NOT NULL`, asi que la
   implementacion solo permite una ubicacion por repuesto. La UI
   tampoco expone varias ubicaciones. **Brecha: parcial.**
6. **El form no captura `warranty_days`, `unit` ni `status`.** RF-02
   los pide, existen en la tabla, pero la ruta fija `unit='pcs'`,
   `warranty_days=0` y `status='active'` sin leerlos del form. **Brecha:
   parcial.** Decision: se opta por defaults explicitos para no
   inflar el modal en una primera entrega, pero se reconoce que el
   alcance academico los pide.
7. **No hay paginacion.** `listar_productos` no usa `LIMIT` ni
   `OFFSET`, y `inventory.html` no muestra controles de paginacion.
   El mockup `inventory_mockup.html` si la dibuja ("Showing 1 to 5 of
   1,240 entries"). **Brecha: faltante.** Decision: aceptable para
   el tamano del dataset academico.
8. **Diferencias entre el mockup y la pantalla real.** El mockup
   `spec/inventory/inventory_mockup.html` muestra una columna final
   con un boton de tres puntos (menu `more_vert`) por fila, pensado
   para abrir acciones como editar o eliminar. La pantalla real
   `templates/inventory.html` no tiene esa columna ni esas acciones.
   Tambien muestra paginacion, que la pantalla real no tiene. **Brecha:
   el mockup es la version de diseno; la pantalla real es la version
   minima viable.**
9. **Sin tests automatizados del modulo.** No hay cobertura para
   `part_crud.crear_producto`, `listar_productos` ni la ruta
   `/inventory`. Cualquier cambio en filtros o en la transaccion
   `part`+`inventory_stock` queda sin red de seguridad. **Brecha:
   faltante.** Se recomienda anadir al menos un test de la
   transaccion (rollback al fallar el segundo `INSERT`) y un test del
   filtro combinado.
10. **Mensajes flash en Latam Spanish, identificadores tecnicos en
    US English.** Se conserva la convencion de `AGENTS.md`: tablas y
    columnas en `native US English` (`part`, `inventory_stock`,
    `reorder_level`, `internal_code`), mensajes y documentacion
    academica en `Latam Spanish`. El handler de la ruta convierte
    vacios a `None` para `oem_code` y `brand` antes de persistir.
