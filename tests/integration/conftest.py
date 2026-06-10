"""Fixtures for the integration test package.

Integration tests run against the real demo database
(``sis122_zarvent_repuestos``). Every test in this package is
automatically marked with ``needs_mysql``; if the database is
unreachable the whole package is skipped with a clear message.

Cleanup strategy: every test inserts rows whose unique columns carry
the ``TEST_CODX_`` prefix (see ``tests/factories.py``). The autouse
``cleanup_test_records`` fixture opens its own short-lived MySQL
connection, runs the cleanup queries **before** each test (to wipe
stale rows from a previous failed run) and **after** each test (to
leave the demo database clean for the next test in the queue).

Why a dedicated connection for cleanup and not the ``db`` fixture?
The ``db`` fixture is closed in its teardown; if cleanup depended on
it, the cleanup would run on a closed connection. A dedicated
connection is cheap and removes the ordering concern entirely.
"""

from __future__ import annotations

import mysql.connector
import pytest

from tests.conftest import _mysql_is_reachable
from tests.factories import CLEANUP_QUERIES, TEST_PREFIX, cleanup_params


# ---------------------------------------------------------------------------
# Skip marker applied to the whole package
# ---------------------------------------------------------------------------

needs_mysql = pytest.mark.skipif(
    not _mysql_is_reachable(),
    reason=(
        "MySQL demo database is not reachable. "
        "Run scripts/database/setup_database.py with admin credentials first."
    ),
)

# Applying the marker at module level so each test in the package is
# skipped automatically without per-test decoration.
pytestmark = needs_mysql


# ---------------------------------------------------------------------------
# Real MySQL connection (per test, autocommit on)
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    """Function-scoped real MySQL connection with autocommit enabled.

    Why per-test and not module-scoped: MySQL's default isolation
    level is REPEATABLE READ, which means a long-lived connection
    takes a snapshot at first SELECT and does not see rows committed
    by *other* connections afterwards. The CRUDs the tests exercise
    each open their own connection, so per-test connections are
    required to make the committed rows visible to the verification
    queries.

    Why autocommit=True: with autocommit on, every statement is its
    own transaction and the snapshot issue does not apply. This also
    makes the cleanup fixture's ``DELETE`` statements visible
    immediately to subsequent tests.
    """
    from zarvent_repuestos.config.db_config import DB_CONFIG

    config = dict(DB_CONFIG)
    config["autocommit"] = True
    connection = mysql.connector.connect(**config)
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture
def db_cursor(db):
    """Returns a fresh dictionary cursor on the real connection. The
    cursor is closed automatically when the fixture tears down."""
    cursor = db.cursor(dictionary=True)
    yield cursor
    cursor.close()


# ---------------------------------------------------------------------------
# Cleanup: wipe TEST_CODX_ rows BEFORE and AFTER every test
# ---------------------------------------------------------------------------

def _run_cleanup() -> None:
    """Opens a short-lived autocommit connection and runs every
    ``CLEANUP_QUERIES`` statement. Best-effort: if one query fails,
    the rest still run; failures are logged but never raised, so the
    test result is not masked by a cleanup bug."""
    from zarvent_repuestos.config.db_config import DB_CONFIG

    config = dict(DB_CONFIG)
    config["autocommit"] = True
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    try:
        for sql, param in zip(CLEANUP_QUERIES, cleanup_params(TEST_PREFIX)):
            try:
                cursor.execute(sql, (param,))
            except mysql.connector.Error:
                # Cleanup is best-effort: keep going so a failed
                # statement does not prevent the next one from
                # running. The next test's pre-cleanup will retry.
                connection.rollback()
                continue
    finally:
        cursor.close()
        connection.close()


@pytest.fixture(autouse=True)
def cleanup_test_records():
    """Wipes every row tagged with ``TEST_CODX_`` BEFORE and AFTER
    each test.

    Running cleanup before the test is the safety net: if a previous
    test crashed mid-way and left rows behind, the next test starts
    with a clean slate. Running cleanup after the test keeps the demo
    database tidy for developers inspecting it with DataGrip.
    """
    _run_cleanup()
    yield
    _run_cleanup()
