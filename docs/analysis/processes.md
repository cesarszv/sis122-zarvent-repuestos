# Procesos

Los procesos son las actividades principales que se realizan dentro del caso de
estudio. En este documento se analiza como trabaja actualmente Zarvent Rent y que
modulos o entidades pueden surgir a partir de esas actividades.

El analisis no debe inventar tablas directamente. Primero se identifican los
procesos reales, los actores que participan, los recursos que usan, la
informacion que manejan y los problemas observados. A partir de eso se pueden
derivar requerimientos, entidades y relaciones para la base de datos.

## Criterio de analisis

Zarvent Rent es un sistema de informacion administrativo para una empresa pequena
de alquiler de vehiculos.

Actualmente la informacion se registra en papel, planillas Excel y mensajes de
WhatsApp. Esto permite trabajar, pero genera problemas de centralizacion,
redundancia, inconsistencia, busqueda lenta de informacion y dificultad para
generar reportes.

Para cada proceso se considera:

- Que actividad se realiza.
- Que actor participa.
- Como se realiza actualmente.
- Que recurso o documento se usa.
- Que informacion se registra.
- Que problema se observa.
- Que modulo o entidad podria surgir en el sistema.

## Flujo general actual

1. El cliente solicita alquilar un vehiculo.
2. El encargado operativo revisa disponibilidad en registros manuales,
   planillas o mensajes.
3. Se registra la informacion del cliente.
4. Se anota o confirma la reserva.
5. Se prepara el contrato de alquiler.
6. Se entrega el vehiculo y se registra su estado inicial.
7. Se registran pagos, anticipos o saldos pendientes.
8. El cliente devuelve el vehiculo.
9. Se revisa el estado final del vehiculo.
10. Se registran cargos adicionales si corresponde.
11. Se actualiza el estado del vehiculo.
12. El gerente revisa ingresos, contratos, pagos pendientes y estado de la
    flota.

## Procesos identificados

### Control de acceso y responsabilidades

**Actividad actual:** la empresa controla las tareas segun la responsabilidad de
cada persona. No existe necesariamente un control digital de usuarios, perfiles y
permisos.

**Actores:** Administrador / Gerente, Encargado operativo, Responsable de
mantenimiento.

**Recursos actuales:** acuerdos internos, documentos compartidos, planillas o
registros fisicos.

**Informacion manejada:** nombre del responsable, rol, actividad realizada y
fecha de registro.

**Problemas detectados:** no siempre queda claro quien registro, modifico o
aprobo una informacion.

**Modulo o entidad que surge:** usuarios, roles, permisos y registro de
actividad.

### Registro de clientes

**Actividad actual:** el cliente entrega sus datos personales y documentos para
poder realizar una reserva o contrato.

**Actores:** Cliente y Encargado operativo.

**Recursos actuales:** formularios fisicos, fotocopias, fotografias de
documentos, planillas Excel o mensajes de WhatsApp.

**Informacion manejada:** nombres, apellidos, CI, telefono, direccion,
documentos, referencias y datos de contacto.

**Problemas detectados:** el mismo cliente puede registrarse mas de una vez con
datos incompletos o escritos de forma diferente.

**Modulo o entidad que surge:** clientes, documentos de cliente y contactos.

### Gestion de vehiculos

**Actividad actual:** la empresa mantiene informacion basica de cada vehiculo
para saber si puede alquilarse.

**Actores:** Administrador / Gerente, Encargado operativo y Responsable de
mantenimiento.

**Recursos actuales:** planilla de vehiculos, carpetas fisicas, fotografias,
documentos del vehiculo y registros de kilometraje.

**Informacion manejada:** placa, marca, modelo, tipo, anio, color, kilometraje,
estado, disponibilidad, combustible y observaciones.

**Problemas detectados:** el estado del vehiculo puede quedar desactualizado si
la informacion se registra en varios medios.

**Modulo o entidad que surge:** vehiculos, tipos de vehiculo, estados de
vehiculo y registro de kilometraje.

### Consulta de disponibilidad

