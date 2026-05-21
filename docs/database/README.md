# Database Documentation

Esta carpeta contiene la documentacion del modelo entidad-relacion de Zarvent
Repuestos.

## Documentos

| Documento | Uso |
| --- | --- |
| [erd.md](erd.md) | Diagrama ERD compacto en Mermaid. |
| [db_explanation.md](db_explanation.md) | Explicacion breve de cada tabla del ERD. |
| [erd_explanation.md](erd_explanation.md) | Defensa tecnica del modelo relacional. |
| [erd_business_research.md](erd_business_research.md) | Justificacion del modelo desde el negocio de repuestos. |
| [../../database/schema.sql](../../database/schema.sql) | Borrador manual del SQL para MySQL Server. |

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

El ERD no busca verse grande. Busca separar conceptos correctamente:

- una persona no es lo mismo que un cliente;
- un repuesto no es lo mismo que su stock;
- una venta no es lo mismo que un pago;
- una compra no es lo mismo que su detalle;
- una devolucion debe apuntar a una venta real;
- la compatibilidad vehicular es una relacion muchos-a-muchos.

Si puedes explicar esas separaciones, puedes defender el modelo relacional.
