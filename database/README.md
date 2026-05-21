# Database

Esta carpeta contiene el borrador del esquema SQL.

## Archivo principal

- [`schema.sql`](schema.sql): archivo donde se escribira manualmente el esquema
  de MySQL.

## Regla de trabajo

El ERD manda conceptualmente. El SQL debe traducir ese modelo a tablas reales.

Orden recomendado:

1. `person`
2. `customer`
3. `supplier`
4. `part_category`
5. `part`
6. `vehicle_model`
7. `part_compatibility`
8. `inventory_stock`
9. `sales_order`
10. `sales_order_item`
11. `payment`
12. `purchase_order`
13. `purchase_order_item`
14. `return_order`
15. `return_order_item`

Primero crea las tablas base. Despues las tablas que dependen de ellas. Eso no
es capricho: las claves foraneas necesitan que la tabla referenciada ya exista.
