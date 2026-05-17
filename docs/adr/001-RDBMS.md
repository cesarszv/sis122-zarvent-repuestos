# ADR 001: Select PostgreSQL 18.4 as the RDBMS

## Status

Accepted.

## Context

Zarvent Repuestos necesita un Relational Database Management System (RDBMS) para
un sistema administrativo de venta de repuestos. El modelo maneja clientes,
proveedores, catalogo de repuestos, compatibilidad con vehiculos, inventario,
ventas, pagos, compras, devoluciones y reportes.

La decision no se toma por moda ni por comodidad falsa. Se toma porque el
negocio tiene relaciones fuertes entre datos: una venta pertenece a un cliente,
una venta tiene lineas, cada linea apunta a un repuesto, los pagos pertenecen a
ventas, las compras pertenecen a proveedores y las devoluciones deben validar una
venta original.

## Quality Indicators

### Efficiency

El sistema debe ser eficiente y aprovechar bien los recursos disponibles.

La eficiencia no significa elegir lo mas rapido de configurar. Significa elegir
un gestor que permita modelar reglas reales sin fabricar deuda tecnica desde el
primer diseno.

### Timelessness

La solucion debe buscar la mayor atemporalidad posible. Esto implica depender de
conceptos estables: SQL, modelo relacional, primary keys, foreign keys, unique
constraints, check constraints y transacciones.

PostgreSQL 18.4 es una version actual del motor PostgreSQL 18, publicada el
2026-05-14 como release menor de correcciones. La decision se apoya en la rama
18, no en una tecnologia experimental.

### Comfort Without Technical Debt

La comodidad es un requisito central. El sistema debe ser comodo para
trabajadores, desarrolladores y usuarios, sin sacrificar calidad.

Comodidad no significa simplificacion mediocre. Significa reducir friccion sin
renunciar a integridad referencial, restricciones, consultas SQL claras y una
base defendible para crecer.

## Decision

Use **PostgreSQL 18.4** as the primary RDBMS for Zarvent Repuestos.

PostgreSQL 18.4 sera el gestor principal para implementar el modelo relacional
del proyecto. El ERD seguira siendo la fuente conceptual del diseno, y el SQL
fisico debera ajustarse a la sintaxis y capacidades de PostgreSQL.

## Options Considered

### Option A: PostgreSQL 18.4

| FODA | Evaluation |
| --- | --- |
| Fortalezas | RDBMS robusto, open source, con soporte fuerte para SQL, foreign keys, unique constraints, check constraints, transacciones y consistencia. Encaja con un modelo operacional serio. |
| Oportunidades | Permite que el proyecto crezca con mejor disciplina tecnica: migraciones, constraints, tipos mas precisos, funciones, vistas y consultas analiticas. |
| Debilidades | Tiene mas curva de aprendizaje que una instalacion academica basica. El equipo debe aprender sintaxis PostgreSQL y herramientas como `psql` o pgAdmin. |
| Amenazas | Si el equipo copia SQL pensado para otro motor sin adaptarlo, aparecen errores de dialecto. Elegir PostgreSQL no arregla un mal modelo relacional. |

### Option B: MySQL

| FODA | Evaluation |
| --- | --- |
| Fortalezas | Muy usado en contextos academicos, con buenas herramientas visuales y suficiente capacidad para un proyecto de Base de Datos I. |
| Oportunidades | Habria alineacion directa con clases donde se trabajo MySQL y MySQL Workbench. |
| Debilidades | Ya no sera el stack elegido para este proyecto. Mantenerlo mezclado con PostgreSQL crearia documentacion contradictoria. |
| Amenazas | Dejar referencias a MySQL despues de elegir PostgreSQL confunde el diseno, las migraciones y la defensa tecnica. |

### Option C: SQLite

| FODA | Evaluation |
| --- | --- |
| Fortalezas | Simple, portable y util para prototipos o pruebas pequenas. |
| Oportunidades | Puede servir como herramienta auxiliar para experimentos locales. |
| Debilidades | No representa bien un gestor cliente-servidor para un sistema administrativo multiusuario. |
| Amenazas | Usarlo como base principal reduciria el proyecto a un prototipo demasiado liviano. |

## Consequences

- Todo SQL fisico debe escribirse y probarse contra PostgreSQL 18.4.
- La documentacion del proyecto debe dejar de hablar de MySQL como gestor
  principal.
- Las migraciones futuras deben usar sintaxis PostgreSQL.
- Las herramientas recomendadas pasan a ser `psql`, pgAdmin o extensiones de
  PostgreSQL para el editor.
- El proyecto gana una base mas fuerte para integridad, consultas y crecimiento,
  pero exige mas disciplina tecnica.

## Sources

- PostgreSQL 18.4 release notes:
  <https://www.postgresql.org/docs/release/18.4/>
- PostgreSQL 18 documentation:
  <https://www.postgresql.org/docs/18/>
- PostgreSQL constraints documentation:
  <https://www.postgresql.org/docs/18/ddl-constraints.html>
