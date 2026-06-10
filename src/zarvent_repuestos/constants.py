"""Centralized status and enum constants for the application.

All status values used across the model, CRUDs, templates, and views must be
imported from this module. The previous codebase used scattered string
literals (`'Paid'`, `'pending'`, `'Completed'`, etc.) which made it easy to
miss mismatches in SQL filters. The constants here match the exact strings
persisted in MySQL.

Conventions:

- Module-level enums are defined as plain classes (no need for `enum.Enum`
  because the values are string literals persisted in the database, and we
  want the strings to be directly comparable in SQL placeholders).
- Every constant is the **exact string** used in the database column. Do not
  rename values here without a migration; the column defaults in
  `init_db.py` and `database/schema.sql` must stay in sync.
- All names are uppercase. Comparisons with column values must be
  case-insensitive only at the SQL collation level (utf8mb4_unicode_ci),
  not at the Python level.
"""

# --- Sales order status ---------------------------------------------------

class SalesOrderStatus:
    """Status values for `sales_order.status` (RF-05, RF-06)."""

    PAID = "Paid"
    PENDING = "Pending"
    CANCELLED = "Cancelled"

    ALL = [PAID, PENDING, CANCELLED]
    # `Paid` is the only status actually inserted by the v1 transaction in
    # `sales_crud.crear_orden_venta`. The other values are reserved for v2.


# --- Purchase order status ------------------------------------------------

class PurchaseOrderStatus:
    """Status values for `purchase_order.status` (RF-07)."""

    PENDING = "Pending"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"

    ALL = [PENDING, PARTIALLY_RECEIVED, RECEIVED, CANCELLED]


# --- Payment status -------------------------------------------------------

class PaymentStatus:
    """Status values for `payment.status` (RF-06)."""

    COMPLETED = "Completed"
    PENDING = "Pending"


# --- Payment methods ------------------------------------------------------
# These literals are stored verbatim in `payment.method`. The Sales POS
# form offers exactly these four options in Latam Spanish.

PAYMENT_METHOD_CASH = "Efectivo"
PAYMENT_METHOD_DEBIT_CARD = "Tarjeta de Débito"
PAYMENT_METHOD_CREDIT_CARD = "Tarjeta de Crédito"
PAYMENT_METHOD_TRANSFER = "Transferencia"

PAYMENT_METHODS = [
    PAYMENT_METHOD_CASH,
    PAYMENT_METHOD_DEBIT_CARD,
    PAYMENT_METHOD_CREDIT_CARD,
    PAYMENT_METHOD_TRANSFER,
]


# --- Part (inventory) status ---------------------------------------------

class PartStatus:
    """Status values for `part.status` (soft-delete)."""

    ACTIVE = "active"
    INACTIVE = "inactive"

    ALL = [ACTIVE, INACTIVE]
    DEFAULT = ACTIVE


# --- Customer status (soft-delete via `is_active`) -----------------------
# Note: customer.is_active is a BOOLEAN column, not a VARCHAR with
# enumerated values. Use the class below for clarity in queries.

class CustomerActiveFilter:
    """Allowed values for the `?filter=` query parameter on /customers."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"

    CHOICES = [ACTIVE, INACTIVE, ALL]
    DEFAULT = ACTIVE


# --- Supplier status (soft-delete via `is_active`) ----------------------

class SupplierActiveFilter:
    """Allowed values for the `?active=` query parameter on /purchases."""

    ACTIVE_ONLY = "1"
    ALL = "0"

    DEFAULT_ACTIVE_ONLY = True


# --- Sales list filter (status query string) ----------------------------

class SalesListFilter:
    """Allowed values for the `?status=` query parameter on /sales."""

    ALL_ORDERS = "All Orders"
    PAID = SalesOrderStatus.PAID

    CHOICES = [ALL_ORDERS, PAID]
    DEFAULT = ALL_ORDERS
