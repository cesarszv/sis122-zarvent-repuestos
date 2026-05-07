# Actores

Un actor es una persona o usuario que interactua con el sistema y cumple un rol
dentro del proceso analizado.

En Zarvent Repuestos, los actores representan una empresa pequena dedicada a la
venta de repuestos de vehiculos. Una misma persona puede cumplir mas de un rol,
pero el sistema debe mantener permisos, registros y responsables para conservar
la calidad de la informacion.

## Administrador / Gerente

Usuario responsable de la supervision general del sistema y de la toma de
decisiones.

Puede
- registrar usuarios
- controlar roles y permisos
- revisar reportes
- autorizar cambios de precio o descuentos importantes
- supervisar ventas, compras, pagos e inventario
- consultar ingresos
- revisar productos mas vendidos
- revisar productos con stock bajo
- controlar proveedores
- verificar margenes de ganancia y rotacion de inventario.

Este rol tambien puede aprobar correcciones cuando exista un error registrado
por ventas, almacen o compras.

## Encargado de ventas / Caja

Usuario que atiende al cliente y registra el ciclo principal de la venta.
Concentra las funciones de busqueda de repuestos, cotizacion, venta, cobro y
emision de comprobantes.

Puede
- registrar clientes
- buscar repuestos por codigo, descripcion, marca o compatibilidad
- verificar stock disponible
- registrar cotizaciones
- registrar ventas
- aplicar descuentos autorizados
- registrar pagos
- emitir comprobantes o facturas
- iniciar solicitudes de devolucion o garantia.

Verifica
- datos del cliente
- compatibilidad del repuesto con el vehiculo
- precio vigente
- stock disponible
- metodo de pago
- detalle del comprobante
- condiciones de garantia.

## Encargado de almacen / Inventario

Usuario que controla las existencias fisicas de los repuestos.

Puede
- registrar ingreso de mercaderia
- registrar salida por venta
- controlar ubicaciones dentro del almacen
- actualizar stock minimo y maximo
- registrar ajustes por conteo fisico
- revisar productos agotados o con baja rotacion
- reportar diferencias entre stock fisico y stock del sistema.

Este rol ayuda a evitar ventas de productos inexistentes y mantiene la
informacion de inventario actualizada.

## Responsable de compras

Usuario encargado de la relacion con proveedores y reposicion de inventario.

Puede
- registrar proveedores
- solicitar cotizaciones a proveedores
- crear ordenes de compra
- registrar costos de compra
- registrar recepciones de mercaderia
- controlar productos pendientes de entrega
- actualizar costos promedio cuando ingresa nueva mercaderia.

## Cliente

Persona que solicita o compra repuestos de vehiculos.

Puede
- consultar disponibilidad de un repuesto
- proporcionar datos de su vehiculo para validar compatibilidad
- solicitar una cotizacion
- comprar uno o mas repuestos
- realizar pagos
- recibir comprobante o factura
- solicitar cambio, devolucion o garantia si corresponde.

## Proveedor

Empresa o persona externa que suministra repuestos a Zarvent Repuestos.

Participa entregando cotizaciones, ordenes atendidas, facturas de compra,
productos recibidos y condiciones de garantia del proveedor.
