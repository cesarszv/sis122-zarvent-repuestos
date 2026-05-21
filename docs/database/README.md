# Database Documentation

Esta carpeta contiene la documentacion del modelo entidad-relacion de Zarvent
Repuestos.

## Documentos

| Documento | Para que sirve |
| --- | --- |
| [`erd.md`](erd.md) | Presenta el diagrama ERD compacto. |
| [`db_explanation.md`](db_explanation.md) | Explica cada tabla, atributo y relacion. |
| [`erd_explanation.md`](erd_explanation.md) | Defiende por que el modelo es relacional y normalizado. |
| [`erd_business_research.md`](erd_business_research.md) | Conecta el modelo con procesos reales del negocio. |
| [`../../database/schema.sql`](../../database/schema.sql) | Borrador manual del SQL que se escribira en MySQL. |

## Bloques del modelo

| Bloque | Tablas |
| --- | --- |
| Identidad y clientes | `PERSON`, `CUSTOMER` |
| Proveedores | `SUPPLIER` |
| Catalogo | `PART_CATEGORY`, `PART` |
| Compatibilidad vehicular | `VEHICLE_MODEL`, `PART_COMPATIBILITY` |
| Inventario | `INVENTORY_STOCK` |
| Ventas y pagos | `SALES_ORDER`, `SALES_ORDER_ITEM`, `PAYMENT` |
| Compras | `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |
| Devoluciones | `RETURN_ORDER`, `RETURN_ORDER_ITEM` |

## Idea central

El modelo no busca tener muchas tablas para verse avanzado. Busca separar bien
los conceptos:

- una persona no es lo mismo que un cliente
- un repuesto no es lo mismo que su stock
- una venta no es lo mismo que un pago
- una devolucion debe apuntar a una venta real
- la compatibilidad vehicular es una relacion muchos-a-muchos

Si entiendes esas separaciones, puedes defender el ERD. Si no, cualquier SQL que
escribas sera solo mecanografia.
