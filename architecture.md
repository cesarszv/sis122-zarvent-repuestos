# Arquitectura de Zarvent Repuestos

## Estado

Aceptado.

## Decisión

Zarvent Repuestos usará **Screaming Architecture**.

La arquitectura debe gritar el dominio del negocio antes que la tecnología:

- `Parts Catalog` (Catálogo de Repuestos)
- `Vehicle Compatibility` (Compatibilidad Vehicular)
- `Inventory` (Inventario)
- `Sales` (Ventas)
- `Payments` (Pagos)
- `Suppliers and Purchases` (Proveedores y Compras)
- `Returns and Warranties` (Devoluciones y Garantías)
- `Reports` (Reportes)
- `Access Control` (Control de Acceso)

Si alguien abre el proyecto y lo primero que entiende es "PostgreSQL",
"controladores", "repositorios", "framework" o "CRUD", el diseño está flojo.
Eso es infraestructura. El sistema existe para controlar una operación de venta
de repuestos.

CONCEPTO BÁSICO: la arquitectura no debe presumir herramientas; debe mostrar
casos de uso.

## Contexto

Zarvent Repuestos es un proyecto académico para `SIS-122` (Base de Datos I). El
sistema representa una empresa pequeña de venta de repuestos de vehículos.

El problema documentado no es inventado:

- la información está dispersa en papel, Excel y WhatsApp
- los clientes pueden duplicarse
- los repuestos pueden tener códigos o descripciones inconsistentes
- el stock puede quedar desactualizado
- las ventas, pagos, compras y devoluciones son difíciles de rastrear
- los reportes tardan porque la información no está centralizada

La decisión del RDBMS está en [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md):
el proyecto usa **PostgreSQL 18.4**.

Pero PostgreSQL NO es la arquitectura. PostgreSQL es el mecanismo de
persistencia. La arquitectura es la forma en que el sistema organiza el dominio,
los casos de uso, las reglas y las dependencias.

El modelo relacional base está en [`docs/database/erd.md`](docs/database/erd.md).
Ese ERD ya muestra el núcleo del negocio: clientes, catálogo, compatibilidad,
inventario, ventas, pagos, compras y devoluciones.

## Principio Arquitectónico

Screaming Architecture propone que la estructura superior del sistema revele sus
casos de uso y su propósito de negocio. La arquitectura no debe estar dominada
por frameworks, bases de datos, web, librerías o carpetas técnicas genéricas.

La pregunta correcta es:

> ¿Qué hace Zarvent Repuestos?

La respuesta mediocre sería:

> Usa PostgreSQL.

La respuesta correcta es:

> Controla el catálogo de repuestos, la compatibilidad vehicular, el stock, las ventas,
> los pagos, las compras a proveedores, las devoluciones, las garantías y los reportes.

Eso es lo que debe gritar la arquitectura.

## Drivers Arquitectónicos

### Control de Stock (Stock Control)

El punto más importante del sistema es el control de stock. En una tienda de
repuestos, vender algo que no existe físicamente es un error grave. Registrar
datos sin controlar la realidad operativa es solo hacer una planilla más bonita.

La arquitectura debe proteger este camino:

```text
PART -> INVENTORY_STOCK -> SALES_ORDER_ITEM
```

El sistema debe permitir saber:

- qué repuesto existe
- dónde está ubicado
- cuánto stock disponible hay
- cuándo debe reponerse
- qué venta lo descontó

### Centralización (Centralization)

El sistema debe centralizar información que hoy está repartida entre registros
manuales, Excel y WhatsApp.

Centralizar no significa meter todo en una tabla gigante. Eso es pereza
disfrazada de simplicidad. Centralizar significa que cada dato importante tiene
un lugar responsable y que las demás partes del sistema se relacionan con ese
dato mediante claves y relaciones.

### Trazabilidad (Traceability)

El sistema debe conservar historia:

- `SALES_ORDER_ITEM.unit_price` guarda el precio histórico de venta
- `PURCHASE_ORDER_ITEM.unit_cost` guarda el costo histórico de compra
- `PAYMENT` se relaciona con una venta real
- `RETURN_ORDER_ITEM` se relaciona con un ítem vendido real
- `INVENTORY_STOCK` muestra el stock actual por repuesto y ubicación

