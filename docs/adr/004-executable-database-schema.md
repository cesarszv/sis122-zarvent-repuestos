# ADR 004: Keep an Executable Initial Database Schema

## Status

Accepted.

## Context

El ERD explica el modelo conceptual. Eso es necesario, pero no basta.

Un diagrama dice que existen tablas y relaciones. Una base de datos real necesita
SQL ejecutable: `CREATE TABLE`, primary keys, foreign keys, unique constraints,
check constraints e indices.

Si el equipo solo mantiene un diagrama, cada persona puede interpretar el modelo
de forma distinta. Eso genera inconsistencias. El proyecto necesita una fuente
fisica clara para crear la base local.

## Decision

Mantener [`database/schema.sql`](../../database/schema.sql) como el **schema
inicial ejecutable** de la base de datos.

Este archivo se deriva del ERD documentado en
[`docs/database/erd.md`](../database/erd.md), pero cumple un rol distinto:

- `docs/database/erd.md` explica el modelo.
- `database/schema.sql` crea el modelo en PostgreSQL.

## How It Works

Cuando se crea una base nueva con Docker Compose, el archivo
`database/schema.sql` se monta dentro del contenedor como:

```text
/docker-entrypoint-initdb.d/001_initial_schema.sql
```

La imagen oficial de PostgreSQL ejecuta ese archivo durante la primera
inicializacion, siempre que el volumen de datos este vacio.

El orden del nombre importa. El prefijo `001_` deja claro que es el primer script
de arranque. Si luego existen mas scripts de inicializacion, se pueden numerar
despues:

```text
001_initial_schema.sql
002_seed_reference_data.sql
003_demo_data.sql
```

## Why This Is Better

Un schema ejecutable obliga a convertir ideas en reglas concretas.

Ejemplos:

- `person.person_id` no es solo "un id"; es una primary key.
- `customer.person_id` no es solo "una relacion"; es una foreign key.
- `part.internal_code` no es solo "un codigo"; es un valor unico.
- `sales_order.total_amount` no queda a confianza; tiene reglas de validacion.

Esto es aprendizaje real de base de datos. No es decorar un documento con
cuadritos.

## Rules

- El ERD sigue siendo la fuente conceptual.
- El SQL debe mantenerse alineado con el ERD.
- Los nombres de tablas y columnas deben estar en English `snake_case`.
- El schema debe poder ejecutarse desde cero.
- Las credenciales locales no deben escribirse dentro del schema.
- Los cambios futuros deben convertirse en migraciones cuando el proyecto deje de
  estar en etapa inicial.

## Consequences

- Crear una base local no requiere copiar SQL a mano.
- `make db-up` crea una base inicial usando el schema.
- `make db-reset` borra el volumen y reconstruye la base desde el schema.
- Editar `database/schema.sql` no modifica una base ya creada. Para aplicar
  cambios de arranque hay que reconstruir la base o crear una migracion.
- El equipo puede defender el modelo desde dos niveles: conceptual con el ERD y
  fisico con SQL.

## Sources

- PostgreSQL constraints documentation:
  <https://www.postgresql.org/docs/current/ddl-constraints.html>
- PostgreSQL identity columns:
  <https://www.postgresql.org/docs/current/ddl-identity-columns.html>
- Docker guide for PostgreSQL initialization:
  <https://docs.docker.com/guides/postgresql/advanced-configuration-and-initialization/>
