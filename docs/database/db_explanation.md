# Database Table Explanation

Este documento explica las tablas del ERD de Zarvent Repuestos de forma corta y
defendible. El diagrama principal esta en [erd.md](erd.md).

El modelo cubre el flujo central del negocio:

`CUSTOMER -> SALES_ORDER -> SALES_ORDER_ITEM -> PART -> INVENTORY_STOCK`

Tambien cubre dos ciclos importantes:

- `SUPPLIER -> PURCHASE_ORDER -> PURCHASE_ORDER_ITEM -> PART`
- `SALES_ORDER -> RETURN_ORDER -> RETURN_ORDER_ITEM -> SALES_ORDER_ITEM`

## Tablas del modelo

| Tabla | Que representa | Atributos clave | Por que existe |
| --- | --- | --- | --- |
| `PERSON` | Identidad civil o contacto base. | `person_id`, `first_name`, `last_name`, `identity_number`, `phone`, `email`, `address` | Evita repetir datos personales en ventas, clientes o devoluciones. |
| `CUSTOMER` | Rol comercial del comprador. | `customer_id`, `person_id`, `billing_name`, `tax_id` | Separa la persona del cliente que compra, factura y tiene historial. |
| `SUPPLIER` | Proveedor que abastece repuestos. | `supplier_id`, `business_name`, `tax_id`, `phone`, `email`, `address`, `is_active` | Permite controlar a quien se compra y mantener historial de compras. |
| `PART_CATEGORY` | Grupo o categoria del repuesto. | `part_category_id`, `name`, `description` | Ordena el catalogo y evita categorias escritas de varias formas. |
| `PART` | Repuesto vendible, comprable e inventariable. | `part_id`, `part_category_id`, `internal_code`, `oem_code`, `name`, `brand`, `unit`, `sale_price`, `purchase_cost`, `warranty_days`, `status` | Es la tabla central del negocio: ventas, compras, stock y compatibilidad dependen de ella. |
| `VEHICLE_MODEL` | Vehiculo usado para validar compatibilidad. | `vehicle_model_id`, `make`, `model`, `year_from`, `year_to` | Permite relacionar repuestos con marca, modelo y anio del vehiculo. |
| `PART_COMPATIBILITY` | Relacion entre repuesto y vehiculo compatible. | `part_compatibility_id`, `part_id`, `vehicle_model_id`, `engine_code`, `notes` | Resuelve la relacion muchos-a-muchos entre repuestos y vehiculos. |
| `INVENTORY_STOCK` | Saldo actual de un repuesto en una ubicacion. | `inventory_stock_id`, `part_id`, `location_name`, `quantity_on_hand`, `reorder_level` | Permite saber cuanto hay y donde esta antes de vender o reponer. |
| `SALES_ORDER` | Cabecera de la venta. | `sales_order_id`, `customer_id`, `order_date`, `status`, `subtotal`, `discount_amount`, `total_amount` | Agrupa cliente, fecha, estado y totales de la venta. |
| `SALES_ORDER_ITEM` | Linea de repuesto vendido. | `sales_order_item_id`, `sales_order_id`, `part_id`, `quantity`, `unit_price`, `discount_amount` | Permite vender varios repuestos en una venta y conservar precio historico. |
| `PAYMENT` | Cobro asociado a una venta. | `payment_id`, `sales_order_id`, `payment_date`, `method`, `amount`, `reference_number`, `status` | Separa cobrar de vender y permite pagos parciales o multiples metodos. |
| `PURCHASE_ORDER` | Cabecera de compra a proveedor. | `purchase_order_id`, `supplier_id`, `order_date`, `expected_date`, `status`, `total_amount` | Controla pedidos de reposicion y compras pendientes. |
| `PURCHASE_ORDER_ITEM` | Linea de repuesto comprado. | `purchase_order_item_id`, `purchase_order_id`, `part_id`, `quantity_ordered`, `quantity_received`, `unit_cost` | Guarda cantidades y costo historico de cada repuesto comprado. |
| `RETURN_ORDER` | Cabecera de devolucion o garantia. | `return_order_id`, `sales_order_id`, `return_date`, `reason`, `resolution`, `status` | Obliga a que una devolucion nazca de una venta real. |
| `RETURN_ORDER_ITEM` | Linea devuelta. | `return_order_item_id`, `return_order_id`, `sales_order_item_id`, `quantity`, `refund_amount`, `restock_allowed` | Permite validar que se devuelva una linea vendida y decidir si vuelve a stock. |

