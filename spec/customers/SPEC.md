# SPEC — Clientes

Modulo de gestion de clientes (RF-01) implementado como pantalla unica Flask
con alta en modal, busqueda por texto, edicion en pantalla completa y borrado
fisico en cascada, respaldado por las tablas `PERSON` y `CUSTOMER` y por el
modulo `customer_crud`.

> **Mockup de diseno:** No existe un mockup dedicado en `.cszv/mockups` para
> este modulo. La pantalla real es la unica referencia visual. Si en el
> futuro se quiere alinear la UI con un diseno academico/mockup, se debera
> crear primero el mockup como tarea separada y recien despues actualizar
> este SPEC.
>
> Verificacion realizada: `.cszv/mockups/` solo contiene
> `dashboard_mockup.html/.png`, `inventory_mockup.html/.png` y
> `sales_mockup.html/.png`. No hay `customers_mockup.*`.

## Objetivo del modulo

Resolver el problema central del negocio descrito en
[`docs/analysis/processes.md`](../../docs/analysis/processes.md) y
[`docs/analysis/procedures.md`](../../docs/analysis/procedures.md):
evitar clientes duplicados o incompletos y permitir que Ventas ubique
rapidamente a un cliente por documento, nombre, NIT o razon social, ya sea
para registrar una venta, cobrar un pago o consultar su historial.

Esto cubre el requerimiento **RF-01** definido en
[`docs/analysis/requirements.md`](../../docs/analysis/requirements.md):
"Registrar clientes y sus datos de contacto/facturacion." Las entidades
relacionadas son `PERSON` y `CUSTOMER`.

Los actores que interactuan con este modulo, segun
[`docs/analysis/actors.md`](../../docs/analysis/actors.md), son:

- **Vendedor tecnico**: registra y consulta clientes.
- **Cajero / Responsable de facturacion**: consulta datos de facturacion
  (`billing_name`, `tax_id`).
- **Cliente externo**: aporta sus datos personales y fiscales.

## Estado actual reverse-engineered

El modulo existe, esta implementado y se ejecuta desde
`src/zarvent_repuestos/web/app.py` y `src/zarvent_repuestos/crud/customer_crud.py`.

### Rutas Flask (`src/zarvent_repuestos/web/app.py:314-426`)

| Metodo | Ruta | Funcion | Descripcion |
| --- | --- | --- | --- |
| `GET` | `/customers` | `customers()` | Lista clientes con filtro opcional `?search=...`. |
| `POST` | `/customers` | `customers()` | Crea un cliente nuevo (mismo endpoint, discriminador `request.method`). |
| `GET` | `/customers/<int:customer_id>/edit` | `edit_customer()` | Carga el cliente en modo edicion. |
| `POST` | `/customers/<int:customer_id>/edit` | `edit_customer()` | Persiste los cambios. |
| `POST` | `/customers/<int:customer_id>/delete` | `delete_customer()` | Borrado fisico con pre-chequeo de ventas. |

Todas las rutas usan el decorador `@login_required` (definido en el mismo
modulo `app.py`).

### Template

Unico template Jinja2:
`src/zarvent_repuestos/web/templates/customers.html`.

- Renderiza la tabla con el listado y la barra de busqueda siempre visibles.
- Contiene el modal `add-customer-modal` (overlay) con `toggleModal()` en
  `{% block extra_js %}`.
- Cuando la vista recibe la variable `editing`, pinta arriba de la tabla
  un panel a pantalla completa con el formulario de edicion (`POST` a
  `/customers/<id>/edit`). **No es una vista separada**: la UI de edicion
  se monta sobre el mismo template que el listado.
- Las acciones de borrado en cada fila usan `onsubmit="return confirm('...')"`
  (confirmacion nativa de JS, no un modal propio).

### Funciones CRUD (`src/zarvent_repuestos/crud/customer_crud.py`)