Si el sistema no puede explicar por qué cambió el dinero, el stock o una
devolución, entonces el sistema no es confiable.

### Comodidad Sin Diseño Débil (Comfort Without Weak Design)

El sistema debe ser cómodo para los trabajadores: registrar ventas, actualizar
stock, recibir mercadería y revisar pendientes no debería ser una tortura.

Pero comodidad no significa romper el modelo. Una interfaz bonita encima de una
base mal modelada sigue siendo mala. La UX reduce la fricción humana; el modelo
relacional protege la verdad de los datos.

### Defensa Académica (Academic Defense)

Este proyecto debe defenderse con conceptos de Base de Datos I:

- entidades
- atributos
- claves primarias
- claves foráneas
- relaciones
- cardinalidad
- normalización
- centralización
- seguridad
- consultas y reportes

No se inventan tablas por gusto. Cada módulo o tabla debe salir de actores,
procesos, procedimientos, recursos o reglas documentadas.

## Módulos del Dominio

Los nombres técnicos se mantienen en native USA English. La explicación puede
estar en español porque el documento es académico y debe ser fácil de defender.

| Módulo (Module) | Responsabilidad | Tablas principales |
| --- | --- | --- |
| `Customers` | Registrar compradores y datos de facturación sin duplicar identidad personal. | `PERSON`, `CUSTOMER` |
| `Parts Catalog` | Administrar repuestos, categorías, códigos, precios, costos, garantía y estado. | `PART_CATEGORY`, `PART` |
| `Vehicle Compatibility` | Validar que un repuesto corresponda a un modelo de vehículo. | `VEHICLE_MODEL`, `PART_COMPATIBILITY` |
| `Inventory` | Controlar cantidad disponible, ubicación y nivel de reposición. | `INVENTORY_STOCK` |
| `Sales` | Registrar ventas y detalle vendido con precio histórico. | `SALES_ORDER`, `SALES_ORDER_ITEM` |
| `Payments` | Registrar pagos, método, referencia y estado del cobro. | `PAYMENT` |
| `Suppliers and Purchases` | Gestionar proveedores, órdenes de compra y cantidades recibidas. | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |
| `Returns and Warranties` | Validar devoluciones contra ventas reales y decidir si el producto vuelve a stock. | `RETURN_ORDER`, `RETURN_ORDER_ITEM` |
| `Reports` | Consultar datos operativos para decisiones de gerencia. | Derivado de ventas, pagos, compras e inventario |
| `Access Control` | Controlar usuarios, roles, permisos y responsables. | Extensión futura; no está en el ERD compacto |

El ERD compacto no incluye todo lo posible. Eso está bien. Agregar tablas sin
justificación no es arquitectura; es ruido.

## Mapa de Casos de Uso

### Registrar Cliente (Register Customer)

Responsable principal: `Customers`.

Flujo:

1. Buscar si la persona ya existe.
2. Registrar datos civiles en `PERSON`.
3. Registrar datos comerciales en `CUSTOMER`.
4. Reutilizar el cliente en ventas, pagos, garantías y devoluciones.

Regla:

`CUSTOMER` no debe duplicar todo lo que ya vive en `PERSON`. Si repites nombres,
teléfonos y direcciones en cada tabla, estás creando inconsistencia desde el
primer día.

### Buscar Repuesto (Find Spare Part)

Responsables principales: `Parts Catalog`, `Vehicle Compatibility` e
`Inventory`.

Flujo:

1. Buscar repuesto por código interno, código OEM, nombre, marca o categoría.
2. Verificar compatibilidad con marca, modelo, año y motor del vehículo.
3. Confirmar precio, garantía y estado.
4. Revisar stock antes de ofrecer el producto.

Regla:

La compatibilidad no debe quedar como una nota suelta en `PART`. Es una relación
muchos-a-muchos entre repuestos y modelos de vehículo, por eso existe
`PART_COMPATIBILITY`.

### Vender Repuesto (Sell Spare Part)

