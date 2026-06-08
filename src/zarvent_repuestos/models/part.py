"""Domain models for the Part and PartCategory entities.

These classes exist because the inventory route in app.py and the
seed script instantiate ``Part`` directly. ``PartCategory`` is
returned as a typed object by ``part_crud.listar_categorias`` so
templates can use attribute access.
"""

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
