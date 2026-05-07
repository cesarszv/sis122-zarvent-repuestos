# Actores

Un actor es una persona o usuario que interactua con el sistema y cumple un rol
dentro del proceso analizado.

Zarvent Repuestos representa una empresa pequena dedicada a la venta de
repuestos de vehiculos. Por eso los actores se definen como **roles
funcionales**, no como empleados obligatoriamente separados. En la practica, una
misma persona puede cumplir mas de un rol, pero el sistema debe distinguirlos
para controlar permisos, responsables, auditoria e integridad de la informacion.

## Criterio segun la materia

Segun las clases, el analisis del sistema actual debe identificar personas que
participan o usan el sistema, los roles que cumplen, las actividades que
realizan y los modulos o entidades que surgen de esas actividades. Todavia no se
esta desarrollando el sistema nuevo; se describe como trabaja la empresa y que
informacion necesita organizar.

Por eso, cada actor se define con:

- **Rol:** responsabilidad principal dentro del negocio.
- **Actividades actuales:** tareas que realiza hoy con papel, Excel, WhatsApp o
  registros manuales.
- **Informacion que maneja:** datos que registra, consulta o valida.
- **Modulos o entidades que surgen:** tablas o partes del sistema que se
  justifican desde ese actor.

## Criterio usado para seleccionar actores

El negocio pertenece al rubro de tiendas de repuestos y accesorios automotrices:
venta de partes nuevas, usadas o reconstruidas, con posible instalacion de
accesorios. En este tipo de negocio las funciones criticas son atencion tecnica
al cliente, busqueda de piezas, control de stock, cobro, compras a proveedores,
devoluciones y supervision.

Para no inventar cargos innecesarios, se agrupan responsabilidades pequenas en
roles amplios:

- **Gerencia** concentra supervision, autorizaciones y reportes.
- **Ventas tecnicas** concentra atencion al cliente, identificacion del repuesto
  y registro de ventas.
- **Caja y facturacion** concentra dinero, pagos y comprobantes.
- **Almacen / inventario** concentra stock fisico, ubicaciones y movimientos.
- **Compras / proveedores** concentra reposicion, costos y ordenes de compra.

## Actores internos

### Administrador / Gerente

**Rol:** responsable de la supervision general del negocio y toma de decisiones.
En el sistema tendra permisos administrativos porque debe controlar usuarios,
reportes y autorizaciones.

**Actividades actuales:**
- definir responsables internos y niveles de autorizacion
- aprobar precios, descuentos y devoluciones importantes
- autorizar anulaciones, correcciones y ajustes importantes de inventario
- revisar ventas, compras, pagos, stock bajo y productos mas vendidos en
  planillas, recibos o registros manuales
- controlar proveedores y condiciones comerciales
- revisar diferencias entre stock fisico y stock registrado
- consultar ingresos, margenes y rotacion de inventario.

**Informacion que maneja o verifica:**
- que cada operacion tenga responsable
- que las ventas y pagos cuadren
- que los productos criticos se repongan a tiempo
- que las devoluciones tengan justificacion
- que los usuarios tengan permisos adecuados a su trabajo.

Este actor es necesario porque en una empresa pequena alguien debe cerrar el
ciclo de control: ventas, caja, compras, inventario y reportes.

**Modulos o entidades que surgen:** `usuario`, `rol`, `permiso`,
`rol_permiso`, reportes, auditoria, ventas, pagos, compras e inventario.

### Vendedor tecnico de repuestos

**Rol:** atiende al cliente en mostrador, telefono o WhatsApp. Su funcion no
es solo vender, sino identificar correctamente el repuesto que el cliente
necesita.

**Actividades actuales:**
- registrar o buscar clientes
- consultar repuestos por codigo interno, codigo OEM, descripcion, marca o
  categoria
- consultar compatibilidad por marca, modelo, anio y motor del vehiculo
- verificar stock disponible antes de confirmar la venta
- preparar cotizaciones
- registrar ventas y detalle de repuestos vendidos
- registrar pedidos pendientes cuando el repuesto no existe en stock
- iniciar solicitudes de cambio, devolucion o garantia.

