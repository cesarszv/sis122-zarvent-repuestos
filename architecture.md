# Zarvent Repuestos Architecture

## Estado

Aceptado.

## Decision

Zarvent Repuestos usara **Screaming Architecture**.

La arquitectura debe gritar el dominio del negocio antes que la tecnologia:

- `Parts Catalog`
- `Vehicle Compatibility`
- `Inventory`
- `Sales`
- `Payments`
- `Suppliers and Purchases`
- `Returns and Warranties`
- `Reports`
- `Access Control`

Si alguien abre el proyecto y lo primero que entiende es "PostgreSQL",
"controllers", "repositories", "framework" o "CRUD", el diseno esta flojo.
Eso es infraestructura. El sistema existe para controlar una operacion de venta
de repuestos.

CONCEPTO BASICO: la arquitectura no debe presumir herramientas; debe mostrar
casos de uso.

## Contexto

Zarvent Repuestos es un proyecto academico para `SIS-122` (Base de Datos I). El
sistema representa una empresa pequena de venta de repuestos de vehiculos.

El problema documentado no es inventado:

- la informacion esta dispersa en papel, Excel y WhatsApp
- los clientes pueden duplicarse
- los repuestos pueden tener codigos o descripciones inconsistentes
- el stock puede quedar desactualizado
- las ventas, pagos, compras y devoluciones son dificiles de trazar
- los reportes tardan porque la informacion no esta centralizada

La decision de RDBMS esta en [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md):
el proyecto usa **PostgreSQL 18.4**.

Pero PostgreSQL NO es la arquitectura. PostgreSQL es el mecanismo de
persistencia. La arquitectura es la forma en que el sistema organiza el dominio,
los casos de uso, las reglas y las dependencias.

El modelo relacional base esta en [`docs/database/erd.md`](docs/database/erd.md).
Ese ERD ya muestra el nucleo del negocio: clientes, catalogo, compatibilidad,
inventario, ventas, pagos, compras y devoluciones.

## Principio Arquitectonico

Screaming Architecture propone que la estructura superior del sistema revele sus
casos de uso y su proposito de negocio. La arquitectura no debe estar dominada
por frameworks, base de datos, web, librerias o carpetas tecnicas genericas.

La pregunta correcta es:

> Que hace Zarvent Repuestos?

La respuesta mediocre seria:

> Usa PostgreSQL.

La respuesta correcta es:

> Controla catalogo de repuestos, compatibilidad vehicular, stock, ventas,
> pagos, compras a proveedores, devoluciones, garantias y reportes.

Eso es lo que debe gritar la arquitectura.

## Drivers Arquitectonicos

### Stock Control

El punto mas importante del sistema es el control de stock. En una tienda de
repuestos, vender algo que no existe fisicamente es un error grave. Registrar
datos sin controlar la realidad operativa es solo hacer una planilla mas bonita.

La arquitectura debe proteger este camino:

```text
PART -> INVENTORY_STOCK -> SALES_ORDER_ITEM
```

El sistema debe permitir saber:

- que repuesto existe
- donde esta ubicado
- cuanto stock disponible hay
- cuando debe reponerse
- que venta lo desconto

### Centralization

El sistema debe centralizar informacion que hoy esta repartida entre registros
manuales, Excel y WhatsApp.

Centralizar no significa meter todo en una tabla gigante. Eso es pereza
disfrazada de simplicidad. Centralizar significa que cada dato importante tiene
un lugar responsable y que las demas partes del sistema se relacionan con ese
dato mediante claves y relaciones.

### Traceability

El sistema debe conservar historia:

- `SALES_ORDER_ITEM.unit_price` guarda el precio historico de venta
- `PURCHASE_ORDER_ITEM.unit_cost` guarda el costo historico de compra
- `PAYMENT` se relaciona con una venta real
- `RETURN_ORDER_ITEM` se relaciona con un item vendido real
- `INVENTORY_STOCK` muestra el stock actual por repuesto y ubicacion

Si el sistema no puede explicar por que cambio el dinero, el stock o una
devolucion, entonces el sistema no es confiable.

### Comfort Without Weak Design

El sistema debe ser comodo para trabajadores: registrar ventas, actualizar
stock, recibir mercaderia y revisar pendientes no deberia ser una tortura.

Pero comodidad no significa romper el modelo. Una interfaz bonita encima de una
base mal modelada sigue siendo mala. La UX reduce friccion humana; el modelo
relacional protege la verdad de los datos.

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

Los nombres tecnicos se mantienen en native USA English. La explicacion puede
estar en espanol porque el documento es academico y debe ser facil de defender.

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

