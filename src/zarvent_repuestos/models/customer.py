"""Domain models representing Person and Customer entities."""

class Person:
    def __init__(self, first_name, last_name, identity_number, phone=None, email=None, address=None, person_id=None):
        self.person_id = person_id
        self.first_name = first_name
        self.last_name = last_name
        self.identity_number = identity_number
        self.phone = phone
        self.email = email
        self.address = address

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.identity_number})"


class Customer:
    def __init__(self, person_id, billing_name=None, tax_id=None, customer_id=None, person=None):
        self.customer_id = customer_id
        self.person_id = person_id
        self.billing_name = billing_name
        self.tax_id = tax_id
        # Optional relation object reference
        self.person = person

    def __str__(self):
        name = self.billing_name if self.billing_name else (str(self.person) if self.person else f"Customer #{self.customer_id}")
        return f"{name} (NIT/CI: {self.tax_id or 'N/A'})"
