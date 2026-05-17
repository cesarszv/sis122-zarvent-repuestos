# Entity Relationship Model Explanation

Este documento explica **que modelo entidad-relacion usaremos en Zarvent
Repuestos, por que lo usaremos, para que sirve, como se construye, cuando se
aplica, donde vive dentro del proyecto y que decisiones NO conviene tomar**.

La idea no es decorar la carpeta `docs/database`. La idea es que el modelo se
pueda defender frente a una pregunta seria: "por que esas entidades y no otras?".
Si una tabla no nace de un proceso real, es humo. Si una relacion no protege una
regla del negocio, es dibujo. Y si el stock es solo un numerito que nadie puede
auditar, eso todavia no es arquitectura seria.

## Decision Summary

Usaremos un **Entity Relationship Model** de tipo **operational relational
model**, representado con un **ERD compacto de notacion Crow's Foot** y pensado
para implementarse despues en **PostgreSQL 18.4**.

En palabras simples:

- **Entity Relationship Model:** porque necesitamos identificar entidades,
  atributos, relaciones, cardinalidades y reglas de negocio antes de crear
  tablas.
- **Relational model:** porque PostgreSQL almacena la informacion en tablas
  relacionadas por primary keys, foreign keys, unique constraints y checks.
- **Operational model:** porque el sistema administra operaciones diarias:
  clientes, repuestos, compatibilidad, stock, ventas, pagos, compras,
  devoluciones y garantias.
- **Compact academic scope:** porque el proyecto debe ser entendible y
  defendible en Base de Datos I, sin intentar copiar todo un ERP industrial.

Este NO sera:

- una planilla Excel con nombres bonitos;
- una sola tabla gigante;
- una base NoSQL documental;
- un modelo `EAV` para guardar cualquier cosa en columnas genericas;
- un data warehouse;
- un ERP completo.

Ese limite importa. El que modela sin limites termina produciendo un monstruo
que nadie entiende, nadie implementa y nadie puede defender.

## Project Context

Zarvent Repuestos representa una empresa pequena de venta de repuestos de
vehiculos. Actualmente maneja informacion en papel, Excel y WhatsApp. Eso deja
trabajar, pero genera problemas clasicos:

- datos duplicados de clientes;
- repuestos repetidos o mal escritos;
- precios desactualizados;
- stock que no coincide con la realidad fisica;
- ventas sin detalle confiable;
- pagos separados de la venta;
- compras pendientes dificiles de seguir;
- devoluciones sin relacion clara con la venta original;
- reportes lentos o poco confiables.

Entonces el ERD no nace de "hagamos tablas porque toca". Nace de una necesidad
concreta: **centralizar informacion operacional y hacer que las relaciones entre
datos reflejen como funciona el negocio**.

## What Model We Will Use

El modelo elegido es:

> **A compact normalized operational Entity Relationship Model for an automotive
> spare parts business, implemented as a relational schema in PostgreSQL 18.4.**

Traducido al trabajo del proyecto:

- `PERSON` representa la identidad civil o de contacto.
- `CUSTOMER` representa el rol comercial del comprador.
- `SUPPLIER` representa al proveedor.
- `PART_CATEGORY` clasifica repuestos.
- `PART` representa el repuesto vendible, comprable e inventariable.
- `VEHICLE_MODEL` representa el vehiculo objetivo para compatibilidad.
- `PART_COMPATIBILITY` conecta repuestos con vehiculos compatibles.
- `INVENTORY_STOCK` guarda saldo actual por repuesto y ubicacion.
- `SALES_ORDER` registra la venta.
- `SALES_ORDER_ITEM` registra el detalle vendido.
- `PAYMENT` registra cobros asociados a la venta.
- `PURCHASE_ORDER` registra compras a proveedores.
- `PURCHASE_ORDER_ITEM` registra el detalle comprado.
- `RETURN_ORDER` registra devoluciones o garantias.
- `RETURN_ORDER_ITEM` registra que linea vendida se devuelve.

El diagrama principal esta en [erd.md](erd.md). Esta explicacion documenta la
razon tecnica y de negocio detras de ese diagrama.

## Why Entity Relationship Modeling

Usamos modelado entidad-relacion porque permite responder preguntas antes de
crear tablas fisicas:

- **Que cosas existen en el negocio?** Clientes, repuestos, proveedores, ventas,
  pagos, compras, stock y devoluciones.
- **Que datos describe cada cosa?** Por ejemplo, `PART` necesita codigo interno,
  codigo OEM, nombre, marca, precio, costo, garantia y estado.
- **Como se conectan?** Una venta pertenece a un cliente, una venta tiene
  lineas, una linea apunta a un repuesto, un pago pertenece a una venta.
- **Cuantas veces puede ocurrir la relacion?** Un cliente puede tener muchas
  ventas; una venta debe tener una o mas lineas; un repuesto puede ser
  compatible con muchos vehiculos.
- **Que reglas deben cumplirse?** No debe existir una linea de venta sin venta,
  ni un pago sin venta, ni una devolucion sin venta original.

Ese es el punto: **el ERD hace visibles las reglas**. Sin eso, el sistema queda
en manos de memoria, formularios improvisados y validaciones sueltas.

## Why Relational and PostgreSQL 18.4

El proyecto usa PostgreSQL 18.4 como gestor principal. Eso vuelve natural
implementar el ERD como modelo relacional:

- Las entidades se convierten en tablas.
- Los atributos se convierten en columnas.
- Las primary keys identifican filas.
- Las foreign keys protegen relaciones.
- Las unique constraints evitan duplicados.
- Las check constraints validan reglas simples.
- Las consultas SQL permiten reportes operativos.

Este negocio tiene relaciones fuertes y repetidas. Ejemplos:

- un `CUSTOMER` tiene muchas `SALES_ORDER`;
- una `SALES_ORDER` tiene muchas `SALES_ORDER_ITEM`;
- un `PART` aparece en muchas ventas y compras;
- un `SUPPLIER` recibe muchas `PURCHASE_ORDER`;
- una `RETURN_ORDER_ITEM` debe apuntar a una `SALES_ORDER_ITEM` real.

Eso no es una coleccion libre de documentos. Es informacion transaccional con
integridad. Por eso el modelo relacional es la eleccion correcta para este
alcance.

## Why Not a Spreadsheet Model

Excel sirve para sobrevivir, no para controlar integridad con seriedad.

Una planilla puede registrar repuestos y ventas, pero no protege bien:

- que un cliente no se duplique;
- que un codigo interno sea unico;
- que una venta tenga cliente existente;
- que una linea de venta apunte a un repuesto existente;
- que una devolucion no exceda lo vendido;
- que los pagos correspondan a una venta;
- que los reportes salgan de datos consistentes.

Si alguien escribe "Toyota", "TOYOTA", "Toyta" y "toyota" en cuatro celdas, la
planilla no entiende el dano conceptual. La base relacional si puede imponer
restricciones y relaciones. ESA es la diferencia entre registrar datos y modelar
datos.

## Why Not One Big Table

Una tabla gigante tipo `SALES_EVERYTHING` podria parecer facil al inicio:

| Column Example   | Problem                                                     |
| ---------------- | ----------------------------------------------------------- |
| `customer_name`  | Se repite en cada venta y se escribe distinto.              |
| `part_name`      | Se duplica por cada linea vendida.                          |
| `supplier_name`  | Mezcla compras con ventas.                                  |
| `vehicle_model`  | No permite compatibilidad muchos-a-muchos.                  |
| `payment_method` | Mezcla cabecera comercial con cobro.                        |
| `return_reason`  | Devoluciones aparecen aunque no todas las ventas devuelvan. |

Eso produce anomalias:

- **Insert anomaly:** no puedes registrar un repuesto nuevo sin inventar una
  venta.
- **Update anomaly:** si cambia el telefono del cliente, debes corregir muchas
  filas.
- **Delete anomaly:** si borras una venta, puedes perder datos del cliente o
  del repuesto.
- **Reporting anomaly:** los totales se contaminan por duplicados.

Por eso el ERD separa entidades y usa relaciones. No por capricho academico,
sino porque mezclar conceptos distintos en una misma tabla destruye la calidad
de los datos.

## Why Not NoSQL for This Project

Una base documental podria guardar una venta completa como JSON:

```json
{
  "customer": "...",
  "items": [
    { "part": "...", "quantity": 2, "unit_price": 120 }
  ],
  "payments": [...]
}
```

Eso puede ser util para ciertos sistemas, pero aqui no es la mejor base:

- `PART` se reutiliza en ventas, compras, stock y devoluciones.
- `CUSTOMER` se reutiliza en historial, pagos y garantias.
- `SUPPLIER` se reutiliza en compras y costos.
- `PART_COMPATIBILITY` necesita consultas cruzadas por vehiculo y repuesto.
- Los reportes necesitan joins confiables.
- Las restricciones entre venta, pago y devolucion importan.

NoSQL no es "malo". Lo mediocre es elegirlo porque suena moderno sin entender
el problema. Para este proyecto, las relaciones son el centro del negocio, asi
que el modelo relacional gana.

## How We Build the Model

El proceso correcto es este:

1. Identificar procesos reales del negocio.
2. Identificar actores que ejecutan o validan esos procesos.
3. Identificar informacion que cada proceso produce o consume.
4. Separar conceptos estables en entidades.
5. Definir atributos necesarios para cada entidad.
6. Definir primary keys.
7. Definir foreign keys.
8. Resolver relaciones many-to-many con tablas intermedias.
9. Definir cardinalidades y opcionalidad.
10. Definir reglas de negocio y restricciones.
11. Validar si el modelo responde las consultas importantes.
12. ReciEN despues pasar al SQL fisico.

Nota la palabra clave: **despues**. Crear tablas sin entender procesos es la
forma rapida de fabricar deuda tecnica desde el primer dia.

## Process to Entity Mapping

