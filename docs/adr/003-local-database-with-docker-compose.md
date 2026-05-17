# ADR 003: Run the Local Database with Docker Compose

## Status

Accepted.

## Context

Zarvent Repuestos necesita una base de datos local para desarrollo y defensa
academica. Esa base debe poder levantarse en mas de una maquina sin depender de
configuraciones manuales escondidas.

Una base de datos "local" no debe significar "solo funciona en la laptop de una
persona". Eso es mediocridad tecnica. Si el proyecto se revisa en otra maquina,
el equipo debe poder reconstruir el entorno con instrucciones claras.

El proyecto usa PostgreSQL 18.4 como RDBMS. Por eso el entorno local tambien
debe correr PostgreSQL 18.4, no una version distinta elegida al azar.

## Decision

Usar **Docker Compose** como forma principal de levantar PostgreSQL localmente.

El archivo [`docker-compose.yml`](../../docker-compose.yml) define un servicio
llamado `postgres` basado en la imagen oficial `postgres:18.4`.

La configuracion local vive en [`.env.example`](../../.env.example). Cada
desarrollador puede copiarlo como `.env` y ajustar valores locales sin subir
credenciales reales al repositorio.

## How It Works

Docker Compose lee un archivo YAML y crea servicios. En este proyecto, el unico
servicio definido por ahora es la base de datos.

El servicio:

- usa la imagen `postgres:18.4`
- expone el puerto interno `5432` en el puerto local `5432`
- crea la base `zarvent_repuestos`
- crea el usuario `zarvent`
- usa una contrasena de desarrollo
- guarda los datos en un volumen Docker persistente
- monta `database/schema.sql` como script de inicializacion

## Why Docker Compose

### Ventajas

- Todos trabajan con la misma version de PostgreSQL.
- La configuracion queda escrita en el repo, no en instrucciones de memoria.
- El entorno se puede borrar y reconstruir con `make db-reset`.
- Evita que cada estudiante instale PostgreSQL de una forma diferente.
- Facilita revisar el proyecto en otra maquina.

### Costos

- Requiere Docker instalado.
- El equipo debe entender volumenes, puertos y variables de entorno.
- Si el volumen ya existe, PostgreSQL no vuelve a ejecutar los scripts de
  inicializacion automaticamente.

Ese ultimo punto es importante. Docker no esta roto si editas `schema.sql` y no
ves cambios en una base ya creada. La imagen oficial de PostgreSQL solo ejecuta
los scripts de `/docker-entrypoint-initdb.d/` cuando el directorio de datos esta
vacio.

## Alternatives Considered

### Install PostgreSQL manually

Es valido y el proyecto lo soporta con `make db-native-create`.

El problema es que depende mas de la configuracion de cada maquina: usuario,
puerto, autenticacion, version instalada y permisos del sistema.

### Use SQLite

Seria mas simple de ejecutar, pero no representa el motor elegido en el ADR 001.
Tambien debilita el aprendizaje de cliente-servidor, usuarios, puertos,
volumenes, conexiones y constraints reales de PostgreSQL.

### Use a remote shared database

Podria funcionar para demostraciones, pero es mala base para desarrollo de
primer ano: si alguien rompe datos, afecta a todos. Ademas exige red,
credenciales compartidas y mas cuidado operacional.

## Consequences

- El comando principal para levantar la base es `make db-up`.
- El comando principal para reconstruirla desde cero es `make db-reset`.
- `.env` queda fuera de Git porque puede contener credenciales locales.
- `docker-compose.yml` queda versionado porque define infraestructura del
  proyecto.
- Los datos locales viven en un volumen Docker y sobreviven a `docker compose
  down`.
- Para forzar la recarga del schema inicial hay que borrar el volumen con
  `docker compose down -v` o usar `make db-reset`.

## Sources

- Docker Compose application model:
  <https://docs.docker.com/compose/intro/compose-application-model/>
- Docker Compose environment variables:
  <https://docs.docker.com/compose/how-tos/environment-variables/>
- Docker guide for PostgreSQL initialization:
  <https://docs.docker.com/guides/postgresql/advanced-configuration-and-initialization/>
- PostgreSQL official Docker image:
  <https://hub.docker.com/_/postgres>
