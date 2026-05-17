# Zarvent Repuestos

Proyecto academico para la asignatura `SIS-122` (Base de Datos I) con el
profesor *Ismael Antonio Delgado Huanca*.

Realizado por
- Cesar Sebastian Zambrana Ventura
- Emanuel Justiniano Peralta

---

## Que hicimos?

Se trata de un sistema administrativo para una empresa ficticia de venta de
repuestos de vehiculos que registra ventas, compras, inventario, pagos,
proveedores y garantias usando papel, Excel y WhatsApp.

Incluye:
- Registro de clientes.
- Registro de proveedores.
- Catalogo de repuestos.
- Compatibilidad de repuestos con vehiculos.
- Control de stock por almacen y ubicacion.
- Compras y recepcion de mercaderia.
- Ventas y detalle de productos vendidos.
- Pagos y comprobantes.
- Devoluciones y garantias.
- Reportes de ventas, compras y stock bajo.

## Base de datos

La documentacion de base de datos para PostgreSQL 18.4 y drawDB esta en:

- [`docs/database/erd.md`](docs/database/erd.md)
- [`database/schema.sql`](database/schema.sql)
- [`docs/database/README.md`](docs/database/README.md)
- [`docs/database/docker.md`](docs/database/docker.md)
- [`docs/database/pseudo_dataset.md`](docs/database/pseudo_dataset.md)

Las decisiones tecnicas estan documentadas como ADR:

- [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md)
- [`docs/adr/003-local-database-with-docker-compose.md`](docs/adr/003-local-database-with-docker-compose.md)
- [`docs/adr/004-executable-database-schema.md`](docs/adr/004-executable-database-schema.md)

Para crear una base local replicable:

```bash
cp .env.example .env
make db-up
```

Si usas PostgreSQL instalado directamente en la maquina:

```bash
make db-native-create
```

Para cargar y probar el dataset de ejemplo:

```bash
make db-pseudo-refresh
```
