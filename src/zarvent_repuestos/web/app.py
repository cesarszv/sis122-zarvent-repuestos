"""Flask web interface for the Zarvent Repuestos prototype."""

import json
import logging
import os
from decimal import Decimal, InvalidOperation
from functools import wraps
from typing import Callable, Optional

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from zarvent_repuestos.access.user_service import authenticate_user
from zarvent_repuestos.constants import (
    CustomerActiveFilter,
    PartStatus,
    PurchaseOrderStatus,
    SalesListFilter,
)
from zarvent_repuestos.crud import customer_crud, part_crud, purchase_crud, sales_crud
from zarvent_repuestos.crud.customer_crud import CustomerHasSalesError
from zarvent_repuestos.database.init_db import crear_tablas
from zarvent_repuestos.database.sql_trace import (
    build_summary,
    clear_request_context,
    clear_sql_trace_entries,
    get_sql_trace_entries,
    is_sql_trace_enabled,
    set_request_context,
)
from zarvent_repuestos.models.part import Part


app = Flask(__name__)
# Default SECRET_KEY is for local development only. Production/demo servers
# must set FLASK_SECRET_KEY to a strong, random value via the environment.
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "zarvent-academic-secret-key-122")
# Reload Jinja templates on every request so template edits are picked up
# without restarting the process. Safe in development with --no-reload.
app.config["TEMPLATES_AUTO_RELOAD"] = True


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


# Ensure MySQL tables exist (idempotent via CREATE TABLE IF NOT EXISTS) so the app
# works whether it is started with `python -m zarvent_repuestos.web.app` or with
# the `flask --app zarvent_repuestos.web.app:app run` CLI (which skips the
# `if __name__ == "__main__":` block at the bottom of this file).
try:
    crear_tablas()
except Exception as _init_error:  # noqa: BLE001 - tolerated on startup
    logger.warning("No se pudieron crear/verificar las tablas al iniciar: %s", _init_error)


# ---------------------------------------------------------------------------
# SQL Trace hooks
# ---------------------------------------------------------------------------

@app.before_request
def _capture_sql_trace_request_context():
    """Labels SQL trace entries with the current Flask request."""
    if is_sql_trace_enabled():
        set_request_context(request.method, request.path)


@app.teardown_request
def _release_sql_trace_request_context(_error=None):
    """Clears SQL trace request labels after each Flask request."""
    if is_sql_trace_enabled():
        clear_request_context()




def parse_str(value: Optional[str], *, default: Optional[str] = None,
              strip: bool = True) -> Optional[str]:
    """Returns the form value as a stripped string, or `default` when missing/empty."""
    if value is None:
        return default
    if strip:
        value = value.strip()
    return value or default


def parse_int(value: Optional[str], *, default: Optional[int] = None,
              minimum: Optional[int] = None) -> Optional[int]:
    """Parses a form value into a non-negative int. Returns default on failure."""
    if value is None or value == "":
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return parsed


def parse_decimal(value: Optional[str], *, default: Optional[float] = None,
                  minimum: Optional[float] = None) -> Optional[float]:
    """Parses a form value into a non-negative float. Returns default on failure."""
    if value is None or value == "":
        return default
    try:
        parsed = float(Decimal(str(value)))
    except (TypeError, ValueError, InvalidOperation):
        return default
    if minimum is not None and parsed < minimum:
        return default
    return default if parsed < 0 and minimum is None else parsed




def login_required(f: Callable) -> Callable:
    """Decorator to require login on private routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sesión para acceder al sistema.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function




@app.route("/", methods=["GET", "POST"])
def home():
    """Renders the login page and processes credentials."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    message = None
    if request.method == "POST":
        username = parse_str(request.form.get("username"), default="")
        password = request.form.get("password", "")

        try:
            user = authenticate_user(username, password)
            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))
            else:
                message = "Usuario o contraseña incorrectos."
        except Exception as error:  # noqa: BLE001 - surfaced to the user
            message = f"Error de conexión con MySQL: {error}"

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    """Clears the session and redirects to login."""
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("home"))




