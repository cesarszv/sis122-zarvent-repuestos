"""Flask web interface for the Zarvent Repuestos prototype."""

import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify

from zarvent_repuestos.access.user_service import authenticate_user
from zarvent_repuestos.database.init_db import crear_tablas
from zarvent_repuestos.database.sql_trace import (
    build_summary,
    clear_request_context,
    clear_sql_trace_entries,
    get_sql_trace_entries,
    is_sql_trace_enabled,
    set_request_context,
)
from zarvent_repuestos.crud import part_crud, customer_crud, sales_crud, purchase_crud
from zarvent_repuestos.crud.customer_crud import CustomerHasSalesError
from zarvent_repuestos.models.part import Part


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "zarvent-academic-secret-key-122")
# Reload Jinja templates on every request so template edits are picked up
# without restarting the process. Safe in development with --no-reload.
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure MySQL tables exist (idempotent via CREATE TABLE IF NOT EXISTS) so the app
# works whether it is started with `python -m zarvent_repuestos.web.app` or with
# the `flask --app zarvent_repuestos.web.app:app run` CLI (which skips the
# `if __name__ == "__main__":` block at the bottom of this file).
try:
    crear_tablas()
except Exception as _init_error:
    print(f"⚠️ No se pudieron crear/verificar las tablas al iniciar: {_init_error}")


@app.before_request
def capture_sql_trace_request_context():
    """Labels SQL trace entries with the current Flask request."""
    if is_sql_trace_enabled():
        set_request_context(request.method, request.path)


@app.teardown_request
def release_sql_trace_request_context(_error=None):
    """Clears SQL trace request labels after each Flask request."""
    if is_sql_trace_enabled():
        clear_request_context()


def login_required(f):
    """Decorator to require login on private routes."""
    from functools import wraps
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
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            user = authenticate_user(username, password)
            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))
            else:
                message = "Usuario o contraseña incorrectos."
        except Exception as error:
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
        # Process new part registration
        name = request.form.get("name", "").strip()
        internal_code = request.form.get("internal_code", "").strip()
        oem_code = request.form.get("oem_code", "").strip()
        brand = request.form.get("brand", "").strip()
        category_id = int(request.form.get("part_category_id"))
        sale_price = float(request.form.get("sale_price"))
        purchase_cost = float(request.form.get("purchase_cost"))
        initial_stock = int(request.form.get("initial_stock", 0))
        location = request.form.get("location_name", "Aisle 1").strip()

        part = Part(
            part_category_id=category_id,
            internal_code=internal_code,
            oem_code=oem_code if oem_code else None,
            name=name,
            brand=brand if brand else None,
            sale_price=sale_price,
            purchase_cost=purchase_cost,
            status="active"
        )

        try:
            success = part_crud.crear_producto(part, initial_stock, location)
            if success:
                flash(f"Producto '{name}' creado con éxito.", "success")
            else:
                flash("Error al registrar el producto en la base de datos.", "error")
        except Exception as e:
            flash(f"Error técnico: {e}", "error")

        return redirect(url_for("inventory"))

    # GET requests - Listing filters
    search = request.args.get("search", "").strip()
    cat_id = request.args.get("category_id", "")
    brand = request.args.get("brand", "")

    category_filter = int(cat_id) if cat_id else None

    parts = part_crud.listar_productos(
        search=search if search else None,
        category_id=category_filter,
        brand=brand if brand else None
    )
    categories = part_crud.listar_categorias()
    brands = part_crud.obtener_marcas()

    return render_template(
        "inventory.html",
        active_page="inventory",
        parts=parts,
        categories=categories,
        brands=brands,
        search_val=search,
        cat_val=cat_id,
        brand_val=brand
    )


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    """Lists sales orders and handles creation of new transactional sales."""
    if request.method == "POST":
        # Check customer mode
        client_mode = request.form.get("client_mode", "existing")
        payment_method = request.form.get("payment_method", "Efectivo")

        customer_id = None

        try:
            # 1. Quick Customer Registration
            if client_mode == "new":
                first_name = request.form.get("new_first_name", "").strip()
                last_name = request.form.get("new_last_name", "").strip()
                identity_number = request.form.get("new_identity_number", "").strip()

                # Check if customer already exists by identity number
                existing = customer_crud.buscar_cliente_por_doc(identity_number)
                if existing:
                    customer_id = existing["customer_id"]
                else:
                    success = customer_crud.crear_cliente(
                        first_name=first_name,
                        last_name=last_name,
                        identity_number=identity_number
                    )
                    if not success:
                        raise ValueError("No se pudo registrar al nuevo cliente.")
                    # Fetch newly created customer
                    new_cust = customer_crud.buscar_cliente_por_doc(identity_number)
                    customer_id = new_cust["customer_id"]
            else:
                cust_val = request.form.get("customer_id")
                if not cust_val:
                    raise ValueError("No se seleccionó ningún cliente.")
                customer_id = int(cust_val)

            # 2. Parse Items JSON
            items_json = request.form.get("items_json", "[]")
            items = json.loads(items_json)

            if not items:
                raise ValueError("La orden debe tener al menos un ítem.")

            # 3. Create Sales Order (handles inventory subtraction and payment)
            sales_order_id = sales_crud.crear_orden_venta(
                customer_id=customer_id,
                items=items,
                payment_method=payment_method
            )

            if sales_order_id:
                flash(f"Venta #{sales_order_id} registrada correctamente.", "success")
            else:
                flash("Error al registrar la venta.", "error")

        except Exception as e:
            flash(f"Error al procesar venta: {e}", "error")

        return redirect(url_for("sales"))

    # GET requests - Listing filters
    status = request.args.get("status", "All Orders")
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    orders = sales_crud.listar_ordenes_venta(
        status=status,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    parts = part_crud.listar_productos()
    customers = customer_crud.listar_clientes()

    return render_template(
        "sales.html",
        active_page="sales",
        orders=orders,
        parts=parts,
        customers=customers,
        status_val=status,
        start_val=start_date,
        end_val=end_date
    )


@app.route("/sales/receipt/<int:sales_order_id>")
@login_required
def receipt(sales_order_id):
    """Returns a raw text layout representing a POS sales voucher."""
    order = sales_crud.obtener_detalles_orden(sales_order_id)
    if not order:
        return abort(404, "Venta no encontrada")

    # Render receipt template as preformatted raw text
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


# --- CUSTOMERS ---

@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers():
    """Lists customers with search, and creates new ones via POST."""
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        identity_number = request.form.get("identity_number", "").strip()
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        address = request.form.get("address", "").strip() or None
        billing_name = request.form.get("billing_name", "").strip() or None
        tax_id = request.form.get("tax_id", "").strip() or None

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
        except Exception as err:
            flash(f"Error al crear cliente: {err}", "error")
            return redirect(url_for("customers"))

        if ok:
            flash(f"Cliente '{first_name} {last_name}' creado con éxito.", "success")
        else:
            flash("No se pudo crear el cliente (revisa datos duplicados o el log del servidor).", "error")
        return redirect(url_for("customers"))

    search = request.args.get("search", "").strip() or None
    customers_list = customer_crud.listar_clientes(search=search)
    return render_template(
        "customers.html",
        active_page="customers",
        customers=customers_list,
        search_val=search or "",
    )


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id):
    """Edits an existing customer."""
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        identity_number = request.form.get("identity_number", "").strip()
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        address = request.form.get("address", "").strip() or None
        billing_name = request.form.get("billing_name", "").strip() or None
        tax_id = request.form.get("tax_id", "").strip() or None

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
    return render_template(
        "customers.html",
        active_page="customers",
        customers=customer_crud.listar_clientes(),
        search_val="",
        editing=customer,
    )


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
def delete_customer(customer_id):
    """Deletes a customer, refusing the operation if it has linked sales."""
    try:
        deleted = customer_crud.delete_customer(customer_id)
    except CustomerHasSalesError as err:
        flash(str(err), "error")
        return redirect(url_for("customers"))

    if deleted:
        flash("Cliente eliminado con éxito.", "success")
    else:
        flash("No se pudo eliminar el cliente.", "error")
    return redirect(url_for("customers"))


