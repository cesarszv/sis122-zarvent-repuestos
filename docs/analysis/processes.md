# Procesos

Los procesos describen como trabaja Zarvent Repuestos y que informacion debe
controlar la base de datos.

El analisis no empieza inventando tablas. Primero se identifican actividades,
actores, documentos, datos y problemas. Despues se derivan entidades,
relaciones y reglas.

## Situacion actual

La empresa usa papel, Excel, WhatsApp y memoria del personal. Eso permite
operar, pero causa problemas tipicos:

- clientes duplicados;
- repuestos escritos de varias formas;
- precios y costos desactualizados;
- stock que no coincide con la realidad;
- ventas sin detalle confiable;
- pagos separados de la venta;
- compras pendientes dificiles de seguir;
- devoluciones sin relacion clara con la venta original.

## Flujo general

1. El cliente consulta por un repuesto.
2. Ventas identifica vehiculo, pieza, codigo o descripcion.
3. Se busca el repuesto en catalogo, stock o registros actuales.
4. Se valida precio, compatibilidad y disponibilidad.
5. Si el cliente acepta, se registra la venta y su detalle.
6. Se registra el pago y el comprobante si corresponde.
7. Inventario descuenta el stock vendido.
8. Si el stock queda bajo, compras solicita reposicion.
9. Al recibir mercaderia, almacen actualiza el stock.
10. Si hay devolucion o garantia, se revisa contra la venta original.
11. Gerencia consulta reportes de ventas, compras, pagos, stock y devoluciones.

## Procesos identificados

| Proceso | Actores principales | Informacion manejada | Problema actual | Entidades o modulos derivados |
| --- | --- | --- | --- | --- |
| Control de acceso y responsabilidades | Gerente, vendedores, almacen, compras | responsable, rol, actividad, fecha | no siempre se sabe quien registro o aprobo algo | usuarios, roles, permisos, auditoria futura |
| Registro de clientes | Cliente, vendedor | nombres, documento, telefono, direccion, datos fiscales | clientes duplicados o incompletos | `PERSON`, `CUSTOMER` |
| Gestion del catalogo de repuestos | Ventas, almacen, gerente | codigo interno, codigo OEM, nombre, marca, categoria, precio, costo, garantia | productos duplicados o mal descritos | `PART_CATEGORY`, `PART` |
| Compatibilidad vehicular | Cliente, vendedor, almacen | marca, modelo, anio, motor, codigo de pieza | venta de piezas incompatibles | `VEHICLE_MODEL`, `PART_COMPATIBILITY` |
| Consulta y control de stock | Ventas, almacen | repuesto, ubicacion, cantidad disponible, stock minimo | stock fantasma o productos agotados no detectados | `INVENTORY_STOCK` |
| Registro de ventas | Cliente, vendedor, gerente | cliente, fecha, estado, repuestos, cantidades, precios, descuentos | ventas sin detalle confiable o sin precio historico | `SALES_ORDER`, `SALES_ORDER_ITEM` |
| Registro de pagos | Cliente, caja, gerente | metodo, monto, fecha, referencia, estado | pagos no vinculados correctamente a ventas | `PAYMENT` |
| Compras a proveedores | Compras, proveedor, almacen, gerente | proveedor, repuestos, cantidades, costos, fecha esperada, estado | pedidos pendientes dispersos o costos perdidos | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM` |
| Recepcion de mercaderia | Almacen, compras, proveedor | orden, repuesto, cantidad pedida, cantidad recibida, costo, ubicacion | stock y costo pueden quedar incorrectos | recepcion futura, stock, movimientos |
| Devoluciones y garantias | Cliente, ventas, almacen, gerente | venta original, repuesto, cantidad, motivo, resolucion, reembolso | devoluciones sin respaldo o sin control de stock | `RETURN_ORDER`, `RETURN_ORDER_ITEM` |
| Reportes y supervision | Gerente | ventas, ingresos, stock bajo, compras pendientes, productos mas vendidos | reportes lentos por datos dispersos | consultas y reportes desde tablas operativas |

## Reglas generales detectadas

- Un repuesto sin stock disponible no debe venderse, salvo que el negocio
  permita pedidos pendientes de forma explicita.
- Una venta debe tener cliente, fecha, estado y una o mas lineas.
- El detalle de venta debe guardar cantidad y precio unitario historico.
- Un pago debe pertenecer a una venta real.
- Una compra debe pertenecer a un proveedor real.
- El detalle de compra debe guardar cantidad y costo historico.
- Una devolucion debe apuntar a la venta y a la linea vendida.
- Un producto devuelto solo vuelve a stock si su estado fisico lo permite.
- El stock actual es util, pero para auditoria futura se necesita historial de
  movimientos.

## Diferencia con procedimientos

Este documento identifica **procesos y datos importantes**. Los pasos concretos
de cada actividad estan en [procedures.md](procedures.md).
