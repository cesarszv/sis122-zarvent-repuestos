# Specs — Zarvent Repuestos

Este directorio agrupa los **contratos funcionales y tecnicos** de cada modulo
de la aplicacion, escritos siguiendo un enfoque **SDD (Spec-Driven Development)**:
primero el contrato, despues el codigo.

## Que NO es este directorio

- No es documentacion de marketing ni un manual de usuario final.
- No reemplaza a `docs/analysis` (procesos, actores, requerimientos) ni a
  `docs/database` (ERD, explicacion del modelo).
- No es un changelog ni un backlog vivo. Es la **fuente de verdad** contra la
  que se compara la implementacion real para detectar brechas.

## Que SI es

- El **contrato esperado** de cada modulo: rutas, tablas, validaciones,
  mensajes, efectos, side effects y reglas de integridad.
- El **estado actual reverse-engineered** del codigo que ya esta en el repo.
- La **matriz de trazabilidad** entre analisis academico (`docs/analysis`),
  modelo de datos (`docs/database`) y codigo real.
- La lista explicita de **brechas y decisiones** que el equipo debe resolver
  antes de pasar a la defensa.

## Convenciones

- Nombres tecnicos (tablas, columnas, rutas, archivos) en **native US English**.
- Descripciones y textos academicos en **Latam Spanish**.
- Cada `SPEC.md` sigue la misma estructura para que sean comparables.
- Esta prohibido inventar mockups, endpoints o tablas: todo surge de evidencia
  del repo.

## Indice de specs por modulo

| Modulo | Ruta Flask principal | Spec | Mockup | Estado |
| --- | --- | --- | --- | --- |
| Dashboard | `/dashboard` | [dashboard/SPEC.md](dashboard/SPEC.md) | `dashboard_mockup.{html,png}` | Implementado |
| Inventario | `/inventory` | [inventory/SPEC.md](inventory/SPEC.md) | `inventory_mockup.{html,png}` | Implementado (con brechas) |
| Ventas | `/sales`, `/sales/receipt/<id>` | [sales/SPEC.md](sales/SPEC.md) | `sales_mockup.{html,png}` | Implementado (con brechas) |
| Clientes | `/customers`, `/customers/<id>/edit`, `/customers/<id>/delete` | [customers/SPEC.md](customers/SPEC.md) | No existe | Implementado (con brechas) |
| Compras | `/purchases`, `/purchases/<id>`, `/purchases/<id>/receive` | [purchases/SPEC.md](purchases/SPEC.md) | No existe | Implementado (con brechas) |
| SQL Trace | `/sql-trace`, `/api/sql-trace`, `/api/sql-trace/clear` | [sql-trace/SPEC.md](sql-trace/SPEC.md) | No existe | Implementado (herramienta didactica) |

> Los mockups faltantes (`customers`, `purchases`, `sql-trace`) **no se
> inventan**. Si el equipo quiere alinear esas pantallas con un diseno
> academico, primero se crea el mockup como tarea separada en
> `.cszv/mockups/` y despues se actualiza el `SPEC.md` correspondiente.

## Estructura de cada SPEC.md

Todos los specs respetan el mismo orden para que se puedan leer uno al lado
del otro:

1. `Objetivo del modulo` — que problema del negocio resuelve.
2. `Estado actual reverse-engineered` — rutas Flask, templates, funciones
   CRUD usadas, tablas relacionadas y comportamiento visible.
3. `Contrato funcional` — flujos permitidos, campos, validaciones, mensajes,
   estados y efectos esperados.
4. `Contrato de datos` — tablas, relaciones, funciones CRUD, side effects y
   reglas de integridad.
5. `Trazabilidad SDD` — matriz contra `docs/analysis` y `docs/database` con
   estado: `implementado`, `parcial`, `faltante` o `fuera de alcance`.
6. `Criterios de aceptacion` — pruebas manuales y automatizadas que
   demuestran que el modulo cumple el contrato.
7. `Brechas y decisiones` — diferencias entre lo propuesto y lo implementado.

## Estados de la matriz de trazabilidad

| Estado | Significado |
| --- | --- |
| `implementado` | La pieza esta en codigo y cumple lo que el analisis/ERD propone. |
| `parcial` | Esta implementada una parte; falta o difiere respecto a lo academico. |
| `faltante` | Identificada en el analisis/ERD pero no implementada. |
| `fuera de alcance` | Reconocida como mejora futura; no se implementa en esta entrega. |

## Como usar estos specs

1. **Antes de tocar codigo** de un modulo, leer su `SPEC.md` para entender el
   contrato y las brechas abiertas.
2. **Antes de la defensa**, usar la matriz de trazabilidad y la seccion de
   brechas como guia para saber que se puede defender y que se debe aclarar
   como limite del alcance academico.
3. **Antes de cambiar comportamiento**, actualizar el `SPEC.md` primero y
   recien despues modificar el codigo. Asi el spec sigue siendo fuente de
   verdad.
4. **Para integrar el spec al plan de defensa**, revisar las pruebas en
   `tests/` mencionadas en cada `Criterios de aceptacion`.

## Cross-references utiles

- Analisis del negocio: `../docs/analysis/`
- Modelo de datos (ERD y explicacion): `../docs/database/`
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
- El modulo SQL Trace esta documentado como transversal, no como parte del
  modelo de negocio, y su inclusion es didactica.

## Specs vecinos (fuera del alcance de este SDD de modulos)

- [docker/spec.md](docker/spec.md): contrato del entorno de ejecucion
  dockerizado para la defensa.
