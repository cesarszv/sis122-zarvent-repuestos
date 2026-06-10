# Specs — Zarvent Repuestos

Este directorio agrupa los **contratos funcionales y tecnicos** de cada modulo
de la aplicacion, escritos siguiendo un enfoque **SDD (Spec-Driven Development)**:
primero el contrato, despues el codigo. Cada `SPEC.md` describe el modulo tal
como esta implementado hoy, lo que el analisis academico espera, las brechas
entre ambos y la matriz de trazabilidad contra `docs/analysis` y
`docs/database`.

El proposito de esta pagina indice es triple:

- Servir como puerta de entrada a los seis `SPEC.md` de modulos.
- Exponer la **matriz RF-01..RF-09** que cruza requerimiento funcional con tema
  academico (PK/FK, CRUD, JOIN, agregaciones, vistas, etc.) y con el modulo
  que lo demuestra en codigo.
- Dar las convenciones, estados y reglas de uso para que un estudiante de
  primer ano pueda leer un spec y defender su implementacion frente al
  profesor sin ambiguedad.

## Que NO es este directorio

- No es documentacion de marketing ni un manual de usuario final.
- No reemplaza a `docs/analysis` (procesos, actores, requerimientos) ni a
  `docs/database` (ERD, explicacion del modelo).
- No es un changelog ni un backlog vivo. Es la **fuente de verdad** contra la
  que se compara la implementacion real para detectar brechas.
- No es una lista de mockups: los mockups son insumos opcionales del modulo,
  no la fuente de verdad.

## Que SI es

- El **contrato esperado** de cada modulo: rutas, tablas, validaciones,
  mensajes, efectos, side effects y reglas de integridad.
- El **estado actual reverse-engineered** del codigo que ya esta en el repo.
- La **matriz de trazabilidad** entre analisis academico (`docs/analysis`),
  modelo de datos (`docs/database`) y codigo real.
- La **matriz RF-01..RF-09** que mapea cada requerimiento funcional al tema
  academico que lo demuestra y al modulo que lo soporta.
- La lista explicita de **brechas y decisiones** que el equipo debe resolver
  antes de pasar a la defensa.

## Convenciones

- Nombres tecnicos (tablas, columnas, rutas, archivos) en **native US English**.
- Descripciones y textos academicos en **Latam Spanish**.
- Cada `SPEC.md` sigue la misma estructura (siete secciones) para que sean
  comparables lado a lado.
- Esta prohibido inventar mockups, endpoints o tablas: todo surge de evidencia
  del repo.
- Los nombres de los nueve requerimientos funcionales son **exactamente**
  `RF-01` a `RF-09` y provienen de `docs/analysis/requirements.md`.

## Matriz RF-01..RF-09

Esta matriz cruza cada requerimiento funcional con el **tema academico** que
el modulo esta demostrando. La columna `#` enumera las filas; `RF` anota a
cual de los nueve requerimientos apunta la fila; `Tema academico` describe
el contenido conceptual (PK/FK, CRUD, JOIN, etc.); `Modulo` indica que
modulo de Zarvent Repuestos lo cubre; `Spec` apunta al `SPEC.md` que sirve
como evidencia; `Estado v1` usa exactamente uno de los cuatro valores
listados en la seccion `Estados de la matriz de trazabilidad`.

Una misma RF puede aparecer varias veces si cubre varios temas academicos
(por ejemplo, RF-05 demuestra CRUD basico y a la vez integridad transaccional).
A la inversa, un tema academico puede ser transversal y no vivir dentro de
un unico modulo (es el caso de vistas, procedimientos o borrado logico).

