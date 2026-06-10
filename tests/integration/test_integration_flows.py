"""End-to-end integration tests against the demo MySQL database.

These tests exercise the real CRUD code paths against
``sis122_zarvent_repuestos``. Every test inserts rows whose unique
columns carry the ``TEST_CODX_`` prefix and the autouse cleanup
fixture in ``tests/integration/conftest.py`` removes them in reverse
FK order. No row inserted here should ever appear in DataGrip after
the suite finishes.

Why the CRUD layer and not raw SQL? Because the goal is to defend
the application contract (atomic transactions, status transitions,
stock updates) end-to-end. The few raw SELECTs are only used to
verify the effects.
"""

import pytest

from tests.factories import (
    TEST_PREFIX,
    make_customer_data,
    make_part_data,
    make_purchase_items,
    make_sale_items,
    make_supplier_data,
)
from zarvent_repuestos.constants import PartStatus, SalesOrderStatus
from zarvent_repuestos.crud import (
    customer_crud,
    part_crud,
    purchase_crud,
    sales_crud,
)
from zarvent_repuestos.models.part import Part


# ---------------------------------------------------------------------------
# Helpers (per-test cursors and ID lookups)
# ---------------------------------------------------------------------------

def _new_cursor(db):
    """Returns a fresh dictionary cursor; closes automatically when
    the test exits. The fixture-level ``db_cursor`` is reused by
    pytest, so this helper opens an independent cursor to avoid
    mixing state."""
    return db.cursor(dictionary=True)