El ERD compacto no incluye todo lo posible. Eso esta bien. Agregar tablas sin
justificacion no es arquitectura; es ruido.

## Mapa de Casos de Uso

### Register Customer

Responsable principal: `Customers`.

Flujo:

1. Buscar si la persona ya existe.
2. Registrar datos civiles en `PERSON`.
3. Registrar datos comerciales en `CUSTOMER`.
4. Reutilizar el cliente en ventas, pagos, garantias y devoluciones.

Regla:

`CUSTOMER` no debe duplicar todo lo que ya vive en `PERSON`. Si repites nombres,
telefonos y direcciones en cada tabla, estas creando inconsistencia desde el
primer dia.

### Find Spare Part

Responsables principales: `Parts Catalog`, `Vehicle Compatibility` e
`Inventory`.

Flujo:

1. Buscar repuesto por codigo interno, codigo OEM, nombre, marca o categoria.
2. Verificar compatibilidad con marca, modelo, anio y motor del vehiculo.
3. Confirmar precio, garantia y estado.
4. Revisar stock antes de ofrecer el producto.

Regla:

La compatibilidad no debe quedar como una nota suelta en `PART`. Es una relacion
muchos-a-muchos entre repuestos y modelos de vehiculo, por eso existe
`PART_COMPATIBILITY`.

### Sell Spare Part

Responsables principales: `Sales`, `Customers`, `Inventory` y `Payments`.

Flujo:

1. Seleccionar cliente.
2. Agregar repuestos al detalle de venta.
3. Validar stock disponible.
4. Guardar cantidad, precio unitario y descuento en `SALES_ORDER_ITEM`.
5. Registrar el pago en `PAYMENT`.
6. Actualizar o explicar la salida de stock.

Regla:

`SALES_ORDER_ITEM.unit_price` debe guardar el precio historico. NO reconstruyas
ventas pasadas usando el precio actual de `PART`. Eso no es simplificar; eso es
corromper el historial.

### Purchase From Supplier

Responsables principales: `Suppliers and Purchases` e `Inventory`.

Flujo:

1. Detectar stock bajo.
2. Seleccionar proveedor.
3. Crear `PURCHASE_ORDER`.
4. Agregar repuestos solicitados en `PURCHASE_ORDER_ITEM`.
5. Registrar cantidades recibidas.
6. Actualizar stock y conservar costo historico.

Regla:

`PURCHASE_ORDER_ITEM.unit_cost` existe porque los costos cambian. El costo de
una compra especifica pertenece al item de compra, no solamente al registro
actual del repuesto.

### Return or Warranty

Responsables principales: `Returns and Warranties`, `Sales` e `Inventory`.

Flujo:

1. Buscar la venta original.
2. Seleccionar el item vendido.
3. Registrar motivo, estado y resolucion.
4. Definir monto devuelto si corresponde.
5. Definir si el producto vuelve al stock.

Regla:

Una devolucion debe apuntar a un `SALES_ORDER_ITEM` real. Si el sistema permite
devoluciones sin evidencia de venta original, no puede defender stock, dinero ni
garantia.

### Report Operations

Responsable principal: `Reports`.

Preguntas que debe responder:

- que productos estan bajos en stock
- que productos se venden mas
- que compras siguen pendientes
- que ventas tienen pagos pendientes
- que devoluciones estan en revision
- cuanto dinero ingreso en un periodo

Regla:

Los reportes no son una verdad separada. Son consultas sobre las tablas
operativas. Si las tablas base estan mal, el reporte tambien estara mal.

## Direccion de Dependencias

La direccion conceptual debe ser:

```text
Business use cases
  -> domain rules and entities
  -> PostgreSQL persistence
  -> UI, reports, scripts and external tools
```

La regla interna no debe depender de una interfaz especifica. Una venta sigue
siendo una venta si se registra desde una app web, una app de escritorio, un
script o una futura app movil.

PostgreSQL es esencial para este proyecto porque el curso es de base de datos,
pero sigue siendo infraestructura. Las reglas del dominio dicen que debe ser
verdad; PostgreSQL ayuda a protegerlo con `PK`, `FK`, `UNIQUE`, `CHECK` y
transacciones.

## Estructura Recomendada

El proyecto actual es principalmente documental. Si luego crece con codigo de
aplicacion, la estructura deberia priorizar modulos del negocio:

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

Esta estructura grita Zarvent Repuestos. No grita framework.

Si despues se usa un framework, sus archivos deben servir a estos modulos. El
framework no debe convertirse en el idioma principal del proyecto.

## Limite de la Base de Datos

