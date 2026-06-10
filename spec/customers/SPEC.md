# SPEC — Clientes

El modulo de Clientes es la pantalla `/customers` de Zarvent Repuestos.
Permite buscar, registrar, editar, **desactivar** y **reactivar** clientes
a partir de las tablas `person` y `customer` de MySQL, y del modulo
`customer_crud`. El borrado es **logico** (soft-delete) mediante la columna
`customer.is_active`. Cubre el requerimiento `RF-01` de
[`docs/analysis/requirements.md`](../../docs/analysis/requirements.md).

> **Mockup academico:** no existe mockup dedicado en `.cszv/mockups/`. Solo
> hay mockups para dashboard, inventory y sales. La pantalla real es la
> unica referencia visual. Si en el futuro se quiere alinear con un
> diseno academico, primero se crea el mockup y despues se actualiza este
> SPEC.

## 1. Estado actual (reverse-engineered)

### Rutas Flask (`src/zarvent_repuestos/web/app.py:314-426`)

| Metodo | Ruta | Funcion | Descripcion |
| --- | --- | --- | --- |
| `GET` | `/customers` | `customers()` | Lista clientes con filtro opcional `?search=...`. |
| `POST` | `/customers` | `customers()` | Crea un cliente nuevo (mismo endpoint, discriminador `request.method`). |
| `GET` | `/customers/<int:customer_id>/edit` | `edit_customer()` | Carga el cliente en modo edicion. |
| `POST` | `/customers/<int:customer_id>/edit` | `edit_customer()` | Persiste los cambios. |
| `POST` | `/customers/<int:customer_id>/delete` | `delete_customer()` | Borrado fisico con pre-chequeo de ventas. |

Todas las rutas usan el decorador `@login_required` (`app.py:69-77`).

### Template

Unico template Jinja2:
`src/zarvent_repuestos/web/templates/customers.html` (237 lineas).

- Renderiza la tabla con el listado y la barra de busqueda siempre
  visibles.
- Contiene el modal `add-customer-modal` (overlay) con `toggleModal()` en
  `{% block extra_js %}`.
- Cuando la vista recibe la variable `editing`, pinta arriba de la tabla
  un panel a pantalla completa con el formulario de edicion (`POST` a
  `/customers/<id>/edit`). **No es una vista separada**: la UI de edicion
  se monta sobre el mismo template que el listado.
- Las acciones de borrado en cada fila usan `onsubmit="return
  confirm('...')"` (confirmacion nativa de JS).

### Funciones CRUD (`src/zarvent_repuestos/crud/customer_crud.py`)

| Funcion | Firma | Rol |
| --- | --- | --- |
| `crear_cliente(first_name, last_name, identity_number, billing_name=None, tax_id=None, phone=None, email=None, address=None) -> bool` | Insert | Inserta `person` y `customer` en una sola transaccion. `False` + rollback ante `mysql.connector.Error`. |
| `listar_clientes(search=None) -> list[dict]` | Read | `SELECT` con `JOIN customer/person`. `LIKE` sobre `first_name`, `last_name`, `identity_number`, `tax_id`, `billing_name`. **No** filtra por `phone`. Ordena por `last_name, first_name`. |
| `buscar_cliente_por_doc(identity_number) -> dict \| None` | Read (uso interno) | Busqueda exacta por `person.identity_number`. |
| `get_customer(customer_id) -> dict \| None` | Read (uno) | Recupera un cliente por `customer_id` con sus datos de `person`. |
| `update_customer(customer_id, first_name, last_name, identity_number, billing_name, tax_id, phone=None, email=None, address=None) -> bool` | Update | `SELECT person_id` + `UPDATE person` + `UPDATE customer` en una transaccion. |
| `delete_customer(customer_id) -> bool` | Delete | Pre-chequea ventas con `_count_customer_sales`; si hay, lanza `CustomerHasSalesError`. Caso contrario, `DELETE FROM customer` (la fila `person` se borra por `ON DELETE CASCADE`). |
Las funciones `deactivate_customer` y `reactivate_customer` en `customer_crud.py` se utilizan para cambiar el estado lógico del cliente. La columna `customer.is_active` está presente en la base de datos para soportar este borrado lógico.

### Excepcion de dominio

