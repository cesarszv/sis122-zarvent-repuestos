-- archivo para guardar el borrador manual del esquema SQL del proyecto

/*
Zarvent Repuestos - MySQL schema draft

This file is intentionally simple.
Write the real MySQL CREATE TABLE statements manually while studying the ERD.

Source model:
docs/database/erd.md
*/

CREATE DATABASE IF NOT EXISTS sis122_zarvent_repuestos;
USE sis122_zarvent_repuestos;

/*
Recommended creation order:

1. person
2. customer
3. supplier
4. part_category
5. part
6. vehicle_model
7. part_compatibility
8. inventory_stock
9. sales_order
10. sales_order_item
11. payment
12. purchase_order
13. purchase_order_item
14. return_order
15. return_order_item

Write each table only after you can explain:

- what the table represents
- its primary key
- its foreign keys
- which attributes are required
- which attributes should be unique
- which business rule the table protects
*/