La base de datos pertenece a la arquitectura porque el proyecto se centra en
diseno relacional. Pero una tabla no es solo un contenedor. Cada tabla debe
representar una entidad, evento o relacion necesaria para el negocio.

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

Los nombres tecnicos usan native USA English:

- tablas
- columnas
- modulos
- carpetas de codigo
- variables
- estados internos

La explicacion documental puede estar en espanol. La UI tambien podria estar en
espanol si se decide para usuarios finales.

Lo que NO se debe hacer es mezclar idiomas dentro de la misma capa tecnica.
Nombres como `productoStatus`, `detalleVentaItem` o `supplier_id_proveedor` son
mediocres. Elige una convencion y respetala.

### Data Integrity

El modelo debe prevenir errores evitables:

- clientes repetidos con distintas escrituras
- repuestos sin codigos estables
- ventas sin detalle
- detalles de venta sin repuesto
- pagos sin venta
- devoluciones sin item vendido original
- compras sin proveedor
- stock sin repuesto

Si la base de datos permite incoherencias, tarde o temprano la aplicacion las va
a guardar. No es mala suerte; es falta de diseno.

### Scope Control

El ERD compacto deja fuera algunos modulos futuros:

- usuarios, roles y permisos completos
- facturas y comprobantes tributarios detallados
- historial completo de movimientos de inventario
- marcas de vehiculo normalizadas
- auditoria avanzada

Son extensiones validas, pero no son obligatorias para el modelo compacto de
Base de Datos I. Mas tablas no significan mejor modelo.

## Alternativas Consideradas

### Layer-First Architecture

Ejemplo:

```text
controllers/
services/
repositories/
models/
```

Ventaja:

- es facil de reconocer para programadores
- sirve para CRUD pequeno

Desventaja:

- esconde el negocio
- la estructura grita capas tecnicas, no repuestos, stock ni ventas
- empuja al equipo a pensar en framework antes que en dominio

### Database-First Only Architecture

Ejemplo:

```text
tables/
queries/
migrations/
```

Ventaja:

- se alinea con Base de Datos I
- mantiene foco en el modelo relacional

Desventaja:

- puede explicar tablas sin explicar procesos
- puede convertir el proyecto en una lista de entidades sin flujo operativo

### Screaming Architecture

Ejemplo:

```text
inventory/
sales/
purchases/
returns/
payments/
reports/
```

Ventaja:

- comunica el negocio desde la primera lectura
- conecta procesos, ERD y futura aplicacion
- deja PostgreSQL y frameworks como herramientas, no como identidad

Desventaja:

- exige entender el dominio; no permite esconderse detras de carpetas genericas

La desventaja es aceptable. De hecho, es saludable. Si el equipo no puede
explicar el dominio, no entiende el proyecto.

## Consecuencias

- La documentacion debe explicar modulos desde procesos reales, no desde una
  lista suelta de tablas.
- El codigo futuro debe agruparse primero por dominio y luego por detalle
  tecnico.
- PostgreSQL 18.4 sigue siendo el RDBMS elegido.
- El ERD sigue siendo la fuente conceptual del modelo relacional.
- Los reportes deben salir de tablas operativas, no inventarse como verdad
  separada.
- Las pantallas futuras deberian usar el mismo lenguaje modular: `Products`,
  `Inventory`, `Sales`, `Purchases`, `Customers`, `Suppliers`, `Payments`,
  `Returns`, `Warranties`, `Reports`.
- Toda tabla nueva debe justificarse con actores, procesos, procedimientos,
  recursos o reglas de negocio.

## Resumen para Defensa

Zarvent Repuestos usa Screaming Architecture porque el proyecto debe organizarse
alrededor de su negocio: repuestos, compatibilidad, inventario, ventas, pagos,
compras, proveedores, devoluciones, garantias y reportes.

PostgreSQL 18.4 es el gestor elegido, pero no es la arquitectura. La
arquitectura es la estructura de dominio y casos de uso que PostgreSQL ayuda a
persistir y proteger.

Esta decision es coherente con el ERD porque las tablas principales ya
representan conceptos del negocio, no conceptos de framework. El modelo es
compacto, pero suficiente para defender centralizacion, normalizacion,
trazabilidad e integridad relacional.

## Sources

- Robert C. Martin, "Screaming Architecture":
  <https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html>
- Robert C. Martin, "The Clean Architecture":
  <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>
- Local ADR: [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md)
- Local ERD: [`docs/database/erd.md`](docs/database/erd.md)
- Local process analysis: [`docs/analysis/processes.md`](docs/analysis/processes.md)
