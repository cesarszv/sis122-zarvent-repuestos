"""Small tests for the Flask login flow."""

import unittest
from unittest.mock import patch

from zarvent_repuestos.web.app import app


class LoginFlowTest(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")

    def test_successful_login_uses_existing_user_service(self):
        with patch(
            "zarvent_repuestos.web.app.authenticate_user",
            return_value={"id": 1, "username": "admin"},
        ) as authenticate_user:
            response = app.test_client().post(
                "/",
                data={"username": " admin ", "password": "admin123"},
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/dashboard")
        authenticate_user.assert_called_once_with("admin", "admin123")


if __name__ == "__main__":
    unittest.main()
