# Requerimientos

Los requerimientos salen del analisis del sistema actual de Zarvent Repuestos:
registros en papel, planillas Excel y mensajes de WhatsApp para ventas,
compras, pagos, inventario, proveedores, devoluciones y garantias. El objetivo
es centralizar la informacion, reducir duplicidad y permitir consultas
confiables.

## Requerimientos funcionales

| Codigo | Requerimiento | Actor principal | Tablas relacionadas |
| --- | --- | --- | --- |
| RF-01 | El sistema debe permitir registrar personas con CI, nombres, fecha de nacimiento, direccion y contactos. | Encargado de ventas | `persona`, `contacto_persona` |
| RF-02 | El sistema debe permitir registrar clientes y datos comerciales basicos. | Encargado de ventas | `cliente`, `persona` |
| RF-03 | El sistema debe permitir registrar usuarios del sistema con rol y password cifrado/hash. | Administrador | `usuario`, `rol`, `permiso`, `rol_permiso` |
| RF-04 | El sistema debe permitir registrar proveedores y sus contactos. | Responsable de compras | `proveedor`, `contacto_proveedor` |
| RF-05 | El sistema debe permitir registrar repuestos con codigo interno, codigo OEM, descripcion, categoria, marca, unidad, precio, costo y garantia. | Administrador / Almacen | `repuesto`, `categoria_repuesto`, `marca_repuesto`, `unidad_medida`, `estado_repuesto` |
| RF-06 | El sistema debe permitir registrar compatibilidad de repuestos con marcas, modelos, anios y motores de vehiculos. | Encargado de ventas / Almacen | `marca_vehiculo`, `modelo_vehiculo`, `compatibilidad_repuesto` |
| RF-07 | El sistema debe permitir consultar stock por repuesto, almacen y ubicacion. | Ventas / Almacen | `stock_repuesto`, `almacen`, `ubicacion_almacen` |
| RF-08 | El sistema debe permitir registrar movimientos de inventario por ingreso, salida, ajuste, devolucion o perdida. | Almacen | `movimiento_inventario`, `tipo_movimiento` |
| RF-09 | El sistema debe permitir crear ordenes de compra a proveedores. | Responsable de compras | `orden_compra`, `detalle_orden_compra`, `estado_compra` |
| RF-10 | El sistema debe permitir registrar recepciones de mercaderia y actualizar stock. | Almacen / Compras | `recepcion_compra`, `detalle_recepcion_compra`, `stock_repuesto` |
| RF-11 | El sistema debe permitir registrar ventas con uno o mas repuestos. | Encargado de ventas | `venta`, `detalle_venta`, `estado_venta` |
| RF-12 | El sistema debe permitir registrar pagos de ventas, saldos y metodos de pago. | Encargado de ventas / Caja | `pago_venta`, `metodo_pago`, `venta` |
| RF-13 | El sistema debe permitir emitir comprobantes o facturas de venta. | Encargado de ventas / Caja | `comprobante_venta`, `tipo_comprobante`, `venta` |
| RF-14 | El sistema debe permitir registrar devoluciones por producto equivocado, defecto, garantia o error de venta. | Encargado de ventas / Almacen | `devolucion_venta`, `detalle_devolucion`, `motivo_devolucion`, `estado_devolucion` |
| RF-15 | El sistema debe permitir consultar reportes de ventas, productos mas vendidos, productos con stock bajo, compras pendientes, pagos e ingresos. | Administrador / Gerente | `venta`, `detalle_venta`, `stock_repuesto`, `orden_compra`, `pago_venta` |

## Requerimientos no funcionales

| Codigo | Requerimiento | Criterio |
| --- | --- | --- |
| RNF-01 | La base de datos debe estar normalizada para evitar duplicidad innecesaria. | Personas, repuestos, proveedores, estados, pagos e inventario deben estar separados. |
| RNF-02 | Las tablas deben tener llaves primarias y relaciones con llaves foraneas. | Cada tabla principal usa `id_*` y las relaciones usan FK. |
| RNF-03 | Los nombres de tablas y campos deben ser descriptivos. | No usar abreviaturas ambiguas como `MNT` sin descripcion. |
| RNF-04 | La informacion critica debe mantener integridad. | CI, codigo interno, usuario, correo y numero de comprobante deben ser unicos cuando corresponda. |
| RNF-05 | Las contrasenas no deben guardarse en texto plano. | `usuario.password_hash` almacena hash. |
| RNF-06 | El sistema debe registrar responsable y fecha en las operaciones principales. | Ventas, pagos, compras, recepciones, movimientos y devoluciones guardan usuario responsable. |
| RNF-07 | El stock debe calcularse con datos centralizados. | No depender de Excel, WhatsApp o registros manuales. |
| RNF-08 | El diseno debe poder implementarse en MySQL. | El SQL debe ser compatible con MySQL y modelable en drawDB. |

## Reglas de negocio

- Un repuesto inactivo, agotado o bloqueado no debe venderse.
- Una venta debe tener al menos un detalle de repuesto.
- El precio unitario de venta se guarda en el detalle para conservar el precio
  historico aunque luego cambie el catalogo.
- Un pago debe estar asociado a una venta.
- La suma de pagos no debe superar el total de la venta.
- La salida de inventario por venta debe disminuir el stock disponible.
- Una recepcion de compra debe aumentar el stock del repuesto recibido.
- No se debe registrar dos repuestos con el mismo codigo interno.
- No se debe registrar el mismo cliente varias veces con nombres escritos de
  forma diferente; se identifica por CI cuando el dato existe.
- Una devolucion debe referenciar una venta y el detalle vendido.
- Un producto devuelto solo vuelve al stock si el estado de la devolucion lo
  permite y el repuesto esta en condiciones de venta.
- Los productos con stock menor o igual al minimo deben aparecer en reportes de
  reposicion.