**Actividad actual:** antes de aceptar una reserva, el encargado revisa si el
vehiculo esta libre para las fechas solicitadas.

**Actores:** Encargado operativo y Cliente.

**Recursos actuales:** planillas Excel, agenda fisica, historial de WhatsApp y
contratos anteriores.

**Informacion manejada:** vehiculo solicitado, fecha de inicio, fecha de fin,
estado del vehiculo y reservas existentes.

**Problemas detectados:** puede existir doble reserva o confusion si la
informacion no esta centralizada.

**Modulo o entidad que surge:** disponibilidad, calendario de reservas y estados
de reserva.

### Registro de reservas

**Actividad actual:** cuando el cliente confirma interes, se aparta un vehiculo
para una fecha determinada.

**Actores:** Cliente y Encargado operativo.

**Recursos actuales:** notas, agenda, planilla Excel, mensajes de WhatsApp o
comprobantes de anticipo.

**Informacion manejada:** cliente, vehiculo, fecha de inicio, fecha de fin,
monto estimado, anticipo, estado de la reserva y observaciones.

**Problemas detectados:** las reservas pueden perderse, duplicarse o no
actualizarse cuando el cliente cancela.

**Modulo o entidad que surge:** reservas, detalle de reserva y estados de
reserva.

### Generacion de contratos de alquiler

**Actividad actual:** el alquiler se formaliza mediante un contrato con datos del
cliente, vehiculo, fechas, precio y condiciones.

**Actores:** Cliente y Encargado operativo.

**Recursos actuales:** contrato impreso, documento Word, plantilla, fotocopias y
firmas.

**Informacion manejada:** datos del cliente, datos del vehiculo, fechas de
alquiler, tarifa, garantia, condiciones, responsabilidades y firma.

**Problemas detectados:** puede haber errores al copiar datos desde otros
registros o dificultad para consultar contratos activos.

**Modulo o entidad que surge:** contratos, condiciones de contrato, garantias y
estado del contrato.

### Entrega del vehiculo

**Actividad actual:** al iniciar el alquiler, se entrega el vehiculo y se deja
constancia de su estado inicial.

**Actores:** Encargado operativo y Cliente.

**Recursos actuales:** checklist fisico, fotografias, contrato, nota de entrega
o registro manual.

**Informacion manejada:** fecha de entrega, kilometraje inicial, combustible,
estado exterior, estado interior, accesorios, observaciones y danos previos.

**Problemas detectados:** si no se registra bien el estado inicial, pueden existir
conflictos al momento de la devolucion.

**Modulo o entidad que surge:** entrega de vehiculo, inspeccion inicial y
registro de danos.

### Registro de pagos

**Actividad actual:** la empresa registra pagos, anticipos, saldos pendientes y
cargos adicionales.

**Actores:** Cliente, Encargado operativo y Administrador / Gerente.

**Recursos actuales:** recibos, comprobantes de transferencia, planillas Excel,
mensajes de WhatsApp y notas manuales.

**Informacion manejada:** monto, fecha, metodo de pago, concepto, saldo,
anticipo, multa o cargo adicional.

**Problemas detectados:** los pagos pueden no coincidir con los contratos o puede
ser dificil identificar saldos pendientes.

**Modulo o entidad que surge:** pagos, metodos de pago, saldos, cargos
adicionales y multas.

### Devolucion del vehiculo

**Actividad actual:** al terminar el alquiler, el cliente devuelve el vehiculo y
se revisa su estado final.

**Actores:** Cliente y Encargado operativo.

**Recursos actuales:** checklist fisico, fotografias, contrato, mensajes,
recibos y notas manuales.

**Informacion manejada:** fecha de devolucion, kilometraje final, combustible,
estado final, danos, retrasos, multas y observaciones.

**Problemas detectados:** si la informacion de entrega y devolucion no esta
relacionada, es dificil justificar cargos adicionales.

**Modulo o entidad que surge:** devoluciones, inspeccion final, cargos por dano,
cargos por retraso y cierre de alquiler.