@app.route("/dashboard")
@login_required
def dashboard():
    """Renders the operational indicators dashboard."""
    metrics = sales_crud.obtener_metricas_dashboard()
    return render_template("dashboard.html", active_page="dashboard", metrics=metrics)




@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    """Lists inventory parts and processes registration of new ones."""
    if request.method == "POST":
        name = parse_str(request.form.get("name"))
        internal_code = parse_str(request.form.get("internal_code"))
        oem_code = parse_str(request.form.get("oem_code"))
        brand = parse_str(request.form.get("brand"))
        category_id = parse_int(request.form.get("part_category_id"), minimum=1)
        sale_price = parse_decimal(request.form.get("sale_price"), minimum=0.01)
        purchase_cost = parse_decimal(request.form.get("purchase_cost"), minimum=0.01)
        initial_stock = parse_int(request.form.get("initial_stock"), default=0, minimum=0)
        location = parse_str(request.form.get("location_name"), default="Aisle 1")
        unit = parse_str(request.form.get("unit"), default="pcs")
        warranty_days = parse_int(request.form.get("warranty_days"), default=0, minimum=0)
        reorder_level = parse_int(request.form.get("reorder_level"), default=10, minimum=0)
        status = parse_str(request.form.get("status"), default=PartStatus.DEFAULT)
        if status not in PartStatus.ALL:
            status = PartStatus.DEFAULT

        if not name or not internal_code or category_id is None \
                or sale_price is None or purchase_cost is None:
            flash("Completa los campos obligatorios del repuesto.", "error")
            return redirect(url_for("inventory"))

        part = Part(
            part_category_id=category_id,
            internal_code=internal_code,
            oem_code=oem_code,
            name=name,
            brand=brand,
            unit=unit,
            sale_price=sale_price,
            purchase_cost=purchase_cost,
            warranty_days=warranty_days,
            status=status,
        )

        try:
            success = part_crud.crear_producto(
                part, initial_stock, location, reorder_level=reorder_level
            )
            if success:
                flash(f"Producto '{name}' creado con éxito.", "success")
            else:
                flash("Error al registrar el producto en la base de datos.", "error")
        except Exception as e:  # noqa: BLE001 - displayed to the user
            flash(f"Error técnico: {e}", "error")

        return redirect(url_for("inventory"))

    # GET
    search = parse_str(request.args.get("search"))
    cat_id = parse_str(request.args.get("category_id"))
    brand = parse_str(request.args.get("brand"))
    status_filter = parse_str(
        request.args.get("status"), default=PartStatus.DEFAULT
    )
    if status_filter not in PartStatus.ALL:
        status_filter = PartStatus.DEFAULT

    category_filter = int(cat_id) if cat_id and cat_id.isdigit() else None

    parts = part_crud.listar_productos(
        search=search,
        category_id=category_filter,
        brand=brand,
        status_filter=status_filter,
    )
    categories = part_crud.listar_categorias()
    brands = part_crud.obtener_marcas()

    return render_template(
        "inventory.html",
        active_page="inventory",
        parts=parts,
        categories=categories,
        brands=brands,
        search_val=search or "",
        cat_val=cat_id or "",
        brand_val=brand or "",
        status_val=status_filter,
    )


