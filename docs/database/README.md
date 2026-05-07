# Diseno de base de datos

Este diseno esta preparado para armar el diagrama en `drawDB` usando MySQL.

## Como usarlo en drawDB

1. Abrir `https://www.drawdb.app/`.
2. Crear un diagrama nuevo y elegir **MySQL**.
3. Importar el archivo [`schema.sql`](schema.sql) desde la opcion de importacion
   SQL, o crear las tablas manualmente usando este documento como guia.
4. Revisar que las relaciones FK queden dibujadas.
5. Acomodar visualmente las tablas por modulos:
   - Personas y acceso.
   - Proveedores.
   - Catalogo de repuestos.
   - Compatibilidad vehicular.
   - Inventario.
   - Compras y recepciones.
   - Ventas, pagos y comprobantes.
   - Devoluciones y garantias.

## Criterios aplicados

- Cada tabla principal tiene un identificador unico `id_*` como llave primaria.
- Los datos naturales importantes tambien tienen `UNIQUE`, por ejemplo `ci`,
  `codigo_interno`, `username`, `correo` y `numero_comprobante`.
- Los nombres no se usan como PK porque pueden repetirse.
- Los datos repetibles se separan en tablas propias: contactos, detalles de
  venta, pagos, movimientos, compatibilidades y devoluciones.
- Los estados y tipos se modelan como catalogos para evitar escribir valores
  distintos para el mismo concepto.
- El stock disponible se centraliza en `stock_repuesto` y se respalda con
  `movimiento_inventario`.
- No se guarda la edad porque se calcula desde `fecha_nacimiento`.
- Los pagos no repiten datos del cliente ni de los repuestos; se relacionan con
  la venta.
- Las contrasenas se guardan como `password_hash`, nunca como texto plano.

## Tablas por modulo

### Personas y acceso

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `persona` | Datos generales de cualquier persona registrada. | PK `id_persona`, UNIQUE `ci` |
| `contacto_persona` | Telefonos, correos, WhatsApp u otros contactos. | FK `id_persona` |
| `cliente` | Datos propios del cliente que compra repuestos. | FK unica `id_persona` |
| `rol` | Perfiles del sistema: administrador, ventas, almacen, compras. | PK `id_rol` |
| `permiso` | Acciones permitidas dentro del sistema. | PK `id_permiso` |
| `rol_permiso` | Relacion N a N entre roles y permisos. | PK compuesta `id_rol`, `id_permiso` |
| `usuario` | Cuentas que pueden iniciar sesion en el sistema. | FK `id_persona`, FK `id_rol` |

### Proveedores

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `proveedor` | Empresas o personas que suministran repuestos. | PK `id_proveedor`, UNIQUE `nit` |
| `contacto_proveedor` | Telefonos, correos o contactos comerciales del proveedor. | FK `id_proveedor` |

### Catalogo y compatibilidad

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `categoria_repuesto` | Categoria: frenos, suspension, motor, filtros, etc. | PK `id_categoria_repuesto` |
| `marca_repuesto` | Marca comercial del repuesto. | PK `id_marca_repuesto` |
| `unidad_medida` | Unidad, pieza, juego, litro u otra unidad. | PK `id_unidad_medida` |
| `estado_repuesto` | Activo, inactivo, agotado o bloqueado. | PK `id_estado_repuesto` |
| `repuesto` | Registro central de cada producto vendido. | UNIQUE `codigo_interno`, UNIQUE opcional `codigo_barra` |
| `marca_vehiculo` | Marca de vehiculo compatible. | PK `id_marca_vehiculo` |
| `modelo_vehiculo` | Modelo asociado a una marca de vehiculo. | FK `id_marca_vehiculo` |
| `compatibilidad_repuesto` | Relacion entre repuesto y modelo vehicular. | FK `id_repuesto`, FK `id_modelo_vehiculo` |

### Inventario

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `almacen` | Lugar fisico donde se guardan repuestos. | PK `id_almacen` |
| `ubicacion_almacen` | Pasillo, estante, caja o zona dentro de un almacen. | FK `id_almacen` |
| `stock_repuesto` | Cantidad actual por repuesto y ubicacion. | UNIQUE `id_repuesto`, `id_ubicacion_almacen` |
| `tipo_movimiento` | Ingreso, salida, ajuste, devolucion, perdida. | PK `id_tipo_movimiento` |
| `movimiento_inventario` | Historial de cambios de stock. | FK `id_repuesto`, FK `id_ubicacion_almacen`, FK `id_usuario` |

### Compras y recepciones

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `estado_compra` | Pendiente, aprobada, recibida, cancelada. | PK `id_estado_compra` |
| `orden_compra` | Pedido realizado a un proveedor. | FK `id_proveedor`, FK `id_estado_compra` |
| `detalle_orden_compra` | Repuestos solicitados en una compra. | FK `id_orden_compra`, FK `id_repuesto` |
| `recepcion_compra` | Recepcion fisica de mercaderia. | FK `id_orden_compra` |
| `detalle_recepcion_compra` | Cantidades recibidas por repuesto. | FK `id_recepcion_compra`, FK `id_repuesto` |