| Business Process       | Main Entities                                           | Reason                                                         |
| ---------------------- | ------------------------------------------------------- | -------------------------------------------------------------- |
| Customer registration  | `PERSON`, `CUSTOMER`                                    | Evita duplicar identidad y permite historial de ventas.        |
| Spare parts catalog    | `PART`, `PART_CATEGORY`                                 | Centraliza codigos, precios, costos, garantia y estado.        |
| Fitment validation     | `VEHICLE_MODEL`, `PART_COMPATIBILITY`                   | Evita vender repuestos incompatibles con el vehiculo.          |
| Stock checking         | `INVENTORY_STOCK`, `PART`                               | Permite saber cantidad disponible y ubicacion.                 |
| Sales registration     | `SALES_ORDER`, `SALES_ORDER_ITEM`                       | Separa cabecera de venta y detalle de repuestos vendidos.      |
| Payment registration   | `PAYMENT`, `SALES_ORDER`                                | Permite uno o varios pagos asociados a una venta.              |
| Supplier purchasing    | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM`     | Permite registrar reposicion, costos y pedidos.                |
| Returns and warranties | `RETURN_ORDER`, `RETURN_ORDER_ITEM`, `SALES_ORDER_ITEM` | Obliga a validar devoluciones contra ventas reales.            |
| Management reports     | Operational tables                                      | Los reportes se consultan desde datos operativos consistentes. |

## Entity Groups

El ERD se organiza en cinco grupos. Esta separacion ayuda a entenderlo sin
memorizar tablas como loro.

### Identity and Customer

| Entity     | Purpose                                    | Why It Exists                                                       |
| ---------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `PERSON`   | Guarda datos de identidad/contacto.        | Una persona puede existir como contacto base antes de tener ventas. |
| `CUSTOMER` | Representa el rol comercial del comprador. | El cliente compra, factura, devuelve y tiene historial.             |

`PERSON` y `CUSTOMER` se separan porque identidad y rol comercial no son lo
mismo. Una persona es alguien con nombre, telefono, correo y direccion. Un
cliente es esa persona actuando frente al negocio como comprador.

**Por que si:** evita duplicar datos civiles cuando se agregan roles o historial.

**Por que no simplificar todo en `CUSTOMER`:** para un proyecto pequeno se puede,
pero ensena peor el concepto. Ademas, si despues aparecen empleados, usuarios o
contactos, repetirias nombres y telefonos en varias tablas.

### Catalog and Fitment

| Entity               | Purpose                                    | Why It Exists                                                       |
| -------------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `PART_CATEGORY`      | Clasifica repuestos.                       | Facilita busqueda, reportes y orden de catalogo.                    |
| `PART`               | Representa el repuesto vendible/comprable. | Es el centro del negocio: precio, costo, codigo, garantia y estado. |
| `VEHICLE_MODEL`      | Representa vehiculo compatible.            | Permite buscar por marca, modelo, anio y motor.                     |
| `PART_COMPATIBILITY` | Relaciona repuestos con vehiculos.         | Resuelve la relacion many-to-many entre `PART` y `VEHICLE_MODEL`.   |

En repuestos, vender "un producto" no basta. Hay que vender **la pieza correcta
para el vehiculo correcto**. Por eso `PART_COMPATIBILITY` es una tabla clave.

**Por que si:** un repuesto puede servir para varios vehiculos, y un vehiculo
puede aceptar muchos repuestos. Eso es many-to-many.

**Por que no guardar compatibilidad como texto dentro de `PART`:** porque
terminarias escribiendo frases libres imposibles de consultar con precision.
Ejemplo mediocre: "sirve para Corolla 2008-2013 mas o menos". Eso no es dato,
es una nota peligrosa.

### Inventory

| Entity            | Purpose                                       | Why It Exists                          |
| ----------------- | --------------------------------------------- | -------------------------------------- |
| `INVENTORY_STOCK` | Guarda saldo actual por repuesto y ubicacion. | Permite saber cuanto hay y donde esta. |

`INVENTORY_STOCK` responde una pregunta operativa inmediata:

> Cuantas unidades de este `PART` hay disponibles en esta ubicacion?

Para el ERD compacto, eso es suficiente. Pero ojo: saldo actual no explica
historia.

**Por que si:** el vendedor necesita verificar stock antes de confirmar venta.

**Por que no es suficiente para arquitectura seria:** sin `INVENTORY_MOVEMENT`
no puedes auditar por que cambio el stock. No sabes si bajo por venta, ajuste,
perdida, error, devolucion o correccion. Para una entrega academica compacta
puede pasar; para un sistema real, queda corto.

### Sales and Payments

| Entity             | Purpose             | Why It Exists                                               |
| ------------------ | ------------------- | ----------------------------------------------------------- |
| `SALES_ORDER`      | Cabecera de venta.  | Relaciona cliente, fecha, estado y totales.                 |
| `SALES_ORDER_ITEM` | Linea de venta.     | Relaciona venta con repuesto, cantidad, precio y descuento. |
| `PAYMENT`          | Cobro de una venta. | Permite pagos parciales, multiples metodos y referencias.   |

La venta se separa en cabecera y detalle porque una venta puede incluir varios
repuestos. Eso es una estructura clasica y correcta:

`SALES_ORDER` -> `SALES_ORDER_ITEM`

**Por que si:** permite vender multiples productos en una sola operacion.

**Por que no guardar todo en `SALES_ORDER`:** porque tendrias columnas como
`part_1`, `part_2`, `part_3`. Eso es diseno de principiante. Rompe consultas,
limita cantidades y duplica estructura.

`PAYMENT` se separa porque pagar no es lo mismo que vender. Una venta puede
pagarse en efectivo y transferencia, o puede quedar parcial, anulada o
pendiente.

### Purchasing

| Entity                | Purpose                           | Why It Exists                                    |
| --------------------- | --------------------------------- | ------------------------------------------------ |
| `SUPPLIER`            | Proveedor que abastece repuestos. | Permite registrar datos comerciales y estado.    |
| `PURCHASE_ORDER`      | Cabecera de compra.               | Relaciona proveedor, fechas, estado y total.     |
| `PURCHASE_ORDER_ITEM` | Linea de compra.                  | Relaciona compra con repuesto, cantidad y costo. |

Compras no es un texto en observaciones. Es un proceso con proveedor, pedido,
cantidades, costos y estado.

**Por que si:** permite reponer stock, comparar costos y saber que esta
pendiente.

**Por que no mezclar compras en `PART`:** porque `PART` describe el repuesto,
no cada evento de compra. El costo actual puede vivir en `PART`, pero el costo
historico de una compra vive en `PURCHASE_ORDER_ITEM`.

### Returns and Warranties

| Entity              | Purpose                            | Why It Exists                                                                |
| ------------------- | ---------------------------------- | ---------------------------------------------------------------------------- |
| `RETURN_ORDER`      | Cabecera de devolucion o garantia. | Relaciona devolucion con venta original, fecha, motivo, resolucion y estado. |
| `RETURN_ORDER_ITEM` | Linea devuelta.                    | Relaciona devolucion con la linea vendida real.                              |

Una devolucion seria no se registra "a ojo". Debe apuntar a la venta original y
al repuesto vendido.

**Por que si:** evita devoluciones inventadas, cantidades excesivas y garantias
sin respaldo.

**Por que no guardar devoluciones como comentario en la venta:** porque un
comentario no valida cantidades, no calcula reembolso, no controla reingreso a
stock y no sirve para reportes confiables.

## Core Relationships

| Relationship                              | Cardinality   | Explanation                                                                         |
| ----------------------------------------- | ------------- | ----------------------------------------------------------------------------------- |
| `PERSON` -> `CUSTOMER`                    | `1` to `0..1` | Una persona puede convertirse en cliente; un cliente debe pertenecer a una persona. |
| `CUSTOMER` -> `SALES_ORDER`               | `1` to `0..N` | Un cliente puede realizar muchas ventas; cada venta pertenece a un cliente.         |
| `SALES_ORDER` -> `SALES_ORDER_ITEM`       | `1` to `1..N` | Una venta debe tener al menos una linea vendida.                                    |
| `PART` -> `SALES_ORDER_ITEM`              | `1` to `0..N` | Un repuesto puede venderse muchas veces.                                            |
| `SALES_ORDER` -> `PAYMENT`                | `1` to `0..N` | Una venta puede tener cero, uno o varios pagos.                                     |
| `PART_CATEGORY` -> `PART`                 | `1` to `0..N` | Una categoria agrupa varios repuestos.                                              |
| `PART` -> `INVENTORY_STOCK`               | `1` to `0..N` | Un repuesto puede tener stock en una o varias ubicaciones.                          |
| `PART` -> `PART_COMPATIBILITY`            | `1` to `0..N` | Un repuesto puede tener varias compatibilidades.                                    |
| `VEHICLE_MODEL` -> `PART_COMPATIBILITY`   | `1` to `0..N` | Un vehiculo puede aceptar varios repuestos.                                         |
| `SUPPLIER` -> `PURCHASE_ORDER`            | `1` to `0..N` | Un proveedor puede recibir muchas ordenes de compra.                                |
| `PURCHASE_ORDER` -> `PURCHASE_ORDER_ITEM` | `1` to `1..N` | Una compra debe tener una o mas lineas.                                             |
| `PART` -> `PURCHASE_ORDER_ITEM`           | `1` to `0..N` | Un repuesto puede comprarse muchas veces.                                           |
| `SALES_ORDER` -> `RETURN_ORDER`           | `1` to `0..N` | Una venta puede tener devoluciones o garantias.                                     |
| `RETURN_ORDER` -> `RETURN_ORDER_ITEM`     | `1` to `1..N` | Una devolucion debe detallar que se devuelve.                                       |
| `SALES_ORDER_ITEM` -> `RETURN_ORDER_ITEM` | `1` to `0..N` | Una linea vendida puede devolverse total o parcialmente.                            |

Estas cardinalidades son la parte que muchos estudiantes se saltan. Mal. Sin
cardinalidad no sabes si el negocio permite cero, uno o muchos. Y sin eso el
modelo queda incompleto.

## Many-to-Many Relationships

Las relaciones many-to-many no se implementan directamente en un modelo
relacional bien hecho. Se resuelven con una tabla intermedia.

En este proyecto, el caso mas claro es:

`PART` <-> `VEHICLE_MODEL`

Un `PART` puede servir para muchos `VEHICLE_MODEL`.
Un `VEHICLE_MODEL` puede aceptar muchos `PART`.

La solucion correcta es:

`PART` -> `PART_COMPATIBILITY` -> `VEHICLE_MODEL`

`PART_COMPATIBILITY` no es una tabla de relleno. Es la entidad que permite
guardar informacion propia de la compatibilidad, como:

- `engine_code`;
- `notes`;
- restricciones de version;
- observaciones tecnicas;
- futuras condiciones de posicion, lado o rango.

Si no entiendes esto, terminas metiendo listas separadas por coma en una celda.
Eso no es base de datos relacional. Eso es una planilla disfrazada.

## Primary Keys

Usaremos primary keys tecnicas con patron `*_id`, por ejemplo:

- `person_id`
- `customer_id`
- `part_id`
- `sales_order_id`
- `sales_order_item_id`
- `payment_id`

La razon es simple: una primary key debe identificar una fila de forma estable.
No conviene usar datos cambiantes o externos como primary key principal.

Ejemplo: `identity_number` puede parecer buen identificador para `PERSON`, pero
puede venir incompleto, corregirse, cambiar de formato o repetirse por error de
captura. Debe ser `UNIQUE` cuando corresponda, pero no necesariamente la primary
key fisica.

## Foreign Keys

Las foreign keys protegen las relaciones. Ejemplos:

- `CUSTOMER.person_id` apunta a `PERSON.person_id`.
- `SALES_ORDER.customer_id` apunta a `CUSTOMER.customer_id`.
- `SALES_ORDER_ITEM.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `SALES_ORDER_ITEM.part_id` apunta a `PART.part_id`.
- `PAYMENT.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `PURCHASE_ORDER.supplier_id` apunta a `SUPPLIER.supplier_id`.
- `PURCHASE_ORDER_ITEM.part_id` apunta a `PART.part_id`.
- `RETURN_ORDER.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `RETURN_ORDER_ITEM.sales_order_item_id` apunta a
  `SALES_ORDER_ITEM.sales_order_item_id`.