@app.route("/inventory/<int:part_id>/edit", methods=["GET", "POST"])
@login_required
def edit_part(part_id: int):
    """Edits a part's editable fields."""
    if request.method == "POST":
        name = parse_str(request.form.get("name"))
        brand = parse_str(request.form.get("brand"))
        unit = parse_str(request.form.get("unit"), default="pcs")
        sale_price = parse_decimal(request.form.get("sale_price"), minimum=0.01)
        purchase_cost = parse_decimal(request.form.get("purchase_cost"), minimum=0.01)
        warranty_days = parse_int(request.form.get("warranty_days"), default=0, minimum=0)
        status = parse_str(request.form.get("status"), default=PartStatus.DEFAULT)
        if status not in PartStatus.ALL:
            status = PartStatus.DEFAULT

        if not name or sale_price is None or purchase_cost is None:
            flash("Nombre, precio de venta y costo de compra son obligatorios.", "error")
            return redirect(url_for("edit_part", part_id=part_id))

        ok = part_crud.update_part(
            part_id=part_id,
            name=name,
            brand=brand,
            unit=unit,
            sale_price=sale_price,
            purchase_cost=purchase_cost,
            warranty_days=warranty_days,
            status=status,
        )
        if ok:
            flash(f"Repuesto #{part_id} actualizado con éxito.", "success")
            return redirect(url_for("inventory"))
        flash("No se pudo actualizar el repuesto.", "error")
        return redirect(url_for("edit_part", part_id=part_id))

    part = part_crud.get_part(part_id)
    if not part:
        return abort(404, "Repuesto no encontrado")
    categories = part_crud.listar_categorias()
    return render_template(
        "part_edit.html",
        active_page="inventory",
        part=part,
        categories=categories,
    )


@app.route("/inventory/<int:part_id>/deactivate", methods=["POST"])
@login_required
def deactivate_part(part_id: int):
    """Soft-deletes a part (status='inactive')."""
    if part_crud.deactivate_part(part_id):
        flash(f"Repuesto #{part_id} inactivado.", "success")
    else:
        flash("No se pudo inactivar el repuesto.", "error")
    return redirect(url_for("inventory"))


@app.route("/inventory/<int:part_id>/reactivate", methods=["POST"])
@login_required
def reactivate_part(part_id: int):
    """Re-activates a previously soft-deleted part."""
    if part_crud.reactivate_part(part_id):
        flash(f"Repuesto #{part_id} reactivado.", "success")
    else:
        flash("No se pudo reactivar el repuesto.", "error")
    return redirect(url_for("inventory"))


@app.route("/inventory/categories", methods=["POST"])
@login_required
def create_category():
    """Creates a new part category from the inventory form."""
    name = parse_str(request.form.get("name"))
    description = parse_str(request.form.get("description"))
    if not name:
        flash("El nombre de la categoría es obligatorio.", "error")
        return redirect(url_for("inventory"))
    if part_crud.crear_categoria(name, description):
        flash(f"Categoría '{name}' creada con éxito.", "success")
    else:
        flash("No se pudo crear la categoría (revisa si ya existe).", "error")
    return redirect(url_for("inventory"))




@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    """Lists sales orders and handles creation of new transactional sales."""
    if request.method == "POST":
        client_mode = parse_str(request.form.get("client_mode"), default="existing")
        payment_method = parse_str(
            request.form.get("payment_method"),
            default="Efectivo",
        )

        customer_id: Optional[int] = None
        try:
            if client_mode == "new":
                first_name = parse_str(request.form.get("new_first_name"))
                last_name = parse_str(request.form.get("new_last_name"))
                identity_number = parse_str(request.form.get("new_identity_number"))

                if not first_name or not last_name or not identity_number:
                    raise ValueError(
                        "Nombres, apellidos y documento son obligatorios para un cliente nuevo."
                    )

                existing = customer_crud.buscar_cliente_por_doc(identity_number)
                if existing:
                    customer_id = existing["customer_id"]
                else:
                    success = customer_crud.crear_cliente(
                        first_name=first_name,
                        last_name=last_name,
                        identity_number=identity_number,
                    )
                    if not success:
                        raise ValueError("No se pudo registrar al nuevo cliente.")
                    new_cust = customer_crud.buscar_cliente_por_doc(identity_number)
                    customer_id = new_cust["customer_id"]
            else:
                customer_id = parse_int(request.form.get("customer_id"), minimum=1)
                if customer_id is None:
                    raise ValueError("No se seleccionó ningún cliente.")

            items_json = parse_str(request.form.get("items_json"), default="[]")
            items = json.loads(items_json or "[]")

            if not items:
                raise ValueError("La orden debe tener al menos un ítem.")

            sales_order_id = sales_crud.crear_orden_venta(
                customer_id=customer_id,
                items=items,
                payment_method=payment_method,
            )

            if sales_order_id:
                flash(f"Venta #{sales_order_id} registrada correctamente.", "success")
            else:
                flash("Error al registrar la venta.", "error")
        except Exception as e:  # noqa: BLE001
            flash(f"Error al procesar venta: {e}", "error")

        return redirect(url_for("sales"))

    # GET
    status = parse_str(
        request.args.get("status"), default=SalesListFilter.DEFAULT
    )
    if status not in SalesListFilter.CHOICES:
        status = SalesListFilter.DEFAULT
    start_date = parse_str(request.args.get("start_date"))
    end_date = parse_str(request.args.get("end_date"))

    orders = sales_crud.listar_ordenes_venta(
        status=status,
        start_date=start_date,
        end_date=end_date,
    )

    parts = part_crud.listar_productos()
    customers = customer_crud.listar_clientes(
        status_filter=CustomerActiveFilter.ACTIVE
    )

    return render_template(
        "sales.html",
        active_page="sales",
        orders=orders,
        parts=parts,
        customers=customers,
        status_val=status,
        start_val=start_date or "",
        end_val=end_date or "",
    )


