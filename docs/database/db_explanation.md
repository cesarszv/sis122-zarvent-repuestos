# Database Table Explanation

Este documento explica cada tabla definida en [erd.md](erd.md).

El modelo corresponde a un sistema administrativo para **Zarvent Repuestos**:
clientes, catalogo de repuestos, compatibilidad con vehiculos, stock, ventas,
pagos, compras a proveedores y devoluciones.

Cada tabla se explica como una unidad completa:

- **Descripcion:** que representa la tabla.
- **Atributos:** que significa cada columna y que regla sostiene.
- **Justificacion:** por que la tabla existe.
- **Fortalezas:** que ventajas tiene el diseno actual.
- **Oportunidades de mejora:** que se podria optimizar o extender.
- **Relaciones:** como se conecta con el resto del ERD.

## Indice de tablas

| Bloque | Tablas |
| --- | --- |
| Identidad y clientes | [`PERSON`](#person), [`CUSTOMER`](#customer) |
| Catalogo y compatibilidad | [`PART_CATEGORY`](#part_category), [`PART`](#part), [`VEHICLE_MODEL`](#vehicle_model), [`PART_COMPATIBILITY`](#part_compatibility) |
| Inventario | [`INVENTORY_STOCK`](#inventory_stock) |
| Ventas y pagos | [`SALES_ORDER`](#sales_order), [`SALES_ORDER_ITEM`](#sales_order_item), [`PAYMENT`](#payment) |
| Compras y devoluciones | [`SUPPLIER`](#supplier), [`PURCHASE_ORDER`](#purchase_order), [`PURCHASE_ORDER_ITEM`](#purchase_order_item), [`RETURN_ORDER`](#return_order), [`RETURN_ORDER_ITEM`](#return_order_item) |

## Lectura general del modelo

El ERD esta organizado en cinco bloques:

| Bloque | Tablas principales | Idea central |
| --- | --- | --- |
| Identidad y clientes | `PERSON`, `CUSTOMER` | Separar los datos civiles del rol comercial de comprador. |
| Catalogo y compatibilidad | `PART_CATEGORY`, `PART`, `VEHICLE_MODEL`, `PART_COMPATIBILITY` | Vender el repuesto correcto para el vehiculo correcto. |
| Inventario | `INVENTORY_STOCK` | Saber cuanto stock existe y donde esta. |
| Ventas y pagos | `SALES_ORDER`, `SALES_ORDER_ITEM`, `PAYMENT` | Registrar la venta, su detalle y sus cobros. |
| Compras y devoluciones | `SUPPLIER`, `PURCHASE_ORDER`, `PURCHASE_ORDER_ITEM`, `RETURN_ORDER`, `RETURN_ORDER_ITEM` | Reponer mercaderia y controlar devoluciones contra ventas reales. |

No estudies esto como una lista. Estudialo como flujo:

`CUSTOMER -> SALES_ORDER -> SALES_ORDER_ITEM -> PART -> INVENTORY_STOCK`

Luego entiende los ciclos complementarios:

`SUPPLIER -> PURCHASE_ORDER -> PURCHASE_ORDER_ITEM -> PART`

`SALES_ORDER -> RETURN_ORDER -> RETURN_ORDER_ITEM -> SALES_ORDER_ITEM`

## `PERSON`

### Descripcion

`PERSON` representa la identidad civil o de contacto de una persona. Guarda
datos como nombre, apellido, documento de identidad, telefono, correo y
direccion.

No representa todavia una venta ni una compra. Representa a la persona como
entidad base.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `person_id` | Identificador tecnico de la persona. | Da una clave estable aunque cambien nombre, telefono o documento. | No depende de datos humanos cambiantes. | Usar `INT AUTO_INCREMENT` o `BIGINT` segun volumen esperado. | `PK`; referenciado por `CUSTOMER.person_id`. |
| `first_name` | Nombre de pila de la persona. | Permite identificar y atender al cliente correctamente. | Es simple y facil de buscar. | Definir si admite nombres compuestos y longitud maxima. | Depende de la identidad civil de `PERSON`. |
| `last_name` | Apellido de la persona. | Completa la identificacion humana en recibos, busquedas y contacto. | Mejora busqueda por nombre completo. | Separar apellido paterno/materno solo si el negocio lo necesita. | Depende de la identidad civil de `PERSON`. |
| `identity_number` | Documento de identidad o numero fiscal personal. | Evita registrar a la misma persona varias veces. | `UK` reduce duplicidad. | Definir formato, obligatoriedad y pais/tipo de documento. | `UK`; usado para busqueda y validacion de duplicados. |
| `phone` | Numero de contacto telefonico. | Permite comunicarse para cotizaciones, pedidos o garantias. | Dato operativo directo para ventas. | Separar varios telefonos en una tabla `PERSON_PHONE` si hace falta. | Dato descriptivo de `PERSON`. |
| `email` | Correo electronico de contacto. | Sirve para enviar informacion, comprobantes o comunicaciones formales. | Facilita contacto digital. | Validar formato y definir si debe ser unico. | Dato descriptivo de `PERSON`. |
| `address` | Direccion de la persona. | Puede usarse para facturacion, entrega o referencia comercial. | Mantiene informacion de contacto centralizada. | Normalizar direcciones si existen entregas frecuentes o varias sucursales. | Dato descriptivo de `PERSON`. |

### Justificacion

Existe para evitar duplicar datos personales cada vez que una persona participa
en el sistema. En los procesos actuales, el cliente puede aparecer en recibos,
facturas, mensajes, garantias y devoluciones. Si esos datos se escriben en cada
tabla, aparecen inconsistencias.

Separar `PERSON` permite manejar una identidad estable y luego conectarla con un
rol comercial como `CUSTOMER`.

### Fortalezas

- Evita repetir nombres, telefono, correo y direccion en tablas de ventas o
  devoluciones.
- Permite buscar personas por `identity_number`, telefono o correo.
- Deja abierto el crecimiento del sistema: una persona podria convertirse luego
  en cliente, contacto, usuario o responsable.
- El atributo `identity_number` como `UK` ayuda a reducir duplicados.

### Oportunidades de mejora

- Definir si `identity_number` siempre es obligatorio o si puede ser nulo para
  clientes ocasionales.
- Separar direcciones o telefonos en tablas propias si una persona puede tener
  varios contactos.
- Agregar auditoria (`created_at`, `updated_at`) si se necesita rastrear cambios
  en datos personales.
- Validar formato de correo y documento desde la aplicacion o con restricciones.

### Relaciones

- `PERSON ||--o| CUSTOMER`: una persona puede tener cero o un registro de
  cliente.
- `CUSTOMER.person_id` es la clave foranea que apunta a `PERSON.person_id`.
- Cardinalidad: una persona puede existir sin ser cliente; un cliente debe
  pertenecer a una persona.

## `CUSTOMER`

### Descripcion

`CUSTOMER` representa el rol comercial del comprador dentro del negocio. No
guarda todos los datos personales; esos viven en `PERSON`. En cambio, agrega
datos propios del cliente como `billing_name` y `tax_id`.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `customer_id` | Identificador tecnico del cliente. | Distingue el rol comercial de la identidad civil. | Permite historial comercial estable. | Usar clave surrogate y mantener `person_id` como candidato unico. | `PK`; referenciado por `SALES_ORDER.customer_id`. |
| `person_id` | Persona asociada al cliente. | Conecta el comprador con sus datos civiles. | Evita duplicar nombre, telefono y direccion. | Declararlo `UK` si una persona solo puede tener un cliente. | `FK` hacia `PERSON.person_id`. |
| `billing_name` | Nombre o razon usado para facturacion. | Puede diferir del nombre civil de la persona. | Da flexibilidad para comprobantes. | Definir si se llena por defecto desde `PERSON` o manualmente. | Depende de reglas de facturacion del cliente. |
| `tax_id` | Numero tributario usado para comprobantes. | Permite registrar NIT/CI/RUC u otro identificador fiscal. | Separa documento civil de documento fiscal. | Definir si debe ser unico y que formatos acepta. | Depende del uso comercial de `CUSTOMER`. |

### Justificacion

Existe porque una persona y un cliente no son el mismo concepto. Una persona es
una identidad. Un cliente es esa persona actuando frente al negocio: compra,
pide factura, paga, devuelve productos y genera historial comercial.

Esta separacion evita mezclar datos civiles con datos comerciales.

### Fortalezas

- Mantiene limpio el modelo: datos personales en `PERSON`, datos comerciales en
  `CUSTOMER`.
- Facilita consultar el historial de ventas por cliente.
- Permite conservar historial aunque cambien algunos datos personales.
- `billing_name` y `tax_id` permiten manejar facturacion o comprobantes.

### Oportunidades de mejora

- Agregar `customer_type` si el negocio atiende tanto personas naturales como
  talleres o empresas.
- Hacer `person_id` unico si una persona solo puede tener un registro de
  cliente.
- Definir si `tax_id` puede diferir de `PERSON.identity_number`.
- Si se necesita una arquitectura mas flexible, evaluar un modelo `PARTY` para
  personas y organizaciones. Es mas potente, pero tambien mas complejo para Base
  de Datos I.

### Relaciones

- `CUSTOMER` depende de `PERSON` mediante `customer.person_id`.
- `CUSTOMER ||--o{ SALES_ORDER`: un cliente puede realizar muchas ventas.
- Cada `SALES_ORDER` pertenece a un solo `CUSTOMER`.
- Cardinalidad: `PERSON` 1 a 0..1 `CUSTOMER`; `CUSTOMER` 1 a 0..N
  `SALES_ORDER`.

## `PART_CATEGORY`

### Descripcion

`PART_CATEGORY` clasifica los repuestos por grupos del catalogo. Ejemplos:
filtros, frenos, suspension, motor, electricidad o accesorios.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `part_category_id` | Identificador tecnico de la categoria. | Permite relacionar repuestos con categorias sin depender del nombre. | Estable aunque se renombre la categoria. | Usar clave surrogate y mantener `name` unico. | `PK`; referenciado por `PART.part_category_id`. |
| `name` | Nombre de la categoria. | Clasifica el catalogo de repuestos. | `UK` evita categorias repetidas. | Normalizar mayusculas/minusculas y nombres equivalentes. | `UK`; usado para busqueda y reportes. |
| `description` | Explicacion breve de la categoria. | Aclara que repuestos entran en ese grupo. | Ayuda a usuarios nuevos y documenta criterio. | Convertir en campo opcional si no todas las categorias requieren detalle. | Dato descriptivo de `PART_CATEGORY`. |

### Justificacion

Existe para ordenar el catalogo y evitar que la categoria sea texto repetido en
cada repuesto. Si se escribe la categoria directamente en `PART`, aparecen
variantes como `Filtro`, `filtros`, `FILTRACION`, etc.

La categoria ayuda a buscar, filtrar y reportar repuestos de forma consistente.

### Fortalezas

- Evita duplicacion textual de categorias.
- `name` como `UK` protege contra categorias repetidas.
- Hace mas claro el catalogo para ventas, almacen y reportes.
- Permite agregar descripcion a cada categoria.

### Oportunidades de mejora

- Agregar jerarquia si existen categorias y subcategorias.
- Normalizar nombres con reglas de mayusculas/minusculas.
- Agregar estado si algunas categorias dejan de usarse.
- Para un modelo industrial, podria alinearse con clasificaciones mas detalladas
  de repuestos, pero eso seria excesivo para un ERD compacto.

### Relaciones

- `PART_CATEGORY ||--o{ PART`: una categoria puede agrupar muchos repuestos.
- `PART.part_category_id` apunta a `PART_CATEGORY.part_category_id`.
- Cardinalidad: una categoria puede existir sin repuestos; cada repuesto
  pertenece a una categoria.

## `PART`

### Descripcion

`PART` representa el repuesto como producto central del negocio. Es vendible,
comprable e inventariable. Contiene codigo interno, codigo OEM, nombre, marca,
unidad, precio de venta, costo de compra, dias de garantia y estado.

Esta es una de las tablas mas importantes del ERD.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `part_id` | Identificador tecnico del repuesto. | Permite relacionar ventas, compras, stock y compatibilidad con un producto estable. | Es la columna central del catalogo. | Usar surrogate key y no codigos comerciales como PK. | `PK`; referenciado por `SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM`, `INVENTORY_STOCK` y `PART_COMPATIBILITY`. |
| `part_category_id` | Categoria a la que pertenece el repuesto. | Ordena el catalogo y permite reportes por grupo. | Evita repetir texto de categoria en cada parte. | Definir si todo repuesto debe tener categoria obligatoria. | `FK` hacia `PART_CATEGORY.part_category_id`. |
| `internal_code` | Codigo interno usado por Zarvent para identificar el repuesto. | Evita confusion entre piezas similares. | `UK` protege unicidad operativa. | Definir formato estandar y codigo de barras si aplica. | `UK`; usado para busqueda y control de inventario. |
| `oem_code` | Codigo de fabricante o referencia OEM. | Ayuda a encontrar equivalencias y compatibilidad. | Util para ventas tecnicas. | Permitir multiples codigos con `PART_IDENTIFIER`. | Dato de identificacion externo de `PART`. |
| `name` | Nombre comercial o descripcion corta del repuesto. | Permite reconocer la pieza en busquedas, ventas y compras. | Facilita uso humano del catalogo. | Agregar descripcion tecnica separada si el nombre queda corto. | Dato descriptivo de `PART`. |
| `brand` | Marca del repuesto. | Diferencia piezas similares de distintos fabricantes. | Ayuda a precios, garantia y preferencia del cliente. | Normalizar en tabla `BRAND` si hay muchos valores repetidos. | Dato descriptivo de `PART`. |
| `unit` | Unidad de medida o venta. | Indica si se vende por unidad, par, juego, litro, etc. | Evita ambiguedad en cantidades. | Controlar con catalogo o `CHECK` para evitar valores libres. | Afecta interpretacion de cantidades en ventas, compras y stock. |
| `sale_price` | Precio actual de venta de referencia. | Permite cotizar rapidamente. | Centraliza precio vigente del catalogo. | Guardar historial de precios si cambian frecuentemente. | No debe usarse para recalcular ventas pasadas; eso vive en `SALES_ORDER_ITEM.unit_price`. |
| `purchase_cost` | Costo actual de compra de referencia. | Ayuda a estimar margen y reposicion. | Centraliza costo vigente. | Guardar costos por proveedor o historial si el precio varia. | No reemplaza `PURCHASE_ORDER_ITEM.unit_cost` historico. |
| `warranty_days` | Dias de garantia ofrecidos para el repuesto. | Apoya decisiones de devolucion o garantia. | Hace explicita una regla comercial. | Validar que no sea negativo y definir garantia por marca/categoria si varia. | Usado logicamente por `RETURN_ORDER` y `RETURN_ORDER_ITEM`. |
| `status` | Estado del repuesto en el catalogo. | Permite diferenciar activo, inactivo, discontinuado o bloqueado. | Evita borrar productos con historial. | Controlar valores con `CHECK` o tabla catalogo. | Afecta si se permite vender o comprar el `PART`. |

### Justificacion

Existe porque Zarvent Repuestos necesita un catalogo confiable. Los procesos de
busqueda, venta, inventario, compra, compatibilidad y devolucion giran alrededor
del repuesto.

Sin `PART`, el sistema queda dependiendo de textos escritos en ventas o compras,
lo cual produce duplicados, precios incoherentes y stock imposible de controlar.

### Fortalezas

- `internal_code` como `UK` identifica el repuesto dentro del negocio.
- `oem_code` ayuda a relacionar la pieza con codigos de fabricante.
- Guarda precio y costo actual de referencia.
- Incluye `warranty_days`, dato importante para devoluciones y garantias.
- Se conecta con ventas, compras, inventario y compatibilidad.

### Oportunidades de mejora

- Un solo `oem_code` puede ser insuficiente. Un repuesto puede tener varios
  codigos: OEM, alternativo, proveedor, barcode o equivalencias. Extension:
  `PART_IDENTIFIER`.
- `brand`, `unit` y `status` como `varchar` son practicos, pero permiten valores
  inconsistentes. Mejorar con `CHECK` o tablas catalogo si el proyecto crece.
- Agregar imagen, descripcion tecnica o atributos especificos si el catalogo
  necesita mas detalle.
- Separar precio actual de listas historicas si existen promociones, monedas o
  precios por cliente.

### Relaciones

- `PART` pertenece a `PART_CATEGORY` mediante `part_category_id`.
- `PART ||--o{ SALES_ORDER_ITEM`: un repuesto puede venderse muchas veces.
- `PART ||--o{ PURCHASE_ORDER_ITEM`: un repuesto puede comprarse muchas veces.
- `PART ||--o{ INVENTORY_STOCK`: un repuesto puede tener stock en varias
  ubicaciones.
- `PART ||--o{ PART_COMPATIBILITY`: un repuesto puede tener varias reglas de
  compatibilidad.
- Cardinalidad clave: `PART` es entidad padre para muchas operaciones, pero no
  debe depender de una venta o compra para existir.

## `VEHICLE_MODEL`

### Descripcion

`VEHICLE_MODEL` representa el vehiculo contra el cual se valida compatibilidad.
Incluye marca (`make`), modelo (`model`) y rango de anios (`year_from`,
`year_to`).

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `vehicle_model_id` | Identificador tecnico del modelo de vehiculo. | Permite conectar vehiculos con compatibilidades. | Estable aunque se ajusten textos de marca o modelo. | Normalizar marca/modelo si el catalogo crece. | `PK`; referenciado por `PART_COMPATIBILITY.vehicle_model_id`. |
| `make` | Marca del vehiculo. | La busqueda de repuestos suele iniciar por marca. | Facil de entender para ventas. | Crear `VEHICLE_MAKE` para evitar duplicados. | Dato descriptivo de `VEHICLE_MODEL`. |
| `model` | Modelo comercial del vehiculo. | Necesario para validar compatibilidad. | Permite consultas por modelo. | Separar version o trim si afecta compatibilidad. | Dato descriptivo de `VEHICLE_MODEL`. |
| `year_from` | Anio inicial del rango compatible. | Un repuesto puede servir solo para ciertos anios. | Resume rangos sin registrar cada anio por separado. | Validar que sea menor o igual a `year_to`. | Depende de `year_to` para definir rango valido. |
| `year_to` | Anio final del rango compatible. | Cierra el rango de fabricacion o aplicacion. | Ayuda a evitar ventas por anio incorrecto. | Permitir nulo si el modelo sigue vigente, o usar regla explicita. | Depende de `year_from` para definir rango valido. |

### Justificacion

Existe porque en un negocio de repuestos no basta saber que la pieza existe. Hay
que saber si sirve para el vehiculo del cliente.

Sin una tabla de vehiculos, la compatibilidad queda como texto libre en
observaciones, y eso genera errores de venta.

### Fortalezas

- Permite buscar repuestos por marca, modelo y anio.
- Reduce ventas incorrectas por incompatibilidad.
- Sirve como base para reportes de demanda por tipo de vehiculo.
- Se conecta con `PART` mediante una tabla intermedia correcta:
  `PART_COMPATIBILITY`.

### Oportunidades de mejora

- El modelo es compacto. En compatibilidad real pueden importar motor,
  cilindrada, version, transmision, posicion o carroceria.
- `make` y `model` como texto pueden duplicarse. Podrian normalizarse en
  `VEHICLE_MAKE` y `VEHICLE_MODEL_NAME`, pero eso aumenta el tamano del ERD.
- Validar que `year_from` sea menor o igual que `year_to`.
- Agregar estado si algunos modelos dejan de usarse en el catalogo.

### Relaciones

- `VEHICLE_MODEL ||--o{ PART_COMPATIBILITY`: un vehiculo puede aceptar muchos
  repuestos.
- `PART_COMPATIBILITY.vehicle_model_id` apunta a
  `VEHICLE_MODEL.vehicle_model_id`.
- La relacion con `PART` es many-to-many y se resuelve mediante
  `PART_COMPATIBILITY`.

## `PART_COMPATIBILITY`

### Descripcion

`PART_COMPATIBILITY` representa la compatibilidad entre un repuesto y un modelo
de vehiculo. Guarda `part_id`, `vehicle_model_id`, `engine_code` y notas.

No es una tabla de relleno. Es la tabla que convierte una relacion
many-to-many en un modelo relacional correcto.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `part_compatibility_id` | Identificador tecnico de la compatibilidad. | Identifica cada regla de aplicacion entre pieza y vehiculo. | Permite administrar compatibilidades individualmente. | Agregar restriccion unica por combinacion relevante. | `PK`. |
| `part_id` | Repuesto que participa en la compatibilidad. | Indica que pieza se esta evaluando. | Conecta compatibilidad con catalogo real. | Debe ser obligatorio para evitar compatibilidades huerfanas. | `FK` hacia `PART.part_id`. |
| `vehicle_model_id` | Vehiculo al que aplica el repuesto. | Indica para que vehiculo sirve la pieza. | Hace consultable el fitment por vehiculo. | Debe ser obligatorio. | `FK` hacia `VEHICLE_MODEL.vehicle_model_id`. |
| `engine_code` | Codigo de motor asociado a la compatibilidad. | Algunas piezas dependen del motor, no solo del modelo y anio. | Aumenta precision tecnica. | Normalizar motores si se vuelve repetitivo. | Complementa la relacion `PART`-`VEHICLE_MODEL`. |
| `notes` | Observaciones de compatibilidad. | Permite registrar restricciones que aun no tienen campo propio. | Da flexibilidad para casos tecnicos. | No abusar de texto libre; convertir reglas frecuentes en columnas. | Depende del contexto tecnico de la compatibilidad. |

### Justificacion

Existe porque un repuesto puede servir para muchos vehiculos y un vehiculo puede
usar muchos repuestos. Esa relacion no se debe guardar como lista separada por
comas dentro de `PART`.

Esta tabla ayuda a evitar ventas incorrectas y devoluciones por
incompatibilidad.

### Fortalezas

- Resuelve correctamente la relacion many-to-many entre `PART` y
  `VEHICLE_MODEL`.
- Permite agregar informacion propia de la compatibilidad, como `engine_code` y
  `notes`.
- Mejora la precision en busqueda de repuestos.
- Protege una regla critica del negocio: vender la pieza correcta.

### Oportunidades de mejora

- Agregar restriccion unica sobre `part_id`, `vehicle_model_id` y
  `engine_code` para evitar compatibilidades repetidas.
- Agregar campos para posicion, version, lado, transmision o restricciones
  tecnicas si se requiere mas precision.
- Normalizar `engine_code` si se vuelve un dato repetido y controlado.
- Definir si `notes` debe ser solo observacion o si algunas condiciones deben
  convertirse en campos estructurados.

### Relaciones

- `PART_COMPATIBILITY.part_id` apunta a `PART.part_id`.
- `PART_COMPATIBILITY.vehicle_model_id` apunta a
  `VEHICLE_MODEL.vehicle_model_id`.
- Cardinalidad: un `PART` puede tener cero o muchas compatibilidades; un
  `VEHICLE_MODEL` puede tener cero o muchas compatibilidades.
- En terminos relacionales, implementa:
  `PART -> PART_COMPATIBILITY -> VEHICLE_MODEL`.

## `INVENTORY_STOCK`

### Descripcion

`INVENTORY_STOCK` guarda el saldo actual de un repuesto en una ubicacion. Sus
datos principales son `part_id`, `location_name`, `quantity_on_hand` y
`reorder_level`.

Responde una pregunta operativa directa: cuanto hay y donde esta.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `inventory_stock_id` | Identificador tecnico del saldo de inventario. | Identifica una fila de stock por pieza y ubicacion. | Facilita operaciones sobre una existencia concreta. | Agregar `UK(part_id, location_name)` para evitar duplicados logicos. | `PK`. |
| `part_id` | Repuesto cuyo stock se controla. | El inventario debe pertenecer a una pieza del catalogo. | Evita stock de productos inexistentes. | Debe ser obligatorio. | `FK` hacia `PART.part_id`. |
| `location_name` | Ubicacion fisica o logica del stock. | Permite saber donde esta el repuesto. | Util para almacen y despacho. | Normalizar en `WAREHOUSE_LOCATION`. | Junto con `part_id` deberia ser unico. |
| `quantity_on_hand` | Cantidad actual disponible en esa ubicacion. | Responde cuanto stock existe ahora. | Soporta consulta previa a la venta. | Validar que no sea negativa y explicar cambios con `INVENTORY_MOVEMENT`. | Depende de ventas, compras, devoluciones y ajustes. |
| `reorder_level` | Nivel minimo para sugerir reposicion. | Ayuda a detectar stock bajo. | Conecta inventario con compras. | Validar que no sea negativo y ajustar por demanda. | Comparado contra `quantity_on_hand`. |

### Justificacion

Existe porque ventas necesita verificar stock antes de confirmar una venta, y
compras necesita saber cuando reponer mercaderia.

Sin esta tabla, el stock queda disperso en Excel, conteos visuales o notas, que
es exactamente el problema descrito en los procesos actuales.

### Fortalezas

- Permite controlar stock por repuesto y ubicacion.
- `quantity_on_hand` ayuda a evitar vender productos inexistentes.
- `reorder_level` permite detectar productos que necesitan reposicion.
- Se conecta directamente con `PART`, que es la entidad inventariable.

### Oportunidades de mejora

- Agregar restriccion unica sobre `part_id` y `location_name` para evitar dos
  saldos del mismo repuesto en la misma ubicacion.
- Normalizar `location_name` en una tabla `WAREHOUSE_LOCATION`.
- La mejora mas importante: agregar `INVENTORY_MOVEMENT`. El saldo actual dice
  cuanto hay, pero no explica por que cambio.
- Validar que `quantity_on_hand` y `reorder_level` no sean negativos.

### Relaciones

- `INVENTORY_STOCK.part_id` apunta a `PART.part_id`.
- `PART ||--o{ INVENTORY_STOCK`: un repuesto puede tener stock en cero, una o
  varias ubicaciones.
- En el flujo operativo, `SALES_ORDER_ITEM`, `PURCHASE_ORDER_ITEM` y
  `RETURN_ORDER_ITEM` afectan el stock, aunque el ERD compacto no modele aun el
  historial de movimientos.

## `SALES_ORDER`

### Descripcion

`SALES_ORDER` representa la cabecera de una venta o pedido de venta. Guarda el
cliente, fecha, estado, subtotal, descuento y total.

No guarda cada repuesto vendido. Eso corresponde a `SALES_ORDER_ITEM`.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `sales_order_id` | Identificador tecnico de la venta. | Permite referenciar la operacion completa. | Estable para pagos, lineas y devoluciones. | Usar numeracion comercial separada si se necesita comprobante visible. | `PK`; referenciado por `SALES_ORDER_ITEM`, `PAYMENT` y `RETURN_ORDER`. |
| `customer_id` | Cliente que realiza la venta. | Toda venta necesita comprador identificable. | Conecta venta con historial del cliente. | Definir si se permiten ventas anonimas; si si, modelarlo explicitamente. | `FK` hacia `CUSTOMER.customer_id`. |
| `order_date` | Fecha de la venta o pedido. | Permite reportes por periodo y control de garantia. | Dato basico para gestion comercial. | Agregar hora si se requiere trazabilidad mas fina. | Base temporal para pagos, devoluciones y reportes. |
| `status` | Estado de la venta. | Indica si esta borrador, confirmada, pagada, anulada o devuelta. | Evita borrar operaciones con historial. | Controlar valores con `CHECK` o tabla catalogo. | Afecta si se permiten pagos, despacho o devolucion. |
| `subtotal` | Suma antes de descuentos finales. | Permite separar valor bruto de descuento y total. | Facilita calculo y auditoria comercial. | Definir si se calcula o almacena; si se almacena, validar consistencia. | Depende de las lineas de `SALES_ORDER_ITEM`. |
| `discount_amount` | Descuento aplicado a la venta completa. | Registra rebajas globales. | Diferencia descuento general de descuento por linea. | Validar que no sea negativo ni mayor que `subtotal`. | Participa en calculo de `total_amount`. |
| `total_amount` | Total neto de la venta. | Es el monto final esperado para cobro. | Simplifica consultas de deuda e ingresos. | Validar contra subtotal, descuentos y reglas de impuesto si aplica. | Debe ser coherente con `PAYMENT.amount` acumulado. |

### Justificacion

Existe porque una venta es un evento comercial completo: ocurre en una fecha,
tiene un cliente, tiene un estado y tiene totales. Ademas, una venta puede tener
varias lineas de repuestos y varios pagos.

Si se mezclan cabecera, detalle y pagos en una sola tabla, el modelo se vuelve
rigido y aparecen duplicaciones.

### Fortalezas

- Separa cabecera de venta y detalle de venta.
- Permite una venta con multiples repuestos.
- Permite asociar pagos parciales o multiples metodos mediante `PAYMENT`.
- Permite asociar devoluciones mediante `RETURN_ORDER`.
- Conserva totales para consulta y defensa comercial de la operacion.

### Oportunidades de mejora

- Definir valores permitidos para `status`: por ejemplo `draft`, `confirmed`,
  `paid`, `cancelled`, `returned`.
- Agregar usuario/responsable si se necesita saber quien realizo la venta.
- Separar comprobante o factura en una tabla propia si el alcance tributario es
  importante.
- Validar que `total_amount = subtotal - discount_amount` segun la regla de
  calculo del sistema.

### Relaciones

- `SALES_ORDER.customer_id` apunta a `CUSTOMER.customer_id`.
- `CUSTOMER ||--o{ SALES_ORDER`: un cliente puede realizar muchas ventas.
- `SALES_ORDER ||--|{ SALES_ORDER_ITEM`: una venta debe tener una o mas lineas.
- `SALES_ORDER ||--o{ PAYMENT`: una venta puede tener cero, uno o varios pagos.
- `SALES_ORDER ||--o{ RETURN_ORDER`: una venta puede tener cero o muchas
  devoluciones.

## `SALES_ORDER_ITEM`

### Descripcion

`SALES_ORDER_ITEM` representa una linea de detalle dentro de una venta. Indica
que repuesto se vendio, en que cantidad, a que precio unitario y con que
descuento.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `sales_order_item_id` | Identificador tecnico de la linea de venta. | Permite apuntar exactamente a un repuesto vendido. | Necesario para devoluciones parciales. | Mantener como surrogate key aunque exista combinacion venta-repuesto. | `PK`; referenciado por `RETURN_ORDER_ITEM.sales_order_item_id`. |
| `sales_order_id` | Venta a la que pertenece la linea. | Todo detalle debe pertenecer a una cabecera de venta. | Protege estructura cabecera-detalle. | Debe ser obligatorio. | `FK` hacia `SALES_ORDER.sales_order_id`. |
| `part_id` | Repuesto vendido en la linea. | Conecta la venta con el catalogo. | Evita escribir productos como texto libre. | Validar que el `PART.status` permita venta. | `FK` hacia `PART.part_id`. |
| `quantity` | Cantidad vendida del repuesto. | Necesaria para calcular importes y descontar stock. | Permite multiples unidades por linea. | Validar que sea mayor que cero y que exista stock suficiente. | Afecta `INVENTORY_STOCK.quantity_on_hand` logicamente. |
| `unit_price` | Precio unitario aplicado en el momento de la venta. | Conserva precio historico aunque cambie `PART.sale_price`. | Protege reportes historicos. | Validar que sea mayor o igual a cero; guardar moneda si aplica. | Copia operativa desde `PART.sale_price` al confirmar venta. |
| `discount_amount` | Descuento aplicado a esa linea. | Permite descuentos por producto. | Da precision al calculo del total. | Validar que no supere cantidad por precio unitario. | Afecta subtotal de linea y `SALES_ORDER.total_amount`. |

### Justificacion

Existe porque una venta puede incluir varios repuestos. La estructura correcta
es cabecera-detalle:

`SALES_ORDER -> SALES_ORDER_ITEM`

Guardar columnas como `part_1`, `part_2`, `part_3` dentro de `SALES_ORDER` seria
un error de principiante: limita la cantidad de productos y rompe consultas.

### Fortalezas

- Permite vender multiples repuestos en una misma venta.
- Guarda `unit_price` historico. Esto es clave: una venta pasada no debe
  recalcularse con el precio actual de `PART`.
- Permite descuentos por linea, no solo por venta completa.
- Sirve como referencia exacta para devoluciones mediante `RETURN_ORDER_ITEM`.

### Oportunidades de mejora

- Validar que `quantity` sea mayor que cero.
- Agregar subtotal de linea si se quiere consultar mas rapido, aunque puede
  calcularse desde cantidad, precio y descuento.
- Registrar costo historico de venta si se quiere calcular margen exacto por
  linea.
- Controlar que la cantidad vendida no exceda stock disponible al confirmar la
  venta. Esto normalmente requiere logica transaccional, no solo una foreign
  key.

### Relaciones

- `SALES_ORDER_ITEM.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `SALES_ORDER_ITEM.part_id` apunta a `PART.part_id`.
- `SALES_ORDER ||--|{ SALES_ORDER_ITEM`: una venta debe tener al menos una
  linea.
- `PART ||--o{ SALES_ORDER_ITEM`: un repuesto puede venderse muchas veces.
- `SALES_ORDER_ITEM ||--o{ RETURN_ORDER_ITEM`: una linea vendida puede ser
  devuelta total o parcialmente.

## `PAYMENT`

### Descripcion

`PAYMENT` registra los cobros asociados a una venta. Contiene fecha de pago,
metodo, monto, numero de referencia y estado.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `payment_id` | Identificador tecnico del pago. | Permite registrar cada cobro individualmente. | Soporta varios pagos para una venta. | Agregar numero de recibo separado si el negocio lo necesita. | `PK`. |
| `sales_order_id` | Venta a la que pertenece el pago. | Todo pago debe imputarse a una venta real. | Evita cobros huerfanos. | Debe ser obligatorio. | `FK` hacia `SALES_ORDER.sales_order_id`. |
| `payment_date` | Fecha en que se registra el pago. | Permite controlar ingresos por periodo. | Separa fecha de venta y fecha de cobro. | Agregar hora o fecha de confirmacion bancaria si hace falta. | Base temporal para reportes de caja. |
| `method` | Metodo de pago utilizado. | Distingue efectivo, transferencia, QR, tarjeta u otros. | Permite reportes por forma de pago. | Controlar valores con catalogo o `CHECK`. | Depende de politicas de caja. |
| `amount` | Monto pagado. | Permite calcular saldo de la venta. | Soporta pagos parciales. | Validar que sea mayor que cero y que acumulado no exceda total sin regla explicita. | Se compara con `SALES_ORDER.total_amount`. |
| `reference_number` | Numero de comprobante o referencia externa. | Ayuda a rastrear transferencias, QR o recibos. | Mejora trazabilidad del cobro. | Definir unicidad por metodo si aplica. | Depende del `method`. |
| `status` | Estado del pago. | Diferencia pagos pendientes, confirmados, anulados o reembolsados. | Evita borrar pagos con historial. | Controlar valores permitidos. | Afecta si el pago cuenta para saldo de la venta. |

### Justificacion

Existe porque vender y cobrar no siempre son el mismo evento. Una venta puede
pagarse en efectivo, transferencia, QR, tarjeta, pago parcial o combinacion de
metodos.

Separar `PAYMENT` permite controlar pagos sin ensuciar la cabecera de venta.

### Fortalezas

- Soporta multiples pagos por una misma venta.
- Permite pagos parciales.
- `reference_number` ayuda a rastrear comprobantes de transferencia, QR o
  recibos.
- `status` permite diferenciar pagos pendientes, confirmados, anulados o
  reembolsados.

### Oportunidades de mejora

- Definir catalogo o `CHECK` para `method`.
- Definir catalogo o `CHECK` para `status`.
- Validar que `amount` sea mayor que cero.
- Controlar que la suma de pagos no exceda el total de la venta, salvo que el
  negocio modele anticipos o saldos a favor.
- Separar factura/comprobante si se requiere control fiscal mas formal.

### Relaciones

- `PAYMENT.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `SALES_ORDER ||--o{ PAYMENT`: una venta puede tener cero, uno o varios pagos.
- Cada pago pertenece a una sola venta.

## `SUPPLIER`

### Descripcion

`SUPPLIER` representa a la empresa o persona que abastece repuestos al negocio.
Contiene datos comerciales como `business_name`, `tax_id`, telefono, correo,
direccion y estado activo.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `supplier_id` | Identificador tecnico del proveedor. | Permite referenciar proveedores sin depender del nombre comercial. | Estable aunque cambie el nombre del negocio. | Usar `BIGINT` si se espera crecimiento grande. | `PK`; referenciado por `PURCHASE_ORDER.supplier_id`. |
| `business_name` | Nombre comercial o razon social del proveedor. | Identifica a quien se compra mercaderia. | Claro para compras y reportes. | Definir longitud y reglas de normalizacion. | Dato descriptivo de `SUPPLIER`. |
| `tax_id` | Identificador fiscal del proveedor. | Evita duplicar proveedores registrados con nombres similares. | `UK` protege consistencia. | Definir formato por pais y si puede ser nulo. | `UK`; candidato natural para detectar duplicados. |
| `phone` | Telefono de contacto del proveedor. | Facilita coordinar cotizaciones, entregas y reclamos. | Dato operativo rapido. | Mover a `SUPPLIER_CONTACT` si hay varios contactos. | Dato descriptivo de `SUPPLIER`. |
| `email` | Correo de contacto del proveedor. | Sirve para ordenes, cotizaciones y respaldo documental. | Mejora trazabilidad de comunicacion. | Validar formato y permitir varios correos si hace falta. | Dato descriptivo de `SUPPLIER`. |
| `address` | Direccion comercial del proveedor. | Apoya compras, recepcion y referencias comerciales. | Centraliza datos del proveedor. | Separar sucursales o almacenes si el proveedor tiene varios puntos. | Dato descriptivo de `SUPPLIER`. |
| `is_active` | Indica si el proveedor esta activo para nuevas compras. | Permite bloquear proveedores sin borrar historial. | Conserva compras antiguas y controla uso futuro. | Reemplazar por `status` si hay estados como blocked, preferred o suspended. | Afecta si se permite crear nuevas `PURCHASE_ORDER`. |

### Justificacion

Existe porque la reposicion de mercaderia no se puede controlar solo desde
`PART`. El sistema necesita saber a quien se compra, que pedidos se hicieron,
cuando se esperan y con que estado.

Sin proveedor, las compras quedan como texto suelto y no se puede analizar
costos, pendientes o abastecimiento.

### Fortalezas

- Centraliza los datos comerciales del proveedor.
- `tax_id` como `UK` reduce duplicados de proveedores.
- `is_active` permite bloquear proveedores que ya no se usan sin borrar
  historial.
- Se conecta naturalmente con `PURCHASE_ORDER`.

### Oportunidades de mejora

- Agregar una tabla `SUPPLIER_CONTACT` si un proveedor tiene varios contactos.
- Registrar condiciones comerciales: plazo de pago, tiempo de entrega, moneda o
  politica de garantia.
- Reemplazar `is_active` por un estado mas expresivo si se requiere controlar
  proveedores suspendidos, preferentes o bloqueados.
- Crear `SUPPLIER_PART` si se quiere saber que proveedor vende que repuesto, con
  codigo propio, costo y disponibilidad.

### Relaciones

- `SUPPLIER ||--o{ PURCHASE_ORDER`: un proveedor puede recibir muchas ordenes de
  compra.
- `PURCHASE_ORDER.supplier_id` apunta a `SUPPLIER.supplier_id`.
- Cardinalidad: un proveedor puede no tener compras registradas aun; cada orden
  de compra debe pertenecer a un proveedor.

## `PURCHASE_ORDER`

### Descripcion

`PURCHASE_ORDER` representa la cabecera de una orden de compra enviada a un
proveedor. Guarda proveedor, fecha de pedido, fecha esperada, estado y total.

No guarda cada repuesto comprado. Eso corresponde a `PURCHASE_ORDER_ITEM`.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `purchase_order_id` | Identificador tecnico de la orden de compra. | Permite referenciar el pedido completo. | Estable para lineas y recepciones futuras. | Usar numero comercial separado si se requiere. | `PK`; referenciado por `PURCHASE_ORDER_ITEM.purchase_order_id`. |
| `supplier_id` | Proveedor al que se realiza la compra. | Toda compra debe tener origen comercial. | Conecta compras con proveedores. | Validar que el proveedor este activo si se crean nuevas compras. | `FK` hacia `SUPPLIER.supplier_id`. |
| `order_date` | Fecha de emision de la orden. | Permite controlar tiempos de reposicion. | Base para reportes de compras. | Agregar hora si el flujo lo exige. | Base temporal del pedido. |
| `expected_date` | Fecha esperada de entrega. | Ayuda a seguir compras pendientes. | Permite detectar retrasos. | Permitir nulo si el proveedor no confirma fecha. | Depende de condiciones del proveedor. |
| `status` | Estado de la orden de compra. | Indica si esta borrador, enviada, parcial, recibida o cancelada. | Controla ciclo de compra. | Catalogar estados para evitar texto inconsistente. | Afecta si se permite recibir mercaderia. |
| `total_amount` | Total estimado o confirmado de la compra. | Permite controlar costo de reposicion. | Resume valor de la orden. | Validar contra suma de `PURCHASE_ORDER_ITEM`. | Depende de cantidades y `unit_cost` de las lineas. |

### Justificacion

Existe porque la reposicion de stock es un proceso propio: se identifica stock
bajo, se selecciona proveedor, se piden repuestos, se espera entrega y se
actualiza inventario.

Sin orden de compra, el negocio no puede controlar pedidos pendientes, costos ni
abastecimiento.

### Fortalezas

- Separa proveedor, fechas, estado y total de los detalles comprados.
- Permite consultar compras pendientes, recibidas o canceladas.
- Se conecta con `SUPPLIER` para analizar abastecimiento.
- Permite agrupar varias lineas de repuestos en una sola compra.

### Oportunidades de mejora

- Definir estados: `draft`, `sent`, `partial`, `received`, `cancelled`.
- Agregar responsable de compra si se modelan usuarios.
- Separar recepcion real en `PURCHASE_RECEIPT` y `PURCHASE_RECEIPT_ITEM`.
- Agregar moneda, condiciones de pago o numero de factura del proveedor si el
  alcance lo requiere.

### Relaciones

- `PURCHASE_ORDER.supplier_id` apunta a `SUPPLIER.supplier_id`.
- `SUPPLIER ||--o{ PURCHASE_ORDER`: un proveedor puede tener muchas ordenes de
  compra.
- `PURCHASE_ORDER ||--|{ PURCHASE_ORDER_ITEM`: una orden de compra debe tener
  una o mas lineas.

## `PURCHASE_ORDER_ITEM`

### Descripcion

`PURCHASE_ORDER_ITEM` representa una linea dentro de una orden de compra.
Registra que repuesto se pidio, que cantidad se ordeno, que cantidad se recibio
y cual fue el costo unitario.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `purchase_order_item_id` | Identificador tecnico de la linea de compra. | Permite controlar cada repuesto pedido. | Facilita recepciones parciales y comparaciones. | Mantener surrogate key para futuras recepciones. | `PK`. |
| `purchase_order_id` | Orden de compra a la que pertenece la linea. | Todo detalle debe pertenecer a una compra. | Protege estructura cabecera-detalle. | Debe ser obligatorio. | `FK` hacia `PURCHASE_ORDER.purchase_order_id`. |
| `part_id` | Repuesto solicitado al proveedor. | Conecta compras con catalogo. | Evita compras como texto libre. | Validar que el repuesto este comprable/activo. | `FK` hacia `PART.part_id`. |
| `quantity_ordered` | Cantidad solicitada al proveedor. | Define la necesidad de reposicion. | Permite comparar pedido contra recepcion. | Validar que sea mayor que cero. | Se compara con `quantity_received`. |
| `quantity_received` | Cantidad recibida hasta el momento. | Controla si la compra esta pendiente, parcial o completa. | Simplifica recepciones en el ERD compacto. | Para trazabilidad seria, mover recepciones a `PURCHASE_RECEIPT_ITEM`. | Debe ser coherente con `quantity_ordered`; afecta stock logicamente. |
| `unit_cost` | Costo unitario de esa compra. | Guarda costo historico del proveedor. | No depende del costo actual en `PART.purchase_cost`. | Validar que sea mayor o igual a cero y manejar moneda si aplica. | Base para margen historico y `PURCHASE_ORDER.total_amount`. |

### Justificacion

Existe porque una compra puede incluir varios repuestos. Tambien permite guardar
el costo historico de esa compra, que no debe depender del costo actual en
`PART`.

Si no existe detalle de compra, no se puede saber que productos componen cada
pedido ni comparar cantidades pedidas contra recibidas.

### Fortalezas

- Permite multiples repuestos por orden de compra.
- Guarda `unit_cost` historico, importante para margen y analisis de costos.
- `quantity_ordered` y `quantity_received` permiten controlar recepciones
  parciales de forma compacta.
- Conecta compras con el catalogo de `PART`.

### Oportunidades de mejora

- Validar que `quantity_ordered` sea mayor que cero.
- Validar que `quantity_received` no sea negativa y no supere lo pedido, salvo
  que el negocio permita sobreentregas.
- La recepcion real deberia modelarse con `PURCHASE_RECEIPT` si se quiere mayor
  trazabilidad.
- Registrar ubicacion de ingreso si la compra actualiza stock en diferentes
  almacenes.

### Relaciones

- `PURCHASE_ORDER_ITEM.purchase_order_id` apunta a
  `PURCHASE_ORDER.purchase_order_id`.
- `PURCHASE_ORDER_ITEM.part_id` apunta a `PART.part_id`.
- `PURCHASE_ORDER ||--|{ PURCHASE_ORDER_ITEM`: una compra debe tener una o mas
  lineas.
- `PART ||--o{ PURCHASE_ORDER_ITEM`: un repuesto puede comprarse muchas veces.

## `RETURN_ORDER`

### Descripcion

`RETURN_ORDER` representa la cabecera de una devolucion o garantia. Guarda la
venta original, fecha de devolucion, motivo, resolucion y estado.

No detalla cada repuesto devuelto. Eso corresponde a `RETURN_ORDER_ITEM`.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `return_order_id` | Identificador tecnico de la devolucion. | Permite referenciar una solicitud o proceso de devolucion. | Estable para lineas devueltas. | Usar numero visible separado si atencion al cliente lo requiere. | `PK`; referenciado por `RETURN_ORDER_ITEM.return_order_id`. |
| `sales_order_id` | Venta original asociada a la devolucion. | Toda devolucion debe validarse contra una venta real. | Evita devoluciones sin respaldo. | Debe ser obligatorio. | `FK` hacia `SALES_ORDER.sales_order_id`. |
| `return_date` | Fecha de la devolucion o solicitud. | Permite validar plazos de garantia y reportes. | Conecta devolucion con calendario comercial. | Agregar hora o fecha de resolucion si el proceso lo requiere. | Se compara logicamente con `SALES_ORDER.order_date` y garantia. |
| `reason` | Motivo de la devolucion. | Explica por que el cliente devuelve o reclama. | Ayuda a detectar problemas de producto, venta o compatibilidad. | Normalizar en catalogo de motivos si se reporta frecuentemente. | Depende del proceso de garantia/devolucion. |
| `resolution` | Decision tomada sobre la devolucion. | Registra si hubo cambio, reembolso, rechazo o reparacion. | Documenta resultado del caso. | Convertir en catalogo o separar resolucion de observaciones. | Afecta pagos, stock y cierre del reclamo. |
| `status` | Estado del proceso de devolucion. | Indica si esta solicitada, aprobada, rechazada o completada. | Controla flujo antes de reembolsar o reingresar stock. | Controlar valores con `CHECK` o tabla catalogo. | Afecta si se procesan `RETURN_ORDER_ITEM`. |

### Justificacion

Existe porque una devolucion seria debe nacer de una venta real. El negocio no
debe aceptar devoluciones "a memoria" sin saber que se vendio, cuando se vendio
y bajo que condiciones.

Esta tabla permite controlar garantias, reclamos, cambios y devoluciones con
trazabilidad.

### Fortalezas

- Obliga a relacionar la devolucion con una venta original.
- Permite registrar motivo, resolucion y estado.
- Soporta varias devoluciones asociadas a una misma venta si el negocio lo
  permite.
- Separa la cabecera de la devolucion de sus lineas.

### Oportunidades de mejora

- Definir estados: `requested`, `approved`, `rejected`, `completed`.
- Agregar responsable que aprobo o rechazo la devolucion.
- Separar motivo en catalogo si se quieren reportes consistentes.
- Agregar evidencias o inspeccion fisica si garantia requiere fotos,
  diagnostico o condicion del producto.

### Relaciones

- `RETURN_ORDER.sales_order_id` apunta a `SALES_ORDER.sales_order_id`.
- `SALES_ORDER ||--o{ RETURN_ORDER`: una venta puede tener cero o muchas
  devoluciones.
- `RETURN_ORDER ||--|{ RETURN_ORDER_ITEM`: una devolucion debe tener una o mas
  lineas.

## `RETURN_ORDER_ITEM`

### Descripcion

`RETURN_ORDER_ITEM` representa el detalle de un repuesto devuelto. Se conecta
con una linea vendida real (`SALES_ORDER_ITEM`), registra cantidad, monto a
reembolsar y si el producto puede volver a stock mediante `restock_allowed`.

### Atributos

| Atributo | Descripcion | Justificacion | Fortalezas | Oportunidades de mejora | Relacion/dependencia |
| --- | --- | --- | --- | --- | --- |
| `return_order_item_id` | Identificador tecnico de la linea devuelta. | Permite controlar cada repuesto devuelto. | Necesario para devoluciones parciales. | Mantener surrogate key para auditoria. | `PK`. |
| `return_order_id` | Devolucion a la que pertenece la linea. | Todo detalle debe pertenecer a una cabecera de devolucion. | Protege estructura cabecera-detalle. | Debe ser obligatorio. | `FK` hacia `RETURN_ORDER.return_order_id`. |
| `sales_order_item_id` | Linea de venta original que se devuelve. | Permite validar el producto y cantidad vendidos. | Evita devoluciones inventadas. | Controlar que no se devuelva mas de lo vendido. | `FK` hacia `SALES_ORDER_ITEM.sales_order_item_id`. |
| `quantity` | Cantidad devuelta. | Permite devoluciones parciales o totales. | Da precision al reembolso y al posible reingreso a stock. | Validar que sea mayor que cero y que acumulado no exceda venta original. | Se compara con `SALES_ORDER_ITEM.quantity`. |
| `refund_amount` | Monto a devolver al cliente. | Registra el impacto economico de la devolucion. | Permite reportes de reembolsos. | Validar contra precio historico y politicas de descuento. | Depende de `SALES_ORDER_ITEM.unit_price`, descuentos y resolucion. |
| `restock_allowed` | Indica si el producto puede volver a inventario. | Diferencia devolucion comercial de reingreso fisico al stock. | Evita reingresar productos defectuosos. | Agregar condicion fisica del producto para decidir mejor. | Si es verdadero, deberia generar entrada de stock o `INVENTORY_MOVEMENT`. |

### Justificacion

Existe porque una devolucion no debe apuntar solo a la venta completa. Debe
apuntar a la linea exacta que se vendio. Esa precision permite validar que no se
devuelva mas de lo vendido y que el reembolso corresponda al producto correcto.

Sin esta tabla, la devolucion queda como comentario y no protege reglas del
negocio.

### Fortalezas

- Relaciona la devolucion con la linea vendida exacta.
- Permite devoluciones parciales por cantidad.
- `refund_amount` permite registrar el monto real devuelto.
- `restock_allowed` separa devolucion comercial de reingreso fisico al
  inventario.

### Oportunidades de mejora

- Validar que `quantity` sea mayor que cero.
- Validar que la suma devuelta no exceda `SALES_ORDER_ITEM.quantity`.
- Agregar condicion del producto: sellado, usado, danado, defectuoso o apto
  para reventa.
- Si se agrega `INVENTORY_MOVEMENT`, una devolucion aprobada y reingresable
  deberia generar un movimiento de entrada al stock.

### Relaciones

- `RETURN_ORDER_ITEM.return_order_id` apunta a
  `RETURN_ORDER.return_order_id`.
- `RETURN_ORDER_ITEM.sales_order_item_id` apunta a
  `SALES_ORDER_ITEM.sales_order_item_id`.
- `RETURN_ORDER ||--|{ RETURN_ORDER_ITEM`: una devolucion debe tener una o mas
  lineas.
- `SALES_ORDER_ITEM ||--o{ RETURN_ORDER_ITEM`: una linea vendida puede tener
  cero o muchas devoluciones parciales.
## Cierre para defensa
La defensa del modelo no debe sonar como "hice tablas porque el diagrama las
tiene". Tiene que sonar asi:

1. El negocio vende repuestos, no textos sueltos. Por eso existe `PART`.
2. El repuesto debe servir para el vehiculo. Por eso existe
   `PART_COMPATIBILITY`.
3. El cliente debe tener historial. Por eso existen `PERSON`, `CUSTOMER` y
   `SALES_ORDER`.
4. La venta puede tener varias lineas. Por eso existe `SALES_ORDER_ITEM`.
5. Cobrar no es lo mismo que vender. Por eso existe `PAYMENT`.
6. Reponer stock es otro proceso. Por eso existen `SUPPLIER`,
   `PURCHASE_ORDER` y `PURCHASE_ORDER_ITEM`.
7. Devolver no es escribir una nota. Por eso existen `RETURN_ORDER` y
   `RETURN_ORDER_ITEM`.
8. El stock actual sirve, pero no basta para auditoria. Por eso
   `INVENTORY_STOCK` es correcto para el ERD compacto, y
   `INVENTORY_MOVEMENT` seria la mejora seria.

Si puedes explicar cada tabla desde un proceso real, una clave primaria, una
clave foranea y una cardinalidad, estas defendiendo un modelo relacional. Si
solo recitas nombres, estas memorizando una planilla con apariencia de base de
datos.
