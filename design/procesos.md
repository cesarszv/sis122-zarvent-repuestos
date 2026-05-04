# Procesos

Los procesos son las acciones o actividades principales que se realizan dentro del
caso de estudio.

En Zarvent Rent, los procesos representan lo que el sistema debe permitir hacer
para administrar el alquiler de vehiculos, desde la atencion inicial del cliente
hasta la devolucion del vehiculo y el control de la flota.

## Proceso general del alquiler

El flujo principal del sistema puede resumirse de la siguiente forma:

1. El cliente solicita alquilar un vehiculo.
2. El encargado operativo verifica la disponibilidad.
3. Se registra una reserva.
4. Se genera el contrato de alquiler.
5. Se entrega el vehiculo al cliente.
6. Se registran los pagos correspondientes.
7. El cliente devuelve el vehiculo.
8. Se revisa el estado del vehiculo.
9. Se registran cargos adicionales si corresponde.
10. Se cierra el alquiler.

## Procesos principales

### Autenticacion y control de usuarios

Permite que los usuarios ingresen al sistema segun su rol y sus permisos.

**Actor principal:** Administrador / Gerente.
    
**Resultado esperado:** usuario autenticado y acceso limitado segun el rol
correspondiente.

### Registro y actualizacion de clientes

Permite registrar y modificar los datos de los clientes que solicitan alquilar
un vehiculo.

**Actor principal:** Encargado operativo.

**Resultado esperado:** cliente registrado con informacion personal, documentos,
contacto y referencias necesarias para reservas y contratos.

### Gestion de vehiculos

Permite registrar y actualizar la informacion de los vehiculos de la empresa.

**Actor principal:** Administrador / Gerente.

**Resultado esperado:** vehiculo registrado con sus caracteristicas, kilometraje,
estado operativo, disponibilidad y condicion general.

### Consulta de disponibilidad

Permite verificar si un vehiculo puede ser alquilado en un rango de fechas.

**Actor principal:** Encargado operativo.

**Resultado esperado:** confirmacion de disponibilidad o rechazo de la solicitud
si el vehiculo ya esta reservado, alquilado, en mantenimiento o fuera de servicio.

### Registro de reservas

Permite apartar un vehiculo para un cliente antes de generar el contrato de
alquiler.

**Actor principal:** Encargado operativo.

**Resultado esperado:** reserva registrada con cliente, vehiculo, fechas,
condiciones iniciales y estado de la reserva.

### Generacion de contratos de alquiler

Permite formalizar el alquiler de un vehiculo entre la empresa y el cliente.

**Actor principal:** Encargado operativo.

**Resultado esperado:** contrato generado con cliente, vehiculo, fechas, precio,
garantia, condiciones del alquiler y responsabilidades.

### Entrega del vehiculo

Permite registrar la salida del vehiculo cuando inicia el alquiler.

**Actor principal:** Encargado operativo.

**Resultado esperado:** vehiculo entregado con registro de kilometraje,
combustible, estado inicial y fecha de entrega.

### Registro de pagos

Permite controlar los pagos realizados por el cliente durante el proceso de
alquiler.

**Actor principal:** Encargado operativo.

**Resultado esperado:** pagos, anticipos, saldos pendientes, cargos adicionales
y multas registrados correctamente.

### Devolucion del vehiculo

Permite registrar la recepcion del vehiculo al finalizar el alquiler.

**Actor principal:** Encargado operativo.

**Resultado esperado:** devolucion registrada con kilometraje, combustible,
estado final, danos, retrasos o cargos adicionales si corresponde.

### Cierre del alquiler

Permite finalizar el alquiler cuando el vehiculo fue devuelto y los pagos fueron
registrados.

**Actor principal:** Encargado operativo.

**Resultado esperado:** contrato cerrado, pagos actualizados y vehiculo devuelto
a su estado correspondiente.

### Gestion de mantenimiento

Permite registrar revisiones, reparaciones y cambios en el estado operativo de
los vehiculos.

**Actor principal:** Responsable de mantenimiento.

**Resultado esperado:** mantenimiento registrado y estado del vehiculo actualizado
como disponible, en mantenimiento o fuera de servicio.

### Reportes y supervision

Permite consultar informacion general para la toma de decisiones.

**Actor principal:** Administrador / Gerente.

**Resultado esperado:** reportes de ingresos, contratos activos, pagos pendientes,
vehiculos mas alquilados y estado general de la flota.

## Reglas generales

- Un vehiculo en mantenimiento o fuera de servicio no puede ser reservado.
- Una reserva debe tener cliente, vehiculo, fechas y estado.
- Un contrato solo puede generarse si el vehiculo esta disponible.
- La devolucion puede generar cargos adicionales por danos, retrasos, combustible
  faltante o multas.
- El mantenimiento puede cambiar la disponibilidad del vehiculo.
- El administrador puede revisar y corregir informacion cuando sea necesario.
