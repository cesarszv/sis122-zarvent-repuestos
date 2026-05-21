# Zarvent Repuestos

Proyecto academico para la asignatura `SIS-122` (Base de Datos I) con el
profesor *Ismael Antonio Delgado Huanca*.

Realizado por:

- Cesar Sebastian Zambrana Ventura
- Emanuel Justiniano Peralta

## Objetivo

Zarvent Repuestos modela una empresa ficticia de venta de repuestos de
vehiculos.

El objetivo actual del repositorio es **defender el modelo de base de datos**:
entidades, atributos, claves primarias, claves foraneas, relaciones,
normalizacion y consultas posibles.

No estamos intentando demostrar arquitectura de software avanzada. Eso seria
ruido para este punto del proyecto.

## Alcance actual

El modelo cubre:

- clientes
- proveedores
- catalogo de repuestos
- compatibilidad de repuestos con vehiculos
- stock actual
- ventas
- pagos
- compras
- devoluciones y garantias
- reportes derivados de las tablas operativas

## Stack academico

Por exigencia del curso, el gestor elegido es **MySQL Server**.

Por ahora el foco sigue siendo la base de datos. Primero se entiende el modelo;
despues se escribe cualquier codigo de aplicacion.

## Documentos principales

- [`docs/database/erd.md`](docs/database/erd.md): diagrama ERD compacto.
- [`docs/database/db_explanation.md`](docs/database/db_explanation.md):
  explicacion tabla por tabla.
- [`docs/database/erd_explanation.md`](docs/database/erd_explanation.md):
  defensa profunda del modelo.
- [`docs/database/erd_business_research.md`](docs/database/erd_business_research.md):
  justificacion del ERD desde el negocio.
- [`docs/analysis`](docs/analysis): actores, procesos, procedimientos,
  requerimientos y recursos.
- [`database/schema.sql`](database/schema.sql): borrador manual del esquema SQL
  a completar en MySQL.

## Como trabajar este repo

1. Lee primero `docs/analysis`.
2. Estudia el ERD en `docs/database/erd.md`.
3. Revisa la explicacion tabla por tabla.
4. Escribe el SQL manualmente en `database/schema.sql`.
5. Valida cada tabla entendiendo que regla del negocio protege.

La regla es simple: si no puedes explicar una tabla, no la metas.
