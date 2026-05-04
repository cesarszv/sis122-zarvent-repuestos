# Actores

Un actor es una persona o usuario que interactua con el sistema y cumple con un rol.

En Zarvent Rent, los actores deben reflejar una empresa pequena de alquiler de vehiculos.
Un actor no representa necesariamente a un empleado diferente. Una misma persona puede cumplir
mas de un rol, pero el sistema debe mantener permisos, registros y controles para conservar la calidad
de la informacion.

En Zarvent Rent, los actores principales pueden ser:

## Administrador / Gerente

Usuario responsable de la supervision general del sistema y de la toma de decisiones.
Puede
- registrar usuarios
- controlar permisos
- revisar reportes
- supervisar reservas, contratos, pagos y mantenimiento
- consultar ingresos
- revisar vehiculos mas alquilados
- revisar contratos activos
- revisar pagos pendientes
- controlar el estado general de la flota.

Este rol tambien puede aprobar cambios importantes o corregir informacion cuando exista un error
registrado por el encargado operativo.

## Encargado operativo

Usuario que atiende al cliente y registra el ciclo principal del alquiler.
Concentra las funciones de reservas, contratos, pagos y devoluciones para evitar depender de varios
empleados distintos.

Puede
- registrar clientes
- registrar reservas
- verificar disponibilidad de vehiculos
- generar contratos de alquiler
- registrar pagos, anticipos, saldos pendientes y cargos adicionales
- registrar la devolucion del vehiculo
- actualizar el estado operativo del alquiler

Verifica
- disponibilidad
- fechas
- datos del cliente
- condiciones del alquiler
- precio
- garantias
- estado del vehiculo al momento de entrega y devolucion
- kilometraje
- combustible
- danos
- multas o cargos extra si corresponde.

## Cliente

Persona que solicita el alquiler de un vehiculo. Proporciona sus datos personales,
- elige un vehiculo
- confirma una reserva
- firma el contrato
- realiza pagos
- entrega garantias si corresponde
- devuelve el vehiculo al finalizar el alquiler.

## Responsable de mantenimiento

Usuario que
registra
- revisiones
- reparaciones
- mantenimiento basico de los vehiculos.
Tambien puede cambiar el estado del vehiculo a disponible, en mantenimiento o fuera de servicio.

Este rol puede ser un empleado interno o un servicio externo, pero debe registrar sus actividades
para que la flota mantenga informacion actualizada y confiable.
