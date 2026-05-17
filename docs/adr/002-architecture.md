# ADR 002: Architecture

## 1. Enfoque del Sistema

### ¿Qué problema principal resuelve Zarvent Repuestos: vender más rápido, controlar stock, reducir errores, generar reportes o todo eso?

El foco de Zarvent Repuestos es controlar el stock.

Lo demás también es importante, pero lo esencial es mantener un buen control del stock, porque trabajamos con distintos proveedores. La idea es que los usuarios también puedan comprar desde la plataforma; por eso existen dos canales principales: proveedores y clientes. Esta plataforma busca ser abierta para que más personas puedan acceder.

### ¿Qué sería un “fracaso” del sistema aunque técnicamente funcione?

Que técnicamente funcione, pero no tenga suficiente calidad en User Experience y User Interface para que los trabajadores puedan actualizar el stock de forma fácil y constante.

También sería un fracaso que el sistema funcione, pero no sea confiable. Si, como “emergencia”, se debe volver temporalmente al manejo físico de la información, el sistema podría llegar a un punto en el que sería inútil.

### ¿Qué información hoy está duplicada o dispersa y debe centralizarse?

La información ya existe; solo falta el sistema para empezar a trabajar y aprovechar lo que ya se tiene.

## 2. Usuarios

### ¿Quiénes usarán el sistema realmente: vendedor, almacén, cajero, compras, gerente?

Mayormente lo usarán trabajadores de la empresa central y clientes. No contaremos con muchos trabajadores, así que el sistema debe ser eficiente. También se debe considerar que hoy puede usarlo “Pedro”, pero mañana le puede tocar a “Carlos”.

Los roles no son totalmente fijos; los permisos o responsabilidades pueden ir rotando.

### ¿Una misma persona puede tener varios roles?

Sí.

### ¿Qué acciones debe poder hacer cada rol y cuáles NO debe tocar?

PENDIENTE

## 3. Módulos

- ¿Cuáles son los bloques principales del sistema: clientes, repuestos, inventario, ventas, pagos, compras, devoluciones, reportes?
- ¿Qué módulo depende de otro para funcionar?
- ¿Qué módulo es más crítico si falla?

## 4. Reglas del Negocio

- ¿Se puede vender un repuesto sin stock?
- ¿Se puede modificar una venta ya pagada?
- ¿Quién puede autorizar descuentos, anulaciones o devoluciones?
- ¿Una devolución siempre devuelve stock o depende del estado del producto?

## 5. Datos

- ¿Qué datos deben guardarse como historial aunque cambien después? Ejemplo: precio de venta, costo de compra, método de pago.
- ¿Qué datos deben ser únicos? Ejemplo: código interno del repuesto, CI/NIT, tax ID del proveedor.
- ¿Qué datos son obligatorios para registrar una venta válida?

## 6. Flujo Principal

- ¿Cuál es el camino normal desde que el cliente pide un repuesto hasta que se registra el pago?
- ¿En qué paso se descuenta el stock?
- ¿Qué pasa si el cliente paga parcialmente o si el pago falla?
- ¿Qué pasa si el vendedor encuentra el repuesto pero no hay stock?

## 7. Inventario

- ¿El sistema solo necesita saber “cuánto stock hay” o también “por qué cambió el stock”?
- ¿Conviene registrar movimientos de inventario desde el inicio o dejarlo como extensión?
- ¿Cómo se corrige una diferencia entre stock físico y stock registrado?

## 8. Arquitectura

- ¿El sistema será solo base de datos y consultas, o tendrá interfaz/app encima?
- Si hay app, ¿conviene separar presentación, lógica de negocio y acceso a datos?
- ¿Qué reglas deben vivir en la aplicación y cuáles deben protegerse también en PostgreSQL con constraints?
- ¿Qué parte del sistema debe ser simple ahora para no sobreingenierizar?

## 9. Reportes

- ¿Qué quiere ver el gerente cada día?
- ¿Qué reportes salen directo de ventas, pagos e inventario?
- ¿Qué decisiones reales se tomarán con esos reportes?

## 10. Calidad

- ¿Qué debe priorizar el sistema: rapidez, integridad de datos, facilidad de uso o trazabilidad?
- ¿Qué errores humanos debe prevenir?
- ¿Qué decisiones deben quedar registradas para auditoría?