@app.route("/sales/receipt/<int:sales_order_id>")
@login_required
def receipt(sales_order_id: int):
    """Returns a raw text layout representing a POS sales voucher."""
    order = sales_crud.obtener_detalles_orden(sales_order_id)
    if not order:
        return abort(404, "Venta no encontrada")
    return render_template("receipt.html", order=order)




@app.route("/sql-trace")
@login_required
def sql_trace():
    """Shows live SQL statements executed by mysql-connector-python."""
    return render_template(
        "sql_trace.html",
        active_page="sql_trace",
        trace_enabled=is_sql_trace_enabled(),
    )


@app.route("/api/sql-trace")
@login_required
def api_sql_trace():
    """Returns recent SQL trace entries for the live presentation view."""
    entries = get_sql_trace_entries()
    return jsonify({"entries": entries, "summary": build_summary(entries)})


@app.route("/api/sql-trace/clear", methods=["POST"])
@login_required
def api_clear_sql_trace():
    """Clears recent SQL trace entries."""
    clear_sql_trace_entries()
    return jsonify({"status": "ok"})




def _resolve_customer_filter() -> str:
    """Returns the validated status filter for /customers."""
    raw = parse_str(request.args.get("filter"), default=CustomerActiveFilter.DEFAULT)
    if raw not in CustomerActiveFilter.CHOICES:
        return CustomerActiveFilter.DEFAULT
    return raw


