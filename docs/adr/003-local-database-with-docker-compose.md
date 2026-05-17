# ADR 003: Run the Local Database with Docker Compose

## Status

Accepted.

## Context

Zarvent Repuestos necesita una base local replicable para desarrollo y defensa
academica. "Local" no puede significar "solo funciona en una laptop".

Como el ADR 001 eligio PostgreSQL 18.4, el entorno local tambien debe correr
PostgreSQL 18.4.

## Decision

Usar **Docker Compose** como forma principal de levantar PostgreSQL localmente.

El archivo [`docker-compose.yml`](../../docker-compose.yml) define el servicio
`postgres` con la imagen `postgres:18.4`. La configuracion base vive en
[`.env.example`](../../.env.example); cada desarrollador puede copiarla como
`.env` sin subir credenciales locales.

## How It Works

El servicio `postgres`:

- usa `postgres:18.4`
- expone `5432`
- crea la base `zarvent_repuestos`
- crea el usuario `zarvent`
- usa una contrasena de desarrollo
- guarda datos en un volumen Docker
- monta `database/schema.sql` como script inicial

## Tradeoffs

| Option | Benefits | Costs / Risks |
| --- | --- | --- |
| Docker Compose | Misma version de PostgreSQL para todos; configuracion versionada; entorno borrable con `make db-reset`; facil de revisar en otra maquina. | Requiere Docker y entender volumenes, puertos y variables. Si el volumen ya existe, PostgreSQL no reejecuta scripts de inicializacion. |
| PostgreSQL manual | Valido y soportado con `make db-native-create`. | Depende mas de usuario, puerto, autenticacion, version y permisos de cada maquina. |
| SQLite | Mas simple de ejecutar. | No representa el motor elegido ni practica cliente-servidor, usuarios, puertos, conexiones y constraints reales. |
| Base remota compartida | Puede servir para demos. | Mala base para primer ano: datos compartidos, riesgo de romper a todos, red obligatoria y credenciales comunes. |

Nota importante: Docker no esta roto si editas `schema.sql` y no ves cambios en
una base ya creada. La imagen oficial solo ejecuta `/docker-entrypoint-initdb.d/`
cuando el directorio de datos esta vacio.

## Consequences

- `make db-up` levanta la base.
- `make db-reset` borra volumen y reconstruye desde cero.
- `.env` queda fuera de Git.
- `docker-compose.yml` queda versionado.
- Los datos sobreviven a `docker compose down`.
- Para recargar el schema inicial hay que usar `docker compose down -v` o
  `make db-reset`.

## Sources

- Docker Compose application model:
  <https://docs.docker.com/compose/intro/compose-application-model/>
- Docker Compose environment variables:
  <https://docs.docker.com/compose/how-tos/environment-variables/>
- Docker guide for PostgreSQL initialization:
  <https://docs.docker.com/guides/postgresql/advanced-configuration-and-initialization/>
- PostgreSQL official Docker image:
  <https://hub.docker.com/_/postgres>