Responsables principales: `Sales`, `Customers`, `Inventory` y `Payments`.

Flujo:

1. Seleccionar cliente.
2. Agregar repuestos al detalle de venta.
3. Validar stock disponible.
4. Guardar cantidad, precio unitario y descuento en `SALES_ORDER_ITEM`.
5. Registrar el pago en `PAYMENT`.
6. Actualizar o explicar la salida de stock.

Regla:

`SALES_ORDER_ITEM.unit_price` debe guardar el precio histórico. NO reconstruyas
ventas pasadas usando el precio actual de `PART`. Eso no es simplificar; eso es
corromper el historial.

### Comprar a Proveedor (Purchase From Supplier)

Responsables principales: `Suppliers and Purchases` e `Inventory`.

Flujo:

1. Detectar stock bajo.
2. Seleccionar proveedor.
3. Crear `PURCHASE_ORDER`.
4. Agregar repuestos solicitados en `PURCHASE_ORDER_ITEM`.
5. Registrar cantidades recibidas.
6. Actualizar stock y conservar costo histórico.

Regla:

`PURCHASE_ORDER_ITEM.unit_cost` existe porque los costos cambian. El costo de
una compra específica pertenece al ítem de compra, no solamente al registro
actual del repuesto.

### Devolución o Garantía (Return or Warranty)

Responsables principales: `Returns and Warranties`, `Sales` e `Inventory`.

Flujo:

1. Buscar la venta original.
2. Seleccionar el ítem vendido.
3. Registrar motivo, estado y resolución.
4. Definir monto devuelto si corresponde.
5. Definir si el producto vuelve al stock.

Regla:

Una devolución debe apuntar a un `SALES_ORDER_ITEM` real. Si el sistema permite
devoluciones sin evidencia de venta original, no puede defender stock, dinero ni
garantía.

### Reportar Operaciones (Report Operations)

Responsable principal: `Reports`.

Preguntas que debe responder:

- qué productos están bajos en stock
- qué productos se venden más
- qué compras siguen pendientes
- qué ventas tienen pagos pendientes
- qué devoluciones están en revisión
- cuánto dinero ingresó en un periodo

Regla:

Los reportes no son una verdad separada. Son consultas sobre las tablas
operativas. Si las tablas base están mal, el reporte también estará mal.

## Dirección de Dependencias

La dirección conceptual debe ser:

```text
Casos de uso del negocio (Business use cases)
  -> Reglas de dominio y entidades (domain rules and entities)
  -> Persistencia en PostgreSQL (PostgreSQL persistence)
  -> UI, reportes, scripts y herramientas externas (UI, reports, scripts and external tools)
```

La regla interna no debe depender de una interfaz específica. Una venta sigue
siendo una venta si se registra desde una app web, una app de escritorio, un
script o una futura app móvil.

PostgreSQL es esencial para este proyecto porque el curso es de base de datos,
pero sigue siendo infraestructura. Las reglas del dominio dicen qué debe ser
verdad; PostgreSQL ayuda a protegerlo con `PK`, `FK`, `UNIQUE`, `CHECK` y
transacciones.

## Estructura Recomendada

El proyecto actual es principalmente documental. Si luego crece con código de
aplicación, la estructura debería priorizar módulos del negocio:

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

Si después se usa un framework, sus archivos deben servir a estos módulos. El
framework no debe convertirse en el idioma principal del proyecto.

## Límite de la Base de Datos

La base de datos pertenece a la arquitectura porque el proyecto se centra en
diseño relacional. Pero una tabla no es solo un contenedor. Cada tabla debe
representar una entidad, evento o relación necesaria para el negocio.

La base debe proteger como mínimo:

- identidad con `PRIMARY KEY`
- integridad relacional con `FOREIGN KEY`
- prevención de duplicados con `UNIQUE`
- valores válidos con `CHECK`
- consistencia de operaciones con transacciones
- precios y costos históricos en tablas de detalle

El ERD es la fuente conceptual. El SQL físico debe adaptar ese diseño a
PostgreSQL 18.4.

## Reglas de Calidad

### Nombrado (Naming)

Los nombres técnicos usan native USA English:

- tablas
- columnas
- módulos
- carpetas de código
- variables
- estados internos

La explicación documental puede estar en español. La UI también podría estar en
español si se decide para usuarios finales.

Lo que NO se debe hacer es mezclar idiomas dentro de la misma capa técnica.
Nombres como `productoStatus`, `detalleVentaItem` o `supplier_id_proveedor` son
mediocres. Elige una convención y respétala.

### Integridad de Datos (Data Integrity)

El modelo debe prevenir errores evitables:

- clientes repetidos con distintas escrituras
- repuestos sin códigos estables
- ventas sin detalle
- detalles de venta sin repuesto
- pagos sin venta
- devoluciones sin ítem vendido original
- compras sin proveedor
- stock sin repuesto

Si la base de datos permite incoherencias, tarde o temprano la aplicación las va
a guardar. No es mala suerte; es falta de diseño.

### Control de Alcance (Scope Control)

El ERD compacto deja fuera algunos módulos futuros:

- usuarios, roles y permisos completos
- facturas y comprobantes tributarios detallados
- historial completo de movimientos de inventario
- marcas de vehículo normalizadas
- auditoría avanzada

Son extensiones válidas, pero no son obligatorias para el modelo compacto de
Base de Datos I. Más tablas no significan mejor modelo.

## Alternativas Consideradas

### Arquitectura Centrada en Capas (Layer-First Architecture)

Ejemplo:

```text
controllers/
services/
repositories/
models/
```

Ventaja:

- es fácil de reconocer para programadores
- sirve para CRUD pequeño

Desventaja:

- esconde el negocio
- la estructura grita capas técnicas, no repuestos, stock ni ventas
- empuja al equipo a pensar en framework antes que en dominio

### Arquitectura Centrada en Base de Datos (Database-First Only Architecture)

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

### Arquitectura que Grita (Screaming Architecture)

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
- conecta procesos, ERD y futura aplicación
- deja PostgreSQL y frameworks como herramientas, no como identidad

Desventaja:

- exige entender el dominio; no permite esconderse detrás de carpetas genéricas

La desventaja es aceptable. De hecho, es saludable. Si el equipo no puede
explicar el dominio, no entiende el proyecto.

## Consecuencias

- La documentación debe explicar módulos desde procesos reales, no desde una
  lista suelta de tablas.
- El código futuro debe agruparse primero por dominio y luego por detalle
  técnico.
- PostgreSQL 18.4 sigue siendo el RDBMS elegido.
- El ERD sigue siendo la fuente conceptual del modelo relacional.
- Los reportes deben salir de tablas operativas, no inventarse como verdad
  separada.
- Las pantallas futuras deberían usar el mismo lenguaje modular: `Products`,
  `Inventory`, `Sales`, `Purchases`, `Customers`, `Suppliers`, `Payments`,
  `Returns`, `Warranties`, `Reports`.
- Toda tabla nueva debe justificarse con actores, procesos, procedimientos,
  recursos o reglas de negocio.

## Resumen para Defensa

Zarvent Repuestos usa Screaming Architecture porque el proyecto debe organizarse
alrededor de su negocio: repuestos, compatibilidad, inventario, ventas, pagos,
compras, proveedores, devoluciones, garantías y reportes.

PostgreSQL 18.4 es el gestor elegido, pero no es la arquitectura. La
arquitectura es la estructura de dominio y casos de uso que PostgreSQL ayuda a
persistir y proteger.

Esta decisión es coherente con el ERD porque las tablas principales ya
representan conceptos del negocio, no conceptos de framework. El modelo es
compacto, pero suficiente para defender centralización, normalización,
trazabilidad e integridad relacional.

## Fuentes (Sources)

- Robert C. Martin, "Screaming Architecture":
  <https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html>
- Robert C. Martin, "The Clean Architecture":
  <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>
- Local ADR: [`docs/adr/001-RDBMS.md`](docs/adr/001-RDBMS.md)
- Local ERD: [`docs/database/erd.md`](docs/database/erd.md)
- Local process analysis: [`docs/analysis/processes.md`](docs/analysis/processes.md)