Sin foreign keys, la base permite basura:

- pagos que apuntan a ventas inexistentes;
- lineas de venta sin venta;
- compras sin proveedor;
- devoluciones sin venta original;
- compatibilidades con repuestos borrados.

Un sistema que permite eso no esta "flexible". Esta mal protegido.

## Unique Constraints

Algunos datos deben ser unicos porque el negocio lo necesita:

| Entity               | Candidate Unique Field                       | Why                                                                      |
| -------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| `PERSON`             | `identity_number`                            | Evita duplicar a la misma persona por CI/NIT cuando aplica.              |
| `CUSTOMER`           | `person_id`                                  | Evita que una persona tenga dos registros de cliente sin razon.          |
| `SUPPLIER`           | `tax_id`                                     | Evita duplicar proveedor por NIT/RUC.                                    |
| `PART_CATEGORY`      | `name`                                       | Evita categorias repetidas como "Filtros" y "filtros".                   |
| `PART`               | `internal_code`                              | Es el codigo operativo del repuesto dentro del negocio.                  |
| `INVENTORY_STOCK`    | `part_id`, `location_name`                   | Evita dos saldos distintos para el mismo repuesto en la misma ubicacion. |
| `PART_COMPATIBILITY` | `part_id`, `vehicle_model_id`, `engine_code` | Reduce duplicados de compatibilidad.                                     |