```python
class CustomerHasSalesError(Exception):
    """Raised when a customer cannot be deleted because sales orders protect them."""
    customer_id: int
    sales_count: int
```

Se lanza desde `delete_customer` y se traduce en la ruta a un
`flash(..., "error")` con el texto `"No se puede eliminar el cliente #N:
tiene K venta(s) registrada(s)."` En el contrato v1 esta excepcion se
mantiene porque la operacion de desactivar tampoco debe romper ventas
asociadas (un cliente inactivo sigue referenciado por sus `sales_order`).

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

Relacion `PERSON 1 .. 0..1 CUSTOMER` mediante `customer.person_id`. El
analisis academico describe esta relacion en
[`docs/database/erd.md`](../../docs/database/erd.md) como
`PERSON ||--o| CUSTOMER : identifica` y en
[`docs/database/db_explanation.md`](../../docs/database/db_explanation.md).

## 2. Contrato objetivo v1

### Flujos permitidos

1. **Listar (GET `/customers`, default).** Muestra los clientes con
   `is_active = TRUE` ordenados por `apellido, nombre`.
2. **Filtrar por estado (GET `/customers?filter=...`).** Valores validos:
   `active` (default), `inactive`, `all`.
3. **Buscar (GET `/customers?search=...`).** Coincidencia parcial en
   `first_name`, `last_name`, `identity_number`, `tax_id`,
   `billing_name` y **`phone`**.
4. **Alta (POST `/customers`).** Abre el modal, completa el formulario,
   crea el cliente.
5. **Edicion (GET/POST `/customers/<id>/edit`).** Carga el cliente en
   modo edicion sobre el mismo template; persiste los cambios.
6. **Desactivar (POST `/customers/<id>/deactivate`).** Cambia
   `customer.is_active` a `FALSE`. El cliente deja de aparecer en
   `?filter=active` pero sigue contando para ventas existentes.
7. **Reactivar (POST `/customers/<id>/reactivate`).** Cambia
   `customer.is_active` a `TRUE`.

### Flujos que el contrato v1 **NO** permite

- **Borrado fisico de clientes** (`DELETE FROM customer`). La ruta
  `/customers/<id>/delete` se elimina del SPEC. La razon: un cliente con
  ventas no se puede borrar por el `ON DELETE RESTRICT` de
  `sales_order.customer_id` (`init_db.py:146`), y un cliente sin ventas
  no deberia desaparecer del historial. El soft-delete es la alternativa
  correcta.
- **Borrado en cascada de `person`**: la cascada `customer.person_id ON
  DELETE CASCADE` se mantiene en el esquema, pero el contrato v1 no la
  ejercita porque ya no se hace `DELETE FROM customer`.

### Campos del formulario POST `/customers` y `/customers/<id>/edit`

| Campo | Destino en BD | Validacion visible |
| --- | --- | --- |
| `first_name` | `person.first_name` | `required` |
| `last_name` | `person.last_name` | `required` |
| `identity_number` | `person.identity_number` | `required`, `UNIQUE` en BD |
| `phone` | `person.phone` | opcional; buscable en v1 |
| `email` | `person.email` | opcional, `type="email"` en HTML |
| `address` | `person.address` | opcional |
| `billing_name` | `customer.billing_name` | opcional; default `"{first_name} {last_name}"` si llega vacio |
| `tax_id` | `customer.tax_id` | opcional; default `identity_number` si llega vacio |

### Validaciones del lado servidor

- **Obligatorios**: `first_name`, `last_name`, `identity_number`. Si
  faltan, `flash("Nombre, apellido y documento son obligatorios.",
  "error")` y redirect a la pantalla correspondiente.
- **Unicidad**: `person.identity_number` es `UNIQUE NOT NULL`. Un
  duplicado rompe `crear_cliente`/`update_customer` con
  `mysql.connector.Error`, que se traduce a flash de error.
- **Estado valido en filtro**: `filter` debe ser uno de `active`,
  `inactive`, `all`. Cualquier otro valor se trata como `active`.
- **Estado valido al desactivar/activar**: la ruta acepta el `customer_id`
  y aplica el `UPDATE` sin pedir confirmacion adicional en el form, pero
  el template usa `onsubmit="return confirm('...')"` para que el usuario
  confirme.