| # | RF | Tema academico | Modulo | Spec | Estado v1 |
| --- | --- | --- | --- | --- | --- |
| 1 | RF-01, RF-02, RF-04, RF-05, RF-07 | PK/FK y normalizacion (1FN/2FN/3FN) | transversal: `person`/`customer`, `part`/`part_category`, `sales_order`/`sales_order_item`, `purchase_order`/`purchase_order_item`, `inventory_stock` | [customers/SPEC.md](customers/SPEC.md), [inventory/SPEC.md](inventory/SPEC.md), [sales/SPEC.md](sales/SPEC.md), [purchases/SPEC.md](purchases/SPEC.md) | implementado v1 |
| 2 | RF-01, RF-02, RF-05, RF-07 | CRUD basico (Create / Read / Update / Delete) | customers, inventory, sales, purchases | [customers/SPEC.md](customers/SPEC.md), [inventory/SPEC.md](inventory/SPEC.md), [sales/SPEC.md](sales/SPEC.md), [purchases/SPEC.md](purchases/SPEC.md) | implementado v1 |
| 3 | RF-09 | `JOIN` para reportes (multiples tablas en una consulta) | dashboard | [dashboard/SPEC.md](dashboard/SPEC.md) | implementado v1 |
| 4 | RF-09 | Agregaciones (`SUM`, `COUNT`, `COALESCE`) | dashboard | [dashboard/SPEC.md](dashboard/SPEC.md) | implementado v1 |
| 5 | RF-09 | Vistas (`vw_low_stock_parts`, `vw_daily_sales_summary`) | transversal: declaradas en `database/schema.sql`, consumidas por `sales_crud.obtener_metricas_dashboard()` y por la lista de stock bajo en `/inventory` | [dashboard/SPEC.md](dashboard/SPEC.md), [inventory/SPEC.md](inventory/SPEC.md) | implementado v1 |
| 6 | RF-05, RF-07 | Procedimientos almacenados y triggers | transversal: no existen `CREATE PROCEDURE` ni `CREATE TRIGGER` en `init_db.py`; toda la logica vive en `crud/*.py` con `try/except/rollback` | (no documentado en un `SPEC.md` propio) | fuera de alcance v1 |
| 7 | RF-01, RF-02, RF-07 | Borrado logico (`is_active`, `status='inactive'`) | customers (`customer.is_active`), inventory (`part.status`), purchases (`supplier.is_active` + cancelacion de orden) | [customers/SPEC.md](customers/SPEC.md), [inventory/SPEC.md](inventory/SPEC.md), [purchases/SPEC.md](purchases/SPEC.md) | implementado v1 |
| 8 | RF-01, RF-02, RF-05, RF-07, RF-09 | Trazabilidad: SQL Trace + logs de cursor + `cursor.rowcount` | sql-trace (transversal) + `customer_crud.delete_customer` (uso de `rowcount`) | [sql-trace/SPEC.md](sql-trace/SPEC.md), [customers/SPEC.md](customers/SPEC.md) | implementado v1 |

Notas por fila:

1. **PK/FK y normalizacion.** Cubre la separacion `PERSON` / `CUSTOMER` (1..0..1
   con `customer.person_id UNIQUE NOT NULL`), `PART_CATEGORY` / `PART`, las
   lineas separadas de orden (`SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM`) y la
   tabla puente `INVENTORY_STOCK`. Se evidencia en cualquier modulo CRUD.
2. **CRUD basico.** `customers`, `inventory`, `sales` y `purchases` exponen
   las cuatro operaciones (crear, listar, editar, desactivar/reactivar).
   `inventory` cubre el CRUD completo con `update_part` y soft-delete
   `deactivate_part` / `reactivate_part`. `customers` y `purchases` usan
   soft-delete via `is_active`; `sales` no expone edicion ni cancelacion
   (queda como `fuera de alcance v1`).
3. **JOIN para reportes.** `obtener_metricas_dashboard()` une `sales_order`
   con `customer` para traer las ultimas 5 ordenes con nombre del cliente.
4. **Agregaciones.** El dashboard calcula ventas del dia con
   `SUM(total_amount)`, stock bajo con `COUNT(*)`, y categorias activas con
   `COUNT(*)`, ademas de `COALESCE(SUM(...), 0.0)` para evitar nulos.
5. **Vistas.** `vw_low_stock_parts` y `vw_daily_sales_summary` se declaran
   en `database/schema.sql` (idempotentes con `CREATE OR REPLACE VIEW`) y se
   consumen desde `sales_crud.obtener_metricas_dashboard()`. Se documentan
   en este README (no en un `SPEC.md` propio, porque no son un modulo de
   negocio).
6. **Procedimientos / Triggers.** No estan incluidos en v1; queda como
   **backlog v2** si se llega a necesitar para la defensa. El plan v1 prioriza
   vistas (objeto academico defendible) y deja procedimientos/triggers
   fuera del alcance.
7. **Borrado logico.** `customer` usa `is_active BOOLEAN` con
   `deactivate_customer` / `reactivate_customer`. `part` usa
   `status VARCHAR(50)` con `deactivate_part` / `reactivate_part` (v1
   expone los botones en `/inventory`). `supplier` mantiene su
   `is_active` y la maquina de ordenes de compra se extiende con
   `Cancelled` (header se marca, `inventory_stock` no se toca).
8. **Trazabilidad.** El modulo `sql-trace` envuelve el cursor MySQL con
   `TracedCursor` cuando `SQL_TRACE_ENABLED=1` y registra
   `method + route + sql + params + duration_ms + status`. Complementa con
   `cursor.rowcount` en `customer_crud.delete_customer` para verificar
   afectacion real.