# --- PURCHASES ---

@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():
    """Lists purchase orders and creates new ones via POST."""
    if request.method == "POST":
        try:
            supplier_id = int(request.form.get("supplier_id", "0"))
        except ValueError:
            flash("Proveedor inválido.", "error")
            return redirect(url_for("purchases"))
        expected_date = request.form.get("expected_date", "").strip() or None
        items_json = request.form.get("items_json", "[]")
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            flash("Items de la orden están mal formados.", "error")
            return redirect(url_for("purchases"))

        if supplier_id <= 0:
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
        except Exception as err:
            flash(f"Error al crear la orden de compra: {err}", "error")
            return redirect(url_for("purchases"))

        if purchase_order_id:
            flash(f"Orden de compra #{purchase_order_id} creada con éxito.", "success")
            return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))
        flash("No se pudo crear la orden de compra.", "error")
        return redirect(url_for("purchases"))

    status = request.args.get("status", "").strip() or None
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


@app.route("/purchases/<int:purchase_order_id>")
@login_required
def purchase_detail(purchase_order_id):
    """Shows a purchase order and its items; provides a form to register reception."""
    order = purchase_crud.get_purchase_order_details(purchase_order_id)
    if not order:
        return abort(404, "Orden de compra no encontrada")
    return render_template(
        "purchase_detail.html",
        active_page="purchases",
        order=order,
    )


@app.route("/purchases/<int:purchase_order_id>/receive", methods=["POST"])
@login_required
def receive_purchase(purchase_order_id):
    """Registers the received quantities for a purchase order."""
    items_json = request.form.get("items_json", "[]")
    try:
        received_items = json.loads(items_json)
    except json.JSONDecodeError:
        flash("Cantidades recibidas mal formadas.", "error")
        return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))

    if not received_items:
        flash("Indica al menos una cantidad recibida.", "error")
        return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))

    try:
        purchase_crud.receive_purchase_order(
            purchase_order_id=purchase_order_id,
            received_items=received_items,
        )
    except ValueError as err:
        flash(f"Error de validación: {err}", "error")
        return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))
    except Exception as err:
        flash(f"Error al recibir la orden: {err}", "error")
        return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))

    flash("Recepción registrada con éxito.", "success")
    return redirect(url_for("purchase_detail", purchase_order_id=purchase_order_id))


if __name__ == "__main__":
    # Tables were already ensured at module load; just start Flask here.
    app.run(debug=True)
