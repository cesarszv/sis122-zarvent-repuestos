# Migrations

son archivos que describen cambios incrementales en la estructura de una base de datos a lo largo del tiempo
funcionan como un `sistema de control de versiones` para el esquema de la base de datos

Por ahora el proyecto usa un schema inicial unico:

```text
database/schema.sql
```

Cuando el modelo cambie, agrega migraciones incrementales aqui en lugar de
editar datos productivos a mano.

Para aplicar migraciones en la base Docker:

```bash
make db-migrate
```

Si Docker requiere `sudo`:

```bash
make db-migrate DOCKER="sudo docker"
```
