"""Tests for the database setup helper."""

import unittest

from scripts.database.setup_database import build_admin_sql


class SetupDatabaseTest(unittest.TestCase):
    def test_admin_sql_creates_and_updates_application_user(self):
        sql = build_admin_sql("sis122_zarvent_repuestos", "zarvent_app", "change_me")

        self.assertIn("CREATE DATABASE IF NOT EXISTS `sis122_zarvent_repuestos`", sql)
        self.assertIn("CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost'", sql)
        self.assertIn("ALTER USER 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me'", sql)
        self.assertIn("GRANT SELECT, INSERT, UPDATE, DELETE", sql)


if __name__ == "__main__":
    unittest.main()
