"""Fixtures specific to the route test package.

Routes are exercised with the real Flask app (no app factory yet) but
with their downstream services patched. ``auth_client`` is already
provided by the root conftest; here we add helpers for the login flow
itself, which intentionally bypasses the session fixture.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from tests.conftest import auth_client as _root_auth_client
from tests.factories import make_login_form


# Re-export so route tests can `from conftest import auth_client`.
auth_client = _root_auth_client


@pytest.fixture
def login_response(client):
    """Performs a real POST against the login route with
    ``authenticate_user`` patched. Returns the response so individual
    tests can assert on it (e.g. redirect target, status code)."""
    with patch(
        "zarvent_repuestos.web.app.authenticate_user",
        return_value={"id": 1, "username": "admin"},
    ) as patched:
        response = client.post("/", data=make_login_form())
    return response, patched
