# Procesos

Los procesos son las actividades principales que se realizan dentro del caso de
estudio. En este documento se analiza como trabaja actualmente Zarvent
Repuestos y que modulos o entidades pueden surgir a partir de esas actividades.

El analisis no debe inventar tablas directamente. Primero se identifican los
procesos reales, los actores que participan, los recursos que usan, la
informacion que manejan y los problemas observados. A partir de eso se pueden
derivar requerimientos, entidades y relaciones para la base de datos.

## Criterio de analisis

Zarvent Repuestos es un sistema de informacion administrativo para una empresa
pequena de venta de repuestos de vehiculos.

Actualmente la informacion se registra en papel, planillas Excel y mensajes de
WhatsApp. Esto permite trabajar, pero genera problemas de centralizacion,
redundancia, inconsistencia, busqueda lenta de informacion, control debil de
stock y dificultad para generar reportes.

Para cada proceso se considera:

- Que actividad se realiza.
- Que actor participa.
- Como se realiza actualmente.
- Que recurso o documento se usa.
- Que informacion se registra.
- Que problema se observa.
- Que modulo o entidad podria surgir en el sistema.

## Flujo general actual

1. El cliente consulta por un repuesto.
2. El encargado de ventas pide datos del vehiculo o codigo de pieza.
3. Se busca el repuesto en Excel, cuadernos, estantes o mensajes anteriores.
4. Se verifica precio y stock disponible.
5. Si el cliente acepta, se registra o identifica al cliente.
6. Se registra la venta y el detalle de repuestos vendidos.
7. Se registra el pago y se emite comprobante o factura.
8. Almacen descuenta el stock del producto vendido.
9. Si el stock queda bajo, compras solicita reposicion a proveedores.
10. Cuando llega mercaderia, almacen registra la recepcion y actualiza stock.
11. Si existe devolucion o garantia, se revisa la venta y el estado del
    producto.
12. El gerente revisa ingresos, stock bajo, compras pendientes y productos mas
    vendidos.

## Procesos identificados

### Control de acceso y responsabilidades

**Actividad actual:** la empresa controla las tareas segun la responsabilidad de
cada persona. No existe necesariamente un control digital de usuarios, perfiles
y permisos.

**Actores:** Administrador / Gerente, Encargado de ventas, Encargado de almacen
y Responsable de compras.

**Recursos actuales:** acuerdos internos, documentos compartidos, planillas o
registros fisicos.

**Informacion manejada:** nombre del responsable, rol, actividad realizada y
fecha de registro.

**Problemas detectados:** no siempre queda claro quien registro, modifico o
aprobo una informacion.

**Modulo o entidad que surge:** usuarios, roles, permisos y registro de
actividad.

### Registro de clientes

**Actividad actual:** el cliente entrega sus datos personales cuando solicita
cotizacion, factura, garantia o devolucion.

**Actores:** Cliente y Encargado de ventas.

**Recursos actuales:** formularios fisicos, recibos, facturas, planillas Excel o
mensajes de WhatsApp.

**Informacion manejada:** nombres, apellidos, CI/NIT, telefono, direccion,
correo y datos de contacto.

**Problemas detectados:** el mismo cliente puede registrarse mas de una vez con
datos incompletos o escritos de forma diferente.

**Modulo o entidad que surge:** clientes, personas y contactos.

### Gestion del catalogo de repuestos

**Actividad actual:** la empresa mantiene una lista de repuestos con precios,
codigos y descripciones, pero la informacion puede estar dispersa entre Excel,
estantes y mensajes.

**Actores:** Administrador / Gerente, Encargado de ventas y Encargado de
almacen.

**Recursos actuales:** planilla de productos, etiquetas, codigos de barra,
fotografias, listas impresas de precios y facturas de proveedores.

**Informacion manejada:** codigo interno, codigo OEM, descripcion, categoria,
marca, unidad, precio, costo, garantia y estado del producto.

**Problemas detectados:** pueden existir productos duplicados, codigos mal
escritos, precios desactualizados o descripciones insuficientes para vender con
seguridad.