| Funcion | Firma | Rol |
| --- | --- | --- |
| `crear_cliente(first_name, last_name, identity_number, billing_name=None, tax_id=None, phone=None, email=None, address=None) -> bool` | Insert | Inserta `person` y luego `customer` en una sola transaccion. Devuelve `False` y hace rollback ante cualquier `mysql.connector.Error`. |
| `listar_clientes(search=None) -> list[dict]` | Read (listado) | `SELECT` con `JOIN customer c ON person p`. Aplica `LIKE %s` sobre `first_name`, `last_name`, `identity_number`, `tax_id` y `billing_name`. Ordena por `last_name, first_name`. |
| `buscar_cliente_por_doc(identity_number) -> dict | None` | Read (busqueda exacta) | Busqueda puntual por `person.identity_number` (uso interno, no expuesto en rutas). |
| `get_customer(customer_id) -> dict | None` | Read (uno) | Recupera un cliente por `customer_id` con sus datos de `person`. |
| `update_customer(customer_id, first_name, last_name, identity_number, billing_name, tax_id, phone=None, email=None, address=None) -> bool` | Update | Hace `SELECT person_id FROM customer WHERE customer_id`, luego `UPDATE person` y `UPDATE customer` en una sola transaccion. |
| `delete_customer(customer_id) -> bool` | Delete | Pre-chequea ventas con `_count_customer_sales`; si hay, lanza `CustomerHasSalesError`. Caso contrario, `DELETE FROM customer` (la fila `person` se borra por `ON DELETE CASCADE`). |
| `_count_customer_sales(customer_id) -> int` | Auxiliar | `SELECT COUNT(*) FROM sales_order WHERE customer_id = %s`. |

### Excepcion de dominio

```python
class CustomerHasSalesError(Exception):
    """Raised when a customer cannot be deleted because sales orders protect them."""
    customer_id: int
    sales_count: int
```

Se lanza desde `delete_customer` y se traduce en la ruta a un `flash(..., "error")`
con el mensaje "No se puede eliminar el cliente #N: tiene K venta(s) registrada(s).".

### Tablas involucradas

Esquema real en `src/zarvent_repuestos/database/init_db.py:60-82`:

