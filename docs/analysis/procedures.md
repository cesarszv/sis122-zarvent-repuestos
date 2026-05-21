# Procedimientos

Los procedimientos son pasos concretos que siguen los actores. Sirven para
validar que el ERD soporte el trabajo diario del negocio.

## Registro de cliente

1. El cliente solicita cotizacion, compra, factura, devolucion o garantia.
2. Ventas busca si ya existe por documento, nombre o telefono.
3. Si no existe, registra datos personales y datos de facturacion.
4. Si existe, revisa que la informacion este actualizada.
5. El cliente queda disponible para ventas, pagos y devoluciones.

## Busqueda de repuesto

1. El cliente indica el repuesto o problema.
2. Ventas solicita marca, modelo, anio, motor o codigo de pieza.
3. Se busca por codigo interno, codigo OEM, nombre, marca o compatibilidad.
4. Se valida precio, stock disponible y garantia.
5. Si hay stock, se informa la cotizacion.
6. Si no hay stock, se registra la necesidad para reposicion.

## Registro de venta

1. Ventas selecciona el cliente.
2. Agrega los repuestos vendidos al detalle de venta.
3. Registra cantidad, precio unitario y descuento.
4. Verifica disponibilidad de stock.
5. Confirma la venta.
6. Registra el pago.
7. Emite recibo o factura si corresponde.
8. Inventario descuenta las cantidades vendidas.

## Registro de compra

1. Compras revisa productos con stock bajo.
2. Selecciona un proveedor.
3. Crea una orden de compra con repuestos, cantidades y costos.
4. El proveedor confirma disponibilidad o entrega mercaderia.
5. Almacen registra la cantidad recibida.
6. Se compara cantidad pedida contra cantidad recibida.
7. Se actualiza stock y costo de referencia si corresponde.

## Control de inventario

1. Almacen revisa existencias fisicas.
2. Compara stock fisico contra stock registrado.
3. Registra ajustes si existen diferencias.
4. Actualiza ubicaciones si cambia la posicion fisica del producto.
5. Reporta productos con stock bajo a compras.

## Devolucion o garantia

1. El cliente presenta comprobante o datos de la venta.
2. Ventas ubica la venta original y la linea vendida.
3. Se registra motivo de devolucion o garantia.
4. Almacen revisa el estado fisico del repuesto.
5. Gerencia o el responsable decide cambio, reembolso, rechazo o garantia.
6. Se registra la resolucion.
7. El producto vuelve a stock solo si esta apto para reventa.

## Reportes de supervision

1. Gerencia selecciona el periodo de consulta.
2. Revisa ventas, pagos, compras, inventario y devoluciones.
3. Identifica ingresos, productos mas vendidos, stock bajo y compras
   pendientes.
4. Usa la informacion para decidir reposicion, precios y control interno.
