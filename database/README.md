# Local Database

Esta carpeta contiene el schema ejecutable de PostgreSQL para Zarvent
Repuestos.

El objetivo es simple: cualquier desarrollador del equipo debe poder crear la
misma base local sin inventar pasos a mano.

## What Exists Here

```text
database/
├── README.md
└── schema.sql
```

`schema.sql` es el archivo que crea la estructura fisica de la base:

- tablas
- primary keys
- foreign keys
- unique constraints
- check constraints
- indices

El ERD explica el diseno. El SQL lo ejecuta.

## Default Database

La base local por defecto usa estos valores:

| Field | Value |
| --- | --- |
| Host | `localhost` |
| Port | `5432` |
| Database | `zarvent_repuestos` |
| User | `zarvent` |
| Password | `zarvent_dev_password` |

Connection string:

```text
postgresql://zarvent:zarvent_dev_password@localhost:5432/zarvent_repuestos
```

Estas credenciales son solo para desarrollo local. No son credenciales de
produccion.

## Recommended Option: Docker

Usa Docker si quieres el entorno mas replicable.

```bash
cp .env.example .env
make db-up
```

Si tu instalacion de Docker exige `sudo`, usa:

```bash
make db-up DOCKER="sudo docker"
```

Que ocurre con esos comandos:

1. `.env.example` se copia como `.env`.
2. Docker Compose lee `.env`.
3. Docker Compose crea un contenedor PostgreSQL 18.4.
4. PostgreSQL crea la base `zarvent_repuestos`.
5. PostgreSQL ejecuta `database/schema.sql` la primera vez.
6. Los datos quedan guardados en un volumen Docker.

## Verify That It Is Running

```bash
make db-status
```

Para ver logs:

```bash
make db-logs
```

Si tienes `psql` instalado:

```bash
psql postgresql://zarvent:zarvent_dev_password@localhost:5432/zarvent_repuestos
```

Luego puedes listar tablas con:

```sql
\dt
```

## Load The Pseudo Dataset

El archivo [`../pseudo_dataset.csv`](../pseudo_dataset.csv) viene de la imagen
[`../pseudo_dataset.jpeg`](../pseudo_dataset.jpeg).

Para validar el CSV, cargarlo en la base y correr tests:

```bash
make db-pseudo-refresh
```

Si Docker requiere `sudo`:

```bash
make db-pseudo-refresh DOCKER="sudo docker"
```

Que hace ese comando:

1. Aplica migraciones pendientes.
2. Lee `pseudo_dataset.csv`.
3. Crea SQL de carga desde el CSV.
4. Inserta repuestos en `part`.
5. Inserta stock en `inventory_stock`.
6. Inserta modelos en `vehicle_model`.
7. Inserta compatibilidades en `part_compatibility`.
8. Ejecuta tests de conteo y consistencia.

La carga es idempotente: puedes correrla varias veces sin duplicar repuestos.

## Reset From Zero

Si cambiaste `database/schema.sql` y quieres reconstruir la base desde cero:

```bash
make db-reset
```

Con Docker usando `sudo`:

```bash
make db-reset DOCKER="sudo docker"
```

Esto borra el volumen Docker y vuelve a crear la base.

Comando equivalente:

```bash
docker compose down -v
docker compose up -d postgres
```

NO confundas reiniciar con reconstruir:

- `docker compose restart` reinicia el contenedor.
- `docker compose down` detiene y elimina el contenedor, pero conserva datos.
- `docker compose down -v` elimina tambien el volumen de datos.

Si el volumen no se borra, `schema.sql` no se ejecuta de nuevo.

## Native PostgreSQL Option

Si tienes PostgreSQL instalado directamente en tu maquina:

```bash
make db-native-create
```

Esto intenta crear la base con tu usuario del sistema.

Si tu instalacion usa otro usuario:

```bash
make db-native-create NATIVE_POSTGRES_USER=postgres
```

Para borrar y recrear la base nativa:

```bash
make db-native-reset NATIVE_POSTGRES_USER=postgres
```

## Files That Should Be Committed

Estos archivos si deben vivir en Git:

- `database/schema.sql`
- `docker-compose.yml`
- `.env.example`
- `Makefile`
- `scripts/database/*.sh`
- documentacion en `docs/`

Estos archivos NO deben subirse:

- `.env`
- volumenes locales de Docker
- dumps temporales con datos reales

## Common Problems

### Port 5432 Is Already Used

Otro PostgreSQL puede estar usando el puerto.

Solucion simple: cambia `POSTGRES_PORT` en `.env`.

```env
POSTGRES_PORT=5433
```

Luego conecta con:

```text
localhost:5433
```

### I Edited schema.sql But Nothing Changed

Eso es esperado si la base ya existia.

El script de inicializacion solo corre cuando el volumen esta vacio.

Usa:

```bash
make db-reset
```

### Docker Needs sudo

Si Docker esta instalado pero tu usuario no tiene permisos, puedes ejecutar:

```bash
make db-up DOCKER="sudo docker"
```

### Docker Is Not Installed

Usa la opcion nativa si tienes PostgreSQL instalado:

```bash
make db-native-create
```

Si no tienes Docker ni PostgreSQL, todavia no tienes un entorno de base de datos
local. Leer el SQL no crea una base. CONCEPTOS PRIMERO.

## Related Documentation

- [Docker and Local PostgreSQL](../docs/database/docker.md)
- [Pseudo Dataset](../docs/database/pseudo_dataset.md)
- [ADR 003: Run the Local Database with Docker Compose](../docs/adr/003-local-database-with-docker-compose.md)
- [ADR 004: Keep an Executable Initial Database Schema](../docs/adr/004-executable-database-schema.md)
- [ERD](../docs/database/erd.md)