```sql
CREATE TABLE IF NOT EXISTS person (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    identity_number VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(50),
    email VARCHAR(100),
    address VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT UNIQUE NOT NULL,
    billing_name VARCHAR(150),
    tax_id VARCHAR(50),
    FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

Relacion `PERSON 1 .. 0..1 CUSTOMER` mediante `customer.person_id`, declarada
tambien en [`docs/database/erd.md`](../../docs/database/erd.md) como
`PERSON ||--o| CUSTOMER : identifica` y en
[`docs/database/db_explanation.md`](../../docs/database/db_explanation.md)
(tabla "Relaciones clave").

## Contrato funcional

### Flujo de alta (modal)

1. El usuario hace clic en **Nuevo Cliente** (boton visible solo cuando
   `not editing`).
2. Se abre el modal `add-customer-modal` (`toggleModal('add-customer-modal', true)`).
3. El usuario completa nombre, apellido, documento (obligatorios) y los
   datos opcionales (`phone`, `email`, `address`, `billing_name`, `tax_id`).
4. Al hacer **Guardar Cliente** se hace `POST` a `/customers`.
5. La ruta valida campos obligatorios. Si faltan, `flash("Nombre, apellido y
   documento son obligatorios.", "error")` y redirect a `/customers`.
6. Llama a `customer_crud.crear_cliente(...)`. Si retorna `True`:
   `flash("Cliente '<nombre> <apellido>' creado con éxito.", "success")`.
   Si retorna `False` (por `IntegrityError`, `UNIQUE` duplicado u otro
   `mysql.connector.Error`): `flash("No se pudo crear el cliente (revisa
   datos duplicados o el log del servidor).", "error")`.
7. Redirect a `/customers` para refrescar el listado.

### Flujo de busqueda por texto

1. La barra superior envia `GET /customers?search=<texto>`.
2. La ruta pasa `search` a `listar_clientes(search=...)`.
3. La consulta SQL agrega `LIKE %<texto>%` a `first_name`, `last_name`,
   `identity_number`, `tax_id` y `billing_name`.
4. La tabla re-renderiza solo con las coincidencias.
5. El boton **Limpiar** aparece solo cuando `search_val` no es vacio y
   apunta a `/customers` (sin query string).

> La busqueda es parcial (`LIKE %texto%`), case-sensitive segun la
> collation `utf8mb4_unicode_ci` configurada en la base, y no pagina
> resultados.

### Flujo de edicion (pantalla completa, no modal)

1. En la tabla, el icono de **edit** apunta a
   `GET /customers/<id>/edit`.
2. La ruta llama a `get_customer(id)`. Si retorna `None`: `abort(404, "Cliente
   no encontrado")`.
3. Renderiza el mismo template `customers.html` con la variable `editing`
   poblada y `customers` recargado con `listar_clientes()` (sin filtro).
4. Sobre la tabla se pinta el panel **Editar Cliente #<id>** con el
   formulario completo.
5. Al **Guardar Cambios** se hace `POST` a la misma ruta.
6. La ruta revalida obligatorios. Si faltan, redirect a la propia pantalla
   de edicion con flash de error.
7. Si `update_customer(...)` retorna `True`: `flash("Cliente actualizado con
   éxito.", "success")` y redirect a `/customers`. Si retorna `False`:
   `flash("No se pudo actualizar el cliente.", "error")` y redirect a la
   pantalla de edicion.

### Flujo de borrado

1. En la tabla, el icono de **delete** envia un formulario `POST` a
   `/customers/<id>/delete`.
2. Antes de submit, JS nativo pregunta:
   `confirm('¿Eliminar cliente? Si tiene ventas, la operación será rechazada.')`.
3. La ruta llama a `delete_customer(id)`. Esta funcion:
   - Cuenta ventas con `_count_customer_sales(id)`.
   - Si el conteo es `> 0`, lanza `CustomerHasSalesError(id, count)`.
   - Caso contrario, ejecuta `DELETE FROM customer WHERE customer_id = %s`.
4. Si se lanza `CustomerHasSalesError`, la ruta captura la excepcion y hace
   `flash(str(err), "error")`. Redirect a `/customers`.
5. Si retorna `True`: `flash("Cliente eliminado con éxito.", "success")`.
6. Si retorna `False` (otro error de DB): `flash("No se pudo eliminar el
   cliente.", "error")`.

### Validaciones

- **Campos obligatorios**: `first_name`, `last_name`, `identity_number`.
  Se validan con `request.form.get(...).strip()` y verificacion de no
  vacio. Si fallan, redirect con flash de error. El template ademas usa
  `required` en el HTML del modal y del formulario de edicion.
- **Formato libre**: `phone`, `email`, `address`, `billing_name`, `tax_id`
  se aceptan como `string` libre. La columna `email` en el template usa
  `type="email"` para que el navegador aplique validacion HTML basica,
  pero el backend no valida formato de email ni de telefono.
- **Unicidad**: `person.identity_number` es `UNIQUE NOT NULL` en la base.
  Un duplicado rompe `crear_cliente`/`update_customer` con un
  `mysql.connector.Error`, que se traduce a flash de error.

### Mensajes flash

Todos los mensajes usan `flash(category, message)` de Flask:

| Categoria | Origen | Mensaje |
| --- | --- | --- |
| `error` | Alta / Edicion | `Nombre, apellido y documento son obligatorios.` |
| `error` | Alta | `Error al crear cliente: <excepcion>` |
| `error` | Alta | `No se pudo crear el cliente (revisa datos duplicados o el log del servidor).` |
| `success` | Alta | `Cliente '<nombre> <apellido>' creado con éxito.` |
| `error` | Edicion | `No se pudo actualizar el cliente.` |
| `success` | Edicion | `Cliente actualizado con éxito.` |
| `error` | Borrado | `No se puede eliminar el cliente #<id>: tiene <n> venta(s) registrada(s).` |
| `error` | Borrado | `No se pudo eliminar el cliente.` |
| `success` | Borrado | `Cliente eliminado con éxito.` |

## Contrato de datos

### Tablas y relacion

La identidad de una persona se guarda en `PERSON` y su rol comercial en
`CUSTOMER`. La relacion es **1 a 0..1**: una persona puede existir solo en
`PERSON` (contacto sin compras) o extenderse a `CUSTOMER` (persona que
compra). El enlace es `customer.person_id` con `UNIQUE NOT NULL` y
`ON DELETE CASCADE`.

```text
PERSON (1) ──< person_id (UNIQUE, FK) >── (0..1) CUSTOMER
```

Ambas tablas usan `ENGINE=InnoDB`, lo que permite `FOREIGN KEY` real y
transacciones.

### Operaciones CRUD y transacciones

| Operacion | SQL que ejecuta | Transaccion |
| --- | --- | --- |
| `crear_cliente` | `INSERT INTO person (...)` seguido de `INSERT INTO customer (person_id, billing_name, tax_id)` | Si. Un solo `commit`. Si falla cualquiera de los dos `INSERT`, se hace `rollback` y la funcion retorna `False`. |
| `listar_clientes` | `SELECT ... FROM customer c JOIN person p ON c.person_id = p.person_id WHERE ...` con `LIKE` opcional. | No (solo lectura). |
| `buscar_cliente_por_doc` | `SELECT ... WHERE p.identity_number = %s` | No (solo lectura). |
| `get_customer` | `SELECT ... WHERE c.customer_id = %s` | No (solo lectura). |
| `update_customer` | `SELECT person_id FROM customer WHERE customer_id`, luego `UPDATE person WHERE person_id`, luego `UPDATE customer WHERE customer_id`. | Si. Un solo `commit`. Si falla, `rollback` y retorna `False`. |
| `delete_customer` | `_count_customer_sales` (pre-check), luego `DELETE FROM customer WHERE customer_id`. | El `DELETE` se hace dentro de un `commit`. La fila `person` se borra por `ON DELETE CASCADE` en una operacion separada por el motor InnoDB. |

### Valores por defecto

Definidos en `customer_crud.py:66-67` y replicados en la ruta
`edit_customer` (`app.py:388-389`) por si el navegador no envia el campo:

- `billing_name`: si llega vacio, se guarda `f"{first_name} {last_name}"`.
- `tax_id`: si llega vacio, se guarda el mismo valor de
  `identity_number` (CI usado como NIT por defecto).

### Reglas de integridad relevantes

- `person.identity_number` es `UNIQUE NOT NULL`. No puede haber dos
  clientes con el mismo documento.
- `customer.person_id` es `UNIQUE NOT NULL`. No puede haber dos filas en
  `customer` apuntando a la misma `person`. Esto refuerza la cardinalidad
  1..0..1 del ERD a nivel fisico.
- `customer.person_id REFERENCES person(person_id) ON DELETE CASCADE`:
  borrar un `customer` borra la `person` asociada. Esto hace que el borrado
  sea fisico, no soft-delete, y arrastra datos que podrian compartirse en
  teoria (hoy no se comparten, pero la cascada no distingue).
- `sales_order.customer_id REFERENCES customer(customer_id) ON DELETE RESTRICT`:
  la base de datos impide borrar un cliente con ventas. Esta es la red de
  seguridad final; la aplicacion la respeta con un pre-check
  (`_count_customer_sales`) para dar un mensaje claro.

### Side effects observables

- Crear un cliente inserta **dos filas** (`person` + `customer`) y devuelve
  el `customer_id` implicitamente via el orden de insercion.
- Editar un cliente puede tocar **dos filas** (`person` + `customer`).
- Borrar un cliente sin ventas borra **dos filas** (`customer` y, en
  cascada, `person`).
- Borrar un cliente con ventas **no** modifica datos: el `DELETE` es
  abortado por la aplicacion (pre-check) o por la base de datos
  (`ON DELETE RESTRICT`).

### Manejo del error 1451 (concurrencia en borrado)

`delete_customer` en `customer_crud.py:212-241` hace dos cosas:

1. **Pre-check**: cuenta ventas con `_count_customer_sales` y rechaza el
   borrado si el conteo es `> 0`. Esto da un mensaje claro y evita el
   error crudo de MySQL.
2. **Race condition**: existe una ventana entre el `COUNT(*)` y el
   `DELETE`. Si en esa ventana otro proceso inserta una `sales_order` para
   ese cliente, MySQL rechaza el `DELETE` con `errno 1451` (error
   `ER_ROW_IS_REFERENCED_2`, equivalente a `ON DELETE RESTRICT`).
3. El codigo detecta `errno == 1451`, vuelve a contar ventas
   (`_count_customer_sales`) y lanza `CustomerHasSalesError` con el conteo
   actualizado. Asi, aunque falle el pre-check, el usuario recibe un
   mensaje honesto en vez de un error generico de MySQL.

Esto vale la pena defenderlo: el proyecto reconoce la condicion de carrera
y la resuelve sin pedirle al usuario que reintente "a ciegas".

## Trazabilidad SDD

Matriz entre el analisis, la base de datos, el codigo actual y el estado
del modulo. Estados posibles: `implementado`, `parcial`, `faltante`,
`fuera de alcance`.

| Tema | docs/analysis | docs/database | Codigo actual | Estado |
| --- | --- | --- | --- | --- |
| Identidad separada del rol comercial | `processes.md` y `procedures.md` mencionan datos personales y datos de facturacion por separado. | `erd.md` declara `PERSON \|\|--o\| CUSTOMER`. | Tablas `person` + `customer` con `person_id` FK unico. | implementado |
| Registro de cliente (RF-01) | `requirements.md` RF-01. | `db_explanation.md` explica ambas tablas. | Ruta `POST /customers` + `crear_cliente()` con transaccion. | implementado |
| Busqueda por documento | `procedures.md` paso 2: "busca si ya existe por documento, nombre o telefono". | n/e | `listar_clientes(search=...)` cubre nombre, apellido, documento, NIT y razon social. Telefono no. | parcial |
| Busqueda por telefono | `procedures.md` paso 2. | n/e | No incluida en el `LIKE` del SQL. | faltante |
| Datos de facturacion (Razon Social y NIT) | `actors.md` describe al Cajero / Responsable de facturacion. | `db_explanation.md` describe `billing_name` y `tax_id`. | Columnas presentes; `billing_name` y `tax_id` opcionales con defaults. | implementado |
| Valores por defecto (`billing_name`, `tax_id`) | n/e | n/e | Aplicados en `crear_cliente` y replicados en la ruta de edicion. | implementado |
| Cardinalidad 1..0..1 reforzada en fisico | n/e | `db_explanation.md` declara 1..0..1. | `customer.person_id` `UNIQUE NOT NULL`. | implementado |
| Borrado bloqueado si hay ventas | `processes.md` describe "ventas sin detalle confiable" como problema a evitar. | `ON DELETE RESTRICT` en `sales_order.customer_id`. | `delete_customer` con pre-check + `CustomerHasSalesError` + manejo de `errno 1451`. | implementado |
| Borrado fisico en cascada | n/e | `ON DELETE CASCADE` en `customer.person_id`. | `DELETE FROM customer`; la `person` se borra por cascada. | implementado |
| Soft-delete / borrado logico | n/e | n/e | No existe. | fuera de alcance |
| Historial de cambios (auditoria) | `processes.md` menciona "auditoria futura". | `db_explanation.md` lo lista como limitacion. | No existe. | fuera de alcance |
| Validacion de formato de email | n/e | n/e | `type="email"` solo en HTML; backend no valida. | parcial |
| Validacion de formato de telefono | n/e | n/e | No existe. | faltante |
| Vista de edicion separada del listado | n/e | n/e | Edita en el mismo template `customers.html` con `{% if editing %}`. | parcial |
| Paginacion del listado | n/e | n/e | No existe; trae todos los clientes. | faltante |
| Mockup academico de la pantalla | n/e | n/e | No existe `.cszv/mockups/customers_mockup.*`. | faltante |

## Criterios de aceptacion

### Pruebas automatizadas

- `tests/test_customer_crud.py` cubre con `unittest` y `MagicMock`:
  - `CrearClienteTest.test_happy_path_inserts_person_and_customer_and_commits`:
    verifica que `crear_cliente` ejecuta ambos `INSERT` y hace `commit`.
  - `CrearClienteTest.test_returns_false_and_rolls_back_when_db_raises_duplicate`:
    simula `mysql.connector.Error` y exige `rollback` y retorno `False`.
  - `ListarClientesTest.test_returns_preset_rows_when_no_search_is_provided`:
    valida que `listar_clientes()` sin `search` retorna las filas tal cual
    el cursor las entrega.
  - `GetCustomerTest.test_returns_row_when_customer_exists` y
    `test_returns_none_when_customer_does_not_exist`: contrato del read
    by id.
  - `UpdateCustomerTest.test_happy_path_issues_person_and_customer_updates`:
    exige ambos `UPDATE` y un solo `commit`.
  - `DeleteCustomerTest.test_raises_customer_has_sales_error_when_sales_count_is_positive`:
    verifica que con `sales_count = 4` se lanza `CustomerHasSalesError`,
    sin siquiera abrir la conexion.
- Comando esperado: `uv run pytest tests/test_customer_crud.py` o
  `uv run python -m unittest tests.test_customer_crud`.

### Pruebas manuales (humano en el navegador)

1. Login con `admin / admin123`. Ir a `/customers`. Ver tabla con los
   cuatro clientes demo.
2. Click en **Nuevo Cliente**. Llenar `first_name`, `last_name`,
   `identity_number`. Dejar `billing_name` y `tax_id` vacios. **Guardar
   Cliente**. Verificar en la tabla que aparece el cliente y que
   "Facturacion" muestra `<nombre> <apellido>` y "NIT" muestra el mismo
   numero del documento. Flash verde arriba.
3. Repetir con el mismo `identity_number`. Verificar flash rojo y que el
   cliente **no** aparece dos veces (UNIQUE en `person.identity_number`).
4. En la barra de busqueda, escribir el apellido. Verificar que la tabla
   filtra y aparece un boton **Limpiar**.
5. Click en el icono de **edit** del primer cliente. Verificar que arriba
   de la tabla aparece el panel **Editar Cliente #<id>** con los campos
   prellenados. Cambiar el telefono. **Guardar Cambios**. Verificar flash
   verde y telefono actualizado en la fila.
6. Intentar editar y dejar `first_name` vacio (borrar valor y enviar).
   Verificar flash rojo "Nombre, apellido y documento son obligatorios."
   y que la pantalla se mantiene en modo edicion.
7. Click en **delete** de un cliente sin ventas. Aceptar el `confirm()`
   de JS. Verificar flash verde y que la fila desaparece.
8. Click en **delete** de un cliente que tenga al menos una venta (en el
   seed: `Elena Rostova` tiene ventas). Aceptar el `confirm()`. Verificar
   flash rojo con el texto "No se puede eliminar el cliente #N: tiene K
   venta(s) registrada(s)." y que el cliente sigue visible.
9. `GET /customers/9999/edit` (id inexistente). Verificar respuesta 404
   con el texto "Cliente no encontrado".

### Criterios de integridad verificables

- `SHOW CREATE TABLE person;` debe incluir
  `UNIQUE KEY identity_number (identity_number)`.
- `SHOW CREATE TABLE customer;` debe incluir
  `UNIQUE KEY person_id (person_id)` y
  `FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE`.
- `SHOW CREATE TABLE sales_order;` debe incluir
  `FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT`.

## Brechas y decisiones

Diferencias entre lo propuesto en el analisis y lo realmente implementado,
o mejoras que se dejaron fuera por alcance academico:

- **Sin validacion de formato de email en backend**: el template usa
  `type="email"` y el navegador puede quejarse, pero `customer_crud` no
  verifica `@` ni dominio. Acepta cualquier string. Tradeoff: simple y
  rapido de implementar, pero el dato basura entra a la base.
- **Sin validacion de formato de telefono**: cualquier string se guarda.
  No hay regex ni longitud minima. Esto es consistente con el resto del
  modulo: el telefono no es critico para facturar.
- **Sin soft-delete**: el borrado es fisico. `DELETE FROM customer` se
  ejecuta y la cascada borra la `person` asociada. No hay columna
  `is_active` ni `deleted_at`. Consecuencia: no se puede recuperar un
  cliente borrado por error. El analisis lo dejo como "auditoria futura"
  en `db_explanation.md`.
- **Sin historial de cambios**: no hay trigger ni tabla
  `customer_audit`. Editar un cliente sobrescribe los valores anteriores
  sin dejar rastro. Es coherente con el alcance academico: defender la
  idea, no construir la auditoria.
- **Borrado en cascada real**: borrar un cliente con cero ventas borra
  tanto la fila `customer` como la fila `person` por el
  `ON DELETE CASCADE`. Hoy `person` solo se usa para clientes, asi que
  en la practica no hay informacion compartida que se pierda, pero la
  cascada es una promesa a futuro: si manana se agrega `EMPLOYEE` que
  reutilice `person`, el `DELETE` de un cliente borraria a un empleado
  que por casualidad comparta `person_id` (no es el caso actual, pero
  hay que tenerlo presente si se extiende el modelo).
- **UI de edicion no es una vista separada**: la pantalla de edicion se
  renderiza sobre el mismo `customers.html` mediante un bloque
  `{% if editing %}`. Esto evita un segundo template pero mezcla en la
  misma URL (`/customers/<id>/edit`) la responsabilidad de mostrar el
  formulario y la de persistir. Para un junior es defendible: "es la
  misma pantalla, en modo edicion".
- **No hay paginacion**: `listar_clientes()` retorna todos los clientes
  en una sola consulta. Para 4 clientes demo no es problema, pero con
  cientos de clientes la consulta y el render se vuelven lentos.
  Mejora futura: agregar `LIMIT/OFFSET` y un paginador en el template.
- **No hay busqueda por telefono**: el `LIKE` de `listar_clientes`
  cubre `first_name`, `last_name`, `identity_number`, `tax_id` y
  `billing_name`, pero no `phone`. Esto contradice el paso 2 de
  "Registro de cliente" en `procedures.md`, que menciona busqueda por
  telefono. Es una brecha consciente: se priorizo unicidad por
  documento, no por telefono.
- **No existe mockup academico**: `.cszv/mockups/` no tiene
  `customers_mockup.*`. La pantalla real (`customers.html`) es la
  unica referencia visual. Esto se declaro al inicio del SPEC.
- **Excepcion de dominio local**: `CustomerHasSalesError` esta definida
  dentro de `customer_crud.py` en lugar de un modulo
  `crud/exceptions.py` compartido. Para este alcance es suficiente, pero
  si otros modulos (proveedores, repuestos) necesitan errores
  equivalentes, convendra centralizar.
- **Mensajes flash en espanol literal**: los strings de error viven en
  las rutas, no en un archivo de i18n. Para una sola locale (Latam
  Spanish) esta bien; para multilenguaje seria otra decision.
- **Decisiones defensibles**: el modulo prioriza simplicidad. No hay
  ORM (se usa `mysql-connector-python` directo), no hay DTO, no hay
  capa de servicio. Esto es coherente con `AGENTS.md`: "modelo
  relacional primero, no arquitectura que el equipo aun no domina".
