# Database Documentation

Esta carpeta contiene la documentacion relacionada con el **diseno de la base de
datos** para PostgreSQL 18.4.

La documentacion se separa en dos niveles:

- diseno conceptual: que entidades existen y por que
- implementacion local: como se crea y ejecuta la base en PostgreSQL

## Main Documents

| Document | Purpose |
| --- | --- |
| [`erd.md`](erd.md) | Diagrama entidad-relacion compacto del negocio. |
| [`db_explanation.md`](db_explanation.md) | Explicacion tabla por tabla para defensa academica. |
| [`erd_business_research.md`](erd_business_research.md) | Justificacion operativa del ERD desde procesos reales. |
| [`erd_explanation.md`](erd_explanation.md) | Explicacion mas profunda del modelo relacional. |
| [`docker.md`](docker.md) | Como funciona PostgreSQL local con Docker Compose. |
| [`pseudo_dataset.md`](pseudo_dataset.md) | Como cargar y probar `pseudo_dataset.csv`. |
| [`../../database/schema.sql`](../../database/schema.sql) | Schema SQL ejecutable para crear la base. |

## Decisions

Las decisiones tecnicas estables estan en ADR:

- [`../adr/001-RDBMS.md`](../adr/001-RDBMS.md): PostgreSQL 18.4 como RDBMS.
- [`../adr/003-local-database-with-docker-compose.md`](../adr/003-local-database-with-docker-compose.md): Docker Compose para la base local.
- [`../adr/004-executable-database-schema.md`](../adr/004-executable-database-schema.md): `database/schema.sql` como schema inicial ejecutable.

## Local Database

Para crear la base local con Docker:

```bash
cp .env.example .env
make db-up
```

Para borrar datos locales y reconstruir desde cero:

```bash
make db-reset
```

Para cargar y probar el dataset de ejemplo:

```bash
make db-pseudo-refresh
```

Para detalles completos, lee [`docker.md`](docker.md) y
[`../../database/README.md`](../../database/README.md).