@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers():
    """Lists customers with search, and creates new ones via POST."""
    if request.method == "POST":
        first_name = parse_str(request.form.get("first_name"))
        last_name = parse_str(request.form.get("last_name"))
        identity_number = parse_str(request.form.get("identity_number"))
        phone = parse_str(request.form.get("phone"))
        email = parse_str(request.form.get("email"))
        address = parse_str(request.form.get("address"))
        billing_name = parse_str(request.form.get("billing_name"))
        tax_id = parse_str(request.form.get("tax_id"))

        if not first_name or not last_name or not identity_number:
            flash("Nombre, apellido y documento son obligatorios.", "error")
            return redirect(url_for("customers"))

        try:
            ok = customer_crud.crear_cliente(
                first_name=first_name,
                last_name=last_name,
                identity_number=identity_number,
                billing_name=billing_name,
                tax_id=tax_id,
                phone=phone,
                email=email,
                address=address,
            )
        except Exception as err:  # noqa: BLE001
            flash(f"Error al crear cliente: {err}", "error")
            return redirect(url_for("customers"))

        if ok:
            flash(f"Cliente '{first_name} {last_name}' creado con éxito.", "success")
        else:
            flash(
                "No se pudo crear el cliente (revisa datos duplicados o el log del servidor).",
                "error",
            )
        return redirect(url_for("customers"))

    search = parse_str(request.args.get("search"))
    status_filter = _resolve_customer_filter()
    customers_list = customer_crud.listar_clientes(
        search=search, status_filter=status_filter
    )
    return render_template(
        "customers.html",
        active_page="customers",
        customers=customers_list,
        search_val=search or "",
        status_val=status_filter,
    )


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id: int):
    """Edits an existing customer."""
    if request.method == "POST":
        first_name = parse_str(request.form.get("first_name"))
        last_name = parse_str(request.form.get("last_name"))
        identity_number = parse_str(request.form.get("identity_number"))
        phone = parse_str(request.form.get("phone"))
        email = parse_str(request.form.get("email"))
        address = parse_str(request.form.get("address"))
        billing_name = parse_str(request.form.get("billing_name"))
        tax_id = parse_str(request.form.get("tax_id"))

        if not first_name or not last_name or not identity_number:
            flash("Nombre, apellido y documento son obligatorios.", "error")
            return redirect(url_for("edit_customer", customer_id=customer_id))

        ok = customer_crud.update_customer(
            customer_id=customer_id,
            first_name=first_name,
            last_name=last_name,
            identity_number=identity_number,
            billing_name=billing_name or f"{first_name} {last_name}",
            tax_id=tax_id or identity_number,
            phone=phone,
            email=email,
            address=address,
        )
        if ok:
            flash("Cliente actualizado con éxito.", "success")
            return redirect(url_for("customers"))
        flash("No se pudo actualizar el cliente.", "error")
        return redirect(url_for("edit_customer", customer_id=customer_id))

    customer = customer_crud.get_customer(customer_id)
    if not customer:
        return abort(404, "Cliente no encontrado")
    status_filter = _resolve_customer_filter()
    return render_template(
        "customers.html",
        active_page="customers",
        customers=customer_crud.listar_clientes(status_filter=status_filter),
        search_val="",
        status_val=status_filter,
        editing=customer,
    )


@app.route("/customers/<int:customer_id>/deactivate", methods=["POST"])
@login_required
def deactivate_customer(customer_id: int):
    """Soft-deletes a customer by setting `is_active = FALSE`."""
    try:
        if customer_crud.deactivate_customer(customer_id):
            flash(f"Cliente #{customer_id} inactivado.", "success")
        else:
            flash("No se pudo inactivar el cliente.", "error")
    except CustomerHasSalesError as err:
        flash(str(err), "error")
    return redirect(url_for("customers"))


@app.route("/customers/<int:customer_id>/reactivate", methods=["POST"])
@login_required
def reactivate_customer(customer_id: int):
    """Re-activates a previously soft-deleted customer."""
    if customer_crud.reactivate_customer(customer_id):
        flash(f"Cliente #{customer_id} reactivado.", "success")
    else:
        flash("No se pudo reactivar el cliente.", "error")
    return redirect(url_for("customers"))




@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():
    """Lists purchase orders and creates new ones via POST."""
    if request.method == "POST":
        supplier_id = parse_int(request.form.get("supplier_id"), minimum=1)
        expected_date = parse_str(request.form.get("expected_date"))
        items_json = parse_str(request.form.get("items_json"), default="[]")
        try:
            items = json.loads(items_json or "[]")
        except json.JSONDecodeError:
            flash("Items de la orden están mal formados.", "error")
            return redirect(url_for("purchases"))

        if supplier_id is None:
            flash("Selecciona un proveedor.", "error")
            return redirect(url_for("purchases"))

        try:
            purchase_order_id = purchase_crud.create_purchase_order(
                supplier_id=supplier_id,
                expected_date=expected_date,
                items=items,
            )
        except ValueError as err:
            flash(f"Error de validación: {err}", "error")
            return redirect(url_for("purchases"))
        except Exception as err:  # noqa: BLE001
            flash(f"Error al crear la orden de compra: {err}", "error")
            return redirect(url_for("purchases"))

        if purchase_order_id:
            flash(
                f"Orden de compra #{purchase_order_id} creada con éxito.",
                "success",
            )
            return redirect(
                url_for("purchase_detail", purchase_order_id=purchase_order_id)
            )
        flash("No se pudo crear la orden de compra.", "error")
        return redirect(url_for("purchases"))

    status = parse_str(request.args.get("status"))
    if status and status not in PurchaseOrderStatus.ALL:
        status = None
    orders = purchase_crud.list_purchase_orders(status=status)
    suppliers = purchase_crud.list_suppliers(active_only=True)
    parts = part_crud.listar_productos()
    return render_template(
        "purchases.html",
        active_page="purchases",
        orders=orders,
        suppliers=suppliers,
        parts=parts,
        status_val=status or "",
    )


