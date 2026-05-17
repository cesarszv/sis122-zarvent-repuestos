# Docker and Local PostgreSQL

Este documento explica como se levanta la base de datos local de Zarvent
Repuestos usando Docker Compose.

La idea no es memorizar comandos. La idea es entender que problema resuelve cada
archivo.

## What We Are Building

Queremos una base de datos PostgreSQL local que sea:

- repetible
- facil de levantar
- facil de borrar y reconstruir
- igual para todos los miembros del equipo
- compatible con el schema del proyecto

La base corre en un contenedor Docker. El contenedor usa la imagen oficial
`postgres:18.4`.

## Files Involved

| File | Purpose |
| --- | --- |
| `docker-compose.yml` | Define el servicio PostgreSQL, puertos, volumenes y variables. |
| `.env.example` | Plantilla de configuracion local. |
| `.env` | Configuracion real de tu maquina. No se sube a Git. |
| `database/schema.sql` | SQL que crea las tablas, relaciones y constraints. |
| `Makefile` | Atajos para no escribir comandos largos. |
| `database/README.md` | Guia rapida para crear o reiniciar la base. |

## The Service

En `docker-compose.yml`, el servicio se llama:

```text
postgres
```

Eso significa que Docker Compose administra un contenedor PostgreSQL como parte
del proyecto.

No estamos instalando PostgreSQL directamente en el sistema operativo. Estamos
ejecutandolo dentro de un contenedor.

## Image

```yaml
image: postgres:18.4
```

Esto indica la version exacta de PostgreSQL que queremos usar.

Fijar la version es importante. Si una maquina usa PostgreSQL 15, otra usa 16 y
otra usa 18, despues aparecen errores que no son del modelo, sino del entorno.

## Environment Variables

```yaml
POSTGRES_DB: ${POSTGRES_DB:-zarvent_repuestos}
POSTGRES_USER: ${POSTGRES_USER:-zarvent}
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-zarvent_dev_password}
```

Estas variables se usan durante la primera inicializacion del contenedor:

- `POSTGRES_DB`: nombre de la base de datos inicial
- `POSTGRES_USER`: usuario creado por PostgreSQL
- `POSTGRES_PASSWORD`: contrasena del usuario

El formato `${VARIABLE:-default}` significa:

> usa el valor de `.env` si existe; si no existe, usa el valor por defecto.

## Ports

```yaml
ports:
  - "${POSTGRES_PORT:-5432}:5432"
```

PostgreSQL escucha dentro del contenedor en el puerto `5432`.

El primer `5432` es el puerto de tu maquina. El segundo `5432` es el puerto del
contenedor.

Por eso la conexion desde tu maquina queda asi:

```text
localhost:5432
```

Si otro servicio ya usa el puerto 5432, puedes cambiar `POSTGRES_PORT` en `.env`.

## Volumes

El proyecto usa dos montajes:

```yaml
volumes:
  - zarvent_postgres_data:/var/lib/postgresql/data
  - ./database/schema.sql:/docker-entrypoint-initdb.d/001_initial_schema.sql:ro
```

### Data Volume

```text
zarvent_postgres_data:/var/lib/postgresql/data
```

Este volumen guarda los datos reales de PostgreSQL.

Si apagas el contenedor, los datos no desaparecen. Eso es correcto: una base de
datos no debe perder informacion solo porque reiniciaste Docker.

### Init Script Mount

```text
./database/schema.sql:/docker-entrypoint-initdb.d/001_initial_schema.sql:ro
```

Esto monta el schema del proyecto dentro de la carpeta especial de inicializacion
de la imagen oficial de PostgreSQL.

`ro` significa read-only. El contenedor puede leer el archivo, pero no
modificarlo.

## Important Initialization Rule

PostgreSQL ejecuta los archivos de `/docker-entrypoint-initdb.d/` solo cuando el
directorio de datos esta vacio.

Eso significa:

- primera vez que levantas la base: ejecuta `schema.sql`
- reinicio normal: NO vuelve a ejecutar `schema.sql`
- si quieres reconstruir desde cero: borra el volumen

Comando recomendado:

```bash
make db-reset
```

Comando equivalente:

```bash
docker compose down -v
docker compose up -d postgres
```

## Commands

### Start Database

```bash
cp .env.example .env
make db-up
```

Esto crea el contenedor si no existe y lo deja corriendo en segundo plano.

Si tu instalacion de Docker requiere `sudo`:

```bash
make db-up DOCKER="sudo docker"
```

### Check Status

```bash
make db-status
```

Muestra si el contenedor esta arriba.

### Read Logs

```bash
make db-logs
```

Sirve para ver errores de arranque, credenciales incorrectas o fallos de SQL.

### Reset Database

```bash
make db-reset
```

Esto borra el volumen local y vuelve a crear la base desde `database/schema.sql`.

Usalo cuando cambiaste el schema inicial y quieres reconstruir todo desde cero.

Si Docker requiere `sudo`:

```bash
make db-reset DOCKER="sudo docker"
```

## Default Connection

```text
Host: localhost
Port: 5432
Database: zarvent_repuestos
User: zarvent
Password: zarvent_dev_password
```

Connection string:

```text
postgresql://zarvent:zarvent_dev_password@localhost:5432/zarvent_repuestos
```

## What This Does Not Solve

Docker no arregla un mal modelo de datos.

Docker solo hace repetible el entorno. La calidad de la base depende de:

- buen ERD
- buen SQL
- constraints correctos
- nombres consistentes
- migraciones cuando el modelo cambie

## Sources

- Docker Compose application model:
  <https://docs.docker.com/compose/intro/compose-application-model/>
- Docker Compose environment variables:
  <https://docs.docker.com/compose/how-tos/environment-variables/>
- Docker guide for PostgreSQL initialization:
  <https://docs.docker.com/guides/postgresql/advanced-configuration-and-initialization/>
- PostgreSQL official Docker image:
  <https://hub.docker.com/_/postgres>
