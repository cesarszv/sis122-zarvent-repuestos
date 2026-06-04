"""Domain models representing PartCategory, Part, and InventoryStock entities."""

class PartCategory:
    def __init__(self, name, description=None, part_category_id=None):
        self.part_category_id = part_category_id
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Part:
    def __init__(self, part_category_id, internal_code, name, sale_price, purchase_cost, 
                 oem_code=None, brand=None, unit='pcs', warranty_days=0, status='active', 
                 part_id=None, category=None):
        self.part_id = part_id
        self.part_category_id = part_category_id
        self.internal_code = internal_code
        self.oem_code = oem_code
        self.name = name
        self.brand = brand
        self.unit = unit
        self.sale_price = sale_price
        self.purchase_cost = purchase_cost
        self.warranty_days = warranty_days
        self.status = status
        # Relation
        self.category = category

    def __str__(self):
        return f"[{self.internal_code}] {self.name} - {self.brand or 'Generic'}"


class InventoryStock:
    def __init__(self, part_id, location_name, quantity_on_hand=0, reorder_level=10, 
                 inventory_stock_id=None, part=None):
        self.inventory_stock_id = inventory_stock_id
        self.part_id = part_id
        self.location_name = location_name
        self.quantity_on_hand = quantity_on_hand
        self.reorder_level = reorder_level
        # Relation
        self.part = part

    def __str__(self):
        part_name = self.part.name if self.part else f"Part ID {self.part_id}"
        return f"{part_name} at {self.location_name}: {self.quantity_on_hand} units"
