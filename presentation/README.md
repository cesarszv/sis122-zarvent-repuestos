# Zarvent Repuestos - Artefacto Docker para la defensa

Este directorio contiene todo lo necesario para correr la app en
cualquier maquina con **Docker Desktop** (Windows, macOS o Linux), sin
instalar Python, `uv` ni MySQL en el sistema host.

## Contenido

```text
presentation/
  docker-compose.yml       # define los servicios `mysql` y `web`
  Dockerfile.web           # imagen del servicio `web`
  .env.example             # plantilla de variables de entorno
  README.md                # este archivo
  docker/
    entrypoint.sh          # pasos de inicio del contenedor `web`
    wait_for_mysql.py      # polling hasta que MySQL responda queries
    01-grants.sql          # GRANTs del usuario `zarvent_app`
  source/                  # COPIA del repo, generada por build script
```

`source/` **no se versiona** en git. Se regenera con:

```bash
uv run python scripts/presentation/build_docker_artifact.py
```

## Requisitos

- Docker Desktop instalado y corriendo.
  - Windows: descargar de <https://www.docker.com/products/docker-desktop/>.
  - Activar WSL2 si Windows lo pide.
- Si es la primera vez, las imagenes `python:3.14-slim` y `mysql:8.4`
  se descargan automaticamente. **Se necesita internet** en esa
  primera corrida. Luego quedan en la cache local.

## Pasos para arrancar (Windows)

1. Abrir Docker Desktop y esperar a que diga "Docker is running".
2. Abrir una terminal (PowerShell o CMD).
3. Ir a esta carpeta:

   ```powershell
   cd presentation
   ```

4. (Opcional) Crear tu propio `.env`:

   ```powershell
   copy .env.example .env
   ```

   Si no lo haces, Docker Compose usa los defaults del
   `docker-compose.yml` y todo funciona igual.

5. Generar la copia del codigo fuente (solo la primera vez, o cuando
   cambie el repo):

   ```powershell
   # Desde la raiz del repo, en una terminal con `uv` instalado:
   uv run python scripts/presentation/build_docker_artifact.py
   ```

   Si solo tenes Docker y no queres instalar `uv`, podes saltar este
   paso y copiar `presentation/` ya construido. El script se corre
   en Ubuntu Linux antes de copiar al USB.

6. Levantar los servicios:

   ```powershell
   docker compose up --build -d
   ```

   La primera vez tarda unos minutos (descarga de imagenes +
   `uv sync`).

7. Abrir la app en el navegador:

   ```text
   http://127.0.0.1:5000
   ```

   Login:

   ```text
   usuario: admin
   contrasena: admin123
   ```

## Operaciones frecuentes

| Quiero... | Comando |
| --- | --- |
| Ver logs del contenedor web | `docker compose logs -f web` |
| Ver logs del contenedor MySQL | `docker compose logs -f mysql` |
| Reiniciar la web (toma cambios en `.py`) | `docker compose restart web` |
| Detener todo (sin borrar datos) | `docker compose down` |
| Reset total (borra la base de datos) | `docker compose down -v` y luego `docker compose up --build -d` |
| Reconstruir la imagen web | `docker compose build --no-cache web` |
| Entrar al contenedor web como shell | `docker compose exec web bash` |
| Entrar al contenedor MySQL como root | `docker compose exec mysql mysql -uroot -p` (password: el de `MYSQL_ROOT_PASSWORD`) |

## Editar codigo durante la defensa

`docker-compose.yml` monta `./source` como volumen en `/workspace`
dentro del contenedor. Eso significa que cualquier cambio que hagas
en `presentation/source/` desde Windows se refleja en el contenedor.

| Cambio en... | Hay que reiniciar el contenedor? |
| --- | --- |
| `presentation/source/src/**/*.py` | Si. `docker compose restart web`. |
| `presentation/source/src/zarvent_repuestos/web/templates/**/*.html` | No. `TEMPLATES_AUTO_RELOAD=True` en `app.py` recarga solo. |
| `presentation/source/src/zarvent_repuestos/web/static/**/*` | No. Flask sirve estaticos por cada request. |
| `presentation/source/pyproject.toml` o `uv.lock` | Si. `docker compose build --no-cache web && docker compose up -d web`. |

## Conexion desde JetBrains DataGrip

| Campo | Valor |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `3307` |
| User | `zarvent_app` |
| Password | `change_me` |
| Database | `sis122_zarvent_repuestos` |
| URL JDBC | `jdbc:mysql://127.0.0.1:3307/sis122_zarvent_repuestos` |

## Tablas que valida este artefacto

El contenedor web corre `src/zarvent_repuestos/database/init_db.py`
que crea, en este orden:

- `person`
- `customer`
- `supplier`
- `part_category`
- `part`
- `inventory_stock`
- `sales_order`
- `sales_order_item`
- `payment`
- `purchase_order`
- `purchase_order_item`
- `users`

Y dos vistas academicas (`vw_low_stock_parts`, `vw_daily_sales_summary`).

El ERD documentado en `docs/database/erd.md` es mas amplio
(`return_order`, `return_order_item`, `vehicle_model`,
`part_compatibility`). Esas tablas **no se crean en runtime**: son
alcance documental del modelo academico. Si el profesor pregunta por
ellas, la respuesta esta en `presentation/docs/20260604.md` (seccion
11: "Diferencia entre ERD completo y tablas de la demo").

## Diagnostico de problemas

### El contenedor `web` queda reiniciandose

```powershell
docker compose logs web
```

Si el error es `Can't connect to MySQL server`, el `wait_for_mysql.py`
llego al timeout. Posibles causas:

- El healthcheck de `mysql` fallo. Ver `docker compose ps`. Si
  `mysql` no esta `(healthy)`, mirar `docker compose logs mysql`.
- La primera vez, MySQL tarda en inicializar el volumen
  (aprox. 30-60 segundos). `WAIT_FOR_MYSQL_TIMEOUT_SECONDS=120` da
  margen.

### Cambie el password de MySQL y ahora nada conecta

Borrar el volumen nombrado y volver a levantar:

```powershell
docker compose down -v
docker compose up --build -d
```

El init script `docker/01-grants.sql` se ejecuta la primera vez
que se inicializa un volumen vacio. Si cambias el password y no
borras el volumen, los GRANTs quedan con el password viejo.

### El navegador no abre `http://127.0.0.1:5000`

1. Confirmar que el contenedor `web` este `(running)`: `docker compose ps`.
2. Confirmar que el puerto `5000` del host este libre: en
   `docker-compose.yml` cambiar `WEB_HOST_PORT=5001` y volver a
   `docker compose up -d web`.
3. Ver logs: `docker compose logs web`.

### Quiero empezar desde cero

```powershell
docker compose down -v
docker compose up --build -d
```

Esto borra el volumen de MySQL, asi que la base se vuelve a crear
desde cero y el seed la puebla de nuevo. El codigo en
`presentation/source/` no se toca.