@app.route("/purchases/suppliers", methods=["POST"])
@login_required
def create_supplier():
    """Creates a new supplier from the purchases form."""
    business_name = parse_str(request.form.get("business_name"))
    tax_id = parse_str(request.form.get("tax_id"))
    phone = parse_str(request.form.get("phone"))
    email = parse_str(request.form.get("email"))
    address = parse_str(request.form.get("address"))

    if not business_name or not tax_id:
        flash("Razón social y NIT son obligatorios.", "error")
        return redirect(url_for("purchases"))

    supplier_id = purchase_crud.create_supplier(
        business_name=business_name,
        tax_id=tax_id,
        phone=phone,
        email=email,
        address=address,
    )
    if supplier_id:
        flash(f"Proveedor '{business_name}' creado con éxito.", "success")
    else:
        flash("No se pudo crear el proveedor (revisa si el NIT ya existe).", "error")
    return redirect(url_for("purchases"))


@app.route("/purchases/<int:purchase_order_id>")
@login_required
def purchase_detail(purchase_order_id: int):
    """Shows a purchase order and its items; provides a form to register reception."""
    order = purchase_crud.get_purchase_order_details(purchase_order_id)
    if not order:
        return abort(404, "Orden de compra no encontrada")
    return render_template(
        "purchase_detail.html",
        active_page="purchases",
        order=order,
    )


@app.route("/purchases/<int:purchase_order_id>/cancel", methods=["POST"])
@login_required
def cancel_purchase(purchase_order_id: int):
    """Cancels a `Pending` order. Does not touch inventory_stock."""
    try:
        purchase_crud.cancel_purchase_order(purchase_order_id)
        flash(f"Orden de compra #{purchase_order_id} cancelada.", "success")
    except ValueError as err:
        flash(f"Error de validación: {err}", "error")
    except Exception as err:  # noqa: BLE001
        flash(f"Error al cancelar la orden: {err}", "error")
    return redirect(url_for("purchases"))


@app.route("/purchases/<int:purchase_order_id>/receive", methods=["POST"])
@login_required
def receive_purchase(purchase_order_id: int):
    """Registers the received quantities for a purchase order."""
    items_json = parse_str(request.form.get("items_json"), default="[]")
    try:
        received_items = json.loads(items_json or "[]")
    except json.JSONDecodeError:
        flash("Cantidades recibidas mal formadas.", "error")
        return redirect(
            url_for("purchase_detail", purchase_order_id=purchase_order_id)
        )

    if not received_items:
        flash("Indica al menos una cantidad recibida.", "error")
        return redirect(
            url_for("purchase_detail", purchase_order_id=purchase_order_id)
        )

    try:
        purchase_crud.receive_purchase_order(
            purchase_order_id=purchase_order_id,
            received_items=received_items,
        )
    except ValueError as err:
        flash(f"Error de validación: {err}", "error")
        return redirect(
            url_for("purchase_detail", purchase_order_id=purchase_order_id)
        )
    except Exception as err:  # noqa: BLE001
        flash(f"Error al recibir la orden: {err}", "error")
        return redirect(
            url_for("purchase_detail", purchase_order_id=purchase_order_id)
        )

    flash("Recepción registrada con éxito.", "success")
    return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))




if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