**Informacion que maneja o verifica:**
- datos del cliente
- datos del vehiculo o pieza solicitada
- compatibilidad del repuesto
- precio vigente
- cantidad disponible
- condiciones de garantia
- observaciones necesarias para evitar una venta incorrecta.

Este actor es el nucleo del sistema porque conecta al cliente con el catalogo,
el inventario y la venta.

**Modulos o entidades que surgen:** `cliente`, `persona`, `contacto_persona`,
`repuesto`, `compatibilidad_repuesto`, `venta`, `detalle_venta`,
`devolucion_venta` y pedidos pendientes.

### Cajero / Responsable de facturacion

**Rol:** registra cobros, pagos y comprobantes. En una empresa
pequena puede ser la misma persona que vende, pero conviene separarlo como rol
porque maneja dinero y documentos tributarios.

**Actividades actuales:**
- registrar pagos de ventas
- seleccionar metodo de pago: efectivo, transferencia, QR, tarjeta u otro
- emitir recibos, notas de venta o facturas
- registrar datos de facturacion del cliente
- anular comprobantes solo si tiene autorizacion
- procesar devoluciones monetarias aprobadas
- cerrar caja o generar resumen de cobros del dia.

**Informacion que maneja o verifica:**
- monto total de la venta
- monto recibido
- cambio o saldo pendiente
- numero de comprobante
- metodo de pago
- responsable del cobro
- relacion entre pago, venta y comprobante.

Este actor reduce errores de caja y permite que los pagos no queden separados de
la venta.

**Modulos o entidades que surgen:** `pago_venta`, `metodo_pago`,
`tipo_comprobante`, `comprobante_venta`, cierre de caja y devoluciones de
dinero.

### Encargado de almacen / Inventario

**Rol:** controla las existencias fisicas de repuestos y mantiene
actualizado el stock del sistema.

**Actividades actuales:**
- registrar ingresos de mercaderia
- registrar salidas por venta
- registrar devoluciones aprobadas que vuelven a stock
- ubicar productos por almacen, pasillo, estante o caja
- registrar ajustes por conteo fisico
- marcar productos defectuosos, danados, bloqueados o no disponibles para venta
- revisar stock minimo, stock maximo y productos agotados
- reportar diferencias de inventario a gerencia.

**Informacion que maneja o verifica:**
- codigo del repuesto
- cantidad recibida o entregada
- ubicacion fisica
- estado del producto
- responsable del movimiento
- fecha y motivo del ajuste
- coincidencia entre stock fisico y stock registrado.

Este actor es necesario porque una venta de repuestos depende directamente de la
existencia fisica y de la ubicacion correcta del producto.

**Modulos o entidades que surgen:** `almacen`, `ubicacion_almacen`,
`stock_repuesto`, `tipo_movimiento`, `movimiento_inventario`, estado del
producto y recepcion de mercaderia.

### Responsable de compras / Proveedores

**Rol:** repone inventario y mantiene relacion con proveedores. En
una empresa pequena esta funcion puede asumirla el gerente, pero debe existir en
el sistema porque genera compras, costos y entradas de mercaderia.

**Actividades actuales:**
- registrar proveedores y contactos comerciales
- revisar productos con stock bajo o agotado
- solicitar precios y disponibilidad a proveedores
- crear ordenes de compra
- registrar costos, plazos y condiciones de entrega
- hacer seguimiento a pedidos pendientes
- coordinar la recepcion de mercaderia con almacen
- actualizar informacion de proveedor por repuesto.

**Informacion que maneja o verifica:**
- proveedor seleccionado
- precio de compra
- cantidad solicitada
- fecha de pedido
- fecha estimada de llegada
- productos pendientes de entrega
- diferencias entre cantidad pedida y cantidad recibida.

Este actor permite que la reposicion no dependa solo de memoria, mensajes o
planillas dispersas.