## Indice de specs por modulo

| Modulo | Ruta Flask | Spec | Estado v1 | Cambios v1 |
| --- | --- | --- | --- | --- |
| Dashboard | `/dashboard` | [dashboard/SPEC.md](dashboard/SPEC.md) | implementado v1 | Mockup `dashboard_mockup.{html,png}`; implementar pagos y compras pendientes para cerrar RF-09 completo. |
| Inventario | `/inventory` | [inventory/SPEC.md](inventory/SPEC.md) | implementado v1 | Mockup `inventory_mockup.{html,png}`; rutas `/inventory/<id>/edit` y borrado lógico (inactivación) implementados. Exposición de `warranty_days` y `status` integrada. |
| Clientes | `/customers`, `/customers/<id>/edit`, `/customers/<id>/delete` | [customers/SPEC.md](customers/SPEC.md) | implementado v1 | Sin mockup dedicado; aniadir busqueda por telefono, paginacion y validacion backend de email/telefono. |
| Ventas | `/sales`, `/sales/receipt/<id>` | [sales/SPEC.md](sales/SPEC.md) | implementado v1 | Mockup `sales_mockup.{html,png}`; permitir pagos multiples/parciales y estados `Pending`/`Cancelled` reales (hoy se inserta siempre `Paid`). |
| Compras | `/purchases`, `/purchases/<id>`, `/purchases/<id>/receive` | [purchases/SPEC.md](purchases/SPEC.md) | implementado v1 | Sin mockup dedicado; exponer `create_supplier` y `create_category` en la UI; aniadir cancelacion de orden. |
| SQL Trace | `/sql-trace`, `/api/sql-trace`, `/api/sql-trace/clear` | [sql-trace/SPEC.md](sql-trace/SPEC.md) | implementado v1 | Herramienta didactica transversal; opt-in via `SQL_TRACE_ENABLED=1`. No implementa RF-09 en si, lo hace visible. |

> Los modulos sin mockup (`customers`, `purchases`, `sql-trace`) **no
> inventan** uno. Si el equipo quiere alinear esas pantallas con un diseno
> academico, primero se crea el mockup como tarea separada en
> `.cszv/mockups/` y despues se actualiza el `SPEC.md` correspondiente.

## Estructura de cada SPEC.md

Todos los specs respetan el mismo orden, en siete secciones, para que se
puedan leer uno al lado del otro:

1. **Estado actual (reverse-engineered).** Rutas Flask reales, templates,
   funciones CRUD usadas, tablas relacionadas y comportamiento visible hoy
   en el repo.    Sale de leer el codigo, no de un diseno imaginado.
2. **Contrato objetivo v1.** Flujos permitidos, campos, validaciones,
   mensajes, estados y efectos esperados por el modulo. Es lo que el spec
   promete y contra lo que se acepta o se rechaza una entrega.
3. **Cambios requeridos v1.** Lista concreta de lo que hay que tocar en
   codigo, en schema o en UI para pasar del estado actual al contrato
   objetivo. Anota que spec vecino (si alguno) se ve afectado.
4. **Aceptacion automatizada.** Tests en `tests/` que demuestran que el
   contrato se cumple sin intervencion humana. Si no hay test, esa fila se
   documenta como brecha.
5. **Aceptacion manual en navegador / DataGrip.** Pasos reproducibles que
   un estudiante de primer ano puede correr para verificar el contrato
   desde la UI o desde un cliente SQL.
6. **Decisiones fuera de alcance.** Lo que el analisis academico pedia pero
   el equipo decidio no entregar en v1 (con justificacion). Si es un
   candidato futuro, queda apuntando al backlog v2.
7. **Trazabilidad RF.** Tabla que conecta cada tema con su RF origen
   (`docs/analysis/requirements.md`), su soporte de datos
   (`docs/database/erd.md`, `db_explanation.md`) y el codigo real que lo
   implementa, con un `Estado v1` por fila.

Esta estructura es la que usan los seis `SPEC.md` de modulos y debe
mantenerse cuando se modifique cualquiera de ellos. La homogeneidad es lo
que hace que la matriz `RF-01..RF-09` de este README siga siendo valida.

## Estados de la matriz de trazabilidad

Los cuatro valores que pueden aparecer en la columna `Estado v1` (tanto en
la matriz principal como en las tablas internas de cada `SPEC.md`) son:

| Estado | Significado |
| --- | --- |
| `implementado v1` | La pieza esta en codigo y cumple lo que el analisis/ERD propone; se puede defender tal cual. |
| `parcial v1` | Esta implementada una parte; falta o difiere respecto a lo academico. El `SPEC.md` debe listar exactamente que falta y que plan hay para cerrarlo en v1. |
| `corregir UI/spec` | El codigo o el modelo estan bien, pero la UI o el `SPEC.md` no reflejan el contrato correcto. No requiere tocar la base ni el CRUD, solo ajustar la pantalla o el documento. |
| `fuera de alcance v1` | Reconocida como mejora futura; no se implementa en esta entrega. Si queda como objetivo futuro, se etiqueta `backlog v2` solo en la columna de cambios, no en `Estado v1`. |

`backlog v2` se usa **unicamente** dentro de la columna `Cambios v1` de la
tabla de indice de specs y dentro de las notas de la matriz principal
(como en compatibilidad vehicular y devoluciones). Nunca aparece en la
columna `Estado v1` de la matriz RF-01..RF-09.

## Como usar estos specs

1. **Antes de tocar codigo** de un modulo, leer su `SPEC.md` para entender
   el contrato y las brechas abiertas.
2. **Antes de la defensa**, usar la matriz de trazabilidad y la seccion de
   brechas como guia para saber que se puede defender y que se debe
   aclarar como limite del alcance academico. La matriz
   `RF-01..RF-09` de este README es la vista rapida; los detalles estan en
   cada `SPEC.md`.
3. **Antes de cambiar comportamiento**, actualizar el `SPEC.md` primero y
   recien despues modificar el codigo. Asi el spec sigue siendo fuente de
   verdad y la matriz de este README no queda desfasada.
4. **Para integrar el spec al plan de defensa**, revisar las pruebas en
   `tests/` mencionadas en cada seccion `Aceptacion automatizada`.
5. **Para mapear un tema academico a un RF**, usar la matriz de este
   README (no la del ERD): cada fila es un tema, no una tabla.

## Cross-references utiles

- Analisis del negocio: `../docs/analysis/`
  - Requerimientos funcionales: `../docs/analysis/requirements.md` (RF-01..RF-09)
  - Procesos: `../docs/analysis/processes.md`
  - Procedimientos: `../docs/analysis/procedures.md`
  - Actores: `../docs/analysis/actors.md`
- Modelo de datos (ERD y explicacion): `../docs/database/`
  - ERD: `../docs/database/erd.md`
  - Explicacion del modelo: `../docs/database/db_explanation.md`
- Schema SQL real (generado por la app, no manual): `../database/schema.sql`
- Codigo fuente Flask: `../src/zarvent_repuestos/web/app.py`
- CRUDs: `../src/zarvent_repuestos/crud/`
- Tests automatizados: `../tests/`
- Spec de Docker (entorno de ejecucion, fuera del alcance de este SDD):
  [docker/spec.md](docker/spec.md)

## Limitaciones aceptadas del SDD actual

- Solo se documenta lo que **ya esta implementado**. Cualquier refactor
  futuro debe actualizar su `SPEC.md` en el mismo PR.
- Los specs **no son contratos legales ni API publica**: son material
  pedagogico y de defensa academica.
- El modulo **SQL Trace** es transversal a RF-01..RF-09: no aparece como
  modulo de negocio en `docs/analysis` ni en el ERD, y su inclusion es
  didactica. Se documenta aparte en [sql-trace/SPEC.md](sql-trace/SPEC.md).
- **Compatibilidad vehicular (RF-03)** y **devoluciones/garantias (RF-08)**
  estan reconocidas en `docs/analysis/requirements.md` pero las tablas
  correspondientes (`VEHICLE_MODEL`, `PART_COMPATIBILITY`, `RETURN_ORDER`,
  `RETURN_ORDER_ITEM`) **no se crean** en `init_db.py`. Quedan como
  `backlog v2` en la columna de cambios de la matriz y como
  `fuera de alcance v1` en cualquier tabla de trazabilidad que las
  mencione.
- Procedimientos almacenados y triggers no forman parte de v1; cuando y si
  se necesitan, se tratan como objetos academicos aislados en el backlog v2,
  no como un modulo nuevo. Las vistas (`vw_low_stock_parts`,
  `vw_daily_sales_summary`) SÍ se entregan en v1.

## Specs vecinos (fuera del alcance de este SDD de modulos)

- [docker/spec.md](docker/spec.md): contrato del entorno de ejecucion
  dockerizado para la defensa. No se modifica desde este README ni desde
  los `SPEC.md` de modulos.