### Mensajes flash

| Caso | Texto |
| --- | --- |
| Alta con campos obligatorios vacios | `"Nombre, apellido y documento son obligatorios."` |
| Exito al crear | `"Cliente '<nombre> <apellido>' creado con exito."` |
| Falla al crear (duplicado u otro) | `"No se pudo crear el cliente (revisa datos duplicados o el log del servidor)."` |
| Exito al editar | `"Cliente actualizado con exito."` |
| Falla al editar | `"No se pudo actualizar el cliente."` |
| Exito al desactivar | `"Cliente '<nombre> <apellido>' desactivado."` |
| Exito al reactivar | `"Cliente '<nombre> <apellido>' reactivado."` |
| Falla al desactivar/activar | `"No se pudo cambiar el estado del cliente."` |

`CustomerHasSalesError` ya no se lanza en el flujo de desactivar
(porque desactivar no rompe ventas). Se mantiene en `customer_crud.py`
solo por compatibilidad hacia atras, sin ruta que la dispare.

### Estados y efectos esperados

- Crear un cliente inserta dos filas (`person` + `customer`) con un solo
  `commit`. Si falla, `rollback`.
- Editar un cliente actualiza dos filas (`person` + `customer`).
- Desactivar un cliente hace un solo `UPDATE customer SET is_active =
  FALSE WHERE customer_id = %s`. No toca `person`, no toca ventas.
- Reactivar un cliente hace un solo `UPDATE customer SET is_active = TRUE
  WHERE customer_id = %s`.
- Listar `?filter=active` retorna solo clientes con `is_active = TRUE`.
  `?filter=inactive` solo `FALSE`. `?filter=all` ambos.
- Buscar aplica `LIKE %texto%` a `first_name`, `last_name`,
  `identity_number`, `tax_id`, `billing_name` y `phone` simultaneamente.

## 3. Cambios requeridos v1

### Cambios en la base de datos

| # | Cambio | Archivo | Detalle |
| --- | --- | --- | --- |
| 1 | Anadir columna `is_active BOOLEAN DEFAULT TRUE` a `customer` mediante una migracion idempotente. | `src/zarvent_repuestos/database/init_db.py` (en `crear_tablas`, despues del `CREATE TABLE IF NOT EXISTS customer`, ejecutar `ALTER TABLE customer ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;` o un `SHOW COLUMNS` + `ALTER` para MySQL 5.7/8.0) | — |

### Cambios en `customer_crud.py`

| # | Cambio | Detalle |
| --- | --- | --- |
| 2 | Anadir `deactivate_customer(customer_id) -> bool` | `UPDATE customer SET is_active = FALSE WHERE customer_id = %s`. Retorna `True` si `cursor.rowcount > 0` (o si la fila existia). |
| 3 | Anadir `reactivate_customer(customer_id) -> bool` | `UPDATE customer SET is_active = TRUE WHERE customer_id = %s`. |
| 4 | Modificar `listar_clientes(search=None, filter="active")` | Acepta `filter="active"`, `"inactive"`, `"all"`. Default `"active"`. Anade `AND c.is_active = TRUE` (o `FALSE`) segun corresponda. |
| 5 | Extender el `LIKE` de busqueda para incluir `person.phone` | Cambiar el `WHERE` en `listar_clientes` para que `p.phone LIKE %s` este dentro del OR junto a los otros cinco campos. |
| 6 | (Opcional) Marcar `delete_customer` como deprecated | No se elimina del modulo, pero deja de tener ruta Flask que lo invoque. |

### Cambios en `app.py`

| # | Cambio | Ruta | Detalle |
| --- | --- | --- | --- |
| 7 | Quitar la ruta `POST /customers/<int:customer_id>/delete` | borrar `delete_customer` route en `app.py:412-426` | La razon: se reemplaza por soft-delete. |
| 8 | Anadir ruta desactivar | `POST /customers/<int:customer_id>/deactivate` | Llama a `customer_crud.deactivate_customer`. Flash segun resultado. Redirect a `/customers`. |
| 9 | Anadir ruta reactivar | `POST /customers/<int:customer_id>/reactivate` | Llama a `customer_crud.reactivate_customer`. Flash segun resultado. Redirect a `/customers`. |
| 10 | Pasar `filter` al handler GET | `GET /customers` | Default `"active"`. Pasa a `customer_crud.listar_clientes(filter=...)`. |
| 11 | Pasar `filter` al template | `render_template(...)` | Para que la UI pueda mostrar el filtro activo. |

