"""Domain models representing Supplier, PurchaseOrder, and PurchaseOrderItem entities."""


class Supplier:
    def __init__(self, business_name, tax_id, phone=None, email=None, address=None,
                 is_active=True, supplier_id=None):
        self.supplier_id = supplier_id
        self.business_name = business_name
        self.tax_id = tax_id
        self.phone = phone
        self.email = email
        self.address = address
        self.is_active = is_active

    def __str__(self):
        return f"{self.business_name} (NIT: {self.tax_id})"


class PurchaseOrder:
    def __init__(self, supplier_id, order_date, total_amount, expected_date=None,
                 status="Pending", purchase_order_id=None, supplier=None, items=None):
        self.purchase_order_id = purchase_order_id
        self.supplier_id = supplier_id
        self.order_date = order_date
        self.expected_date = expected_date
        self.status = status
        self.total_amount = total_amount
        self.supplier = supplier
        self.items = items if items is not None else []

    def __str__(self):
        return f"PurchaseOrder #{self.purchase_order_id} - {self.status} - ${self.total_amount}"


class PurchaseOrderItem:
    def __init__(self, purchase_order_id, part_id, quantity_ordered, unit_cost,
                 quantity_received=0, purchase_order_item_id=None, part=None):
        self.purchase_order_item_id = purchase_order_item_id
        self.purchase_order_id = purchase_order_id
        self.part_id = part_id
        self.quantity_ordered = quantity_ordered
        self.quantity_received = quantity_received
        self.unit_cost = unit_cost
        self.part = part

    def __str__(self):
        part_name = self.part.name if self.part else f"Part ID {self.part_id}"
        return f"{part_name}: ordered={self.quantity_ordered} received={self.quantity_received}"
