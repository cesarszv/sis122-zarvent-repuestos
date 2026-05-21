# Actores

Un actor es una persona, rol o entidad externa que participa en los procesos de
Zarvent Repuestos y usa, registra o valida informacion del negocio.

Este proyecto modela **roles funcionales**, no cargos separados por empleado. En
una empresa pequena una misma persona puede vender, cobrar y revisar stock, pero
para el analisis conviene separar responsabilidades.

## Criterio de seleccion

Se incluyen actores que afectan datos importantes para la base de datos:

- clientes y proveedores;
- catalogo de repuestos;
- compatibilidad vehicular;
- inventario;
- ventas;
- pagos;
- compras;
- devoluciones;
- reportes.

No se agregan cargos solo para que el documento se vea mas grande. Cada actor
debe justificar informacion, procesos o entidades del ERD.

## Actores internos

| Actor | Responsabilidad principal | Informacion que maneja | Entidades o modulos relacionados |
| --- | --- | --- | --- |
| Administrador / Gerente | Supervisa el negocio, autoriza operaciones importantes y revisa reportes. | responsables, ventas, pagos, compras, stock bajo, devoluciones, proveedores | usuarios, roles, ventas, pagos, compras, inventario, reportes |
| Vendedor tecnico | Atiende al cliente e identifica el repuesto correcto. | cliente, vehiculo, codigo de pieza, compatibilidad, precio, stock, garantia | `PERSON`, `CUSTOMER`, `PART`, `VEHICLE_MODEL`, `PART_COMPATIBILITY`, `SALES_ORDER` |
| Cajero / Responsable de facturacion | Registra cobros y comprobantes. | metodo de pago, monto, referencia, estado del pago, datos de facturacion | `PAYMENT`, `SALES_ORDER`, comprobantes |
| Encargado de almacen / Inventario | Controla existencias fisicas y ubicaciones. | repuesto, cantidad, ubicacion, stock minimo, estado fisico | `PART`, `INVENTORY_STOCK`, futuros movimientos de inventario |
| Responsable de compras | Repone productos y coordina proveedores. | proveedor, productos pedidos, costos, fechas, cantidades recibidas | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |

## Actores externos

| Actor | Responsabilidad principal | Informacion que aporta o recibe | Entidades o modulos relacionados |
| --- | --- | --- | --- |
| Cliente | Consulta, cotiza, compra, paga o solicita devolucion/garantia. | datos personales, datos fiscales, vehiculo, comprobante, motivo de devolucion | `PERSON`, `CUSTOMER`, `SALES_ORDER`, `PAYMENT`, `RETURN_ORDER` |
| Proveedor | Abastece repuestos y confirma precios, disponibilidad o entregas. | datos comerciales, listas de precios, facturas, fechas de entrega | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |

## Actores no incluidos como principales

| Actor | Motivo |
| --- | --- |
| Repartidor | Solo seria necesario si el alcance incluye entregas a domicilio. |
| Mecanico | Para este alcance actua como cliente o taller cliente; no administra el sistema. |
| Contador | Puede consultar reportes, pero no participa en el flujo operativo principal. |
| Marketing | No es central para el modelo de Base de Datos I. |

## Criterio academico aplicado

- Primero se identifican actores, actividades e informacion.
- Luego se derivan procesos, requerimientos, entidades y relaciones.
- Las entidades no se inventan por intuicion; deben salir de procesos reales,
  registros, formularios, ventas, compras, pagos o devoluciones.

## Fuentes de referencia

- [U.S. Census Bureau, NAICS 441310](https://www.census.gov/naics/resources/archives/sect44-45.html):
  define el rubro de tiendas de repuestos y accesorios automotrices.
- [O*NET 41-2022.00, Parts Salespersons](https://www.onetonline.org/link/details/41-2022.00):
  respalda tareas de venta tecnica de repuestos.
- [O*NET 53-7065.00, Stockers and Order Fillers](https://www.onetonline.org/link/details/53-7065.00):
  respalda tareas de almacen, stock y preparacion de productos.
- [U.S. Bureau of Labor Statistics, Cashiers](https://www.bls.gov/ooh/sales/cashiers.htm):
  respalda tareas de cobro, recibos y caja.
