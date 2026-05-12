# Business Research Guide for the ERD

Esta guia explica la logica de negocio detras del ERD de Zarvent Repuestos. No
esta escrita para decorar la documentacion. Esta escrita para que puedas
defender cada tabla con una razon operativa real.

## Research Sources

- U.S. Census NAICS define `Automotive Parts and Accessories Stores` como
  negocios que venden repuestos y accesorios automotrices nuevos, usados o
  reconstruidos, incluso con instalacion o reparacion asociada. Fuente:
  [U.S. Census NAICS 441310](https://www.census.gov/naics/resources/archives/sect44-45.html).
- Auto Care Association define `ACES` como estandar de datos para comunicar
  `product fitment`, y `PIES` como estandar para comunicar informacion de
  producto. Fuente:
  [Auto Care Data Standards](https://www.autocare.org/data-standards).
- Auto Care Association explica que `VCdb` sirve para busquedas por year, make
  and model, y comunica compatibilidad de productos con vehiculos mediante
  datos codificados. Fuente:
  [Auto Care VCdb](https://www.autocare.org/data-and-information/data-standards/databases/vehicle-configuration-database-vcdb).
- Auto Care Association explica que `PAdb` guarda atributos especificos del
  producto, como material, color, diametro o potencia, para diferenciar piezas
  similares. Fuente:
  [Auto Care PAdb](https://www.autocare.org/data-and-information/data-standards/databases/product-attribute-database-padb).
- Oracle JD Edwards documenta que una compra para inventario sigue un ciclo de
  orden, recepcion y voucher/pago, y que cada linea debe tener cantidad y costo.
  Fuente:
  [Oracle JD Edwards Order Processing Cycle](https://docs.oracle.com/en/applications/jd-edwards/supply-management/9.2/eoapr/order-processing-cycle.html).
- Oracle Inventory documenta que una venta sale desde inventario si existe
  cantidad reservable/transactable, y que una devolucion del cliente usa RMA
  contra una venta previa. Fuente:
  [Oracle Inventory Management](https://docs.oracle.com/cd/E18727-01/doc.121/e49332/ofbsk_chap31.htm).
- IBM Maximo resume tareas tipicas de inventario de repuestos: controlar stock,
  reordenar al bajar de un punto minimo, crear ordenes de compra, registrar
  recibos, salidas, retornos, transferencias y ubicaciones. Fuente:
  [IBM Maximo Inventory Module](https://www.ibm.com/docs/en/masv-and-l/maximo-manage/cd?topic=manage-inventory-module).

## Real Operating Logic

Un negocio de repuestos no vende solamente "productos". Vende piezas que deben
cumplir tres condiciones al mismo tiempo:

1. La pieza correcta debe existir en el catalogo.
2. La pieza debe ser compatible con el vehiculo del cliente.
3. La pieza debe estar disponible fisicamente para venderse.

Si cualquiera de esas tres falla, el negocio pierde tiempo, dinero o confianza:
venta equivocada, devolucion, reclamo de garantia, stock fantasma o compra
innecesaria. Por eso el ERD debe proteger catalogo, compatibilidad, inventario,
ventas, compras y devoluciones como un flujo completo.

El flujo real es:

1. El cliente consulta por un repuesto.
2. Ventas identifica el vehiculo, codigo OEM, marca, modelo, anio, motor o
   descripcion de la pieza.
3. Ventas busca en `PART`, `PART_CATEGORY` y `PART_COMPATIBILITY`.
4. Ventas verifica `INVENTORY_STOCK`.
5. Si el cliente acepta, se crea `SALES_ORDER` con lineas en
   `SALES_ORDER_ITEM`.
6. Se registra el cobro en `PAYMENT`.
7. Inventario debe descontar stock.
8. Si el stock queda bajo, compras crea `PURCHASE_ORDER`.
9. Al recibir mercaderia, almacen actualiza cantidades recibidas y stock.
10. Si hay error, defecto o garantia, se crea `RETURN_ORDER` y
    `RETURN_ORDER_ITEM`, siempre referenciado contra la venta original.

NO memorices tablas. Entiende eventos: consulta, venta, cobro, salida de stock,
compra, recepcion, devolucion.

## Current ERD Validation

| Table | Business meaning | Validation |
| --- | --- | --- |
| `PERSON` | Identidad civil/contacto base. | Correcta para evitar duplicar datos de una persona. |
| `CUSTOMER` | Rol comercial del comprador. | Valida para clientes persona. Para talleres o empresas falta `customer_type` o una entidad comercial mas flexible. |
| `SUPPLIER` | Empresa que abastece repuestos. | Correcta. Mas adelante puede necesitar `SUPPLIER_CONTACT` y condiciones comerciales. |
| `PART_CATEGORY` | Clasificacion simple del repuesto. | Correcta para proyecto compacto. En industria real se parece a jerarquias tipo `PCdb`. |
| `PART` | SKU vendible, comprable e inventariable. | Es la tabla central. Bien que tenga `internal_code`, precio, costo, garantia y estado. Debil si solo tiene un `oem_code`. |
| `VEHICLE_MODEL` | Vehiculo objetivo para compatibilidad. | Util, pero simplificada. Fitment real suele requerir motor, version, posicion, restricciones y qualifiers. |
| `PART_COMPATIBILITY` | Relacion many-to-many entre pieza y vehiculo. | MUY correcta. Sin esta tabla el sistema venderia por memoria y texto suelto. |
| `INVENTORY_STOCK` | Saldo actual por pieza y ubicacion. | Necesaria, pero peligrosa si no existe historial de movimientos. El saldo responde cuanto hay; no responde por que cambio. |
| `SALES_ORDER` | Venta/cotizacion/pedido del cliente. | Correcta. Debe tener estados claros: draft, confirmed, paid, cancelled, returned. |
| `SALES_ORDER_ITEM` | Linea vendida. | Correcta porque guarda precio historico. No uses `PART.sale_price` para reconstruir ventas pasadas. |
| `PAYMENT` | Cobros asociados a la venta. | Correcta porque permite pagos parciales o multiples metodos. |
| `PURCHASE_ORDER` | Pedido a proveedor. | Correcta para reposicion. |
| `PURCHASE_ORDER_ITEM` | Linea comprada. | Correcta para costo historico. Pero `quantity_received` es una simplificacion fuerte. |
| `RETURN_ORDER` | Devolucion o garantia contra venta original. | Correcta. La devolucion debe nacer de una venta previa. |
| `RETURN_ORDER_ITEM` | Linea devuelta contra una linea vendida. | Correcta. Permite validar cantidad devuelta y monto reembolsado. |

## Red Flags

Estas no son "opiniones". Son riesgos de negocio.

1. `INVENTORY_STOCK` sin `INVENTORY_MOVEMENT` no basta para arquitectura seria.
   El stock actual puede decir "quedan 4", pero no explica si esos 4 vienen de
   venta, compra, devolucion, ajuste, perdida o correccion. Eso es MEDIOCRE si
   despues quieres auditoria.
2. `PURCHASE_ORDER_ITEM.quantity_received` mezcla pedido y recepcion. En la
   operacion real puede haber recepciones parciales, errores, correcciones y
   devoluciones a proveedor. Para eso conviene `PURCHASE_RECEIPT` y
   `PURCHASE_RECEIPT_ITEM`.
3. `PART.oem_code` como campo unico es debil. Un repuesto puede tener codigo
   OEM, codigo alternativo, codigo de proveedor, barcode y equivalencias. Mejor
   extension: `PART_IDENTIFIER`.
4. `VEHICLE_MODEL` es demasiado compacto para compatibilidad real. A una pieza
   le puede importar motor, cilindrada, transmision, posicion, lado, version o
   rango exacto de fabricacion.
5. `CUSTOMER` ligado siempre a `PERSON` funciona para clientes individuales,
   pero un taller o empresa no es una persona. Si el negocio vende a talleres,
   usa `customer_type` o un modelo tipo `PARTY`.
6. Campos como `status`, `method`, `unit` y `brand` en `varchar` son rapidos,
   pero dejan entrar basura: "activo", "Active", "ACT", "actvo". Para un
   proyecto compacto puede pasar; para solidez usa `CHECK` o tablas catalogo.
7. Falta `USER_ACCOUNT` o responsable de operacion. Tus propios procesos dicen
   que importa saber quien registro, modifico o aprobo. Entonces no lo escondas.
8. Falta comprobante/factura. El ERD compacto lo excluye, pero si el sistema
   realmente factura, `SALES_ORDER` y `PAYMENT` no reemplazan el documento
   fiscal/comercial.

## Minimum Business Rules

Estas reglas deben aparecer como restricciones, validaciones o procedimientos.
Si no existen, las tablas son solo dibujos.

- `PART.internal_code` debe ser unico.
- `CUSTOMER.person_id` deberia ser unico si una persona solo puede tener un rol
  de cliente.
- `INVENTORY_STOCK` deberia tener una restriccion unica por `part_id` y
  `location_name`.
- Una venta confirmada no debe vender cantidad mayor al stock disponible, salvo
  que el negocio permita backorders explicitamente.
- `SALES_ORDER_ITEM.unit_price` debe copiar el precio de venta al momento de la
  venta.
- `PURCHASE_ORDER_ITEM.unit_cost` debe copiar el costo al momento de la compra.
- La suma pagada en `PAYMENT` no debe exceder el total neto de la venta, salvo
  anticipos o saldos a favor modelados explicitamente.
- La suma devuelta en `RETURN_ORDER_ITEM.quantity` no debe exceder la cantidad
  vendida en `SALES_ORDER_ITEM.quantity`.
- Una devolucion solo puede reingresar a stock si `restock_allowed = true` y el
  estado fisico del repuesto lo permite.
- Una compra recibida debe aumentar stock.
- Una venta entregada debe reducir stock.
- Un ajuste manual de stock debe guardar responsable, fecha y motivo.

## Recommended Next Version

Si quieres mantener el ERD compacto para la materia, esta bien. Pero si quieres
que sea base de arquitectura y conocimiento, el minimo serio seria agregar:

| New table | Why it matters |
| --- | --- |
| `INVENTORY_MOVEMENT` | Historial de entradas, salidas, devoluciones, ajustes y transferencias. Sin esto no hay trazabilidad. |
| `PURCHASE_RECEIPT` | Cabecera de recepcion real de mercaderia. Separa lo pedido de lo recibido. |
| `PURCHASE_RECEIPT_ITEM` | Detalle recibido por pieza, cantidad, costo y ubicacion. |
| `WAREHOUSE_LOCATION` | Normaliza ubicaciones fisicas en vez de texto libre. |
| `PART_IDENTIFIER` | Permite varios codigos por repuesto: internal, OEM, supplier, barcode, interchange. |
| `SUPPLIER_PART` | Relaciona proveedor, repuesto, codigo del proveedor, costo, lead time y disponibilidad. |
| `USER_ACCOUNT` | Permite saber quien vendio, cobro, recibio, ajusto o aprobo. |
| `SALES_INVOICE` | Separa venta comercial de comprobante/factura cuando el alcance tributario importe. |

## Alternatives

### Option A: Compact Academic ERD

Mantienes el ERD actual y documentas reglas. Es rapido y defendible si la
materia quiere un modelo simple.

Tradeoff: aprendes menos control operativo y no puedes auditar inventario con
seriedad.

### Option B: Strong Academic ERD

Agregas `INVENTORY_MOVEMENT`, `PURCHASE_RECEIPT`, `PURCHASE_RECEIPT_ITEM`,
`USER_ACCOUNT` y restricciones basicas.

Tradeoff: mas tablas, pero el modelo empieza a comportarse como sistema real.
Esta es la opcion que recomendaria.

### Option C: Industry-Grade ERD

Normalizas marcas, unidades, atributos, codigos alternativos, fitment avanzado,
precios por lista, garantias, facturacion, auditoria y devoluciones a proveedor.

Tradeoff: demasiado grande para un proyecto final si todavia estas aprendiendo
fundamentos. No corras antes de caminar.

## Mental Model

El ERD actual tiene una buena columna vertebral:

`CUSTOMER -> SALES_ORDER -> SALES_ORDER_ITEM -> PART -> INVENTORY_STOCK`

Y tiene dos ciclos necesarios:

`SUPPLIER -> PURCHASE_ORDER -> PURCHASE_ORDER_ITEM -> PART`

`SALES_ORDER -> RETURN_ORDER -> RETURN_ORDER_ITEM -> SALES_ORDER_ITEM`

La mejora conceptual seria dejar de tratar stock como un numero magico y
tratarlo como consecuencia de movimientos:

`purchase receipt + sale delivery + return + adjustment = stock balance`

Ese es el salto entre "hice tablas con IA" y "entiendo la arquitectura del
negocio".
