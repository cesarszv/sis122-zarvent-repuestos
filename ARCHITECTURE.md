# Zarvent Repuestos Architecture

## Estado

Aceptado.

## Decision

Zarvent Repuestos usa **Screaming Architecture**.

La arquitectura debe mostrar primero el negocio: catalogo de repuestos,
compatibilidad vehicular, inventario, ventas, pagos, compras, devoluciones y
reportes.

Si al abrir el proyecto lo primero que se entiende es "PostgreSQL",
"controllers", "repositories", "framework" o "CRUD", el diseno esta flojo. Eso
es infraestructura. El sistema existe para controlar una operacion de venta de
repuestos.

## Contexto

Zarvent Repuestos es un proyecto academico para `SIS-122` (Base de Datos I). El
sistema representa una empresa pequena que vende repuestos para vehiculos.

El problema operativo es claro:

- informacion dispersa entre papel, Excel y WhatsApp
- clientes duplicados
- codigos y descripciones inconsistentes
- stock desactualizado
- ventas, pagos, compras y devoluciones dificiles de trazar
- reportes lentos porque la informacion no esta centralizada

La decision de RDBMS esta en [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md):
el proyecto usa **PostgreSQL 18.4**.

PostgreSQL es el mecanismo de persistencia. La arquitectura es la forma en que
el sistema organiza dominio, casos de uso, reglas y dependencias.

El modelo relacional base esta en [`docs/database/erd.md`](docs/database/erd.md).

## Principio Arquitectonico

La estructura superior del sistema debe revelar lo que el sistema hace, no la
tecnologia que usa.

La pregunta correcta es:

> Que hace Zarvent Repuestos?

Respuesta correcta:

> Controla catalogo de repuestos, compatibilidad vehicular, stock, ventas,
> pagos, compras a proveedores, devoluciones, garantias y reportes.

Eso es lo que debe gritar la arquitectura.

## Drivers Arquitectonicos

### Stock Control

El control de stock es el punto mas importante. En una tienda de repuestos,
vender algo que no existe fisicamente es un error grave.

Camino critico:

```text
PART -> INVENTORY_STOCK -> SALES_ORDER_ITEM
```

El sistema debe permitir saber que repuesto existe, donde esta, cuanto stock hay,
cuando debe reponerse y que venta lo desconto.

### Centralization

Centralizar no significa meter todo en una tabla gigante. Significa que cada
dato importante tiene un lugar responsable y que las demas partes del sistema se
conectan con ese dato mediante claves y relaciones.

### Traceability

El sistema debe conservar historia:

- `SALES_ORDER_ITEM.unit_price` guarda el precio historico de venta
- `PURCHASE_ORDER_ITEM.unit_cost` guarda el costo historico de compra
- `PAYMENT` se relaciona con una venta real
- `RETURN_ORDER_ITEM` se relaciona con un item vendido real
- `INVENTORY_STOCK` muestra el stock actual por repuesto y ubicacion

Si el sistema no puede explicar por que cambio el dinero, el stock o una
devolucion, entonces no es confiable.

### Comfort Without Weak Design

El sistema debe ser comodo para los trabajadores, pero la comodidad no puede
romper el modelo. La UX reduce friccion humana; el modelo relacional protege la
verdad de los datos.

### Academic Defense

Este proyecto debe defenderse con conceptos de Base de Datos I:

- entidades
- atributos
- claves primarias
- claves foraneas
- relaciones
- cardinalidad
- normalizacion
- centralizacion
- seguridad
- consultas y reportes

No se inventan tablas por gusto. Cada modulo o tabla debe salir de actores,
procesos, procedimientos, recursos o reglas documentadas.

## Modulos del Dominio

Los nombres tecnicos se mantienen en native US English. La explicacion puede
estar en espanol porque el documento es academico.

