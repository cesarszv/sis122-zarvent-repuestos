"""Small tests for the Flask login flow.

The login flow patches ``authenticate_user`` because that function
goes through bcrypt; we keep it out of the test surface and assert
that the route forwards the (stripped) credentials correctly and
redirects on success.
"""

from unittest.mock import patch

from tests.factories import make_login_form


def test_successful_login_uses_existing_user_service(client):
    with patch(
        "zarvent_repuestos.web.app.authenticate_user",
        return_value={"id": 1, "username": "admin"},
    ) as authenticate_user:
        response = client.post(
            "/", data=make_login_form(" admin ", "admin123"),
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/dashboard"
    authenticate_user.assert_called_once_with("admin", "admin123")