def _find_customer_by_tax(db, tax_id):
    cursor = _new_cursor(db)
    try:
        cursor.execute(
            """
            SELECT c.customer_id, c.is_active, c.billing_name, c.tax_id,
                   p.first_name, p.last_name, p.identity_number
            FROM customer c JOIN person p ON c.person_id = p.person_id
            WHERE c.tax_id = %s
            """,
            (tax_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def _find_part_by_code(db, internal_code):
    cursor = _new_cursor(db)
    try:
        cursor.execute(
            "SELECT part_id, status, sale_price FROM part WHERE internal_code = %s",
            (internal_code,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def _stock_for_part(db, part_id):
    cursor = _new_cursor(db)
    try:
        cursor.execute(
            "SELECT quantity_on_hand, reorder_level FROM inventory_stock "
            "WHERE part_id = %s",
            (part_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()


def _create_category(db, name_suffix, description="Test category"):
    """Inserts a TEST_CODX_ part_category and returns its id."""
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO part_category (name, description) VALUES (%s, %s)",
            (f"{TEST_PREFIX}CAT_{name_suffix}", description),
        )
        db.commit()
        return cursor.lastrowid
    finally:
        cursor.close()


def _create_part_with_stock(db, category_id, data, initial_stock=10):
    """Inserts a TEST_CODX_ part and its inventory_stock row, returns
    the new part_id."""
    part = Part(
        part_category_id=category_id,
        internal_code=data["internal_code"],
        oem_code=data["oem_code"],
        name=data["name"],
        brand=data["brand"],
        unit=data["unit"],
        sale_price=data["sale_price"],
        purchase_cost=data["purchase_cost"],
        warranty_days=data["warranty_days"],
        status=data["status"],
    )
    ok = part_crud.crear_producto(
        part,
        initial_stock=initial_stock,
        location=data["location_name"],
        reorder_level=data["reorder_level"],
    )
    assert ok, "crear_producto failed in the integration setup"
    row = _find_part_by_code(db, data["internal_code"])
    assert row is not None, f"Part {data['internal_code']!r} not found after insert"
    return row["part_id"]


# ---------------------------------------------------------------------------
# 1. Create customer and see it in the list
# ---------------------------------------------------------------------------

def test_create_customer_appears_in_active_list(db):
    data = make_customer_data()
    assert customer_crud.crear_cliente(
        first_name=data["first_name"],
        last_name=data["last_name"],
        identity_number=data["identity_number"],
        phone=data["phone"],
        email=data["email"],
        address=data["address"],
        billing_name=data["billing_name"],
        tax_id=data["tax_id"],
    ) is True

    row = _find_customer_by_tax(db, data["tax_id"])
    assert row is not None
    assert row["is_active"] in (1, True)
    assert row["first_name"] == data["first_name"]
    assert row["identity_number"] == data["identity_number"]

    # The list (active filter) must include the new customer.
    listed = customer_crud.listar_clientes(search=data["identity_number"])
    assert any(c["tax_id"] == data["tax_id"] for c in listed)


# ---------------------------------------------------------------------------
# 2. Create category + part + initial stock
# ---------------------------------------------------------------------------

def test_create_category_part_and_initial_stock(db):
    category_id = _create_category(db, name_suffix="FLOW2")
    data = make_part_data(category_id=category_id)
    part_id = _create_part_with_stock(db, category_id, data, initial_stock=15)

    stock = _stock_for_part(db, part_id)
    assert stock is not None
    assert stock["quantity_on_hand"] == 15
    assert stock["reorder_level"] == data["reorder_level"]


# ---------------------------------------------------------------------------
# 3. Sale records payment, reduces stock, supports discount
# ---------------------------------------------------------------------------

def test_sale_records_payment_reduces_stock_and_supports_discount(db):
    # Setup: customer + category + part with 20 units on hand.
    customer_data = make_customer_data()
    assert customer_crud.crear_cliente(
        first_name=customer_data["first_name"],
        last_name=customer_data["last_name"],
        identity_number=customer_data["identity_number"],
        tax_id=customer_data["tax_id"],
    ) is True
    customer_row = _find_customer_by_tax(db, customer_data["tax_id"])

    category_id = _create_category(db, name_suffix="FLOW3")
    part_data = make_part_data(category_id=category_id)
    part_id = _create_part_with_stock(db, category_id, part_data, initial_stock=20)
    initial_stock = _stock_for_part(db, part_id)["quantity_on_hand"]

    # 2 units * 25.0 = 50.0 subtotal, discount 5.0 per unit = 10.0,
    # total = 40.0
    items = make_sale_items(
        part_id=part_id, quantity=2, unit_price=25.0, discount_amount=5.0,
    )
    sales_order_id = sales_crud.crear_orden_venta(
        customer_id=customer_row["customer_id"],
        items=items,
        payment_method="Efectivo",
    )
    assert isinstance(sales_order_id, int) and sales_order_id > 0

    # Verify header + items + payment + stock effect.
    details = sales_crud.obtener_detalles_orden(sales_order_id)
    assert details is not None
    assert details["status"] == SalesOrderStatus.PAID
    assert float(details["subtotal"]) == pytest.approx(50.0)
    assert float(details["discount_amount"]) == pytest.approx(10.0)
    assert float(details["total_amount"]) == pytest.approx(40.0)
    assert len(details["items"]) == 1
    assert details["items"][0]["quantity"] == 2

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT method, amount, status FROM payment WHERE sales_order_id = %s",
            (sales_order_id,),
        )
        payment = cursor.fetchone()
    finally:
        cursor.close()
    assert payment is not None
    assert payment["method"] == "Efectivo"
    assert float(payment["amount"]) == pytest.approx(40.0)

    new_stock = _stock_for_part(db, part_id)["quantity_on_hand"]
    assert new_stock == initial_stock - 2


# ---------------------------------------------------------------------------
# 4. Purchase pending -> partial reception -> full reception
# ---------------------------------------------------------------------------

def test_purchase_full_flow_pending_to_received_increases_stock(db):
    # Setup: supplier + category + part with 5 units on hand.
    supplier_data = make_supplier_data()
    supplier_id = purchase_crud.create_supplier(
        business_name=supplier_data["business_name"],
        tax_id=supplier_data["tax_id"],
        phone=supplier_data["phone"],
        email=supplier_data["email"],
        address=supplier_data["address"],
    )
    assert isinstance(supplier_id, int) and supplier_id > 0

    category_id = _create_category(db, name_suffix="FLOW4")
    part_data = make_part_data(category_id=category_id)
    part_id = _create_part_with_stock(db, category_id, part_data, initial_stock=5)
    initial_stock = _stock_for_part(db, part_id)["quantity_on_hand"]

    # 1. Create a Pending purchase order of 10 units.
    po_id = purchase_crud.create_purchase_order(
        supplier_id=supplier_id,
        expected_date=None,
        items=make_purchase_items(part_id=part_id, quantity=10, unit_cost=8.0),
    )
    assert isinstance(po_id, int) and po_id > 0
    details = purchase_crud.get_purchase_order_details(po_id)
    assert details["status"] == "Pending"

    # 2. Partial reception of 4 units: header -> Partially Received.
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT purchase_order_item_id FROM purchase_order_item "
            "WHERE purchase_order_id = %s",
            (po_id,),
        )
        item_id = cursor.fetchone()["purchase_order_item_id"]
    finally:
        cursor.close()

    partial = purchase_crud.receive_purchase_order(
        purchase_order_id=po_id,
        received_items=[
            {"purchase_order_item_id": item_id, "quantity_received": 4},
        ],
    )
    assert partial["status"] == "Partially Received"
    assert _stock_for_part(db, part_id)["quantity_on_hand"] == initial_stock + 4

    # 3. Full reception of 6 more units (cumulative 10): header -> Received.
    final = purchase_crud.receive_purchase_order(
        purchase_order_id=po_id,
        received_items=[
            {"purchase_order_item_id": item_id, "quantity_received": 10},
        ],
    )
    assert final["status"] == "Received"
    assert _stock_for_part(db, part_id)["quantity_on_hand"] == initial_stock + 10


def test_purchase_cancellation_does_not_touch_stock(db):
    """A cancelled order was never received: inventory must stay
    untouched, even though the header status flips to Cancelled."""
    supplier_data = make_supplier_data()
    supplier_id = purchase_crud.create_supplier(
        business_name=supplier_data["business_name"],
        tax_id=supplier_data["tax_id"],
    )
    assert supplier_id

    category_id = _create_category(db, name_suffix="FLOW4B")
    part_data = make_part_data(category_id=category_id)
    part_id = _create_part_with_stock(db, category_id, part_data, initial_stock=3)
    initial_stock = _stock_for_part(db, part_id)["quantity_on_hand"]

    po_id = purchase_crud.create_purchase_order(
        supplier_id=supplier_id,
        expected_date=None,
        items=make_purchase_items(part_id=part_id, quantity=7, unit_cost=9.0),
    )
    assert po_id

    cancelled = purchase_crud.cancel_purchase_order(purchase_order_id=po_id)
    assert cancelled["status"] == "Cancelled"

    # Stock is exactly what it was before the order was even created.
    assert _stock_for_part(db, part_id)["quantity_on_hand"] == initial_stock


# ---------------------------------------------------------------------------
# 5. Soft-delete / reactivate customer and part
# ---------------------------------------------------------------------------

def test_soft_delete_and_reactivate_customer_and_part(db):
    # Customer
    customer_data = make_customer_data()
    customer_crud.crear_cliente(
        first_name=customer_data["first_name"],
        last_name=customer_data["last_name"],
        identity_number=customer_data["identity_number"],
        tax_id=customer_data["tax_id"],
    )
    customer_row = _find_customer_by_tax(db, customer_data["tax_id"])
    assert customer_row["is_active"] in (1, True)

    assert customer_crud.deactivate_customer(customer_row["customer_id"]) is True
    assert _find_customer_by_tax(db, customer_data["tax_id"])["is_active"] in (0, False)

    # The Inactive filter must surface the row.
    inactive = customer_crud.listar_clientes(
        search=customer_data["identity_number"],
        status_filter="inactive",
    )
    assert any(c["tax_id"] == customer_data["tax_id"] for c in inactive)

    assert customer_crud.reactivate_customer(customer_row["customer_id"]) is True
    assert _find_customer_by_tax(db, customer_data["tax_id"])["is_active"] in (1, True)

    # Part
    category_id = _create_category(db, name_suffix="FLOW5")
    part_data = make_part_data(category_id=category_id)
    part_id = _create_part_with_stock(db, category_id, part_data, initial_stock=4)
    assert _find_part_by_code(db, part_data["internal_code"])["status"] == PartStatus.ACTIVE

    assert part_crud.deactivate_part(part_id) is True
    assert _find_part_by_code(db, part_data["internal_code"])["status"] == PartStatus.INACTIVE

    assert part_crud.reactivate_part(part_id) is True
    assert _find_part_by_code(db, part_data["internal_code"])["status"] == PartStatus.ACTIVE
