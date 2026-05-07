# Procedimientos

Los procedimientos describen los pasos concretos que siguen los actores en el
sistema actual. Sirven para justificar los modulos y las tablas del diseno de
base de datos.

## Registro de cliente

1. El cliente solicita una cotizacion o compra.
2. El encargado de ventas pregunta si ya esta registrado.
3. Se busca al cliente por CI, nombre o telefono.
4. Si no existe, se registran sus datos personales y contactos.
5. Si existe, se verifica que sus datos esten actualizados.
6. La informacion queda disponible para futuras ventas, pagos y devoluciones.

## Busqueda de repuesto

1. El cliente indica el repuesto que necesita.
2. El encargado de ventas solicita datos del vehiculo: marca, modelo, anio,
   motor o codigo de pieza si lo tiene.
3. Se busca el repuesto por codigo interno, codigo OEM, descripcion, marca o
   compatibilidad.
4. Se verifica precio, stock disponible y condiciones de garantia.
5. Si existe stock, se informa el precio al cliente.
6. Si no existe stock, se registra la necesidad para compras o reposicion.

## Registro de venta

1. El encargado de ventas selecciona el cliente.
2. Se agregan los repuestos vendidos al detalle de venta.
3. El sistema calcula subtotal, descuento, impuestos si corresponde y total.
4. Se confirma la disponibilidad de stock.
5. Se registra el metodo de pago.
6. Se emite comprobante o factura.
7. El inventario registra la salida de los repuestos vendidos.
8. La venta queda disponible para reportes, devoluciones o garantia.

## Registro de compra a proveedor

1. El responsable de compras revisa productos con stock bajo.
2. Se selecciona un proveedor.
3. Se crea una orden de compra con los repuestos, cantidades y costos.
4. El proveedor confirma o entrega la mercaderia.
5. Al recibir los productos, almacen registra la recepcion.
6. Se comparan cantidades recibidas contra cantidades pedidas.
7. Se actualiza el stock y el costo de los repuestos recibidos.

## Control de inventario

1. El encargado de almacen revisa existencias fisicas.
2. Se comparan cantidades fisicas contra cantidades del sistema.
3. Si hay diferencias, se registra un movimiento de ajuste con observacion.
4. Se actualizan ubicaciones si un repuesto cambia de estante o almacen.
5. Los productos con stock bajo se reportan a compras.

## Devolucion o garantia

1. El cliente presenta el comprobante o datos de la venta.
2. El encargado de ventas ubica la venta y el detalle del repuesto vendido.
3. Se identifica el motivo: producto equivocado, defecto, garantia, error de
   venta u otro.
4. Se registra la solicitud de devolucion.
5. Almacen revisa el estado fisico del repuesto.
6. Se decide si el producto vuelve a stock, se cambia por otro o se rechaza la
   devolucion.
7. Se registra la resolucion y el responsable.

## Reportes de supervision

1. El gerente selecciona el periodo de consulta.
2. El sistema consulta ventas, pagos, compras e inventario.
3. Se revisan ingresos, productos mas vendidos, stock bajo y compras pendientes.
4. La informacion se usa para tomar decisiones de reposicion, precios y control.
