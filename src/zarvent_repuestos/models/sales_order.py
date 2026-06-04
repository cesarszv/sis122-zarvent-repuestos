"""Domain models representing SalesOrder, SalesOrderItem, and Payment entities."""

class SalesOrder:
    def __init__(self, customer_id, order_date, subtotal, total_amount, discount_amount=0.00,
                 status='pending', sales_order_id=None, customer=None, items=None):
        self.sales_order_id = sales_order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.status = status
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.total_amount = total_amount
        # Relations
        self.customer = customer
        self.items = items if items is not None else []

    def __str__(self):
        return f"Order #{self.sales_order_id} - Total: ${self.total_amount} ({self.status})"


class SalesOrderItem:
    def __init__(self, sales_order_id, part_id, quantity, unit_price, discount_amount=0.00,
                 sales_order_item_id=None, part=None):
        self.sales_order_item_id = sales_order_item_id
        self.sales_order_id = sales_order_id
        self.part_id = part_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_amount = discount_amount
        # Relation
        self.part = part

    def __str__(self):
        part_name = self.part.name if self.part else f"Part ID {self.part_id}"
        return f"{self.quantity} x {part_name} @ ${self.unit_price}"


class Payment:
    def __init__(self, sales_order_id, payment_date, method, amount, reference_number=None,
                 status='completed', payment_id=None):
        self.payment_id = payment_id
        self.sales_order_id = sales_order_id
        self.payment_date = payment_date
        self.method = method
        self.amount = amount
        self.reference_number = reference_number
        self.status = status

    def __str__(self):
        return f"Payment #{self.payment_id} via {self.method} for ${self.amount}"