Estas restricciones no son lujo. Son defensa contra datos mediocres.

## Historical Values

El ERD guarda valores historicos en las lineas:

- `SALES_ORDER_ITEM.unit_price`
- `SALES_ORDER_ITEM.discount_amount`
- `PURCHASE_ORDER_ITEM.unit_cost`

Esto es obligatorio si quieres reportes confiables.

Ejemplo: hoy `PART.sale_price` puede ser 150. La semana pasada era 120. Si una
venta de la semana pasada solo apunta a `PART.sale_price`, el reporte historico
mentira cuando el precio cambie.

Por eso:

- `PART.sale_price` es precio actual de referencia.
- `SALES_ORDER_ITEM.unit_price` es precio de la venta en ese momento.
- `PART.purchase_cost` es costo actual de referencia.
- `PURCHASE_ORDER_ITEM.unit_cost` es costo de esa compra en ese momento.

El estudiante que recalcula ventas pasadas con precios actuales no esta
optimizando. Esta destruyendo evidencia historica.

## Status Fields

El ERD compacto usa campos `status` en varias tablas:

- `PART.status`
- `SALES_ORDER.status`
- `PAYMENT.status`
- `PURCHASE_ORDER.status`
- `RETURN_ORDER.status`

Para una version academica compacta puede usarse `varchar` con reglas
documentadas. Para una version mas seria conviene:

- `CHECK` constraints;
- tablas catalogo como `SALES_ORDER_STATUS`;
- enums controlados desde la aplicacion;
- validaciones consistentes en formularios.

Ejemplos razonables:

| Entity           | Status Examples                                       |
| ---------------- | ----------------------------------------------------- |
| `PART`           | `active`, `inactive`, `discontinued`, `blocked`       |
| `SALES_ORDER`    | `draft`, `confirmed`, `paid`, `cancelled`, `returned` |
| `PAYMENT`        | `pending`, `confirmed`, `voided`, `refunded`          |
| `PURCHASE_ORDER` | `draft`, `sent`, `partial`, `received`, `cancelled`   |
| `RETURN_ORDER`   | `requested`, `approved`, `rejected`, `completed`      |

No aceptes estados escritos libremente tipo "pagado", "Pago", "PAG", "pagooo".
Eso es exactamente como se pudre una base de datos.

## Business Rules

Estas reglas deben convertirse en restricciones, validaciones o procedimientos:

| Rule                                                              | Where It Applies                       | Reason                                                  |
| ----------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------- |
| `PART.internal_code` must be unique.                              | `PART`                                 | Evita repuestos duplicados en el catalogo.              |
| `SALES_ORDER_ITEM.quantity` must be greater than zero.            | `SALES_ORDER_ITEM`                     | No existe venta de cantidad cero o negativa.            |
| `PURCHASE_ORDER_ITEM.quantity_ordered` must be greater than zero. | `PURCHASE_ORDER_ITEM`                  | No existe compra real de cantidad cero o negativa.      |
| `PAYMENT.amount` must be greater than zero.                       | `PAYMENT`                              | Un pago negativo no es pago; seria devolucion o ajuste. |
| Total returned quantity cannot exceed sold quantity.              | `RETURN_ORDER_ITEM`                    | Evita devolver mas de lo vendido.                       |
| A returned item can restock only if `restock_allowed = true`.     | `RETURN_ORDER_ITEM`, `INVENTORY_STOCK` | Evita reingresar productos defectuosos o no aptos.      |
| Confirmed sales must validate available stock.                    | `SALES_ORDER_ITEM`, `INVENTORY_STOCK`  | Evita vender stock inexistente.                         |
| Payments must belong to a valid sale.                             | `PAYMENT`                              | Protege trazabilidad de cobros.                         |
| Purchase items must belong to a valid purchase order.             | `PURCHASE_ORDER_ITEM`                  | Protege trazabilidad de reposicion.                     |
| Returns must belong to a valid original sale.                     | `RETURN_ORDER`                         | Protege garantia y devolucion.                          |