### Cambios en `templates/customers.html`

| # | Cambio | Detalle |
| --- | --- | --- |
| 12 | Anadir combo `Estado` al formulario de filtros | Opciones `Activos` (default), `Inactivos`, `Todos`. Autoenvia al cambiar. |
| 13 | Cambiar el icono `delete` por icono `deactivate` o `reactivate` | El form de la accion envia `POST` a la ruta correspondiente segun el estado actual del cliente. |
| 14 | Anadir columna "Estado" a la tabla | Badge verde `Activo` o gris `Inactivo` segun `customer.is_active`. |
| 15 | Mostrar en la barra de busqueda que el telefono es buscable | El placeholder puede ser `"Buscar por nombre, documento, telefono o NIT..."`. |

## 4. Aceptacion automatizada

| Test | Cubre | Detalle |
| --- | --- | --- |
| `tests/test_customer_crud.py::CrearClienteTest::test_happy_path_inserts_person_and_customer_and_commits` | `crear_cliente` happy path | Verifica que `crear_cliente` ejecuta ambos `INSERT` y hace `commit`. |
| `tests/test_customer_crud.py::CrearClienteTest::test_returns_false_and_rolls_back_when_db_raises_duplicate` | rollback en duplicado | Simula `mysql.connector.Error` y exige `rollback` + retorno `False`. |
| `tests/test_customer_crud.py::ListarClientesTest::test_returns_preset_rows_when_no_search_is_provided` | `listar_clientes` sin search | Verifica que retorna las filas del cursor tal cual. |
| `tests/test_customer_crud.py::GetCustomerTest` (dos tests) | `get_customer` por id | Cubre el caso `id existe` y `id no existe`. |
| `tests/test_customer_crud.py::UpdateCustomerTest::test_happy_path_issues_person_and_customer_updates` | `update_customer` happy path | Exige ambos `UPDATE` y un solo `commit`. |
| `tests/test_customer_crud.py::DeleteCustomerTest::test_raises_customer_has_sales_error_when_sales_count_is_positive` | pre-check de ventas | Verifica que con `sales_count = 4` se lanza `CustomerHasSalesError` sin abrir la conexion. |

Comando esperado: `uv run pytest tests/test_customer_crud.py` o
`uv run python -m unittest tests.test_customer_crud`.

### Brechas de cobertura

- **Tests para `deactivate_customer` / `reactivate_customer`**:
  Las funciones de borrado lógico están testeadas en `tests/unit/test_customer_soft_delete.py`, verificando que el `UPDATE` a `is_active` se ejecuta correctamente y gestiona transacciones (commit/rollback) en caso de error.
  seguridad.
- **No hay test para la busqueda por `phone`**: el cambio en el `LIKE`
  no tiene asserts.
- **No hay test de integracion Flask** para las rutas nuevas
  (`/customers/<id>/deactivate`, `/customers/<id>/reactivate`).
- **No hay test para la migracion idempotente** que anade
  `customer.is_active`. La migracion debe ser ejecutable multiples veces
  sin error.

## 5. Aceptacion manual en navegador / DataGrip

### Pasos en navegador (estudiante junior)

1. Login con `admin / admin123`. Ir a `/customers`. Ver la tabla con
   clientes activos del seed.
2. Verificar que la columna "Estado" muestra `Activo` para todos.
3. Click en "Nuevo Cliente". Llenar `first_name`, `last_name`,
   `identity_number`. Dejar `billing_name` y `tax_id` vacios. **Guardar
   Cliente**. Verificar en la tabla: aparece el cliente, "Facturacion"
   muestra `<nombre> <apellido>`, "NIT" muestra el mismo numero del
   documento. Flash verde.
4. Repetir con el mismo `identity_number`. Verificar flash rojo y que
   el cliente **no** aparece dos veces (`UNIQUE` en
   `person.identity_number`).
