"""Shared pytest fixtures for the Zarvent Repuestos test suite.

Layered fixtures:

- ``app`` / ``client`` / ``auth_client`` are the Flask primitives used by
  both the route tests (with patched CRUDs) and integration smoke tests.
- ``mock_db_connection`` is the building block for unit tests that exercise
  CRUD functions with a ``MagicMock`` connection.
- The session-level autouse fixture ``_ensure_demo_schema`` runs the
  application ``crear_tablas()`` so any test that lands on the demo DB
  finds a consistent schema. It only does work on integration; for unit
  tests it is a no-op because they never touch the real connection.
"""

from __future__ import annotations

import os
from typing import Tuple
from unittest.mock import MagicMock

import pytest

from zarvent_repuestos.database.connection import get_database_connection
from zarvent_repuestos.web.app import app as flask_app


# ---------------------------------------------------------------------------
# Flask primitives
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Flask app configured for testing. Reset between tests so the secret
    key and the SQL trace state are predictable."""
    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret",
        WTF_CSRF_ENABLED=False,
    )
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client bound to the testing app."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client with a valid Flask session.

    We set the session via ``session_transaction`` instead of patching
    ``authenticate_user`` so the login flow itself is not exercised twice
    per test. Route tests can still assert on the session contents.
    """
    with client.session_transaction() as session_:
        session_["user_id"] = 1
        session_["username"] = "admin"
    return client


# ---------------------------------------------------------------------------
# MySQL mock primitives (used by tests/unit)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db_connection() -> Tuple[MagicMock, MagicMock]:
    """Returns a ``(mock_conn, mock_cursor)`` pair.

    The mock cursor is reachable both as ``mock_conn.cursor()`` (the
    default constructor) and ``mock_conn.cursor(dictionary=True)`` (the
    variant used by list endpoints). All unit tests should use this
    fixture instead of defining their own ``_make_connection()`` helper.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # `cursor()` and `cursor(dictionary=True)` must return the same mock
    # so that CRUDs that switch modes mid-flow still operate on the same
    # object. unittest.mock treats both call shapes as equal.
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# ---------------------------------------------------------------------------
# Demo database bootstrap (used only when integration tests run)
# ---------------------------------------------------------------------------

def _mysql_is_reachable() -> bool:
    """Returns True if the demo MySQL connection opens and closes cleanly."""
    try:
        connection = get_database_connection()
    except Exception:  # noqa: BLE001 - any error means "not reachable"
        return False
    try:
        connection.close()
    except Exception:  # noqa: BLE001
        return False
    return True


@pytest.fixture(scope="session", autouse=True)
def _ensure_demo_schema():
    """Creates/verifies the schema once per session so integration tests
    find a clean, up-to-date demo database. If MySQL is not reachable
    this fixture is a no-op; integration tests will skip themselves
    via the ``needs_mysql`` marker."""
    if not _mysql_is_reachable():
        yield
        return
    # Importing here so the cost is paid only when the DB is reachable.
    from zarvent_repuestos.database.init_db import crear_tablas

    try:
        crear_tablas()
    except Exception:  # noqa: BLE001 - tolerated; the conftest reports skips
        pass
    yield


# ---------------------------------------------------------------------------
# Test isolation
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_sql_trace_state():
    """Clears the SQL trace buffer and request context around every test.

    Several tests in ``test_sql_trace.py`` and the Flask routes inspect
    the global SQL trace state. Without this fixture, leakage between
    tests makes the assertions non-deterministic.
    """
    from zarvent_repuestos.database.sql_trace import (
        clear_request_context,
        clear_sql_trace_entries,
    )

    clear_sql_trace_entries()
    clear_request_context()
    # Opt-in only; tests that need the trace enabled must set the env
    # variable themselves. We never force-enable it because it doubles
    # the SQL execution path.
    os.environ.setdefault("SQL_TRACE_ENABLED", "0")
    yield
    clear_request_context()