### Cierre del alquiler

**Actividad actual:** despues de la devolucion se verifica si el contrato quedo
pagado y si el vehiculo puede volver a estar disponible.

**Actores:** Encargado operativo y Administrador / Gerente.

**Recursos actuales:** contrato, recibos, planilla de pagos, registro de
vehiculos y notas de devolucion.

**Informacion manejada:** estado del contrato, pagos registrados, saldo final,
cargos adicionales y estado actualizado del vehiculo.

**Problemas detectados:** puede quedar informacion incompleta si no se verifica
contrato, pago y estado del vehiculo en conjunto.

**Modulo o entidad que surge:** cierre de contrato, estado de alquiler y
actualizacion de disponibilidad.

### Gestion de mantenimiento

**Actividad actual:** se registran revisiones, reparaciones y trabajos basicos
realizados sobre los vehiculos.

**Actores:** Responsable de mantenimiento, Encargado operativo y Administrador /
Gerente.

**Recursos actuales:** notas de taller, facturas, fotografias, planillas,
mensajes y reportes manuales.

**Informacion manejada:** vehiculo, fecha, tipo de mantenimiento, descripcion,
costo, responsable, kilometraje y estado posterior.

**Problemas detectados:** si el mantenimiento no se registra a tiempo, un
vehiculo podria figurar como disponible aunque no este listo para alquilarse.

**Modulo o entidad que surge:** mantenimiento, tipo de mantenimiento, costos,
responsables y estado operativo del vehiculo.

### Reportes y supervision

**Actividad actual:** el gerente revisa informacion para tomar decisiones sobre
ingresos, reservas, pagos pendientes y uso de la flota.

**Actores:** Administrador / Gerente.

**Recursos actuales:** planillas Excel, contratos fisicos, recibos, mensajes y
registros manuales.

**Informacion manejada:** ingresos, contratos activos, pagos pendientes,
vehiculos mas alquilados, vehiculos en mantenimiento y estado general de la
flota.

**Problemas detectados:** los reportes toman tiempo porque la informacion esta
dispersa y puede no estar actualizada.

**Modulo o entidad que surge:** reportes, indicadores, ingresos, contratos
activos, pagos pendientes y estado de flota.

## Procesos y entidades derivadas

| Proceso | Entidades o modulos relacionados |
| ------- | -------------------------------- |
| Control de acceso y responsabilidades | usuarios, roles, permisos |
| Registro de clientes | clientes, documentos, contactos |
| Gestion de vehiculos | vehiculos, tipos, estados, kilometraje |
| Consulta de disponibilidad | disponibilidad, reservas, calendario |
| Registro de reservas | reservas, estados de reserva |
| Generacion de contratos | contratos, garantias, condiciones |
| Entrega del vehiculo | entregas, inspecciones, danos |
| Registro de pagos | pagos, metodos de pago, saldos, multas |
| Devolucion del vehiculo | devoluciones, inspecciones finales, cargos |
| Cierre del alquiler | contratos cerrados, disponibilidad |
| Gestion de mantenimiento | mantenimientos, costos, responsables |
| Reportes y supervision | reportes, indicadores, ingresos |

## Reglas generales detectadas

- Un vehiculo en mantenimiento o fuera de servicio no debe reservarse.
- Una reserva debe relacionar cliente, vehiculo, fechas y estado.
- Un contrato solo debe generarse si existe disponibilidad.
- La entrega debe registrar kilometraje, combustible y estado inicial.
- La devolucion debe compararse con la entrega para identificar danos, retrasos o
  cargos adicionales.
- Un pago debe relacionarse con un contrato o reserva.
- Un vehiculo solo debe volver a estar disponible despues de cerrar el alquiler o
  finalizar su mantenimiento.
- La informacion debe centralizarse para evitar registros duplicados,
  inconsistentes o desactualizados.

## Diferencia con procedimientos

Este documento identifica los procesos del caso de estudio. Los pasos detallados
de como se realiza cada actividad deben colocarse en `procedimientos.md`.
