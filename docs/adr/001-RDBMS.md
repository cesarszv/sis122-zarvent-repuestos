# ADR 001: Select PostgreSQL 18.4 as the RDBMS

## Status

Accepted.

## Context

Zarvent Repuestos necesita un RDBMS para un negocio con relaciones fuertes:
clientes, proveedores, catalogo, compatibilidad vehicular, inventario, ventas,
pagos, compras, devoluciones y reportes.

La decision no es por moda. El modelo necesita reglas reales: ventas con
clientes, lineas de venta con repuestos, pagos ligados a ventas, compras ligadas
a proveedores y devoluciones validadas contra una venta original.

## Decision

Usar **PostgreSQL 18.4** como RDBMS principal.

El ERD sigue siendo la fuente conceptual del diseno; el SQL fisico debe ajustarse
a PostgreSQL 18.4.

## Evaluation Criteria

| Criterio | Lo que exige el proyecto |
| --- | --- |
| Efficiency | Modelar reglas reales sin deuda tecnica desde el primer diseno. |
| Timelessness | Apoyarse en SQL, modelo relacional, `PK`, `FK`, `UNIQUE`, `CHECK` y transacciones. |
| Comfort | Reducir friccion sin sacrificar integridad referencial ni consultas claras. |

PostgreSQL 18.4 es una version actual de la rama PostgreSQL 18, publicada el
2026-05-14 como release menor de correcciones.

## Options Considered

| Option | Strengths | Weaknesses / Risks |
| --- | --- | --- |
| PostgreSQL 18.4 | RDBMS robusto, open source, con buen soporte para SQL, constraints, transacciones, vistas, funciones y consultas analiticas. | Mayor curva de aprendizaje; el equipo debe aprender sintaxis PostgreSQL y no copiar SQL de otro motor sin adaptarlo. |
| MySQL | Comun en contextos academicos y con buenas herramientas visuales. | Ya no es el stack elegido; mezclarlo con PostgreSQL confundiria documentacion, migraciones y defensa tecnica. |
| SQLite | Simple y portable para prototipos o pruebas pequenas. | No representa bien un sistema cliente-servidor multiusuario; como base principal dejaria el proyecto demasiado liviano. |

## Consequences

- Todo SQL fisico debe escribirse y probarse contra PostgreSQL 18.4.
- La documentacion debe dejar de tratar MySQL como gestor principal.
- Las migraciones futuras deben usar sintaxis PostgreSQL.
- Las herramientas recomendadas son `psql`, pgAdmin o extensiones PostgreSQL
  para el editor.
- El proyecto gana integridad, consultas y capacidad de crecimiento, pero exige
  mas disciplina tecnica.

## Sources

- PostgreSQL 18.4 release notes:
  <https://www.postgresql.org/docs/release/18.4/>
- PostgreSQL 18 documentation:
  <https://www.postgresql.org/docs/18/>
- PostgreSQL constraints documentation:
  <https://www.postgresql.org/docs/18/ddl-constraints.html>
