# Entity Relationship Model Explanation

Este documento explica por que Zarvent Repuestos usa un modelo
entidad-relacion operacional, compacto y relacional, implementable en MySQL
Server.

El diagrama principal esta en [erd.md](erd.md).

## Decision

El proyecto usara un **ERD compacto** con notacion Crow's Foot. El objetivo es
modelar el nucleo del negocio sin convertir el proyecto de Base de Datos I en
un ERP completo.

El modelo NO sera:

- una planilla Excel con nombres bonitos;
- una sola tabla gigante;
- una base NoSQL;
- un data warehouse;
- un sistema industrial completo de inventario y facturacion.

## Contexto

Zarvent Repuestos maneja clientes, repuestos, compatibilidad vehicular, stock,
ventas, pagos, compras, proveedores y devoluciones.

Hoy esa informacion puede estar dispersa en papel, Excel, WhatsApp o memoria
del personal. La base de datos debe centralizarla y proteger relaciones
importantes:

- una venta debe pertenecer a un cliente;
- una linea de venta debe apuntar a un repuesto real;
- un pago debe pertenecer a una venta;
- una compra debe pertenecer a un proveedor;
- una devolucion debe apuntar a una venta original;
- un repuesto puede ser compatible con muchos vehiculos.

## Por que modelo relacional y MySQL

MySQL Server es el gestor exigido para el proyecto. El modelo relacional encaja
bien porque el negocio tiene datos conectados por reglas claras.

| Concepto | Uso en el proyecto |
| --- | --- |
| Entidad | tabla, por ejemplo `PART` o `CUSTOMER` |
| Atributo | columna, por ejemplo `internal_code` o `sale_price` |
| Primary key | identificador estable de una fila |
| Foreign key | relacion protegida entre tablas |
| Unique constraint | defensa contra duplicados |
| Check constraint | defensa contra valores invalidos simples |

No se elige MySQL porque "suena mejor". Se usa porque el profesor lo exige y
porque el modelo necesita integridad entre tablas.

## Por que no una sola tabla

Una sola tabla mezclaria clientes, repuestos, pagos, compras y devoluciones.
Eso genera errores clasicos:

| Error | Ejemplo |
| --- | --- |
| Duplicacion | repetir nombre del cliente en cada venta |
| Inconsistencia | escribir el mismo repuesto con nombres distintos |
| Perdida de historial | cambiar el precio actual y alterar reportes pasados |
| Mala cardinalidad | limitar la venta a `part_1`, `part_2`, `part_3` |
| Devoluciones debiles | guardar el reclamo como texto sin validar la venta original |

Separar entidades no es complicar por gusto. Es proteger datos.

## Mapa de procesos a entidades

| Proceso | Entidades principales | Razon |
| --- | --- | --- |
| Registro de clientes | `PERSON`, `CUSTOMER` | separa identidad y rol comercial |
| Catalogo de repuestos | `PART_CATEGORY`, `PART` | ordena productos, precios, costos y garantia |
| Compatibilidad | `VEHICLE_MODEL`, `PART_COMPATIBILITY` | evita vender piezas incompatibles |
| Inventario | `PART`, `INVENTORY_STOCK` | permite consultar cantidad y ubicacion |
| Ventas | `SALES_ORDER`, `SALES_ORDER_ITEM` | separa cabecera y detalle |
| Pagos | `PAYMENT`, `SALES_ORDER` | permite varios pagos por venta |
| Compras | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` | controla reposicion y costo historico |
| Devoluciones | `RETURN_ORDER`, `RETURN_ORDER_ITEM`, `SALES_ORDER_ITEM` | valida devoluciones contra ventas reales |

## Grupos del modelo

| Grupo | Tablas | Idea central |
| --- | --- | --- |
| Identidad y clientes | `PERSON`, `CUSTOMER` | una persona no es lo mismo que su rol comercial |
| Catalogo y compatibilidad | `PART_CATEGORY`, `PART`, `VEHICLE_MODEL`, `PART_COMPATIBILITY` | vender la pieza correcta para el vehiculo correcto |
| Inventario | `INVENTORY_STOCK` | saber cuanto hay y donde esta |
| Ventas y pagos | `SALES_ORDER`, `SALES_ORDER_ITEM`, `PAYMENT` | registrar venta, detalle y cobro |
| Compras | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` | reponer stock y guardar costo historico |
| Devoluciones | `RETURN_ORDER`, `RETURN_ORDER_ITEM` | controlar reclamos contra ventas reales |

## Relaciones importantes