| Module | Responsabilidad | Tablas principales |
| --- | --- | --- |
| `Customers` | Registrar compradores y datos de facturacion sin duplicar identidad personal. | `PERSON`, `CUSTOMER` |
| `Parts Catalog` | Administrar repuestos, categorias, codigos, precios, costos, garantia y estado. | `PART_CATEGORY`, `PART` |
| `Vehicle Compatibility` | Validar que un repuesto corresponda a un modelo de vehiculo. | `VEHICLE_MODEL`, `PART_COMPATIBILITY` |
| `Inventory` | Controlar cantidad disponible, ubicacion y nivel de reposicion. | `INVENTORY_STOCK` |
| `Sales` | Registrar ventas y detalle vendido con precio historico. | `SALES_ORDER`, `SALES_ORDER_ITEM` |
| `Payments` | Registrar pagos, metodo, referencia y estado del cobro. | `PAYMENT` |
| `Suppliers and Purchases` | Gestionar proveedores, ordenes de compra y cantidades recibidas. | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |
| `Returns and Warranties` | Validar devoluciones contra ventas reales y decidir si el producto vuelve a stock. | `RETURN_ORDER`, `RETURN_ORDER_ITEM` |
| `Reports` | Consultar datos operativos para decisiones de gerencia. | Derivado de ventas, pagos, compras e inventario |
| `Access Control` | Controlar usuarios, roles, permisos y responsables. | Extension futura; no esta en el ERD compacto |

El ERD compacto no incluye todo lo posible. Eso esta bien. Mas tablas no
significan mejor modelo.

## Casos de Uso Principales

### Register Customer

`Customers` registra datos civiles en `PERSON` y datos comerciales en
`CUSTOMER`.

Regla: `CUSTOMER` no debe duplicar nombres, telefonos ni direcciones que ya
pertenecen a `PERSON`.

### Find Spare Part

`Parts Catalog`, `Vehicle Compatibility` e `Inventory` permiten buscar repuestos,
verificar compatibilidad y revisar stock antes de ofrecer el producto.

Regla: la compatibilidad no debe quedar como una nota suelta en `PART`. Es una
relacion muchos-a-muchos entre repuestos y modelos de vehiculo; por eso existe
`PART_COMPATIBILITY`.

### Sell Spare Part

`Sales`, `Customers`, `Inventory` y `Payments` registran cliente, detalle de
venta, stock disponible y pago.

Regla: `SALES_ORDER_ITEM.unit_price` guarda el precio historico. NO reconstruyas
ventas pasadas usando el precio actual de `PART`; eso corrompe el historial.

### Purchase From Supplier

`Suppliers and Purchases` e `Inventory` registran proveedor, orden de compra,
repuestos solicitados, cantidades recibidas y costo historico.

Regla: `PURCHASE_ORDER_ITEM.unit_cost` existe porque los costos cambian. El
costo de una compra especifica pertenece al item de compra.

### Return or Warranty

`Returns and Warranties`, `Sales` e `Inventory` validan devoluciones contra una
venta real.

Regla: una devolucion debe apuntar a un `SALES_ORDER_ITEM`. Sin evidencia de
venta original, el sistema no puede defender stock, dinero ni garantia.

### Report Operations

`Reports` responde preguntas operativas:

- productos bajos en stock
- productos mas vendidos
- compras pendientes
- ventas con pagos pendientes
- devoluciones en revision
- ingresos por periodo

Regla: los reportes son consultas sobre tablas operativas. Si las tablas base
estan mal, el reporte tambien estara mal.

## Direccion de Dependencias

La direccion conceptual debe ser:

```text
Business use cases
  -> domain rules and entities
  -> PostgreSQL persistence
  -> UI, reports, scripts and external tools
```

La regla de negocio no debe depender de una interfaz especifica. Una venta sigue
siendo una venta si se registra desde una app web, una app de escritorio, un
script o una futura app movil.

PostgreSQL ayuda a proteger las reglas con `PK`, `FK`, `UNIQUE`, `CHECK` y
transacciones, pero no reemplaza el diseno del dominio.

## Estructura Recomendada

Si el proyecto crece con codigo de aplicacion, la estructura debe priorizar
modulos del negocio:

```text
src/
  modules/
    customers/
    parts-catalog/
    vehicle-compatibility/
    inventory/
    sales/
    payments/
    suppliers-purchases/
    returns-warranties/
    reports/
    access-control/
  shared/
  infrastructure/
    database/
      postgresql/
docs/
  analysis/
  adr/
  database/
scripts/
  migrations/
```

El framework, si aparece, debe servir a estos modulos. No debe convertirse en el
idioma principal del proyecto.

## Limite de la Base de Datos

La base debe proteger como minimo:

- identidad con `PRIMARY KEY`
- integridad relacional con `FOREIGN KEY`
- prevencion de duplicados con `UNIQUE`
- valores validos con `CHECK`
- consistencia de operaciones con transacciones
- precios y costos historicos en tablas de detalle

El ERD es la fuente conceptual. El SQL fisico debe adaptar ese diseno a
PostgreSQL 18.4.

## Reglas de Calidad

### Naming

Los nombres tecnicos usan native US English:

- tablas
- columnas
- modulos
- carpetas de codigo
- variables
- estados internos

La explicacion documental puede estar en espanol. Lo que NO se debe hacer es
mezclar idiomas dentro de la misma capa tecnica.

### Data Integrity

El modelo debe prevenir errores evitables:

- clientes repetidos
- repuestos sin codigos estables
- ventas sin detalle
- pagos sin venta
- devoluciones sin item vendido original
- compras sin proveedor
- stock sin repuesto

Si la base permite incoherencias, tarde o temprano la aplicacion terminara
guardandolas. No es mala suerte; es falta de diseno.

### Scope Control

El ERD compacto deja fuera algunos modulos futuros:

- usuarios, roles y permisos completos
- facturas y comprobantes tributarios detallados
- historial completo de movimientos de inventario
- marcas de vehiculo normalizadas
- auditoria avanzada

Son extensiones validas, pero no son obligatorias para el modelo compacto de
Base de Datos I.

## Alternativas Consideradas

| Alternativa | Ventaja | Desventaja |
| --- | --- | --- |
| Layer-first architecture | Facil de reconocer para CRUD pequeno. | Esconde el negocio detras de capas tecnicas. |
| Database-first only architecture | Se alinea con Base de Datos I. | Puede explicar tablas sin explicar procesos. |
| Screaming Architecture | Comunica el negocio desde la primera lectura. | Exige entender el dominio. |

La desventaja de Screaming Architecture es aceptable. Si el equipo no puede
explicar el dominio, no entiende el proyecto.

## Consecuencias

- La documentacion debe explicar modulos desde procesos reales.
- El codigo futuro debe agruparse primero por dominio y luego por detalle
  tecnico.
- PostgreSQL 18.4 sigue siendo el RDBMS elegido.
- El ERD sigue siendo la fuente conceptual del modelo relacional.
- Los reportes deben salir de tablas operativas.
- Toda tabla nueva debe justificarse con actores, procesos, procedimientos,
  recursos o reglas de negocio.

## Resumen para Defensa

Zarvent Repuestos usa Screaming Architecture porque el proyecto debe organizarse
alrededor de su negocio: repuestos, compatibilidad, inventario, ventas, pagos,
compras, proveedores, devoluciones, garantias y reportes.

PostgreSQL 18.4 es el gestor elegido, pero no es la arquitectura. La
arquitectura es la estructura de dominio y casos de uso que PostgreSQL ayuda a
persistir y proteger.

Esta decision es coherente con el ERD porque las tablas principales representan
conceptos del negocio, no conceptos de framework. El modelo es compacto, pero
suficiente para defender centralizacion, normalizacion, trazabilidad e
integridad relacional.

## Sources

- Robert C. Martin, "Screaming Architecture":
  <https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html>
- Robert C. Martin, "The Clean Architecture":
  <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>
- Local ADR: [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md)
- Local ERD: [`docs/database/erd.md`](docs/database/erd.md)
- Local process analysis: [`docs/analysis/processes.md`](docs/analysis/processes.md)
