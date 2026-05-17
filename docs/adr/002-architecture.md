# ADR 002: Architecture Discovery

## 1. System Focus

Zarvent Repuestos debe priorizar **control de stock**.

Vender, cobrar, comprar y reportar tambien importan, pero el sistema pierde
valor si el inventario no se actualiza de forma facil, constante y confiable.
Como existen proveedores y clientes, la plataforma debe manejar ambos canales y
seguir siendo abierta para mas usuarios.

## 2. Failure Conditions

El sistema fracasa aunque "funcione" si:

- la UX/UI impide que trabajadores actualicen stock sin friccion
- la informacion vuelve a depender de registros fisicos por falta de confianza
- el sistema deja de ser util cuando cambia la persona encargada

## 3. Users and Roles

Usuarios principales:

- trabajadores de la empresa central
- clientes

Los roles no son totalmente fijos. Una misma persona puede tener varios roles y
las responsabilidades pueden rotar entre trabajadores.

Pendiente: definir que acciones puede y no puede hacer cada rol.

## 4. Open Architecture Questions

| Area | Questions |
| --- | --- |
| Modules | ¿Cuales son los bloques principales: clientes, repuestos, inventario, ventas, pagos, compras, devoluciones, reportes? ¿Que modulo depende de otro? ¿Cual es critico si falla? |
| Business rules | ¿Se puede vender sin stock? ¿Modificar una venta pagada? ¿Quien autoriza descuentos, anulaciones o devoluciones? ¿Una devolucion siempre devuelve stock? |
| Data | ¿Que datos deben quedar como historial? ¿Que datos deben ser unicos? ¿Que datos son obligatorios para una venta valida? |
| Main flow | ¿Como va el flujo desde pedido del cliente hasta pago? ¿Cuando se descuenta stock? ¿Que pasa con pagos parciales, pagos fallidos o falta de stock? |
| Inventory | ¿Solo importa cuanto stock hay o tambien por que cambio? ¿Se registran movimientos desde el inicio? ¿Como se corrige diferencia entre stock fisico y registrado? |
| Application architecture | ¿Solo base de datos y consultas, o tambien interfaz/app? ¿Que reglas viven en la app y cuales se protegen con constraints en PostgreSQL? |
| Reports | ¿Que necesita ver gerencia cada dia? ¿Que reportes salen de ventas, pagos e inventario? ¿Que decisiones se tomaran con ellos? |
| Quality | ¿Se prioriza rapidez, integridad, facilidad de uso o trazabilidad? ¿Que errores humanos debe prevenir? ¿Que decisiones deben quedar auditables? |

## Current Direction

- El sistema debe centralizar informacion que ya existe, no inventar el negocio
  desde cero.
- El control de stock manda sobre la arquitectura.
- La facilidad de uso importa, pero no puede romper integridad ni trazabilidad.
- Las decisiones pendientes deben resolverse antes de convertir roles, permisos
  o flujos complejos en schema definitivo.
