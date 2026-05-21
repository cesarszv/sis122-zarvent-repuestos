# Requerimientos

Los requerimientos salen del analisis del sistema actual de Zarvent Repuestos.
El objetivo principal es centralizar informacion, reducir duplicidad y permitir
consultas confiables.

| Codigo | Requerimiento | Entidades relacionadas |
| --- | --- | --- |
| RF-01 | Registrar clientes y sus datos de contacto/facturacion. | `PERSON`, `CUSTOMER` |
| RF-02 | Administrar catalogo de repuestos con codigo, categoria, precio, costo, garantia y estado. | `PART_CATEGORY`, `PART` |
| RF-03 | Registrar compatibilidad entre repuestos y vehiculos. | `VEHICLE_MODEL`, `PART_COMPATIBILITY` |
| RF-04 | Consultar stock por repuesto y ubicacion. | `PART`, `INVENTORY_STOCK` |
| RF-05 | Registrar ventas con una o mas lineas de repuestos. | `SALES_ORDER`, `SALES_ORDER_ITEM` |
| RF-06 | Registrar pagos asociados a ventas. | `PAYMENT`, `SALES_ORDER` |
| RF-07 | Registrar proveedores y compras de reposicion. | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |
| RF-08 | Registrar devoluciones o garantias contra ventas reales. | `RETURN_ORDER`, `RETURN_ORDER_ITEM`, `SALES_ORDER_ITEM` |
| RF-09 | Consultar reportes basicos de ventas, pagos, stock bajo, compras pendientes y devoluciones. | tablas operativas |

## Requerimientos no funcionales

- Usar nombres tecnicos en ingles.
- Mantener el modelo entendible para estudiantes de Base de Datos I.
- Implementar el esquema fisico en MySQL Server.
- Evitar datos duplicados mediante claves primarias, claves foraneas y
  restricciones de unicidad.