| Relacion | Cardinalidad | Defensa |
| --- | --- | --- |
| `PERSON` -> `CUSTOMER` | 1 a 0..1 | una persona puede existir sin comprar todavia |
| `CUSTOMER` -> `SALES_ORDER` | 1 a 0..N | un cliente puede comprar muchas veces |
| `SALES_ORDER` -> `SALES_ORDER_ITEM` | 1 a 1..N | una venta debe tener una o mas lineas |
| `PART` -> `SALES_ORDER_ITEM` | 1 a 0..N | un repuesto puede venderse muchas veces |
| `SALES_ORDER` -> `PAYMENT` | 1 a 0..N | una venta puede tener varios pagos |
| `PART` -> `PART_COMPATIBILITY` -> `VEHICLE_MODEL` | muchos a muchos | un repuesto puede servir para varios vehiculos |
| `SUPPLIER` -> `PURCHASE_ORDER` | 1 a 0..N | un proveedor puede tener muchas compras |
| `PURCHASE_ORDER` -> `PURCHASE_ORDER_ITEM` | 1 a 1..N | una compra debe tener detalle |
| `SALES_ORDER` -> `RETURN_ORDER` | 1 a 0..N | una venta puede tener devoluciones |
| `RETURN_ORDER_ITEM` -> `SALES_ORDER_ITEM` | N a 1 | una devolucion apunta a la linea vendida |

## Many-to-many principal

La relacion mas importante de muchos-a-muchos es:

`PART` <-> `VEHICLE_MODEL`

Un repuesto puede servir para varios vehiculos. Un vehiculo puede aceptar varios
repuestos. En un modelo relacional eso se resuelve con una tabla intermedia:

`PART -> PART_COMPATIBILITY -> VEHICLE_MODEL`

`PART_COMPATIBILITY` no es una tabla de relleno. Guarda informacion propia de
la compatibilidad, como `engine_code` y `notes`.

## Reglas de integridad

- Las tablas usan primary keys tecnicas con patron `*_id`.
- Las relaciones se protegen con foreign keys.
- `PART.internal_code` debe ser unico.
- `PART_CATEGORY.name` debe ser unico.
- `SUPPLIER.tax_id` debe ser unico cuando exista.
- `INVENTORY_STOCK` deberia ser unico por `part_id` y `location_name`.
- Cantidades y montos no deben ser negativos.
- Los estados deben documentarse o restringirse para evitar textos
  inconsistentes.

## Valores historicos

El modelo guarda precio y costo historico en los detalles:

- `SALES_ORDER_ITEM.unit_price`
- `SALES_ORDER_ITEM.discount_amount`
- `PURCHASE_ORDER_ITEM.unit_cost`

Esto es necesario porque el precio actual de `PART` puede cambiar. Una venta
pasada debe conservar el precio que se aplico en ese momento.

## Limites del alcance

El ERD actual es compacto y defendible, pero no cubre todo.

| Limite | Por que importa | Mejora futura |
| --- | --- | --- |
| No hay historial de stock | no explica por que cambio el saldo | `INVENTORY_MOVEMENT` |
| No hay recepcion separada | mezcla pedido y recepcion | `PURCHASE_RECEIPT` |
| Un solo codigo OEM | una pieza puede tener varios codigos | `PART_IDENTIFIER` |
| Estados como texto | pueden escribirse de varias formas | `CHECK` o catalogos |
| No hay usuario responsable | no se sabe quien hizo cada operacion | `USER_ACCOUNT` |
| No hay factura separada | venta y comprobante no siempre son lo mismo | `SALES_INVOICE` |

Estas limitaciones no hacen malo al ERD. Solo marcan lo que queda fuera para
mantener un alcance academico.

## Guia para pasar a SQL

Al convertir el ERD a MySQL:

1. Crear primero tablas independientes: `PERSON`, `SUPPLIER`,
   `PART_CATEGORY`, `VEHICLE_MODEL`.
2. Crear tablas dependientes simples: `CUSTOMER`, `PART`.
3. Crear tablas de relacion y stock: `PART_COMPATIBILITY`,
   `INVENTORY_STOCK`.
4. Crear cabeceras: `SALES_ORDER`, `PURCHASE_ORDER`.
5. Crear detalles: `SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM`.
6. Crear eventos dependientes: `PAYMENT`, `RETURN_ORDER`,
   `RETURN_ORDER_ITEM`.
7. Agregar primary keys, foreign keys, unique constraints y checks.
8. Probar casos basicos: venta con varias lineas, pago parcial, compra,
   devolucion y stock bajo.

## Posicion final

Zarvent Repuestos usara un modelo entidad-relacion operacional, compacto y
relacional en MySQL Server. El modelo separa identidad, clientes, proveedores,
catalogo, compatibilidad, inventario, ventas, pagos, compras y devoluciones.

La idea central es simple: cada tabla debe nacer de un proceso real y cada
relacion debe proteger una regla del negocio.

## Fuentes

- Peter P. Chen, **The Entity-Relationship Model: Toward a Unified View of
  Data**: <https://dl.acm.org/doi/10.1145/320434.320440>
- E. F. Codd, **A Relational Model of Data for Large Shared Data Banks**:
  <https://research.ibm.com/publications/a-relational-model-of-data-for-large-shared-data-banks>
- MySQL Documentation: <https://dev.mysql.com/doc/>
- Auto Care Association, **Auto Care Data Standards**:
  <https://www.autocare.org/data-standards>
