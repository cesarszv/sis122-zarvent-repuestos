"""Fixtures specific to the unit test package.

The ``mock_db_connection`` fixture lives in the root ``conftest.py`` so
it is shared with other packages. This module re-exports the most
common fixtures for convenience and adds a parametrized helper for the
``PART_INTERNALS`` rotation used by some part CRUD tests.
"""

from __future__ import annotations

import pytest

from tests.conftest import mock_db_connection as _root_mock_db_connection


@pytest.fixture
def mock_db():
    """Alias of the root ``mock_db_connection`` that returns the cursor
    alone. Use this when a CRUD opens exactly one cursor."""
    _conn, cursor = _root_mock_db_connection()
    return cursor


# Re-export so `from conftest import mock_db_connection` keeps working
# inside the unit/ subtree.
mock_db_connection = _root_mock_db_connection
