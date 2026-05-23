# Architecture

Este documento explica la arquitectura actual de Zarvent Repuestos.

La meta no es parecer una empresa grande. La meta es que un estudiante junior
pueda abrir el repo, entender donde va cada cosa y defender la decision ante el
profesor.

## Idea principal

El proyecto usa una arquitectura modular simple.

Eso significa:

- el codigo se separa por responsabilidad;
- los nombres de carpetas dicen que hace el sistema;
- no se crean capas vacias solo porque suenan profesionales;
- la base de datos sigue siendo el centro academico del proyecto;
- Python y Flask existen para demostrar uso, no para esconder el modelo
  relacional.

## Screaming Architecture

Screaming Architecture significa que la estructura del proyecto debe "gritar"
de que trata el sistema.

En este repo, el dominio es una tienda de repuestos. Por eso, cuando el sistema
crezca, deberian aparecer modulos con nombres como:

| Modulo futuro | Que representaria |
| --- | --- |
| `catalog` | repuestos, categorias y compatibilidad vehicular |
| `inventory` | stock, ubicaciones y niveles de reposicion |
| `sales` | ventas, detalles de venta y pagos |
| `purchases` | proveedores y ordenes de compra |
| `returns` | devoluciones, garantias y resoluciones |

Esos modulos aun no existen en `src/` porque todavia no hay codigo real para
ellos. Crear carpetas vacias ahora seria ruido.

La regla es simple:

> Si una carpeta no tiene codigo real que defender, todavia no merece existir.

## Modular Architecture

Modular Architecture significa que cada parte del sistema tiene una
responsabilidad clara.

Un modulo no es solo una carpeta. Un modulo es una parte del negocio o de la
aplicacion que se puede explicar con una frase.

La estructura actual es pequena:

```text
src/
`-- zarvent_repuestos/
    |-- access/
    |   `-- user_service.py
    |-- database/
    |   `-- connection.py
    `-- web/
        |-- app.py
        |-- templates/
        `-- static/
```

## Responsabilidades actuales

| Carpeta | Responsabilidad | Por que existe |
| --- | --- | --- |
| `access` | Login, usuarios y contrasenas. | La app actual necesita autenticar un usuario demo. |
| `database` | Conexion tecnica con MySQL. | El proyecto usa MySQL Server y `mysql-connector-python`. |
| `web` | Interfaz Flask. | Permite probar el login en navegador. |

Esta separacion es suficiente para el alcance actual.

No usamos carpetas como `domain`, `application`, `adapters` o `use_cases`
porque el prototipo todavia es muy pequeno. Esas carpetas pueden ser buenas en
proyectos mas grandes, pero aqui agregarian conceptos antes de necesitarlos.

## Flujo del login

Cuando un usuario intenta entrar desde la pantalla web, el flujo es:

1. `web/app.py` recibe el formulario Flask.
2. `web/app.py` llama a `access/user_service.py`.
3. `access/user_service.py` busca el usuario en MySQL.
4. `database/connection.py` abre la conexion usando `.env`.
5. `access/user_service.py` compara la contrasena con `bcrypt`.
6. `web/app.py` muestra el resultado en `login.html`.

En forma corta:

```text
browser -> web -> access -> database -> MySQL
```

Esa direccion importa. La interfaz web puede llamar al modulo de acceso, y el
modulo de acceso puede usar la base de datos. La base de datos no debe conocer
Flask ni pantallas.

## Scripts de base de datos

Los scripts de base de datos viven en:

```text
scripts/database/
```

La estructura actual es:

```text
scripts/database/
|-- run_mysql_script.py
|-- 001_create_project_database.sql
|-- 002_create_login_users_table.sql
|-- 003_create_mysql_app_users.sql
|-- seed_demo_login_user.py
`-- check_login_database.py
```

### Orden de ejecucion

1. `001_create_project_database.sql`
   - Crea la base `sis122_zarvent_repuestos`.

2. `002_create_login_users_table.sql`
   - Crea la tabla `users` usada por el login demo.

3. `003_create_mysql_app_users.sql`
   - Crea el usuario tecnico `zarvent_app`.
   - Le da permisos solo sobre `sis122_zarvent_repuestos`.

4. `seed_demo_login_user.py`
   - Crea o actualiza el usuario demo `admin`.
   - Guarda la contrasena con hash `bcrypt`.

5. `check_login_database.py`
   - Verifica conexion, base activa, tabla `users` y cantidad de usuarios.

`run_mysql_script.py` existe porque en algunos equipos el comando `mysql` no
esta en el `PATH`. Este script permite ejecutar SQL usando Python y
`mysql-connector-python`.

## Por que hay dos carpetas llamadas database

Hay dos usos distintos:

| Ruta | Uso |
| --- | --- |
| `database/` | SQL academico del modelo relacional. |
| `src/zarvent_repuestos/database/` | Codigo Python para conectarse a MySQL. |

La primera carpeta pertenece al estudio de la base de datos.

La segunda pertenece a la aplicacion Python.

No son la misma cosa.

## Reglas para agregar codigo nuevo

### 1. Primero debe existir una razon del negocio

No se agrega un modulo porque "suena bien". Se agrega porque aparece en:

- `docs/analysis/processes.md`;
- `docs/analysis/requirements.md`;
- `docs/database/erd.md`;
- `database/schema.sql`.

Ejemplo: si se implementa stock, el modulo deberia llamarse `inventory`, porque
esa palabra existe en el modelo y en el negocio.

### 2. El nombre debe ser claro en ingles

Los nombres tecnicos van en ingles:

- `access`
- `database`
- `web`
- `user_service.py`
- `run_mysql_script.py`

Las explicaciones academicas pueden estar en espanol.

### 3. No crear carpetas vacias

Una carpeta nueva debe tener codigo real.

No se debe crear esto todavia:

```text
sales/
inventory/
purchases/
returns/
```

Se crean cuando exista una pantalla, servicio o script que los use.

### 4. No esconder SQL detras de magia

Este es un proyecto de Base de Datos I. La aplicacion puede ayudar, pero no debe
ocultar lo importante:

- tablas;
- claves primarias;
- claves foraneas;
- restricciones;
- normalizacion;
- consultas;
- reglas de negocio.

Por eso no usamos ORM por ahora. Es mejor ver el SQL y entenderlo.

### 5. Mantener dependencias simples

Las dependencias actuales son suficientes:

- `mysql-connector-python`
- `python-dotenv`
- `bcrypt`
- `flask`

Agregar una libreria nueva requiere una razon concreta.

## Como crecer sin sobreingenieria

Si manana se implementa ventas, una estructura razonable seria:

```text
src/zarvent_repuestos/
|-- sales/
|   `-- sales_service.py
|-- access/
|-- database/
`-- web/
```

Si despues ventas crece mucho, recien ahi se podria dividir:

```text
sales/
|-- sales_service.py
|-- sales_repository.py
`-- payment_service.py
```

Pero esa division solo vale la pena cuando el archivo se vuelve dificil de
leer. Antes de eso, es solo ruido.

## Regla de defensa ante el profesor

Si te preguntan por la arquitectura, la respuesta corta es:

> Usamos una arquitectura modular simple. Los modulos se organizan por
> responsabilidades reales del sistema. `access` maneja login, `database`
> maneja la conexion MySQL y `web` maneja Flask. No creamos capas avanzadas
> porque el objetivo del curso es entender y defender el modelo relacional.

Esa respuesta es honesta, tecnica y defendible.