### Ventas, pagos y comprobantes

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `estado_venta` | Pendiente, pagada, anulada, devuelta parcial. | PK `id_estado_venta` |
| `venta` | Cabecera de la venta. | FK `id_cliente`, FK `id_usuario`, FK `id_estado_venta` |
| `detalle_venta` | Repuestos vendidos, cantidad y precio historico. | FK `id_venta`, FK `id_repuesto` |
| `metodo_pago` | Efectivo, transferencia, QR, tarjeta, etc. | PK `id_metodo_pago` |
| `pago_venta` | Pagos asociados a una venta. | FK `id_venta`, FK `id_metodo_pago` |
| `tipo_comprobante` | Recibo, factura, nota de venta. | PK `id_tipo_comprobante` |
| `comprobante_venta` | Comprobante emitido para la venta. | UNIQUE `numero_comprobante`, FK `id_venta` |

### Devoluciones y garantias

| Tabla | Proposito | Llaves principales |
| --- | --- | --- |
| `motivo_devolucion` | Defecto, producto equivocado, garantia, error de venta. | PK `id_motivo_devolucion` |
| `estado_devolucion` | Solicitada, aprobada, rechazada, cerrada. | PK `id_estado_devolucion` |
| `devolucion_venta` | Cabecera de devolucion vinculada a una venta. | FK `id_venta`, FK `id_estado_devolucion` |
| `detalle_devolucion` | Repuestos devueltos, cantidad y resolucion. | FK `id_devolucion_venta`, FK `id_detalle_venta` |

## Relaciones principales

| Relacion | Cardinalidad | Justificacion |
| --- | --- | --- |
| `persona` -> `contacto_persona` | 1 a N | Una persona puede tener varios contactos. |
| `persona` -> `cliente` | 1 a 0..1 | No toda persona es cliente. |
| `persona` -> `usuario` | 1 a 0..1 | Solo algunas personas tienen acceso al sistema. |
| `rol` -> `usuario` | 1 a N | Un rol puede asignarse a varios usuarios. |
| `rol` <-> `permiso` | N a N | Un rol tiene varios permisos y un permiso puede estar en varios roles. |
| `proveedor` -> `orden_compra` | 1 a N | Un proveedor puede recibir muchas ordenes de compra. |
| `categoria_repuesto` -> `repuesto` | 1 a N | Una categoria agrupa varios repuestos. |
| `marca_repuesto` -> `repuesto` | 1 a N | Una marca puede tener varios repuestos. |
| `marca_vehiculo` -> `modelo_vehiculo` | 1 a N | Una marca puede tener varios modelos. |
| `repuesto` <-> `modelo_vehiculo` | N a N | Un repuesto puede servir para varios modelos y un modelo usa varios repuestos. |
| `repuesto` -> `stock_repuesto` | 1 a N | Un repuesto puede estar en varias ubicaciones. |
| `venta` -> `detalle_venta` | 1 a N | Una venta tiene uno o mas repuestos vendidos. |
| `venta` -> `pago_venta` | 1 a N | Una venta puede tener uno o varios pagos. |
| `venta` -> `comprobante_venta` | 1 a 0..1 | Una venta puede tener un comprobante emitido. |
| `orden_compra` -> `detalle_orden_compra` | 1 a N | Una orden compra varios repuestos. |
| `orden_compra` -> `recepcion_compra` | 1 a N | Una orden puede recibirse en partes. |
| `devolucion_venta` -> `detalle_devolucion` | 1 a N | Una devolucion puede incluir varios productos. |

## Valores sugeridos para catalogos

`estado_repuesto`:
- Activo
- Inactivo
- Agotado
- Bloqueado

`estado_venta`:
- Pendiente
- Pagada
- Anulada
- Devuelta parcial
- Devuelta total

`estado_compra`:
- Pendiente
- Aprobada
- Recibida parcial
- Recibida total
- Cancelada

`estado_devolucion`:
- Solicitada
- En revision
- Aprobada
- Rechazada
- Cerrada

`metodo_pago`:
- Efectivo
- Transferencia bancaria
- QR
- Tarjeta

`tipo_movimiento`:
- Ingreso por compra
- Salida por venta
- Ajuste positivo
- Ajuste negativo
- Devolucion de cliente
- Perdida o dano

## Reglas que debe controlar el sistema

- No vender repuestos sin stock disponible.
- No vender repuestos con estado `Inactivo` o `Bloqueado`.
- No aceptar cantidades negativas o iguales a cero en compras, ventas o
  movimientos.
- No permitir dos repuestos con el mismo `codigo_interno`.
- Una venta debe tener al menos un detalle.
- El detalle de venta conserva el precio unitario historico.
- Los pagos deben tener metodo, monto, fecha y responsable de registro.
- La recepcion de compra debe actualizar stock y registrar movimiento de
  inventario.
- Una devolucion debe estar asociada a una venta y a su detalle.
- El producto devuelto solo vuelve a stock si la revision lo aprueba.

## Recomendaciones para dibujarlo

- Ubica los catalogos arriba o al lado izquierdo.
- Ubica las tablas transaccionales en el centro: `venta`, `detalle_venta`,
  `orden_compra`, `recepcion_compra`, `stock_repuesto`.
- Ubica compatibilidad cerca de `repuesto`, `marca_vehiculo` y
  `modelo_vehiculo`.
- Ubica pagos y comprobantes cerca de `venta`.
- No dupliques en `venta` los nombres del cliente ni las descripciones completas
  del repuesto: se obtienen por relaciones desde `cliente` y `detalle_venta`.
- Si drawDB no importa alguna restriccion `CHECK`, mantenla como nota del
  diagrama o agregala manualmente en la columna.