5. En la barra de busqueda, escribir un numero de telefono existente.
   Verificar que la tabla filtra y aparece un boton "Limpiar".
6. Cambiar el filtro de estado a `Inactivos`. La tabla debe quedar
   vacia. Cambiar a `Todos`. Deben verse todos.
7. Click en el icono "Editar" del primer cliente. Verificar que arriba
   de la tabla aparece el panel "Editar Cliente #<id>". Cambiar el
   telefono. **Guardar Cambios**. Verificar flash verde y telefono
   actualizado.
8. Intentar editar y dejar `first_name` vacio. Verificar flash rojo
   "Nombre, apellido y documento son obligatorios." y que la pantalla se
   mantiene en modo edicion.
9. Click en "Desactivar" de un cliente. Aceptar el `confirm()` de JS.
   Verificar flash verde y que el cliente desaparece de la lista por
   defecto (`?filter=active`).
10. Verificar que el cliente desactivado **sigue existiendo** en
    `?filter=all` y en `?filter=inactive`.
11. Click en "Reactivar" del mismo cliente. Verificar que vuelve a
    aparecer en `?filter=active`.
12. `GET /customers/9999/edit` (id inexistente). Verificar `404` con el
    texto "Cliente no encontrado".
13. Visitar `/customers/<id>/delete` (ruta que ya no debe existir). El
    servidor debe responder `404` o `405`.

### Pasos en DataGrip (cliente SQL)

1. Conectarse a `sis122_zarvent_repuestos`.
2. Verificar la nueva columna:
   `SHOW COLUMNS FROM customer;`
   Debe incluir `is_active BOOLEAN DEFAULT TRUE`.
3. Verificar que la migracion es idempotente: ejecutar dos veces el
   `ALTER TABLE` desde `init_db.py` y confirmar que no rompe.
4. Ver el contenido:
   `SELECT customer_id, person_id, billing_name, tax_id, is_active
   FROM customer;`
   La columna `is_active` debe ser `1` (TRUE) para todos los clientes
   preexistentes.
5. Probar soft-delete manual:
   `UPDATE customer SET is_active = FALSE WHERE customer_id = 1;`
   `SELECT * FROM customer WHERE customer_id = 1;` debe mostrar
   `is_active = 0`.
6. Confirmar que el cliente sigue visible para ventas existentes:
   `SELECT * FROM sales_order WHERE customer_id = 1;` debe seguir
   mostrando las ordenes previas (la columna `is_active` de `customer`
   no afecta `sales_order`).
7. Verificar integridad:
   `SHOW CREATE TABLE person;` debe incluir
   `UNIQUE KEY identity_number (identity_number)`.
8. `SHOW CREATE TABLE customer;` debe incluir
   `UNIQUE KEY person_id (person_id)` y
   `FOREIGN KEY (person_id) REFERENCES person (person_id) ON DELETE CASCADE`.
9. `SHOW CREATE TABLE sales_order;` debe incluir
   `FOREIGN KEY (customer_id) REFERENCES customer (customer_id) ON DELETE RESTRICT`.

## 6. Decisiones fuera de alcance

1. **Borrado fisico de clientes**: se mantiene en `customer_crud.py`
   (`delete_customer`) por compatibilidad, pero **no tiene ruta Flask**
   que lo invoque. La razon academica: un cliente con ventas no se puede
   borrar (FK `RESTRICT`), y un cliente sin ventas no deberia
   desaparecer del historial. El soft-delete (`is_active`) es la
   alternativa correcta. `fuera de alcance v1` para la UI.
2. **Borrado en cascada de `person`**: la cascada `customer.person_id ON
   DELETE CASCADE` se mantiene en el esquema, pero el contrato v1 no la
   ejercita. `fuera de alcance v1` para la operacion.
3. **Auditoria de cambios**: no hay `customer_audit` ni triggers. Editar
   un cliente sobrescribe los valores anteriores sin dejar rastro.
   `fuera de alcance v1`.
4. **Validacion de formato de email en backend**: el template usa
   `type="email"` y el navegador puede quejarse, pero `customer_crud` no
   valida el formato. Acepta cualquier string. `fuera de alcance v1`.
5. **Validacion de formato de telefono**: cualquier string se guarda.
   `fuera de alcance v1`.
