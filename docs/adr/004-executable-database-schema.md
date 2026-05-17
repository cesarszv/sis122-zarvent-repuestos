# ADR 004: Keep an Executable Initial Database Schema

## Status

Accepted.

## Context

El ERD explica el modelo conceptual, pero una base real necesita SQL ejecutable:
`CREATE TABLE`, primary keys, foreign keys, unique constraints, check constraints
e indices.

Si solo existe el diagrama, cada persona puede interpretar el modelo de forma
distinta. El proyecto necesita una fuente fisica clara para crear la base local.

## Decision

Mantener [`database/schema.sql`](../../database/schema.sql) como **schema inicial
ejecutable**.

Roles:

- [`docs/database/erd.md`](../database/erd.md): explica el modelo.
- [`database/schema.sql`](../../database/schema.sql): crea el modelo en
  PostgreSQL.

## How It Works

Docker Compose monta `database/schema.sql` como:

```text
/docker-entrypoint-initdb.d/001_initial_schema.sql
```

La imagen oficial de PostgreSQL ejecuta ese archivo solo durante la primera
inicializacion, cuando el volumen esta vacio. El prefijo `001_` marca el orden
de arranque y permite agregar scripts posteriores:

```text
001_initial_schema.sql
002_seed_reference_data.sql
003_demo_data.sql
```

## Why It Matters

Un schema ejecutable convierte ideas en reglas concretas:

- `person.person_id` es una primary key.
- `customer.person_id` es una foreign key.
- `part.internal_code` es unico.
- `sales_order.total_amount` tiene reglas de validacion.

Eso es aprendizaje real de base de datos, no decoracion de diagramas.

## Rules

- El ERD sigue siendo la fuente conceptual.
- El SQL debe mantenerse alineado con el ERD.
- Tablas y columnas usan English `snake_case`.
- El schema debe poder ejecutarse desde cero.
- Las credenciales locales no van dentro del schema.
- Cuando el proyecto deje la etapa inicial, los cambios deben pasar a
  migraciones.

## Consequences

- Crear la base local no requiere copiar SQL a mano.
- `make db-up` crea una base inicial desde el schema.
- `make db-reset` borra el volumen y reconstruye desde el schema.
- Editar `database/schema.sql` no cambia una base ya creada; hay que reconstruir
  o crear una migracion.
- El modelo se puede defender en dos niveles: ERD conceptual y SQL fisico.

## Sources

- PostgreSQL constraints documentation:
  <https://www.postgresql.org/docs/current/ddl-constraints.html>
- PostgreSQL identity columns:
  <https://www.postgresql.org/docs/current/ddl-identity-columns.html>
- Docker guide for PostgreSQL initialization:
  <https://docs.docker.com/guides/postgresql/advanced-configuration-and-initialization/>
