"""Domain model representing an administrative user."""

class User:
    def __init__(self, username, password, id=None):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return f"{self.id or 'NULL'} - {self.username}"