**Modulos o entidades que surgen:** `proveedor`, `contacto_proveedor`,
`orden_compra`, `detalle_orden_compra`, `estado_compra`, `recepcion_compra` y
`detalle_recepcion_compra`.

## Actores externos

### Cliente

**Rol:** persona o taller que solicita, cotiza o compra repuestos.

**Actividades actuales:**
- consulta disponibilidad de un repuesto
- proporciona datos del vehiculo o codigo de pieza
- solicita una cotizacion
- compra uno o mas repuestos
- realiza pagos
- pide factura o recibo
- solicita cambio, devolucion o garantia.

El sistema debe registrar al cliente cuando sea necesario para facturacion,
garantia, historial de compras o devolucion.

**Modulos o entidades que surgen:** `cliente`, datos de facturacion, historial
de ventas, garantia y devolucion.

### Proveedor

**Rol:** empresa o persona externa que vende repuestos a Zarvent Repuestos.

**Actividades actuales:**
- entrega listas de precios
- confirma disponibilidad
- recibe ordenes de compra
- entrega mercaderia
- emite factura o nota de entrega
- responde por garantias, defectos o cambios de producto.

El proveedor no administra el sistema, pero sus datos son necesarios para
compras, costos, reposicion y trazabilidad de productos.

**Modulos o entidades que surgen:** `proveedor`, `contacto_proveedor`,
ordenes de compra, recepciones, costos y garantias del proveedor.

## Actores no incluidos como cargos separados

No se separan como actores principales:

- **Repartidor:** solo seria necesario si el proyecto incluye entregas a
  domicilio como modulo formal.
- **Mecanico:** normalmente actua como cliente o cliente-taller; no necesita rol
  propio si no accede al sistema.
- **Contador:** puede usar reportes, pero no participa en el flujo operativo
  principal de ventas, stock y compras.
- **Marketing:** no es esencial para el alcance de Base de Datos I del proyecto.

## Material de clase aplicado

- `SIS122 2026-04-29.md`: el profesor indica que un actor es una persona o
  usuario que interactua con el sistema, cumple un rol y realiza actividades.
  Tambien relaciona actor, rol, actividades, modulos y operaciones sobre datos.
- `SIS122 2026-04-29.md`: el analisis del sistema actual debe describir actores,
  recursos, procesos, procedimientos y problemas antes de pasar a
  requerimientos.
- `SIS122 2026-02-20.md`: las entidades no deben inventarse; deben salir de
  encuestas, formularios, procesos reales y registros manuales como libretas,
  ventas, pedidos y facturas.
- `SIS122 2026-02-25.md`: las tablas y entidades necesitan respaldo
  metodologico: encuestas, formularios u otra bibliografia especializada.
- Diapositivas `[SIS122] [1-2026] 1.pdf`: refuerzan centralizacion, seguridad,
  eficiencia, entidades, relaciones, claves primarias y cardinalidad.

## Fuentes de referencia

- [U.S. Census Bureau, NAICS 441310](https://www.census.gov/naics/resources/archives/sect44-45.html):
  tiendas de repuestos y accesorios automotrices.
- [O*NET 41-2022.00, Parts Salespersons](https://www.onetonline.org/link/details/41-2022.00):
  tareas de vendedores de repuestos.
- [O*NET 53-7065.00, Stockers and Order Fillers](https://www.onetonline.org/link/details/53-7065.00):
  tareas de stock, almacen y preparacion de pedidos.
- [O*NET 41-1011.00, First-Line Supervisors of Retail Sales Workers](https://www.onetonline.org/link/details/41-1011.00):
  tareas de supervision de ventas minoristas.
- [U.S. Bureau of Labor Statistics, Cashiers](https://www.bls.gov/ooh/sales/cashiers.htm):
  tareas de caja, cobro y recibos.
- [U.S. Bureau of Labor Statistics, Purchasing Managers, Buyers, and Purchasing Agents](https://www.bls.gov/ooh/business-and-financial/purchasing-managers-buyers-and-purchasing-agents.htm):
  tareas de compras, proveedores y seguimiento de costos.
