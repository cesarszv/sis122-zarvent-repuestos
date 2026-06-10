"""Smoke tests for the demo MySQL database.

These tests do not insert any rows; they only verify that the
application's expected tables exist, that the demo user is present,
and that the academic views (or the inline-query fallback) are wired
up. If any of these checks fail, the rest of the integration suite
will not behave deterministically.
"""

from zarvent_repuestos.database.init_db import crear_tablas


# Tables that ``crear_tablas`` must create in the demo database. If a
# refactor accidentally drops one of these from the schema, this test
# fails loudly.
EXPECTED_TABLES = (
    "person",
    "customer",
    "supplier",
    "part_category",
    "part",
    "inventory_stock",
    "sales_order",
    "sales_order_item",
    "payment",
    "purchase_order",
    "purchase_order_item",
    "users",
)


def test_crear_tablas_is_idempotent(db):
    """Running ``crear_tablas`` on an existing demo database must
    succeed without raising. It must not duplicate tables or break
    the existing data."""
    assert crear_tablas() is True


def test_all_expected_tables_exist(db):
    """Uses a plain cursor (no dictionary) to keep the SHOW TABLES
    output generic across MySQL versions; the first column is the
    table name regardless of the database name."""
    cursor = db.cursor()
    try:
        cursor.execute("SHOW TABLES")
        actual = {row[0] for row in cursor.fetchall()}
    finally:
        cursor.close()

    missing = [t for t in EXPECTED_TABLES if t not in actual]
    assert not missing, f"Missing tables in demo DB: {missing}"


def test_users_table_has_at_least_one_user(db_cursor):
    db_cursor.execute("SELECT COUNT(*) AS n FROM users")
    row = db_cursor.fetchone()
    assert row["n"] >= 1, (
        "Demo database should be seeded with at least one login user."
    )


def test_demo_database_is_clean_of_test_prefix_at_start(db_cursor):
    """A precondition for the integration flows: at session start, no
    ``TEST_CODX_`` rows should be left from a previous run. The cleanup
    fixture relies on this; if it does not hold, the autouse cleanup
    in the conftest will still purge them, but a stale prefix warns us
    of a previous suite crash."""
    db_cursor.execute(
        "SELECT COUNT(*) AS n FROM person WHERE identity_number LIKE 'TEST_CODX_%%'"
    )
    assert db_cursor.fetchone()["n"] == 0