No todo se resuelve con foreign keys. Algunas reglas necesitan transacciones,
triggers, procedimientos o logica de aplicacion. Por ejemplo, validar stock
disponible antes de confirmar una venta suele requerir leer saldo, reservar o
descontar dentro de una operacion controlada.

## Where This Model Lives

| File                                                   | Role                                                          |
| ------------------------------------------------------ | ------------------------------------------------------------- |
| [erd.md](erd.md)                                       | Diagrama ERD principal en Mermaid.                            |
| [erd_explanation.md](erd_explanation.md)               | Explicacion tecnica y defensa del modelo.                     |
| [erd_business_research.md](erd_business_research.md)   | Investigacion de negocio e industria que justifica entidades. |
| [../analysis/processes.md](../analysis/processes.md)   | Procesos reales que originan entidades y reglas.              |
| [../analysis/actors.md](../analysis/actors.md)         | Actores que interactuan con el sistema.                       |
| [../analysis/procedures.md](../analysis/procedures.md) | Pasos operativos que deben soportarse.                        |
| [schema.sql](schema.sql)                               | Futuro SQL fisico; debe alinearse con el ERD final.           |

Nota tecnica importante: actualmente `schema.sql` todavia no representa un SQL
fisico completo para PostgreSQL 18.4. Contiene un boceto parcial. El modelo
defendible esta en `erd.md`; luego el SQL debe actualizarse para reflejarlo.

## When We Use the ERD

El ERD se usa en varias etapas:

| Moment             | How It Helps                                                                 |
| ------------------ | ---------------------------------------------------------------------------- |
| Analysis           | Permite comprobar que los procesos reales tienen datos representados.        |
| Design             | Define entidades, relaciones, cardinalidades y restricciones.                |
| SQL implementation | Guia la creacion de tablas, keys y constraints.                              |
| UI design          | Indica formularios, modulos, filtros y vistas necesarias.                    |
| Testing            | Permite crear casos: venta con lineas, pago parcial, devolucion, stock bajo. |
| Reporting          | Muestra de donde salen ventas, compras, pagos y stock.                       |
| Maintenance        | Ayuda a entender impacto antes de cambiar una tabla.                         |

No se hace ERD solo para entregar una imagen. Se hace para tomar decisiones
mejores durante todo el proyecto.

## Where It Applies in the Business