**Modulo o entidad que surge:** repuestos, categorias, marcas, unidades,
estados y precios.

### Compatibilidad de repuestos con vehiculos

**Actividad actual:** para evitar errores de venta, el encargado verifica si el
repuesto corresponde al vehiculo del cliente.

**Actores:** Cliente, Encargado de ventas y Encargado de almacen.

**Recursos actuales:** experiencia del vendedor, catalogos impresos,
fotografias, codigos OEM, mensajes de proveedores y consulta manual en internet.

**Informacion manejada:** marca del vehiculo, modelo, anio, motor, codigo de
pieza y observaciones de compatibilidad.

**Problemas detectados:** si la compatibilidad no esta centralizada, se puede
vender un producto incorrecto y generar devoluciones.

**Modulo o entidad que surge:** marcas de vehiculo, modelos de vehiculo y
compatibilidad de repuestos.

### Consulta y control de stock

**Actividad actual:** antes de vender, el encargado revisa si el producto existe
fisicamente en almacen o en la planilla.

**Actores:** Encargado de ventas y Encargado de almacen.

**Recursos actuales:** planilla Excel, conteo visual de estantes, cuaderno de
salidas, mensajes y notas manuales.

**Informacion manejada:** repuesto, cantidad disponible, ubicacion, stock
minimo, stock maximo y estado del producto.

**Problemas detectados:** puede venderse un producto inexistente, quedar stock
desactualizado o no detectar a tiempo productos agotados.

**Modulo o entidad que surge:** stock, almacenes, ubicaciones y movimientos de
inventario.

### Registro de ventas

**Actividad actual:** cuando el cliente confirma la compra, se registra la venta
en una libreta, planilla o comprobante.

**Actores:** Cliente, Encargado de ventas y Administrador / Gerente.

**Recursos actuales:** recibos, facturas, planillas Excel, mensajes de WhatsApp
y notas manuales.

**Informacion manejada:** cliente, fecha, usuario que vende, repuestos
vendidos, cantidades, precio unitario, descuento, total, estado de la venta y
observaciones.

**Problemas detectados:** las ventas pueden no coincidir con el stock, los
precios historicos pueden perderse y los reportes de ingresos toman tiempo.

**Modulo o entidad que surge:** ventas, detalle de venta, estados de venta,
pagos y comprobantes.

### Registro de pagos y comprobantes

**Actividad actual:** la empresa registra pagos en efectivo, transferencia, QR o
tarjeta, y emite recibo o factura segun corresponda.

**Actores:** Cliente, Encargado de ventas / Caja y Administrador / Gerente.

**Recursos actuales:** recibos, comprobantes de transferencia, facturas,
planillas Excel y mensajes de WhatsApp.

**Informacion manejada:** monto, fecha, metodo de pago, numero de comprobante,
NIT/CI, razon social, subtotal, descuento, impuesto y total.

**Problemas detectados:** los pagos pueden no estar relacionados correctamente
con la venta o puede ser dificil identificar ventas pagadas, anuladas o con
saldo pendiente.

**Modulo o entidad que surge:** metodos de pago, pagos de venta, tipos de
comprobante y comprobantes.

### Gestion de compras a proveedores

**Actividad actual:** cuando un producto esta agotado o bajo en stock, compras
coordina la reposicion con proveedores.

**Actores:** Responsable de compras, Proveedor, Encargado de almacen y
Administrador / Gerente.

**Recursos actuales:** cotizaciones, facturas de compra, mensajes de WhatsApp,
listas de precios de proveedores y planillas Excel.

**Informacion manejada:** proveedor, repuestos solicitados, cantidades, costos,
fecha de pedido, fecha estimada, estado de compra y observaciones.

**Problemas detectados:** puede perderse informacion de pedidos pendientes,
costos anteriores o proveedores que abastecen cada producto.

**Modulo o entidad que surge:** proveedores, ordenes de compra, detalle de
compra y estados de compra.

### Recepcion de mercaderia

**Actividad actual:** cuando llega mercaderia, almacen verifica las cantidades y
actualiza el inventario.

**Actores:** Encargado de almacen, Responsable de compras y Proveedor.

