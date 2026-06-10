"""Tests for the database setup helper.

These tests verify the SQL generator without touching the network. The
demo MySQL server is exercised by the integration suite, not here.
"""

from scripts.database.setup_database import build_admin_sql


def test_admin_sql_creates_and_updates_application_user():
    sql = build_admin_sql("sis122_zarvent_repuestos", "zarvent_app", "change_me")

    assert "CREATE DATABASE IF NOT EXISTS `sis122_zarvent_repuestos`" in sql
    assert "CREATE USER IF NOT EXISTS 'zarvent_app'@'localhost'" in sql
    assert (
        "ALTER USER 'zarvent_app'@'localhost' IDENTIFIED BY 'change_me'" in sql
    )
    assert "GRANT SELECT, INSERT, UPDATE, DELETE" in sql
