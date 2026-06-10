"""Test data factories for the Zarvent Repuestos test suite.

Every value produced here carries the ``TEST_CODX_`` prefix on string fields
that hit unique columns (``internal_code``, ``tax_id``, ``identity_number``,
``business_name``). This makes the integration tests greppable: a developer
looking at the demo database in DataGrip can tell test rows apart from real
rows at a glance, and the integration autouse cleanup uses the prefix to
purge everything the suite created without needing per-test bookkeeping.

The factories are intentionally tiny. They are not full object models; they
return ``dict`` payloads ready to be passed to CRUD functions or HTTP form
``data=`` parameters. The unique-suffix is generated with ``uuid4().hex``
truncated to 8 chars so it is short enough to read in test output while still
colliding only in the heat death of the universe.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4


# Centralized prefix so a single edit changes the whole suite. Anything
# persisted in MySQL that needs to be cleaned up must use this prefix.
TEST_PREFIX = "TEST_CODX_"


def _suffix(explicit: Optional[str] = None) -> str:
    """Returns an 8-char hex suffix. Pass an explicit value to make test
    output deterministic (e.g. when debugging a failing case)."""
    return explicit or uuid4().hex[:8]


# ---------------------------------------------------------------------------
# Core domain dicts
# ---------------------------------------------------------------------------

def make_customer_data(suffix: Optional[str] = None) -> Dict[str, Any]:
    """Returns a dict ready for `customer_crud.crear_cliente` or the
    `/customers` POST form."""
    s = _suffix(suffix)
    return {
        "first_name": f"Name{s}",
        "last_name": f"Last{s}",
        "identity_number": f"{TEST_PREFIX}DOC{s}",
        "phone": f"7000{s[:4]}",
        "email": f"test{s}@example.com",
        "address": f"Av. Test {s}",
        "billing_name": f"Billing {s} SRL",
        "tax_id": f"{TEST_PREFIX}TAX{s}",
    }


def make_part_data(suffix: Optional[str] = None,
                   category_id: int = 1) -> Dict[str, Any]:
    """Returns a dict shaped like the `/inventory` POST form."""
    s = _suffix(suffix)
    return {
        "name": f"Repuesto Test {s}",
        "internal_code": f"{TEST_PREFIX}INT{s}",
        "oem_code": f"OEM-{s}",
        "brand": f"Brand{s[:4]}",
        "part_category_id": category_id,
        "sale_price": 100.0,
        "purchase_cost": 60.0,
        "initial_stock": 10,
        "location_name": "Aisle TEST",
        "unit": "pcs",
        "warranty_days": 0,
        "reorder_level": 5,
        "status": "active",
    }


def make_supplier_data(suffix: Optional[str] = None) -> Dict[str, Any]:
    """Returns a dict ready for `purchase_crud.create_supplier`."""
    s = _suffix(suffix)
    return {
        "business_name": f"{TEST_PREFIX}Supplier {s}",
        "tax_id": f"{TEST_PREFIX}SUP{s}",
        "phone": f"7200{s[:4]}",
        "email": f"supplier{s}@example.com",
        "address": f"Calle Test {s}",
    }


# ---------------------------------------------------------------------------
# Transaction payloads
# ---------------------------------------------------------------------------

def make_purchase_items(part_id: int,
                        quantity: int = 5,
                        unit_cost: float = 12.5) -> List[Dict[str, Any]]:
    """Returns the items list for `create_purchase_order`."""
    return [
        {"part_id": part_id, "quantity_ordered": quantity, "unit_cost": unit_cost},
    ]


def make_sale_items(part_id: int,
                    quantity: int = 2,
                    unit_price: float = 25.0,
                    discount_amount: float = 0.0) -> List[Dict[str, Any]]:
    """Returns the items list for `crear_orden_venta`."""
    return [
        {
            "part_id": part_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_amount": discount_amount,
        },
    ]


# ---------------------------------------------------------------------------
# Form payloads (Flask routes)
# ---------------------------------------------------------------------------

def make_login_form(username: str = "admin", password: str = "admin123") -> Dict[str, str]:
    """Returns the form `data=` for the `/` POST login form."""
    return {"username": username, "password": password}


# ---------------------------------------------------------------------------
# Cleanup queries
# ---------------------------------------------------------------------------
# These are DELETE statements used by the integration conftest to wipe
# everything tagged with the prefix. The order respects FK constraints:
# children first, parents last.
#
# Every WHERE clause filters on a string column carrying the
# ``TEST_CODX_`` prefix. We never touch rows outside the test scope, so
# the demo database stays intact between runs.
#
# Note: the ``users`` table is NOT cleaned; the demo admin user is
# required for the manual login flow.

CLEANUP_QUERIES: List[str] = [
    # 1. Payment rows whose sales_order is linked to a TEST_CODX_ customer.
    "DELETE FROM payment "
    "WHERE sales_order_id IN ("
    "  SELECT so.sales_order_id FROM sales_order so "
    "  JOIN customer c ON so.customer_id = c.customer_id "
    "  JOIN person p ON c.person_id = p.person_id "
    "  WHERE p.identity_number LIKE %s"
    ")",
    # 2. sales_order_item rows whose sales_order is linked to a TEST_CODX_ customer.
    "DELETE FROM sales_order_item "
    "WHERE sales_order_id IN ("
    "  SELECT so.sales_order_id FROM sales_order so "
    "  JOIN customer c ON so.customer_id = c.customer_id "
    "  JOIN person p ON c.person_id = p.person_id "
    "  WHERE p.identity_number LIKE %s"
    ")",
    # 3. sales_order rows whose customer is TEST_CODX_.
    "DELETE FROM sales_order "
    "WHERE customer_id IN ("
    "  SELECT c.customer_id FROM customer c "
    "  JOIN person p ON c.person_id = p.person_id "
    "  WHERE p.identity_number LIKE %s"
    ")",
    # 4. purchase_order_item rows whose purchase_order uses a TEST_CODX_ supplier.
    "DELETE FROM purchase_order_item "
    "WHERE purchase_order_id IN ("
    "  SELECT po.purchase_order_id FROM purchase_order po "
    "  JOIN supplier s ON po.supplier_id = s.supplier_id "
    "  WHERE s.tax_id LIKE %s"
    ")",
    # 5. purchase_order rows whose supplier is TEST_CODX_.
    "DELETE FROM purchase_order "
    "WHERE supplier_id IN ("
    "  SELECT s.supplier_id FROM supplier s WHERE s.tax_id LIKE %s"
    ")",
    # 6. inventory_stock rows whose part is TEST_CODX_.
    "DELETE FROM inventory_stock "
    "WHERE part_id IN ("
    "  SELECT part_id FROM part WHERE internal_code LIKE %s"
    ")",
    # 7. parts with TEST_CODX_ internal_code.
    "DELETE FROM part WHERE internal_code LIKE %s",
    # 8. part_category rows whose name carries the prefix.
    "DELETE FROM part_category WHERE name LIKE %s",
    # 9. supplier rows.
    "DELETE FROM supplier WHERE tax_id LIKE %s",
    # 10. customer rows linked to a TEST_CODX_ person.
    "DELETE FROM customer "
    "WHERE person_id IN ("
    "  SELECT person_id FROM person WHERE identity_number LIKE %s"
    ")",
    # 11. person rows with the prefix.
    "DELETE FROM person WHERE identity_number LIKE %s",
]


def cleanup_params(prefix: str = TEST_PREFIX) -> List[str]:
    """Returns the parameter list matching ``CLEANUP_QUERIES``.

    All eleven statements use the same ``prefix%`` LIKE pattern, so we
    can return the same value eleven times.
    """
    return [f"{prefix}%"] * len(CLEANUP_QUERIES)
