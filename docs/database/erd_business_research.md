# Business Research Guide for the ERD

Esta guia conecta el ERD con la logica real de un negocio de repuestos. Su
objetivo es ayudar a defender por que existen las tablas, no llenar la carpeta
con teoria.

## Logica del negocio

Un negocio de repuestos no vende solo productos. Vende piezas que deben cumplir
tres condiciones:

1. La pieza debe existir en el catalogo.
2. La pieza debe ser compatible con el vehiculo del cliente.
3. La pieza debe estar disponible fisicamente.

Si una de esas condiciones falla, aparecen errores: venta equivocada,
devolucion, garantia, stock fantasma o compra innecesaria.

Por eso el ERD protege seis bloques:

- catalogo de repuestos;
- compatibilidad vehicular;
- inventario;
- ventas;
- compras;
- devoluciones.

## Flujo operativo defendible

1. El cliente consulta por un repuesto.
2. Ventas identifica vehiculo, codigo o descripcion.
3. Se busca el repuesto en `PART` y `PART_CATEGORY`.
4. Se valida compatibilidad en `PART_COMPATIBILITY`.
5. Se consulta stock en `INVENTORY_STOCK`.
6. Si el cliente compra, se crea `SALES_ORDER` y `SALES_ORDER_ITEM`.
7. El cobro se registra en `PAYMENT`.
8. Si el stock queda bajo, compras crea `PURCHASE_ORDER`.
9. El detalle comprado se guarda en `PURCHASE_ORDER_ITEM`.
10. Si hay devolucion, se registra en `RETURN_ORDER` y
    `RETURN_ORDER_ITEM`, siempre contra la venta original.

## Validacion de tablas

| Tabla | Validacion de negocio |
| --- | --- |
| `PERSON` | Centraliza identidad y contacto para evitar duplicados. |
| `CUSTOMER` | Representa al comprador y su historial comercial. |
| `SUPPLIER` | Permite controlar de quien se compra. |
| `PART_CATEGORY` | Ordena el catalogo. |
| `PART` | Es el repuesto vendible, comprable e inventariable. |
| `VEHICLE_MODEL` | Permite buscar compatibilidad por vehiculo. |
| `PART_COMPATIBILITY` | Evita vender piezas incompatibles. |
| `INVENTORY_STOCK` | Responde cuanto stock hay y donde esta. |
| `SALES_ORDER` | Registra la venta como evento comercial. |
| `SALES_ORDER_ITEM` | Guarda que repuestos se vendieron y a que precio historico. |
| `PAYMENT` | Registra cobros asociados a una venta. |
| `PURCHASE_ORDER` | Controla pedidos de reposicion a proveedores. |
| `PURCHASE_ORDER_ITEM` | Guarda cantidades y costos historicos de compra. |
| `RETURN_ORDER` | Relaciona devoluciones con una venta real. |
| `RETURN_ORDER_ITEM` | Relaciona cada devolucion con una linea vendida. |

## Riesgos del ERD compacto

| Riesgo | Explicacion | Mejora recomendada |
| --- | --- | --- |
| Stock sin historial | `INVENTORY_STOCK` muestra saldo, pero no explica por que cambio. | `INVENTORY_MOVEMENT` |
| Recepcion simplificada | `PURCHASE_ORDER_ITEM.quantity_received` mezcla pedido y recepcion. | `PURCHASE_RECEIPT`, `PURCHASE_RECEIPT_ITEM` |
| Un solo codigo externo | `PART.oem_code` puede ser insuficiente. | `PART_IDENTIFIER` |
| Compatibilidad basica | Marca, modelo y anio pueden no bastar para piezas reales. | mas atributos en `PART_COMPATIBILITY` |
| Clientes empresa | `CUSTOMER` ligado a `PERSON` funciona mejor para personas naturales. | `customer_type` o modelo `PARTY` |
| Estados como texto libre | Valores como "pagado", "Pago" y "PAG" crean inconsistencia. | `CHECK` o tablas catalogo |
| Sin responsable | No queda claro quien registro cada operacion. | `USER_ACCOUNT` |

## Reglas minimas

- `PART.internal_code` debe ser unico.
- `INVENTORY_STOCK` deberia ser unico por `part_id` y `location_name`.
- Una venta confirmada debe validar stock disponible.
- `SALES_ORDER_ITEM.unit_price` debe guardar precio historico.
- `PURCHASE_ORDER_ITEM.unit_cost` debe guardar costo historico.
- La suma devuelta no debe exceder la cantidad vendida.
- Un producto devuelto solo vuelve a stock si esta apto para reventa.
- Una compra recibida debe aumentar stock.
- Una venta entregada debe reducir stock.

## Alternativa recomendada

Para Base de Datos I, el ERD compacto es defendible. La mejora mas valiosa, si
el profesor permite ampliar el alcance, es agregar `INVENTORY_MOVEMENT`.

Esa tabla convierte el stock en una consecuencia de eventos:

`recepcion + venta + devolucion + ajuste = saldo de stock`

Ese razonamiento es mas fuerte que tratar el stock como un numero escrito a
mano.

## Fuentes de referencia

- [U.S. Census NAICS 441310](https://www.census.gov/naics/resources/archives/sect44-45.html):
  define el rubro de tiendas de repuestos y accesorios automotrices.
- [Auto Care Data Standards](https://www.autocare.org/data-standards):
  respalda la importancia de catalogo y compatibilidad de productos.
- [Oracle JD Edwards Order Processing Cycle](https://docs.oracle.com/en/applications/jd-edwards/supply-management/9.2/eoapr/order-processing-cycle.html):
  respalda el ciclo orden, recepcion y costo.
- [IBM Maximo Inventory Module](https://www.ibm.com/docs/en/masv-and-l/maximo-manage/cd?topic=manage-inventory-module):
  respalda control de stock, entradas, salidas, retornos y ubicaciones.