**Recursos actuales:** factura de proveedor, nota de entrega, orden de compra,
conteo fisico y planilla de inventario.

**Informacion manejada:** orden de compra, repuesto, cantidad pedida, cantidad
recibida, costo unitario, fecha de recepcion, ubicacion y responsable.

**Problemas detectados:** si la recepcion no se registra con detalle, el stock y
el costo pueden quedar incorrectos.

**Modulo o entidad que surge:** recepciones de compra, detalle de recepcion,
stock y movimientos de inventario.

### Devoluciones y garantias

**Actividad actual:** si un repuesto sale defectuoso o no corresponde al
vehiculo del cliente, se revisa la venta y se evalua si corresponde cambio,
devolucion o garantia.

**Actores:** Cliente, Encargado de ventas, Encargado de almacen y Administrador
/ Gerente.

**Recursos actuales:** comprobante, factura, producto fisico, fotografias,
mensajes, notas manuales y condiciones del proveedor.

**Informacion manejada:** venta original, detalle vendido, repuesto, cantidad,
motivo, estado del producto, resolucion, monto devuelto y responsable.

**Problemas detectados:** sin relacion entre venta y devolucion, es dificil
validar garantias, evitar devoluciones indebidas y controlar si el producto
vuelve al stock.

**Modulo o entidad que surge:** devoluciones, detalle de devolucion, motivos y
estados de devolucion.

### Reportes y supervision

**Actividad actual:** el gerente revisa informacion para tomar decisiones sobre
ventas, compras, inventario, precios y proveedores.

**Actores:** Administrador / Gerente.

**Recursos actuales:** planillas Excel, facturas, recibos, cuadernos de ventas,
mensajes y conteos manuales.

**Informacion manejada:** ingresos, ventas por periodo, productos mas vendidos,
stock bajo, compras pendientes, pagos registrados, devoluciones y margen de
ganancia.

**Problemas detectados:** los reportes toman tiempo porque la informacion esta
dispersa y puede no estar actualizada.

**Modulo o entidad que surge:** reportes, indicadores, ingresos, rotacion de
inventario, stock bajo y compras pendientes.

## Procesos y entidades derivadas

| Proceso | Entidades o modulos relacionados |
| ------- | -------------------------------- |
| Control de acceso y responsabilidades | usuarios, roles, permisos |
| Registro de clientes | clientes, personas, contactos |
| Gestion del catalogo de repuestos | repuestos, categorias, marcas, unidades, estados |
| Compatibilidad de repuestos | marcas de vehiculo, modelos, compatibilidades |
| Consulta y control de stock | stock, almacenes, ubicaciones, movimientos |
| Registro de ventas | ventas, detalle de venta, estados |
| Registro de pagos y comprobantes | pagos, metodos de pago, comprobantes |
| Gestion de compras a proveedores | proveedores, ordenes de compra, detalle de compra |
| Recepcion de mercaderia | recepciones, detalle de recepcion, stock |
| Devoluciones y garantias | devoluciones, detalle de devolucion, motivos, estados |
| Reportes y supervision | reportes, indicadores, ingresos, stock bajo |

## Reglas generales detectadas

- Un repuesto sin stock disponible no debe venderse.
- Una venta debe relacionar cliente, usuario, fecha, estado y detalle de
  repuestos.
- El detalle de venta debe guardar cantidad y precio unitario historico.
- Una compra debe relacionar proveedor, estado y detalle de repuestos pedidos.
- Una recepcion debe registrar cantidad recibida y actualizar inventario.
- Un movimiento de inventario debe guardar tipo, cantidad, responsable y fecha.
- Una devolucion debe relacionarse con la venta y el detalle vendido.
- Un producto devuelto solo vuelve a stock si su estado lo permite.
- Los pagos deben relacionarse con una venta.
- La informacion debe centralizarse para evitar registros duplicados,
  inconsistentes o desactualizados.

## Diferencia con procedimientos

Este documento identifica los procesos del caso de estudio. Los pasos detallados
de como se realiza cada actividad deben colocarse en `procedimientos.md`.