## Relaciones clave

| Relacion | Cardinalidad | Explicacion |
| --- | --- | --- |
| `PERSON` -> `CUSTOMER` | 1 a 0..1 | Una persona puede convertirse en cliente. |
| `CUSTOMER` -> `SALES_ORDER` | 1 a 0..N | Un cliente puede tener muchas ventas. |
| `SALES_ORDER` -> `SALES_ORDER_ITEM` | 1 a 1..N | Una venta debe tener al menos una linea. |
| `PART` -> `SALES_ORDER_ITEM` | 1 a 0..N | Un repuesto puede venderse muchas veces. |
| `SALES_ORDER` -> `PAYMENT` | 1 a 0..N | Una venta puede tener varios pagos. |
| `PART_CATEGORY` -> `PART` | 1 a 0..N | Una categoria agrupa varios repuestos. |
| `PART` -> `PART_COMPATIBILITY` -> `VEHICLE_MODEL` | muchos a muchos | Un repuesto puede servir para varios vehiculos y un vehiculo puede aceptar varios repuestos. |
| `PART` -> `INVENTORY_STOCK` | 1 a 0..N | Un repuesto puede tener stock en varias ubicaciones. |
| `SUPPLIER` -> `PURCHASE_ORDER` | 1 a 0..N | Un proveedor puede recibir muchas compras. |
| `PURCHASE_ORDER` -> `PURCHASE_ORDER_ITEM` | 1 a 1..N | Una compra debe tener una o mas lineas. |
| `SALES_ORDER` -> `RETURN_ORDER` | 1 a 0..N | Una venta puede tener devoluciones. |
| `RETURN_ORDER_ITEM` -> `SALES_ORDER_ITEM` | N a 1 | Cada devolucion apunta a una linea vendida real. |

## Reglas que deben defenderse

- `PART.internal_code` debe ser unico.
- `PERSON.identity_number` y `SUPPLIER.tax_id` deben evitar duplicados cuando
  el dato exista.
- `SALES_ORDER_ITEM.unit_price` guarda el precio historico de venta.
- `PURCHASE_ORDER_ITEM.unit_cost` guarda el costo historico de compra.
- Una venta confirmada no debe vender mas que el stock disponible.
- Un pago debe pertenecer a una venta real.
- Una devolucion debe apuntar a una venta real y a una linea vendida.
- La cantidad devuelta no debe exceder la cantidad vendida.
- Un producto devuelto solo vuelve a stock si `restock_allowed = true`.

## Limitaciones aceptadas

El ERD es compacto para Base de Datos I. Por eso deja fuera algunas mejoras:

| Mejora futura | Por que seria util |
| --- | --- |
| `INVENTORY_MOVEMENT` | Explica por que sube o baja el stock. |
| `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM` | Separa lo pedido de lo recibido. |
| `PART_IDENTIFIER` | Permite varios codigos por repuesto: OEM, proveedor, barcode, alternativo. |
| `USER_ACCOUNT` | Registra quien vendio, cobro, compro o ajusto stock. |
| `SALES_INVOICE` | Separa la venta del documento fiscal o comercial. |

Estas limitaciones no invalidan el modelo. Muestran que el alcance actual es
academico y que hay una ruta clara para fortalecerlo.

## Cierre para defensa

La defensa no debe sonar como una lista memorizada. Debe sonar asi:

1. El negocio vende repuestos, por eso existe `PART`.
2. El repuesto debe servir para un vehiculo, por eso existe
   `PART_COMPATIBILITY`.
3. El cliente necesita historial, por eso existen `PERSON`, `CUSTOMER` y
   `SALES_ORDER`.
4. Una venta puede tener varios repuestos, por eso existe `SALES_ORDER_ITEM`.
5. Cobrar no es lo mismo que vender, por eso existe `PAYMENT`.
6. Reponer stock es otro proceso, por eso existen `SUPPLIER`,
   `PURCHASE_ORDER` y `PURCHASE_ORDER_ITEM`.
7. Devolver no es escribir una nota, por eso existen `RETURN_ORDER` y
   `RETURN_ORDER_ITEM`.
8. El stock actual sirve para operar, pero una version mas fuerte deberia
   agregar `INVENTORY_MOVEMENT`.