| Business Area          | ERD Support                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| Sales counter          | `CUSTOMER`, `PART`, `PART_COMPATIBILITY`, `INVENTORY_STOCK`, `SALES_ORDER` |
| Warehouse              | `PART`, `INVENTORY_STOCK`, `PURCHASE_ORDER_ITEM`, `RETURN_ORDER_ITEM`      |
| Purchasing             | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM`, `PART`                |
| Cashier                | `SALES_ORDER`, `PAYMENT`                                                   |
| Returns and warranties | `RETURN_ORDER`, `RETURN_ORDER_ITEM`, `SALES_ORDER_ITEM`                    |
| Management             | Reportes desde ventas, compras, pagos, inventario y devoluciones           |

El ERD conecta areas. Ventas no puede vivir aislada de inventario. Inventario no
puede vivir aislado de compras. Devoluciones no pueden vivir aisladas de ventas.
Ese es el punto de una base de datos centralizada.

## What Questions the Model Can Answer

Con este modelo se pueden responder consultas importantes:

- Que repuestos estan activos?
- Que repuestos pertenecen a una categoria?
- Que repuestos son compatibles con cierto vehiculo?
- Cuanto stock hay por repuesto y ubicacion?
- Que clientes compraron en cierto periodo?
- Que repuestos se vendieron mas?
- Que ventas estan pagadas, pendientes o anuladas?
- Que pagos se registraron por venta?
- Que proveedores abastecen compras?
- Que compras estan pendientes o parcialmente recibidas?
- Que ventas tuvieron devoluciones?
- Que repuestos devueltos pueden volver a stock?
- Que margen aproximado existe entre precio de venta y costo historico?

Si el modelo no puede responder preguntas operativas, esta mal orientado. El
ERD no es arte. Es una herramienta para decidir, controlar y consultar.

## Normalization Level

El modelo apunta a una normalizacion practica, cercana a tercera forma normal
para el alcance academico:

- Cada entidad representa un concepto principal.
- Los atributos dependen de la primary key de su entidad.
- Los datos repetibles se separan en tablas hijas.
- Las relaciones many-to-many se resuelven con tablas intermedias.
- Los valores historicos importantes se guardan en las lineas operativas.

Ejemplos:

- `SALES_ORDER_ITEM` existe porque una venta puede tener varias lineas.
- `PURCHASE_ORDER_ITEM` existe porque una compra puede tener varias lineas.
- `PART_COMPATIBILITY` existe porque compatibilidad es many-to-many.
- `PAYMENT` existe porque el cobro tiene vida propia frente a la venta.

Pero no se normaliza todo al extremo. Por ejemplo, en el ERD compacto:

- `PART.brand` queda como texto;
- `PART.unit` queda como texto;
- `INVENTORY_STOCK.location_name` queda como texto;
- `VEHICLE_MODEL.make` queda como texto.

Eso es aceptable para un proyecto compacto. La version mas fuerte podria
separar `BRAND`, `UNIT`, `WAREHOUSE_LOCATION`, `VEHICLE_MAKE` y otros catalogos.

## Compact Model vs Strong Model

El ERD actual es una buena base compacta. Pero hay que decir la verdad: no es
la version mas robusta posible.

| Option                 | What It Means                                                                                            | Tradeoff                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Compact Academic Model | Mantener entidades actuales y documentar reglas.                                                         | Mas simple y defendible para Base de Datos I, pero menos trazable.     |
| Strong Academic Model  | Agregar `INVENTORY_MOVEMENT`, recepciones, usuarios y constraints mas estrictos.                         | Mas trabajo, pero mucho mejor control operativo.                       |
| Industry-Grade Model   | Agregar fitment avanzado, codigos alternativos, facturacion, auditoria completa y proveedores por pieza. | Excelente, pero probablemente demasiado grande para el proyecto final. |

Recomendacion honesta: usar el **Compact Academic Model** como entrega base y
dejar documentada la ruta hacia el **Strong Academic Model**.

## Known Limitations

| Limitation                  | Why It Matters                                                        | Recommended Extension                                           |
| --------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------- |
| No `INVENTORY_MOVEMENT`     | No explica por que cambio el stock.                                   | Agregar entradas, salidas, ajustes, devoluciones y responsable. |
| No `PURCHASE_RECEIPT`       | Mezcla compra con recepcion real.                                     | Agregar `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM`.           |
| Single `PART.oem_code`      | Un repuesto puede tener multiples codigos.                            | Agregar `PART_IDENTIFIER`.                                      |
| Simple `VEHICLE_MODEL`      | Fitment real puede requerir motor, version, posicion o restricciones. | Fortalecer `PART_COMPATIBILITY`.                                |
| `CUSTOMER` tied to `PERSON` | Talleres o empresas no siempre son personas naturales.                | Agregar `customer_type` o modelo `PARTY`.                       |
| Free-text statuses          | Permite valores inconsistentes.                                       | Usar `CHECK` constraints o catalogos.                           |
| No `USER_ACCOUNT`           | No queda claro quien hizo cada operacion.                             | Agregar usuarios, roles y auditoria.                            |
| No invoice table            | Venta y comprobante fiscal no son lo mismo.                           | Agregar `SALES_INVOICE` si el alcance tributario importa.       |

Esto no invalida el ERD. Lo ubica. Saber que queda fuera es senal de criterio,
no de debilidad.

## Why This Scope Is Correct for the Project

El proyecto es de Base de Datos I. El objetivo no es construir SAP. El objetivo
es demostrar que sabemos:

- identificar entidades reales;
- separar conceptos;
- definir relaciones;
- aplicar primary keys y foreign keys;
- evitar duplicidad;
- proteger reglas basicas;
- justificar el modelo desde procesos;
- producir un diseno que luego pueda implementarse en SQL.

El modelo elegido cubre el flujo principal:

`CUSTOMER` -> `SALES_ORDER` -> `SALES_ORDER_ITEM` -> `PART`

Y conecta los ciclos secundarios:

`SUPPLIER` -> `PURCHASE_ORDER` -> `PURCHASE_ORDER_ITEM` -> `PART`

`SALES_ORDER` -> `RETURN_ORDER` -> `RETURN_ORDER_ITEM` -> `SALES_ORDER_ITEM`

`PART` -> `PART_COMPATIBILITY` -> `VEHICLE_MODEL`

`PART` -> `INVENTORY_STOCK`

Ese es el corazon operativo del negocio. Si eso esta bien, el proyecto tiene
base. Si eso esta mal, ninguna pantalla bonita lo salva.

## Implementation Guidelines

Cuando el ERD se convierta a SQL, se deben seguir estas reglas:

| Guideline                                                  | Reason                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------- |
| Use English table and column names.                        | Mantiene consistencia tecnica y estilo profesional.         |
| Use singular table names.                                  | `PART`, `CUSTOMER`, `PAYMENT` son entidades, no listas.     |
| Use `snake_case` for columns.                              | `sales_order_id`, `unit_price`, `return_date` son legibles. |
| Use surrogate primary keys.                                | Evita depender de datos externos o cambiantes.              |
| Add foreign keys explicitly.                               | Protege integridad referencial.                             |
| Add unique constraints where business requires uniqueness. | Evita duplicados silenciosos.                               |
| Add check constraints for positive quantities and amounts. | Evita datos absurdos.                                       |
| Store historical prices and costs in detail rows.          | Protege reportes historicos.                                |
| Do not delete operational history casually.                | Ventas, pagos y devoluciones son evidencia.                 |
| Document status values.                                    | Evita estados libres inconsistentes.                        |

Tambien conviene crear las tablas en orden:

1. Tablas independientes: `PERSON`, `SUPPLIER`, `PART_CATEGORY`,
   `VEHICLE_MODEL`.
2. Tablas dependientes simples: `CUSTOMER`, `PART`.
3. Tablas de relacion y stock: `PART_COMPATIBILITY`, `INVENTORY_STOCK`.
4. Cabeceras operativas: `SALES_ORDER`, `PURCHASE_ORDER`.
5. Detalles operativos: `SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM`.
6. Eventos dependientes: `PAYMENT`, `RETURN_ORDER`, `RETURN_ORDER_ITEM`.

El orden importa porque las foreign keys necesitan que las tablas padre existan
antes.

## Validation Examples

Casos que el modelo debe soportar:

### Sale With Multiple Parts

Un cliente compra aceite, filtro y pastillas de freno.

- Existe un `CUSTOMER`.
- Se crea una `SALES_ORDER`.
- Se crean tres `SALES_ORDER_ITEM`.
- Cada linea apunta a un `PART`.
- Se registra uno o mas `PAYMENT`.
- El stock debe reducirse segun cantidades vendidas.

### Part Compatible With Multiple Vehicles

Un filtro sirve para varios modelos de Toyota.

- Existe un `PART`.
- Existen varios `VEHICLE_MODEL`.
- Se crean varias filas en `PART_COMPATIBILITY`.

No se repite el repuesto. No se escriben vehiculos como texto dentro del
repuesto. Se modela la relacion.

### Partial Payment

Un cliente paga una parte por transferencia y otra en efectivo.

- Una `SALES_ORDER` puede tener varias filas en `PAYMENT`.
- Cada `PAYMENT` tiene `method`, `amount`, `reference_number` y `status`.

Esto evita forzar una venta a tener un solo metodo de pago.

### Return Against Original Sale

Un cliente devuelve una pieza defectuosa.

- Se ubica la `SALES_ORDER`.
- Se identifica la `SALES_ORDER_ITEM`.
- Se crea una `RETURN_ORDER`.
- Se crea una `RETURN_ORDER_ITEM`.
- Se valida cantidad devuelta.
- Se decide si `restock_allowed` es verdadero o falso.

La devolucion no flota en el aire. Esta anclada a la venta.

## Common Mistakes This ERD Avoids

| Mistake                                             | Why It Is Wrong                                 | ERD Solution                                    |
| --------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| Repeating customer data in every sale               | Produce duplicados y errores de actualizacion.  | `PERSON` and `CUSTOMER`.                        |
| Storing sold products in columns `part_1`, `part_2` | Limita cantidad y rompe consultas.              | `SALES_ORDER_ITEM`.                             |
| Using current price for old sales                   | Rompe reportes historicos.                      | `SALES_ORDER_ITEM.unit_price`.                  |
| Storing compatibility as free text                  | No permite buscar ni validar bien.              | `PART_COMPATIBILITY`.                           |
| Recording returns without original sale             | Permite fraude o errores.                       | `RETURN_ORDER` linked to `SALES_ORDER`.         |
| Mixing purchase header and purchase detail          | Repite proveedor, fecha y estado por linea.     | `PURCHASE_ORDER` and `PURCHASE_ORDER_ITEM`.     |
| Treating payment as a field in sale only            | No soporta pagos parciales o multiples metodos. | `PAYMENT`.                                      |
| Using stock as magic number                         | No explica cambios ni soporta auditoria.        | `INVENTORY_STOCK`, future `INVENTORY_MOVEMENT`. |

## Final Model Position

La posicion final del proyecto debe ser esta:

> Zarvent Repuestos usara un modelo entidad-relacion operacional, compacto y
> relacional, implementable en PostgreSQL 18.4, con entidades separadas para
> identidad, clientes, proveedores, catalogo de repuestos, compatibilidad
> vehicular, stock, ventas, pagos, compras y devoluciones.

Este modelo se elige porque:

- coincide con los procesos reales documentados;
- reduce duplicidad;
- mantiene integridad referencial;
- soporta reportes operativos;
- conserva precios y costos historicos;
- modela compatibilidad como relacion many-to-many;
- conecta devoluciones con ventas reales;
- permite crecer hacia auditoria de inventario, recepciones y usuarios.

Tambien se reconoce que el modelo compacto no cubre todo. La mejora mas
importante seria agregar `INVENTORY_MOVEMENT`, porque el stock serio no es solo
un saldo: es una consecuencia de eventos.

## Research Sources

Fuentes conceptuales y tecnicas usadas para sostener el criterio del modelo:

- Peter P. Chen, **The Entity-Relationship Model: Toward a Unified View of
  Data**. Trabajo fundacional del modelo entidad-relacion.
  <https://dl.acm.org/doi/10.1145/320434.320440>
- E. F. Codd, **A Relational Model of Data for Large Shared Data Banks**.
  Trabajo fundacional del modelo relacional.
  <https://research.ibm.com/publications/a-relational-model-of-data-for-large-shared-data-banks>
- PostgreSQL 18.4 Documentation, **Data Definition / Constraints**, para
  criterios de primary keys, foreign keys, unique constraints y check
  constraints.
  <https://www.postgresql.org/docs/18/ddl-constraints.html>
- Auto Care Association, **Auto Care Data Standards**, para la importancia de
  catalogo y compatibilidad de repuestos en la industria automotriz.
  <https://www.autocare.org/data-standards>
- Oracle JD Edwards, **Order Processing Cycle**, para el ciclo de compras,
  recepcion y costos.
  <https://docs.oracle.com/en/applications/jd-edwards/supply-management/9.2/eoapr/order-processing-cycle.html>
- IBM Maximo, **Inventory Module**, para tareas tipicas de inventario:
  recepciones, salidas, retornos, transferencias, ubicaciones y reorden.
  <https://www.ibm.com/docs/en/masv-and-l/maximo-manage/cd?topic=manage-inventory-module>
