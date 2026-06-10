"""Centralized status and enum constants for the application.

Every constante es el string exacto que se persiste en MySQL.
No renombrar valores sin actualizar `init_db.py` y `database/schema.sql`.
"""



class SalesOrderStatus:
    """Status values for `sales_order.status` (RF-05, RF-06)."""

    PAID = "Paid"
    PENDING = "Pending"
    CANCELLED = "Cancelled"

    ALL = [PAID, PENDING, CANCELLED]
    # `Paid` es el unico estado que inserta la transaccion de venta actual.




class PurchaseOrderStatus:
    """Status values for `purchase_order.status` (RF-07)."""

    PENDING = "Pending"
    PARTIALLY_RECEIVED = "Partially Received"
    RECEIVED = "Received"
    CANCELLED = "Cancelled"

    ALL = [PENDING, PARTIALLY_RECEIVED, RECEIVED, CANCELLED]




class PaymentStatus:
    """Status values for `payment.status` (RF-06)."""

    COMPLETED = "Completed"
    PENDING = "Pending"


# Metodos de pago (valores exactos en `payment.method`).

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




class PartStatus:
    """Status values for `part.status` (soft-delete)."""

    ACTIVE = "active"
    INACTIVE = "inactive"

    ALL = [ACTIVE, INACTIVE]
    DEFAULT = ACTIVE


# customer.is_active es BOOLEAN, no VARCHAR. La clase agrupa los
# valores permitidos en el parametro ?filter= de /customers.

class CustomerActiveFilter:
    """Allowed values for the `?filter=` query parameter on /customers."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"

    CHOICES = [ACTIVE, INACTIVE, ALL]
    DEFAULT = ACTIVE




class SupplierActiveFilter:
    """Allowed values for the `?active=` query parameter on /purchases."""

    ACTIVE_ONLY = "1"
    ALL = "0"

    DEFAULT_ACTIVE_ONLY = True




class SalesListFilter:
    """Allowed values for the `?status=` query parameter on /sales."""

    ALL_ORDERS = "All Orders"
    PAID = SalesOrderStatus.PAID

    CHOICES = [ALL_ORDERS, PAID]
    DEFAULT = ALL_ORDERS