6. **Paginacion del listado**: `listar_clientes` no usa `LIMIT/OFFSET`.
   `fuera de alcance v1`.
7. **Mockup academico**: no existe `customers_mockup.*` en
   `.cszv/mockups/`. La pantalla real es la unica referencia visual.
   `fuera de alcance v1`.
8. **Multi-telefono / multi-email**: el modelo guarda un solo telefono y
   un solo email. `fuera de alcance v1`.
9. **Roles de cliente** (`vip`, `corporativo`, `mayorista`): no hay
   clasificacion. `fuera de alcance v1`.

## 7. Trazabilidad RF

| Tema | `docs/analysis` | `docs/database` | Codigo actual | Estado v1 |
| --- | --- | --- | --- | --- |
| RF-01 identidad separada del rol comercial | `processes.md`, `procedures.md` separan datos personales y de facturacion | `erd.md` `PERSON \|\|--o\| CUSTOMER` | `person` + `customer` con `person_id` FK unico | implementado v1 |
| RF-01 registro de cliente | `requirements.md` RF-01 | `db_explanation.md` | `POST /customers` + `crear_cliente()` con transaccion | implementado v1 |
| RF-01 edicion de cliente | `procedures.md` paso 4 ("revisa que la informacion este actualizada") | `db_explanation.md` | `GET/POST /customers/<id>/edit` + `update_customer()` | implementado v1 |
| RF-01 soft-delete / borrado logico | — | nueva columna `customer.is_active` | Columna `is_active` y funciones `deactivate_customer`/`reactivate_customer` implementadas | implementado v1 |
| RF-01 borrado fisico (decidir si se conserva) | — | `ON DELETE CASCADE` en `customer.person_id` | `delete_customer` se mantiene en CRUD sin ruta en la UI | implementado v1 |
| RF-01 busqueda por documento, nombre, NIT, razon social | `procedures.md` paso 2 | `db_explanation.md` | `listar_clientes(search=...)` cubre cinco campos | implementado v1 |
| RF-01 busqueda por telefono | `procedures.md` paso 2 | — | Búsqueda por teléfono incluida en `listar_clientes()` | implementado v1 |
| RF-01 datos de facturacion (Razon Social y NIT) | `actors.md` Cajero / Responsable de facturacion | `db_explanation.md` `billing_name`, `tax_id` | Columnas presentes; defaults replicados en ruta de edicion | implementado v1 |
| RF-01 valores por defecto (`billing_name`, `tax_id`) | — | — | Aplicados en `crear_cliente` y `edit_customer` | implementado v1 |
| Cardinalidad 1..0..1 reforzada en fisico | — | `db_explanation.md` declara 1..0..1 | `customer.person_id` `UNIQUE NOT NULL` | implementado v1 |
| Bloqueo de borrado si hay ventas (ya no aplica a UI) | `processes.md` "ventas sin detalle confiable" | `ON DELETE RESTRICT` en `sales_order.customer_id` | `delete_customer` + `CustomerHasSalesError` (se mantienen en CRUD sin ruta) | implementado v1 |
| Filtro por estado (`active`/`inactive`/`all`) | — | nueva columna `customer.is_active` | Filtro `filter` soportado en listado y UI | implementado v1 |
| Autenticacion previa | `actors.md` | `users` (`init_db.py:206`) | `@login_required` en `app.py:316` | implementado v1 |
| Trazabilidad: SQL trace + `cursor.rowcount` | — | — | `sql_trace.py` opt-in + `customer_crud.delete_customer` usa `cursor.rowcount` | implementado v1 |
| Historial de cambios (auditoria) | `processes.md` "auditoria futura" | `db_explanation.md` lo lista como limitacion | NO existe | fuera de alcance v1 |
| Validacion de formato de email | — | — | `type="email"` solo en HTML; backend no valida | fuera de alcance v1 |
| Validacion de formato de telefono | — | — | NO existe | fuera de alcance v1 |
| Vista de edicion separada del listado | — | — | Edita en el mismo `customers.html` con `{% if editing %}` | implementado v1 |
| Paginacion del listado | — | — | NO existe | fuera de alcance v1 |
| Mockup academico del modulo | — | — | NO existe `customers_mockup.*` | fuera de alcance v1 |
